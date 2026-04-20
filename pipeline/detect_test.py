from ultralytics import YOLO
import cv2

model = YOLO("yolov8n.pt")

video_path = "../dataset/videos/CAM 1.mp4"
output_path = "output.mp4"

cap = cv2.VideoCapture(video_path)

# Get video properties
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

# Video writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, conf=0.5)
    annotated_frame = results[0].plot()

    out.write(annotated_frame)

cap.release()
out.release()

print("✅ Output saved as output.mp4")