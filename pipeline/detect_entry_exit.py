import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import cv2
import requests
import uuid
from datetime import datetime
from ultralytics import YOLO

# ---------------- CONFIG ----------------
API_URL = "http://127.0.0.1:8000/events/ingest"
VIDEO_PATH = "../dataset/videos/CAM 1.mp4"

# ---------------- ZONES ----------------
ZONES = {
    "RACK_1": (0, 0, 400, 300),
    "RACK_2": (400, 0, 800, 300),
    "RACK_3": (0, 300, 400, 800),
    "RACK_4": (400, 300, 800, 800)
}

# ---------------- MODEL ----------------
model = YOLO("yolov8n.pt")

# ---------------- TRACKING ----------------
trackers = {}
entered = set()
frame_count = {}
next_id = 0

FPS = 30  # assume fps

# ---------------- FUNCTIONS ----------------
def get_center(box):
    x1, y1, x2, y2 = box
    return int((x1 + x2) / 2), int((y1 + y2) / 2)

def assign_id(center):
    global next_id

    for tid, prev in trackers.items():
        if abs(center[0] - prev[0]) < 80 and abs(center[1] - prev[1]) < 80:
            trackers[tid] = center
            return tid

    trackers[next_id] = center
    next_id += 1
    return next_id - 1

def get_zone(center):
    x, y = center
    for z, (x1, y1, x2, y2) in ZONES.items():
        if x1 <= x <= x2 and y1 <= y <= y2:
            return z
    return None

# ---------------- START ----------------
cap = cv2.VideoCapture(VIDEO_PATH)

ret, frame = cap.read()
if not ret:
    print("❌ Video not loading")
    exit()

print("🚀 Running...")

# ---------------- LOOP ----------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # FAST INFERENCE
    results = model(frame, conf=0.4, imgsz=320, verbose=False)

    for r in results:
        for box, cls in zip(r.boxes.xyxy, r.boxes.cls):

            if int(cls) != 0:  # only person
                continue

            x1, y1, x2, y2 = map(int, box)
            center = get_center((x1, y1, x2, y2))
            track_id = assign_id(center)

            # ---------------- ENTRY ----------------
            if track_id not in entered:
                entered.add(track_id)

                print(f"ENTRY → ID {track_id}")

                event = {
                    "event_id": str(uuid.uuid4()),
                    "store_id": "STORE_001",
                    "camera_id": "CAM_1",
                    "visitor_id": f"VIS_{track_id}",
                    "event_type": "ENTRY",
                    "timestamp": datetime.utcnow().isoformat(),
                    "zone_id": None,
                    "dwell_ms": 0,
                    "is_staff": False,
                    "confidence": 0.95,
                    "metadata": {}
                }

                requests.post(API_URL, json=[event])

            # ---------------- ZONE + DWELL ----------------
            zone = get_zone(center)

            if zone:
                if track_id not in frame_count:
                    frame_count[track_id] = {zone: 1}
                else:
                    if zone not in frame_count[track_id]:
                        frame_count[track_id][zone] = 1
                    else:
                        frame_count[track_id][zone] += 1

                        dwell_ms = (frame_count[track_id][zone] / FPS) * 1000

                        if dwell_ms > 2000:  # 2 sec
                            print(f"🟡 ID {track_id} in {zone} for {int(dwell_ms)} ms")

                            event = {
                                "event_id": str(uuid.uuid4()),
                                "store_id": "STORE_001",
                                "camera_id": "CAM_1",
                                "visitor_id": f"VIS_{track_id}",
                                "event_type": "DWELL",
                                "timestamp": datetime.utcnow().isoformat(),
                                "zone_id": zone,
                                "dwell_ms": int(dwell_ms),
                                "is_staff": False,
                                "confidence": 0.90,
                                "metadata": {}
                            }

                            requests.post(API_URL, json=[event])

                            # RESET TIMER
                            frame_count[track_id][zone] = 0

            # ---------------- DRAW ----------------
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"ID {track_id}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # DRAW ZONES
    for z, (x1, y1, x2, y2) in ZONES.items():
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 1)
        cv2.putText(frame, z, (x1 + 5, y1 + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

    cv2.imshow("Store Feed", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

print("✅ DONE")