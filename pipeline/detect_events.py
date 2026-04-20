from ultralytics import YOLO
import cv2
from deep_sort_realtime.deepsort_tracker import DeepSort
import json
import uuid
from datetime import datetime

model = YOLO("yolov8n.pt")
tracker = DeepSort(max_age=30)

video_path = "../dataset/videos/CAM 1.mp4"
output_events = "events.jsonl"

cap = cv2.VideoCapture(video_path)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

line_y = height // 2
track_positions = {}

events_file = open(output_events, "w")

def current_time():
    return datetime.utcnow().isoformat() + "Z"

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)[0]
    detections = []

    for box in results.boxes:
        x1, y1, x2, y2 = box.xyxy[0]
        conf = float(box.conf[0])
        cls = int(box.cls[0])

        if cls == 0:
            detections.append(([x1, y1, x2-x1, y2-y1], conf, 'person'))

    tracks = tracker.update_tracks(detections, frame=frame)

    for track in tracks:
        if not track.is_confirmed():
            continue

        track_id = track.track_id
        l, t, w, h = track.to_ltrb()

        x1, y1, x2, y2 = int(l), int(t), int(w), int(h)
        center_y = (y1 + y2) // 2

        if track_id not in track_positions:
            track_positions[track_id] = center_y

        prev_y = track_positions[track_id]

        event_type = None

        if prev_y < line_y and center_y >= line_y:
            event_type = "ENTRY"
        elif prev_y > line_y and center_y <= line_y:
            event_type = "EXIT"

        track_positions[track_id] = center_y

        if event_type:
            event = {
                "event_id": str(uuid.uuid4()),
                "store_id": "STORE_001",
                "camera_id": "CAM_1",
                "visitor_id": f"VIS_{track_id}",
                "event_type": event_type,
                "timestamp": current_time(),
                "zone_id": None,
                "dwell_ms": 0,
                "is_staff": False,
                "confidence": 0.9,
                "metadata": {}
            }

            events_file.write(json.dumps(event) + "\n")

cap.release()
events_file.close()

print("✅ Events saved to events.jsonl")