import cv2
import numpy as np
import sqlite3
import time
import os
import math
from datetime import datetime
from ultralytics import YOLO

# Create the automated screenshots target folder if it doesn't exist yet
# os.makedirs("alerts", create_mode=True if not os.path.exists("alerts") else False)
# if not os.path.exists("alerts"):
#     os.makedirs("alerts")
os.makedirs("alerts", exist_ok=True)

model = YOLO("models/yolov8n.pt")

video_sources = [
    "datasets/videos/railway_station.mp4",
    "datasets/videos/railway_st.mp4",
    "datasets/videos/railway_st1.mp4"
]
caps = [cv2.VideoCapture(src) for src in video_sources]

# Optimized Track Intrusion Coordinates
TRACK_ZONE_X1, TRACK_ZONE_Y1 = 0, 420
TRACK_ZONE_X2, TRACK_ZONE_Y2 = 520, 720

# Configuration variables for Crowd Tracking Integration
DISTANCE_THRESHOLD = 100
CROWD_THRESHOLD = 5

window_name = "Rakshak AI - Central Multi-Camera Control Center"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, 1400, 800)

last_logged_time = {i: {"TRACK": 0, "CROWD": 0} for i in range(len(video_sources))}

def log_alert_to_db(camera_id, alert_type, count, frame_to_save):
    """Logs the analytical anomaly to sqlite database and archives file evidence."""
    try:
        now_epoch = int(time.time())
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Form clean clean filename matching your pattern
        alert_clean_name = alert_type.replace(' ', '_').lower()
        filename = f"alerts/cam{camera_id}_{alert_clean_name}_{now_epoch}.jpg"
        
        # Save snapshot file to disk
        cv2.imwrite(filename, frame_to_save)
        
        # Save record line entry including the new file path metadata column
        conn = sqlite3.connect("database/alerts.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO alerts (timestamp, camera_name, alert_type, people_count, image_path) VALUES (?, ?, ?, ?, ?)",
            (now_str, f"Camera {camera_id}", alert_type, count, filename)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database/Snapshot Error: {e}")

while True:
    processed_frames = []
    total_system_people = 0
    active_crowd_alerts = 0
    active_track_alerts = 0
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

        # Draw danger zone track markers
        cv2.rectangle(annotated_frame, (TRACK_ZONE_X1, TRACK_ZONE_Y1), 
                      (TRACK_ZONE_X2, TRACK_ZONE_Y2), (0, 0, 255), 2)

        if results[0].boxes is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            total_people = len(boxes)
            total_system_people += total_people

            track_ids = []
            if results[0].boxes.id is not None:
                track_ids = results[0].boxes.id.int().cpu().tolist()

            for idx, box in enumerate(boxes):
                x1, y1, x2, y2 = map(int, box[:4])
                x_center = int((x1 + x2) / 2)
                y_center = int((y1 + y2) / 2)
                centers.append((x_center, y_center))
                
                p_id = track_ids[idx] if idx < len(track_ids) else idx + 1

                is_intruder = False
                if (TRACK_ZONE_X1 <= x_center <= TRACK_ZONE_X2) and (TRACK_ZONE_Y1 <= y_center <= TRACK_ZONE_Y2):
                    track_intrusion = True
                    is_intruder = True

                box_color = (0, 0, 255) if is_intruder else (255, 255, 0)
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), box_color, 2)
                cv2.putText(annotated_frame, f"P{p_id}", (x1, y1 - 7), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, box_color, 2)

        # BUG FIX: Accurate proximity grouping logic applied per camera stream
        crowd_gathering_detected = False
        max_group_count = 0
        for idx_a in range(len(centers)):
            group_count = 1
            for idx_b in range(len(centers)):
                if idx_a != idx_b:
                    dist = math.sqrt((centers[idx_a][0] - centers[idx_b][0])**2 + (centers[idx_a][1] - centers[idx_b][1])**2)
                    if dist < DISTANCE_THRESHOLD:
                        group_count += 1
            if group_count > max_group_count:
                max_group_count = group_count

        if max_group_count >= CROWD_THRESHOLD:
            crowd_gathering_detected = True

        # Process alerts states
        if track_intrusion:
            active_track_alerts += 1
            status_text = "DANGER: INTRUSION"
            status_color = (0, 0, 255)
            if current_time_epoch - last_logged_time[i]["TRACK"] > 5:
                log_alert_to_db(i + 1, "Track Intrusion", total_people, annotated_frame)
                last_logged_time[i]["TRACK"] = current_time_epoch
                
        elif crowd_gathering_detected:
            active_crowd_alerts += 1
            status_text = "WARNING: GATHERING"
            status_color = (0, 165, 255)
            if current_time_epoch - last_logged_time[i]["CROWD"] > 5:
                log_alert_to_db(i + 1, "Crowd Gathering", total_people, annotated_frame)
                last_logged_time[i]["CROWD"] = current_time_epoch
        else:
            status_text = "STATUS: SAFE"
            status_color = (0, 255, 0)

        # Individual Video Feed Overlays
        cv2.rectangle(annotated_frame, (0, 0), (320, 95), (15, 15, 15), -1)
        cv2.putText(annotated_frame, f"CAMERA CH 0{i + 1}", (15, 25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(annotated_frame, f"People: {total_people}", (15, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(annotated_frame, status_text, (15, 75), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 2)

        resized_view = cv2.resize(annotated_frame, (640, 360))
        processed_frames.append(resized_view)

    # Render unified layout HUD panels
    dashboard_summary = np.zeros_like(processed_frames[2])
    current_time = datetime.now().strftime("%H:%M:%S")

    cv2.putText(dashboard_summary, "RAKSHAK AI COMMAND CENTER", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    cv2.putText(dashboard_summary, f"Time: {current_time} | Active Feeds: {len(video_sources)}", (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (240, 240, 240), 1)
    cv2.putText(dashboard_summary, f"Total System Passengers: {total_system_people}", (20, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
    cv2.putText(dashboard_summary, f"Active Live Alerts: Crowd={active_crowd_alerts} | Track={active_track_alerts}", (20, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 165, 255) if (active_crowd_alerts+active_track_alerts)>0 else (150,150,150), 1)

    cv2.putText(dashboard_summary, "RECENT SECURITY LOGS (DB ACCESS):", (20, 165), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    try:
        conn = sqlite3.connect("database/alerts.db")
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, camera_name, alert_type FROM alerts ORDER BY id DESC LIMIT 4")
        recent_logs = cursor.fetchall()
        conn.close()
        y_offset = 200
        for log in recent_logs:
            t_stamp = log[0].split(" ")[1]
            log_line = f"[{t_stamp}] {log[1]} - {log[2]}"
            text_color = (0, 0, 255) if "Intrusion" in log[2] else (0, 165, 255)
            cv2.putText(dashboard_summary, log_line, (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.4, text_color, 1)
            y_offset += 25
    except Exception:
        cv2.putText(dashboard_summary, "Awaiting thread logs...", (20, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (100, 100, 100), 1)

    top_row = np.hstack((processed_frames[0], processed_frames[1]))
    bottom_row = np.hstack((processed_frames[2], dashboard_summary))
    control_wall_grid = np.vstack((top_row, bottom_row))

    cv2.imshow(window_name, control_wall_grid)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

for cap in caps:
    cap.release()
cv2.destroyAllWindows()
cv2.waitKey(1)