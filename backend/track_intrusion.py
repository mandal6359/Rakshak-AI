import cv2
from ultralytics import YOLO

# 1. Initialize YOLO Model
model = YOLO("models/yolov8n.pt")

# 2. Open Video Stream
video_path = "datasets/videos/track_intrusion_1.mp4"
cap = cv2.VideoCapture(video_path)

# Set up the professional display window
window_name = "Rakshak AI - Track Intrusion Detection"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, 1200, 700)

# ==========================================
# TRACK INTRUSION CONFIGURATION
# ==========================================
# This is the horizontal line splitting the platform and tracks.
# Adjust this value up or down depending on your video's layout!
TRACK_ZONE_X1 = 0
TRACK_ZONE_Y1 = 300
TRACK_ZONE_X2 = 450
TRACK_ZONE_Y2 = 900 
# ==========================================

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # Run YOLO tracker silently
    results = model.track(frame, persist=True, classes=[0], verbose=False)
    
    # Get the annotated image frame
    annotated_frame = results[0].plot()

    # Step 2: Draw the Red Danger Line on the frame
    # (0, danger_line_y) is the start on the left; (width, danger_line_y) is the end on the right
    frame_width = annotated_frame.shape[1]
    cv2.rectangle(
        annotated_frame, 
        (TRACK_ZONE_X1, TRACK_ZONE_Y1), 
        (TRACK_ZONE_X2, TRACK_ZONE_Y2), 
        (0, 0, 255),  # Red bounding color (BGR format)
        3             # Thickness of the zone border
    )

    # Flag to monitor if anyone crossed the line in this frame
    track_intrusion = False
    total_people = 0

    # Step 3: Check if any person crosses the danger line
    if results[0].boxes is not None:
        boxes = results[0].boxes.xyxy.cpu().numpy()
        total_people = len(boxes)
        
        for box in boxes:
            x1, y1, x2, y2 = box[:4]
            
            # Calculate the center point of the person
            x_center = int((x1 + x2) / 2)
            y_center = int((y1 + y2) / 2)
            
            # Visual marker: Draw a yellow dot for every person's tracking center
            cv2.circle(annotated_frame, (x_center, y_center), 5, (0, 255, 255), -1)
            
            # CRITICAL CHECK: If center point is below the line (Y is greater)
            if (TRACK_ZONE_X1 <= x_center <= TRACK_ZONE_X2) and (TRACK_ZONE_Y1 <= y_center <= TRACK_ZONE_Y2):
                track_intrusion = True
                # Highlight the specific intruder on screen with a bold red marker
                cv2.circle(annotated_frame, (x_center, y_center), 8, (0, 0, 255), -1)

            # =========================================================================
    # VISUAL OUTPUT: HEADS-UP DISPLAY (HUD)
    # ==========================================
    # Top-left background card for security status
    cv2.rectangle(annotated_frame, (0, 0), (500, 110), (0, 0, 0), -1)
    
    # Display Total Passengers Spotted
    cv2.putText(annotated_frame, f"Passengers on Platform: {total_people}", (20, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # Display Intrusion Alert Status
    if track_intrusion:
        # Flash Red Warning
        cv2.putText(annotated_frame, "STATUS: 🚨 TRACK INTRUSION DETECTED 🚨", (20, 85), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)
    else:
        # Green Safe Status
        cv2.putText(annotated_frame, "STATUS: SECURE", (20, 85), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    # ==========================================

    # Show the final frame
    cv2.imshow(window_name, annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
cv2.waitKey(1)