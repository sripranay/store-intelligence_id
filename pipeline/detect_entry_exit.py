from ultralytics import YOLO
import cv2
from deep_sort_realtime.deepsort_tracker import DeepSort

model = YOLO("yolov8n.pt")
tracker = DeepSort(max_age=30)

video_path = "../dataset/videos/CAM 1.mp4"
output_path = "entry_exit_output.mp4"

cap = cv2.VideoCapture(video_path)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

# Line position
line_y = height // 2

# Track positions
track_positions = {}

entry_count = 0
exit_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)[0]

    detections = []

    for box in results.boxes:
        x1, y1, x2, y2 = box.xyxy[0]
        conf = box.conf[0]
        cls = int(box.cls[0])

        if cls == 0:
            detections.append(([x1, y1, x2-x1, y2-y1], conf, 'person'))

    tracks = tracker.update_tracks(detections, frame=frame)

    # Draw line
    cv2.line(frame, (0, line_y), (width, line_y), (0,0,255), 2)

    for track in tracks:
        if not track.is_confirmed():
            continue

        track_id = track.track_id
        l, t, w, h = track.to_ltrb()

        x1, y1, x2, y2 = int(l), int(t), int(w), int(h)
        center_y = (y1 + y2) // 2

        # Store previous position
        if track_id not in track_positions:
            track_positions[track_id] = center_y

        prev_y = track_positions[track_id]

        # ENTRY
        if prev_y < line_y and center_y >= line_y:
            entry_count += 1

        # EXIT
        elif prev_y > line_y and center_y <= line_y:
            exit_count += 1

        track_positions[track_id] = center_y

        # Draw box + ID
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
        cv2.putText(frame, f"ID {track_id}", (x1, y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

    # Show counts
    cv2.putText(frame, f"Entry: {entry_count}", (10,30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    cv2.putText(frame, f"Exit: {exit_count}", (10,70),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

    out.write(frame)

cap.release()
out.release()

print("✅ Entry/Exit video saved as entry_exit_output.mp4")