import cv2
import numpy as np
from datetime import datetime
from ultralytics import YOLO

# 1. Initialize the YOLO model
model = YOLO("models/yolov8n.pt")

# 2. Define multi-camera streams
video_sources = [
    "datasets/videos/railway_station.mp4",
    "datasets/videos/railway_st.mp4",
    "datasets/videos/railway_st1.mp4"
]

caps = [cv2.VideoCapture(src) for src in video_sources]

# Optimized Track Intrusion Zone Coordinates
TRACK_ZONE_X1, TRACK_ZONE_Y1 = 0, 420
TRACK_ZONE_X2, TRACK_ZONE_Y2 = 520, 720

window_name = "Rakshak AI - Central Multi-Camera Control Center"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, 1400, 800)

print("Rakshak AI Multi-Camera Server Active with Custom HUD Rendering...")

while True:
    processed_frames = []
    
    # Global counters for the Command Center (Reset every frame cycle)
    total_system_people = 0
    active_crowd_alerts = 0
    active_track_alerts = 0

    # Loop through each camera feed
    for i, cap in enumerate(caps):
        success, frame = cap.read()
        
        # Continuous stream loopback configuration
        if not success:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            success, frame = cap.read()
            if not success:
                frame = np.zeros((540, 960, 3), dtype=np.uint8)

        # IMPORTANT: We DO NOT use results[0].plot() anymore to avoid messy labels.
        # Instead, we copy the raw frame and draw our own custom boxes.
        annotated_frame = frame.copy()

        # Run analytics silently
        results = model.track(frame, persist=True, classes=[0], verbose=False)
        
        total_people = 0
        track_intrusion = False

        # Draw the Track Zone boundary cleanly
        cv2.rectangle(annotated_frame, (TRACK_ZONE_X1, TRACK_ZONE_Y1), 
                      (TRACK_ZONE_X2, TRACK_ZONE_Y2), (0, 0, 255), 2)

        if results[0].boxes is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            total_people = len(boxes)
            total_system_people += total_people  # Add to command center grand total

            # Check if IDs are available from ByteTrack
            track_ids = []
            if results[0].boxes.id is not None:
                track_ids = results[0].boxes.id.int().cpu().tolist()

            # Iterate through targets to draw customized minimalist boxes
            for idx, box in enumerate(boxes):
                x1, y1, x2, y2 = map(int, box[:4])
                x_center = int((x1 + x2) / 2)
                y_center = int((y1 + y2) / 2)

                # Fetch unique tracking ID if it exists, otherwise fall back to sequential loop index
                p_id = track_ids[idx] if idx < len(track_ids) else idx + 1

                # Evaluate Track Zone Intrusion
                is_intruder = False
                if (TRACK_ZONE_X1 <= x_center <= TRACK_ZONE_X2) and (TRACK_ZONE_Y1 <= y_center <= TRACK_ZONE_Y2):
                    track_intrusion = True
                    is_intruder = True

                # Select box color: Red if intruding, Cyan/Green if safe
                box_color = (0, 0, 255) if is_intruder else (255, 255, 0)

                # Draw minimalist bounding box around the passenger
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), box_color, 2)

                # Draw clean custom label tag (e.g., "P14")
                label = f"P{p_id}"
                cv2.putText(annotated_frame, label, (x1, y1 - 7), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_color, 2)

        # Update global alert aggregators based on camera analytics
        if track_intrusion:
            active_track_alerts += 1
            status_text = "DANGER: INTRUSION"
            status_color = (0, 0, 255)
        elif total_people > 20:  # Simple crowd threshold for warning
            active_crowd_alerts += 1
            status_text = "WARNING: CROWDED"
            status_color = (0, 165, 255)
        else:
            status_text = "STATUS: SAFE"
            status_color = (0, 255, 0)

        # Draw a dark metadata overlay panel on top of each channel feed
        cv2.rectangle(annotated_frame, (0, 0), (320, 95), (15, 15, 15), -1)
        cv2.putText(annotated_frame, f"CAMERA CH 0{i + 1}", (15, 25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(annotated_frame, f"People: {total_people}", (15, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(annotated_frame, status_text, (15, 75), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 2)

        # Resize for layout symmetry
        resized_view = cv2.resize(annotated_frame, (640, 360))
        processed_frames.append(resized_view)

    # 4. Construct the Command Center Analytics Display Panel
    dashboard_summary = np.zeros_like(processed_frames[2])
    
    # Generate real-time system clock string
    current_time = datetime.now().strftime("%H:%M:%S")

    # Draw Text Elements inside the Command Center Window Block
    cv2.putText(dashboard_summary, "RAKSHAK AI COMMAND CENTER", (30, 45), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    cv2.putText(dashboard_summary, f"System Time  : {current_time}", (30, 90), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (240, 240, 240), 1)
    
    cv2.putText(dashboard_summary, f"Total Cameras: {len(video_sources)}", (30, 130), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    cv2.putText(dashboard_summary, f"Total People : {total_system_people}", (30, 170), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    # Dynamic styling for Crowd Alerts counter
    crowd_color = (0, 165, 255) if active_crowd_alerts > 0 else (200, 200, 200)
    cv2.putText(dashboard_summary, f"Crowd Alerts : {active_crowd_alerts}", (30, 210), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, crowd_color, 2 if active_crowd_alerts > 0 else 1)
    
    # Dynamic styling for Track Alerts counter
    track_color = (0, 0, 255) if active_track_alerts > 0 else (200, 200, 200)
    cv2.putText(dashboard_summary, f"Track Alerts : {active_track_alerts}", (30, 250), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, track_color, 2 if active_track_alerts > 0 else 1)
    
    # System Operational Integrity Status
    sys_status_text = "SYSTEM STATUS: SYSTEM THREAT" if (active_track_alerts > 0 or active_crowd_alerts > 0) else "SYSTEM STATUS: ACTIVE"
    sys_status_color = (0, 0, 255) if (active_track_alerts > 0 or active_crowd_alerts > 0) else (0, 255, 0)
    cv2.putText(dashboard_summary, sys_status_text, (30, 310), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, sys_status_color, 2)

    # Assemble the 2x2 multi-camera screen matrix
    top_row = np.hstack((processed_frames[0], processed_frames[1]))
    bottom_row = np.hstack((processed_frames[2], dashboard_summary))
    control_wall_grid = np.vstack((top_row, bottom_row))

    # Output to the screen
    cv2.imshow(window_name, control_wall_grid)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        print("Safely powering down monitoring wall matrix...")
        break

for cap in caps:
    cap.release()
cv2.destroyAllWindows()
cv2.waitKey(1)