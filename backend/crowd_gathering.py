import cv2
import math
import time  # 1. Added time module for the validation timer
from ultralytics import YOLO

# Initialize YOLO Model
model = YOLO("models/yolov8n.pt")

# Open Video Stream
video_path = "datasets/videos/track_intrusion_1.mp4"
cap = cv2.VideoCapture(video_path)

# Set up the professional display window
window_name = "Rakshak AI - Crowd Gathering Detection v2"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, 1200, 700)

# ==========================================
# CROWD DETECTION CONFIGURATION
# ==========================================
DISTANCE_THRESHOLD = 100   # Max distance in pixels to consider people "close"
CROWD_THRESHOLD = 5        # Minimum number of close people to trigger a cluster
TIME_THRESHOLD = 10.0      # How many seconds a crowd must persist before alert
# ==========================================

# 2. Initialize the timer variable before the loop
gathering_start_time = None

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # Run YOLO tracker silently
    results = model.track(frame, persist=True, classes=[0], verbose=False)
    
    # Get the annotated image frame
    annotated_frame = results[0].plot()

    centers = []

    # Extract bounding box coordinates if people are detected
    if results[0].boxes is not None:
        boxes = results[0].boxes.xyxy.cpu().numpy()
        
        for box in boxes:
            x1, y1, x2, y2 = box[:4]
            x_center = int((x1 + x2) / 2)
            y_center = int((y1 + y2) / 2)
            centers.append((x_center, y_center))
            
            # Draw center point marker
            cv2.circle(annotated_frame, (x_center, y_center), 5, (0, 255, 0), -1)

    # Check distances to find crowd groups
    total_people = len(centers)
    crowd_detected = False
    max_group_count = 0

    for i in range(total_people):
        group_count = 1
        for j in range(total_people):
            if i != j:
                dist = math.sqrt((centers[i][0] - centers[j][0])**2 + (centers[i][1] - centers[j][1])**2)
                if dist < DISTANCE_THRESHOLD:
                    group_count += 1
        
        if group_count > max_group_count:
            max_group_count = group_count

    # ==========================================
    # SMART TIMER LOGIC (Filters False Positives)
    # ==========================================
    if max_group_count >= CROWD_THRESHOLD:
        # If the crowd just formed, start the clock
        if gathering_start_time is None:
            gathering_start_time = time.time()
        
        # Calculate how long this specific crowd has been gathering
        elapsed_time = time.time() - gathering_start_time
        
        # Only trigger alert if crowd persists longer than our threshold
        if elapsed_time > TIME_THRESHOLD:
            crowd_detected = True
    else:
        # Reset the timer immediately if the crowd breaks up
        gathering_start_time = None
    # ==========================================

    # ==========================================
    # VISUAL OUTPUT: HEADS-UP DISPLAY (HUD)
    # ==========================================
    # Expand the background banner to fit the new debug metrics
    cv2.rectangle(annotated_frame, (0, 0), (450, 160), (0, 0, 0), -1)
    
    # Display Total People Count
    cv2.putText(annotated_frame, f"People Count: {total_people}", (20, 35), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # Display Largest Group Size (New Debug Metric)
    cv2.putText(annotated_frame, f"Largest Group: {max_group_count}", (20, 70), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    # Display Dynamic Timer Progress
    if gathering_start_time is not None and not crowd_detected:
        timer_text = f"Forming... ({elapsed_time:.1f}s / {TIME_THRESHOLD}s)"
        cv2.putText(annotated_frame, timer_text, (20, 105), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
    elif crowd_detected:
        cv2.putText(annotated_frame, f"Duration: {elapsed_time:.1f}s", (20, 105), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    else:
        cv2.putText(annotated_frame, "Timer: Idle", (20, 105), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 1)

    # Display Security Status
    if crowd_detected:
        cv2.putText(annotated_frame, "STATUS: !!! CROWD GATHERING !!!", (20, 140), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)
    else:
        cv2.putText(annotated_frame, "STATUS: SAFE", (20, 140), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    # ==========================================

    # Show the results
    cv2.imshow(window_name, annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
cv2.waitKey(1)