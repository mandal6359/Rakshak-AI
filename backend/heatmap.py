import cv2
import numpy as np
import os
from ultralytics import YOLO

# Initialize YOLO Model
model = YOLO("models/yolov8n.pt")

# Open Video Stream
video_path = "datasets/videos/railway_station.mp4"
cap = cv2.VideoCapture(video_path)

# Ensure alerts directory exists for saving the live file asset
os.makedirs("alerts", exist_ok=True)

# Fixed Resizable Window Footprint
window_name = "Rakshak AI - Advanced Crowd Density Heatmap"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, 1200, 700) 

while True:
    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # Loop video continuously
        ret, frame = cap.read()
        if not ret:
            break

    # Run YOLO detection on persons (class 0) silently
    results = model(frame, classes=[0], verbose=False)

    # Base black canvas layout for gradient tracing
    heatmap = np.zeros((frame.shape[0], frame.shape[1]), dtype=np.float32)

    if results[0].boxes is not None:
        boxes = results[0].boxes.xyxy.cpu().numpy()

        for box in boxes:
            x1, y1, x2, y2 = map(int, box[:4])
            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            # =========================================================================
            # UPGRADE: INCREASED RADIUS AND INTENSITY WEIGHT
            # Radius increased from 40 to 120. Accumulation weight increased from 1 to 3.
            # =========================================================================
            cv2.circle(
                heatmap, 
                (cx, cy), 
                120, 
                3, 
                -1
            )
            # =========================================================================

    # =========================================================================
    # UPGRADE: HEAVY BLUR THERMAL KERNEL
    # Kernel dimensions increased from (51, 51) to a wide smooth layout (151, 151)
    # =========================================================================
    heatmap = cv2.GaussianBlur(
        heatmap, 
        (151, 151), 
        0
    )
    # =========================================================================

    # Normalize map values relative to 0-255 scaling threshold limits
    heatmap_norm = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
    
    # Extract the absolute peak pixel value to calculate concentration pressure
    max_density = np.max(heatmap_norm)

    if max_density < 50:
        density_level = "LOW"
        density_color = (0, 255, 0)    # Green (Safe)
    elif max_density < 150:            
        density_level = "MEDIUM"
        density_color = (0, 165, 255)  # Orange (Warning)
    else:
        density_level = "HIGH"
        density_color = (0, 0, 255)    # Red (Critical Congestion)

    # Convert normalized image to 8-bit array configuration and map spectrum colors
    heatmap_color = cv2.applyColorMap(heatmap_norm.astype(np.uint8), cv2.COLORMAP_JET)

    # Merge alpha frames transparency blend: 70% Original Video, 30% Thermal Canvas
    output = cv2.addWeighted(frame, 0.7, heatmap_color, 0.3, 0)

    # Visual HUD Overlays
    cv2.rectangle(output, (0, 0), (450, 95), (15, 15, 15), -1)
    cv2.putText(output, "ANALYTICS: LIVE CROWD HEATMAP", (20, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
    cv2.putText(output, f"CROWD DENSITY: {density_level}", (20, 70), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, density_color, 2)

    # Save file to disk on every frame cycle for Streamlit integration
    cv2.imwrite("alerts/latest_heatmap.jpg", output)

    # Render on computer monitor
    cv2.imshow(window_name, output)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
cv2.waitKey(1)