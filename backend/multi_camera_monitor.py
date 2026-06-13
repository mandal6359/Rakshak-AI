import cv2
import numpy as np
import sqlite3
import time
import os
import math
import winsound
from datetime import datetime
from ultralytics import YOLO

# Expose backend child modules to system workspace environment execution loops
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.email_alert import send_security_alert_email

os.makedirs("alerts", exist_ok=True)
model = YOLO("models/yolov8n.pt")

# =========================================================================
# INDUSTRIAL NETWORK LAYER: DYNAMIC RTSP CAPTURE STREAM ENGINE WITH FALLBACK
# =========================================================================
def initialize_camera_streams():
    """Queries active database camera registries and attempts network handshakes."""
    conn = sqlite3.connect("database/alerts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT camera_name, camera_path, location FROM cameras WHERE status='ONLINE'")
    db_feeds = cursor.fetchall()
    conn.close()
    
    active_caps = []
    active_names = []
    
    for feed in db_feeds:
        name, path, location = feed
        print(f"📡 Attempting network socket handshake with {name} at URI: {path}...")
        
        cap = cv2.VideoCapture(path)
        
        # Network verification block routine check
        if not cap.isOpened():
            print(f"⚠️ Warning: Connection to live RTSP endpoint '{path}' dropped or unroutable.")
            # Fail-safe automatic recovery loop to local dataset file mock arrays for flawless hackathon presentations
            mock_fallback_path = "datasets/videos/railway_station.mp4"
            print(f"🔄 Activating Fail-Safe Layer: Redirecting {name} to local backup array resource: {mock_fallback_path}")
            cap = cv2.VideoCapture(mock_fallback_path)
            
        active_caps.append(cap)
        active_names.append(name)
        
    return active_caps, active_names

caps, camera_names = initialize_camera_streams()
# =========================================================================

TRACK_ZONE_X1, TRACK_ZONE_Y1, TRACK_ZONE_X2, TRACK_ZONE_Y2 = 0, 420, 520, 720
DISTANCE_THRESHOLD = 100
CROWD_THRESHOLD = 5

last_logged_time = {i: {"TRACK": 0, "CROWD": 0} for i in range(len(caps))}
last_screenshot_time = {i: 0 for i in range(len(caps))}

def update_zone_in_db(zone_name, count, status):
    try:
        conn = sqlite3.connect("database/alerts.db")
        cursor = conn.cursor()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "UPDATE zones SET people_count=?, status=?, last_updated=? WHERE zone_name=?",
            (count, status, now_str, zone_name)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Zone Sync Error: {e}")

def log_alert_to_db(camera_id, camera_name, alert_type, count, severity, frame_to_save):
    try:
        now_epoch = int(time.time())
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = None
        
        # Bounded hard drive safeguard parameters rule check
        if severity in ["CRITICAL", "EMERGENCY"]:
            if now_epoch - last_screenshot_time[camera_id] > 30:
                filename = f"alerts/{camera_name.lower().replace(' ', '_')}_{now_epoch}.jpg"
                cv2.imwrite(filename, frame_to_save)
                last_screenshot_time[camera_id] = now_epoch

        conn = sqlite3.connect("database/alerts.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO alerts (timestamp, camera_name, alert_type, people_count, image_path, severity) VALUES (?, ?, ?, ?, ?, ?)",
            (now_str, camera_name, alert_type, count, filename, severity)
        )
        conn.commit()
        conn.close()

        # Execute high priority notification mail delivery dispatches 
        if filename and severity in ["CRITICAL", "EMERGENCY"]:
            html_payload = f"""
            <h3>🚨 RAKSHAK AI — SYSTEM ALARM EVENT BROADCAST</h3>
            <p><b>Threat Level Priority Class:</b> <span style='color:red;'>{severity}</span></p>
            <p><b>Event Anomaly Type:</b> {alert_type}</p>
            <p><b>Source Hardware Identity:</b> {camera_name}</p>
            <p><b>Calculated On-Scene Population:</b> {count} Persons</p>
            <p><b>Timestamp:</b> {now_str}</p>
            """
            send_security_alert_email(
                subject=f"CRITICAL OVERHEAT BREACH: {alert_type} verified on {camera_name}",
                text_message=html_payload,
                attachment_path=filename
            )
            
    except Exception as e:
        print(f"Logging System Error: {e}")

global_frame_ticks = 0
print("🚀 Rakshak AI Industrial RTSP Network Server Platform initialized.")

