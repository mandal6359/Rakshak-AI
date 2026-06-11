import cv2
from ultralytics import YOLO

# 1. Initialize the YOLOv8 model
model = YOLO("models/yolov8n.pt")

# 2. Open the video file
video_path = "datasets/videos/track_intrusion_1.mp4"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(f"Error: Could not open video file {video_path}")
    exit()

# =========================================================================
# FIX 2 (Professional): Create a resizable window BEFORE the loop starts.
# This prevents 1080p or 4K videos from spilling off your monitor.
# =========================================================================
window_name = "Rakshak AI - Person Tracking"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, 1200, 700) 
# =========================================================================

# 3. Stream processing loop
while cap.isOpened():
    success, frame = cap.read()

    if not success:
        print("Video stream finished or interrupted.")
        break

    # 4. Run the YOLO tracker
    # FIX: Added verbose=False to stop the terminal spam every single frame
    results = model.track(
        frame,
        persist=True,
        tracker="bytetrack.yaml",
        classes=[0],
        verbose=False
   )

    # 5. Draw the tracking bounding boxes
    annotated_frame = results[0].plot(labels=True)

    # 6. Display the frame in our pre-resized, professional window
    cv2.imshow(window_name, annotated_frame)

    # 7. Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord("q"):
        print("Tracking stopped by user.")
        break

# 8. Clean up resources safely
cap.release()
cv2.destroyAllWindows()
cv2.waitKey(1)