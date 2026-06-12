import cv2
import numpy as np
import sqlite3
import time
import os
import math
import winsound  # <--- Added for control room sirens dispatch
from datetime import datetime
from ultralytics import YOLO

os.makedirs("alerts", exist_ok=True)
model = YOLO("models/yolov8n.pt")

def load_cameras_from_db():
    conn = sqlite3.connect("database/alerts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT camera_name, camera_path FROM cameras WHERE status='ONLINE'")
    feeds = cursor.fetchall()
    conn.close()
    return feeds

camera_feeds = load_cameras_from_db()
video_sources = [feed[1] for feed in camera_feeds]
camera_names = [feed[0] for feed in camera_feeds]
caps = [cv2.VideoCapture(src) for src in video_sources]

TRACK_ZONE_X1, TRACK_ZONE_Y1, TRACK_ZONE_X2, TRACK_ZONE_Y2 = 0, 420, 520, 720
DISTANCE_THRESHOLD = 100
CROWD_THRESHOLD = 5

last_logged_time = {i: {"TRACK": 0, "CROWD": 0} for i in range(len(video_sources))}

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

def log_alert_to_db(camera_name, alert_type, count, severity, frame_to_save):
    try:
        now_epoch = int(time.time())
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = f"alerts/{camera_name.lower().replace(' ', '_')}_{now_epoch}.jpg"
        cv2.imwrite(filename, frame_to_save)
        
        conn = sqlite3.connect("database/alerts.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO alerts (timestamp, camera_name, alert_type, people_count, image_path, severity) VALUES (?, ?, ?, ?, ?, ?)",
            (now_str, camera_name, alert_type, count, filename, severity)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Logging Error: {e}")

while True:
    processed_frames = []
    total_system_people = 0
    current_time_epoch = time.time()

    for i, cap in enumerate(caps):
        success, frame = cap.read()
        if not success:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            success, frame = cap.read()
            if not success:
                frame = np.zeros((540, 960, 3), dtype=np.uint8)

        annotated_frame = frame.copy()
        results = model.track(frame, persist=True, classes=[0], verbose=False)
        
        centers = []
        track_intrusion = False
        total_people = 0
        cam1_track_count = 0
        cam1_platform_count = 0

        cv2.rectangle(annotated_frame, (TRACK_ZONE_X1, TRACK_ZONE_Y1), (TRACK_ZONE_X2, TRACK_ZONE_Y2), (0, 0, 255), 2)

        if results[0].boxes is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            total_people = len(boxes)
            total_system_people += total_people
            track_ids = results[0].boxes.id.int().cpu().tolist() if results[0].boxes.id is not None else []

            for idx, box in enumerate(boxes):
                x1, y1, x2, y2 = map(int, box[:4])
                x_center, y_center = int((x1 + x2) / 2), int((y1 + y2) / 2)
                centers.append((x_center, y_center))

                if (TRACK_ZONE_X1 <= x_center <= TRACK_ZONE_X2) and (TRACK_ZONE_Y1 <= y_center <= TRACK_ZONE_Y2):
                    track_intrusion = True
                    cam1_track_count += 1
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                else:
                    cam1_platform_count += 1
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (255, 255, 0), 2)

        crowd_gathering_detected = False
        max_group_count = 0
        for idx_a in range(len(centers)):
            group_count = 1
            for idx_b in range(len(centers)):
                if idx_a != idx_b:
                    if math.sqrt((centers[idx_a][0] - centers[idx_b][0])**2 + (centers[idx_a][1] - centers[idx_b][1])**2) < DISTANCE_THRESHOLD:
                        group_count += 1
            if group_count > max_group_count:
                max_group_count = group_count

        if max_group_count >= CROWD_THRESHOLD:
            crowd_gathering_detected = True

        # =========================================================================
        # AUTOMATED SEVERITY SELECTION ENGINE & SPECIFIC WINSOUND SIRENS
        # =========================================================================
        if track_intrusion:
            severity = "EMERGENCY" if cam1_track_count >= 2 else "CRITICAL"
            status_text = f"🚨 {severity}: INTRUSION"
            status_color = (0, 0, 255)
            
            # Contextual audio sirens routing configuration
            if severity == "CRITICAL":
                winsound.Beep(1000, 500)
            elif severity == "EMERGENCY":
                winsound.Beep(1500, 1000)
                
            if current_time_epoch - last_logged_time[i]["TRACK"] > 5:
                log_alert_to_db(camera_names[i], "Track Intrusion", total_people, severity, annotated_frame)
                last_logged_time[i]["TRACK"] = current_time_epoch
                
        elif crowd_gathering_detected:
            if total_people > 40: severity = "CRITICAL"
            elif total_people > 30: severity = "VERY HIGH"
            else: severity = "HIGH"
            
            status_text = f"⚠️ {severity} CROWD"
            status_color = (0, 165, 255)
            
            if severity == "CRITICAL":
                winsound.Beep(1000, 500)
                
            if current_time_epoch - last_logged_time[i]["CROWD"] > 5:
                log_alert_to_db(camera_names[i], "Crowd Gathering", total_people, severity, annotated_frame)
                last_logged_time[i]["CROWD"] = current_time_epoch
        else:
            status_text = "STATUS: SAFE"
            status_color = (0, 255, 0)

        # Sync current state metrics to the database
        if camera_names[i] == "Camera 01":
            update_zone_in_db("Platform 1 Track Area", cam1_track_count, "DANGER" if track_intrusion else "NORMAL")
            update_zone_in_db("Platform 1 Passenger Walkway", cam1_platform_count, "CROWDED" if crowd_gathering_detected else "NORMAL")
        elif camera_names[i] == "Camera 02":
            update_zone_in_db("Main Waiting Hall Center", total_people, "CROWDED" if crowd_gathering_detected else "NORMAL")
        elif camera_names[i] == "Camera 03":
            update_zone_in_db("Ticketing Counter Queue", total_people, "CROWDED" if crowd_gathering_detected else "NORMAL")

        cv2.rectangle(annotated_frame, (0, 0), (320, 95), (15, 15, 15), -1)
        cv2.putText(annotated_frame, camera_names[i], (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(annotated_frame, f"People: {total_people}", (15, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(annotated_frame, status_text, (15, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 2)

        resized_frame = cv2.resize(annotated_frame, (640, 360))
        processed_frames.append(resized_frame)
        cv2.imwrite(f"alerts/live_cam_{i+1}.jpg", resized_frame)

    dashboard_summary = np.zeros_like(processed_frames[0])
    top_row = np.hstack((processed_frames[0], processed_frames[1]))
    bottom_row = np.hstack((processed_frames[2], dashboard_summary))
    cv2.imshow("Rakshak AI - Computer Vision Stream Server", np.vstack((top_row, bottom_row)))

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

for cap in caps:
    cap.release()
cv2.destroyAllWindows()