while True:
    processed_frames = []
    total_system_people = 0
    current_time_epoch = time.time()
    global_frame_ticks += 1

    for i, cap in enumerate(caps):
        success, frame = cap.read()
        if not success:
            # Re-index looping sequence safely if backup streams complete execution
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            success, frame = cap.read()
            if not success:
                frame = np.zeros((540, 960, 3), dtype=np.uint8)

        # Performance constraints downscaler optimization step
        frame = cv2.resize(frame, (640, 360))

        if global_frame_ticks % 5 != 0:
            processed_frames.append(frame)
            continue

        annotated_frame = frame.copy()
        results = model.track(frame, persist=True, classes=[0], verbose=False)
        
        centers = []
        track_intrusion = False
        total_people = 0
        cam1_track_count = 0
        cam1_platform_count = 0

        SCALE_X, SCALE_Y = 640 / 960, 360 / 540
        current_zone_x1, current_zone_y1 = int(TRACK_ZONE_X1 * SCALE_X), int(TRACK_ZONE_Y1 * SCALE_Y)
        current_zone_x2, current_zone_y2 = int(TRACK_ZONE_X2 * SCALE_X), int(TRACK_ZONE_Y2 * SCALE_Y)

        cv2.rectangle(annotated_frame, (current_zone_x1, current_zone_y1), (current_zone_x2, current_zone_y2), (0, 0, 255), 1)

        if results[0].boxes is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            total_people = len(boxes)
            total_system_people += total_people
            track_ids = results[0].boxes.id.int().cpu().tolist() if results[0].boxes.id is not None else []

            for idx, box in enumerate(boxes):
                x1, y1, x2, y2 = map(int, box[:4])
                x_center, y_center = int((x1 + x2) / 2), int((y1 + y2) / 2)
                centers.append((x_center, y_center))

                if (current_zone_x1 <= x_center <= current_zone_x2) and (current_zone_y1 <= y_center <= current_zone_y2):
                    track_intrusion = True
                    cam1_track_count += 1
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 0, 255), 1)
                else:
                    cam1_platform_count += 1
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (255, 255, 0), 1)

        crowd_gathering_detected = False
        max_group_count = 0
        for idx_a in range(len(centers)):
            group_count = 1
            for idx_b in range(len(centers)):
                if idx_a != idx_b:
                    if math.sqrt((centers[idx_a][0] - centers[idx_b][0])**2 + (centers[idx_a][1] - centers[idx_b][1])**2) < (DISTANCE_THRESHOLD * SCALE_X):
                        group_count += 1
            if group_count > max_group_count:
                max_group_count = group_count

        if max_group_count >= CROWD_THRESHOLD:
            crowd_gathering_detected = True

        if track_intrusion:
            severity = "EMERGENCY" if cam1_track_count >= 2 else "CRITICAL"
            status_text = f"🚨 {severity}: INTRUSION"
            status_color = (0, 0, 255)
            
            if severity == "CRITICAL": winsound.Beep(1000, 150)
            elif severity == "EMERGENCY": winsound.Beep(1500, 300)

            if current_time_epoch - last_logged_time[i]["TRACK"] > 10:  
                log_alert_to_db(i, camera_names[i], "Track Intrusion", total_people, severity, annotated_frame)
                last_logged_time[i]["TRACK"] = current_time_epoch
                
        elif crowd_gathering_detected:
            if total_people > 20: severity = "CRITICAL"
            elif total_people > 15: severity = "VERY HIGH"
            else: severity = "HIGH"
            
            status_text = f"⚠️ {severity} CROWD"
            status_color = (0, 165, 255)
            
            if severity == "CRITICAL": winsound.Beep(1000, 150)

            if current_time_epoch - last_logged_time[i]["CROWD"] > 10:
                log_alert_to_db(i, camera_names[i], "Crowd Gathering", total_people, severity, annotated_frame)
                last_logged_time[i]["CROWD"] = current_time_epoch
        else:
            status_text = "STATUS: SAFE"
            status_color = (0, 255, 0)

        if camera_names[i] == "Camera 01":
            update_zone_in_db("Platform 1 Track Area", cam1_track_count, "DANGER" if track_intrusion else "NORMAL")
            update_zone_in_db("Platform 1 Passenger Walkway", cam1_platform_count, "CROWDED" if crowd_gathering_detected else "NORMAL")
        elif camera_names[i] == "Camera 02":
            update_zone_in_db("Main Waiting Hall Center", total_people, "CROWDED" if crowd_gathering_detected else "NORMAL")
        elif camera_names[i] == "Camera 03":
            update_zone_in_db("Ticketing Counter Queue", total_people, "CROWDED" if crowd_gathering_detected else "NORMAL")

        cv2.rectangle(annotated_frame, (0, 0), (220, 65), (15, 15, 15), -1)
        cv2.putText(annotated_frame, camera_names[i], (10, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
        cv2.putText(annotated_frame, f"People: {total_people}", (10, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        cv2.putText(annotated_frame, status_text, (10, 54), cv2.FONT_HERSHEY_SIMPLEX, 0.4, status_color, 1)

        resized_frame = cv2.resize(annotated_frame, (640, 360))
        processed_frames.append(resized_frame)
        cv2.imwrite(f"alerts/live_cam_{i+1}.jpg", resized_frame)

    if len(processed_frames) == len(camera_names):
        top_row = np.hstack((processed_frames[0], processed_frames[1]))
        bottom_row = np.hstack((processed_frames[2], np.zeros_like(processed_frames[0])))
        cv2.imshow("Rakshak AI - Computer Vision Stream Server", np.vstack((top_row, bottom_row)))

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

for cap in caps: cap.release()
cv2.destroyAllWindows()