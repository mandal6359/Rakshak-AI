import cv2
from ultralytics import YOLO

# 1. Load the model once
from config import *

model = YOLO(MODEL_PATH)

video_path = "datasets/videos/track_intrusion_1.mp4"
cap = cv2.VideoCapture(video_path)

# Check if video opened successfully
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 2. Optimized Inference (People detection only)
    results = model(frame, stream=True, verbose=False, classes=[0])

    person_count = 0

    # Process detections and draw bounding boxes
    for r in results:
        for box in r.boxes:
            person_count += 1
            
            # Extract coordinates safely
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # Draw green bounding box for every detected person
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # 3. Crowd Alert Logic (Evaluated every frame based on final person_count)
    if person_count < SAFE_THRESHOLD:
        status = "STATUS: SAFE"
        status_color = (0, 255, 0)      # Green BGR
    elif person_count < WARNING_THRESHOLD:
        status = "STATUS: WARNING"
        status_color = (0, 165, 255)    # Orange BGR
    else:
        status = "STATUS: DANGER"
        status_color = (0, 0, 255)      # Red BGR

    # 4. Enhanced UI Display
    # Draw a semi-transparent black background box for metrics to look professional
    cv2.rectangle(frame, (10, 10), (330, 105), (0, 0, 0), -1)
    
    # Line 1: Total People Count (Yellow for readability)
    cv2.putText(
        frame,
        f"People Count: {person_count}",
        (20, 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2,
        cv2.LINE_AA
    )
    
    # Line 2: Dynamic Alert Status (Color changes dynamically)
    cv2.putText(
        frame,
        status,
        (20, 85),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        status_color,
        2,
        cv2.LINE_AA
    )

    # Show the output window
    cv2.imshow("Rakshak AI", frame)

    # Break loop with 'q' key
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()