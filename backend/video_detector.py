import cv2
from ultralytics import YOLO

# 1. Load the model once
model = YOLO("yolov8n.pt")

video_path = "datasets/videos/railway_station.mp4"
cap = cv2.VideoCapture(video_path)

# Check if video opened successfully
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 2. Optimized Inference: 
    # stream=True uses a generator (saves memory)
    # verbose=False stops terminal spamming
    # classes=[0] filters for people at the model level (massive speedup!)
    results = model(frame, stream=True, verbose=False, classes=[0])

    person_count = 0

    for r in results:
        for box in r.boxes:
            person_count += 1
            
            # Extract coordinates safely
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # Draw green bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # 3. Enhanced UI: Added a background contrast box for the text so it's readable
    cv2.rectangle(frame, (10, 15), (280, 65), (0, 0, 0), -1)
    cv2.putText(
        frame,
        f"People Count: {person_count}",
        (20, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 255),  # Yellow text stands out better
        2,
        cv2.LINE_AA
    )

    cv2.imshow("Rakshak AI", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()