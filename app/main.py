from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import random
from datetime import datetime

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ---------------- DB ----------------
events_db = []

# ---------------- MODEL ----------------
class Event(BaseModel):
    event_id: str
    store_id: str
    camera_id: str
    visitor_id: str
    event_type: str
    timestamp: str
    zone_id: Optional[str] = None
    dwell_ms: int = 0
    is_staff: bool = False
    confidence: float = 0.9
    metadata: dict = {}

# ---------------- ROOT ----------------
@app.get("/")
def root():
    return {"message": "Store Intelligence API running"}

# ---------------- INGEST ----------------
@app.post("/events/ingest")
def ingest(events: List[Event]):
    for e in events:
        events_db.append(e.dict())
    return {"status": "ok", "count": len(events)}

# ---------------- METRICS ----------------
@app.get("/stores/{store_id}/metrics")
def metrics(store_id: str):
    entries = 0
    visitors = set()
    dwell_total = 0

    for e in events_db:
        if e["store_id"] == store_id:
            if e["event_type"] == "ENTRY":
                entries += 1
                visitors.add(e["visitor_id"])
            if e["event_type"] == "DWELL":
                dwell_total += e["dwell_ms"]

    avg_dwell = dwell_total / entries if entries else 0

    return {
        "store_id": store_id,
        "entries": entries,
        "unique_visitors": len(visitors),
        "avg_dwell_ms": int(avg_dwell)
    }

# ---------------- HEATMAP ----------------
@app.get("/stores/{store_id}/heatmap")
def heatmap(store_id: str):
    zone_count = {}

    for e in events_db:
        if e["store_id"] == store_id and e["zone_id"]:
            zone = e["zone_id"]
            zone_count[zone] = zone_count.get(zone, 0) + 1

    return zone_count

# ---------------- DUMMY DATA ----------------
@app.get("/generate-dummy")
def generate_dummy():
    stores = ["STORE_001", "STORE_002"]

    for i in range(100):
        store = random.choice(stores)
        event = {
            "event_id": str(i),
            "store_id": store,
            "camera_id": "CAM_1",
            "visitor_id": f"VIS_{random.randint(1,20)}",
            "event_type": random.choice(["ENTRY", "DWELL"]),
            "timestamp": datetime.utcnow().isoformat(),
            "zone_id": random.choice(["RACK_1", "RACK_2", "RACK_3", "RACK_4"]),
            "dwell_ms": random.randint(1000, 5000),
            "is_staff": False,
            "confidence": 0.9,
            "metadata": {}
        }
        events_db.append(event)

    return {"status": "dummy data added", "count": len(events_db)}