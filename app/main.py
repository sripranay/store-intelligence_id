from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
import json
import os

app = FastAPI()

# -----------------------------
# In-memory DB
# -----------------------------
events_db = []

# -----------------------------
# MODEL
# -----------------------------
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
    confidence: float = 1.0
    metadata: dict = {}

# -----------------------------
# LOAD FILE DATA (SAFE)
# -----------------------------
def load_events():
    file_path = os.path.join(os.path.dirname(__file__), "../pipeline/events.jsonl")

    if not os.path.exists(file_path):
        print("No events file found → using dummy data")
        generate_dummy_data()
        return

    try:
        with open(file_path, "r") as f:
            for line in f:
                try:
                    events_db.append(json.loads(line.strip()))
                except:
                    pass
        print(f"Loaded {len(events_db)} events")
    except:
        generate_dummy_data()

# -----------------------------
# DUMMY DATA (FOR DEPLOY)
# -----------------------------
def generate_dummy_data():
    now = datetime.now(timezone.utc).isoformat()

    for i in range(10):
        events_db.append({
            "event_id": f"e{i}",
            "store_id": "STORE_001",
            "camera_id": "CAM_1",
            "visitor_id": f"v{i%3}",
            "event_type": "ENTRY",
            "timestamp": now,
            "zone_id": "RACK_1",
            "dwell_ms": 2000 + i * 500,
            "is_staff": False,
            "confidence": 0.9,
            "metadata": {}
        })

    for i in range(5):
        events_db.append({
            "event_id": f"p{i}",
            "store_id": "STORE_001",
            "camera_id": "CAM_1",
            "visitor_id": f"v{i%3}",
            "event_type": "PURCHASE",
            "timestamp": now,
            "zone_id": "BILLING",
            "dwell_ms": 1000,
            "is_staff": False,
            "confidence": 0.95,
            "metadata": {}
        })

# Load on start
load_events()

# -----------------------------
# ROOT
# -----------------------------
@app.get("/")
def root():
    return {"message": "Store Intelligence API running"}

# -----------------------------
# HEALTH ✅ FIXED
# -----------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

# -----------------------------
# INGEST
# -----------------------------
@app.post("/events/ingest")
def ingest(events: List[Event]):
    for e in events:
        events_db.append(e.dict())
    return {"status": "ok", "count": len(events)}

# -----------------------------
# METRICS
# -----------------------------
@app.get("/stores/{store_id}/metrics")
def metrics(store_id: str):
    visitors = set()
    entries = 0
    purchases = 0

    for e in events_db:
        if e["store_id"] == store_id:
            if e["event_type"] == "ENTRY":
                entries += 1
                visitors.add(e["visitor_id"])
            if e["event_type"] == "PURCHASE":
                purchases += 1

    conversion = purchases / entries if entries else 0

    return {
        "store_id": store_id,
        "entries": entries,
        "unique_visitors": len(visitors),
        "purchases": purchases,
        "conversion_rate": round(conversion, 2)
    }

# -----------------------------
# FUNNEL
# -----------------------------
@app.get("/stores/{store_id}/funnel")
def funnel(store_id: str):
    f = {"entry": 0, "browse": 0, "billing": 0, "purchase": 0}

    for e in events_db:
        if e["store_id"] == store_id:
            if e["event_type"] == "ENTRY":
                f["entry"] += 1
            elif e["event_type"] == "BROWSE":
                f["browse"] += 1
            elif e["event_type"] == "BILLING":
                f["billing"] += 1
            elif e["event_type"] == "PURCHASE":
                f["purchase"] += 1

    return f

# -----------------------------
# HEATMAP DATA
# -----------------------------
@app.get("/stores/{store_id}/heatmap")
def heatmap(store_id: str):
    zone_counts = {}

    for e in events_db:
        if e["store_id"] == store_id and e.get("zone_id"):
            z = e["zone_id"]
            zone_counts[z] = zone_counts.get(z, 0) + 1

    return zone_counts

# -----------------------------
# ANOMALIES
# -----------------------------
@app.get("/stores/{store_id}/anomalies")
def anomalies(store_id: str):
    result = []

    for e in events_db:
        if e["store_id"] == store_id:
            if e["event_type"] == "EXIT" and e["dwell_ms"] < 2000:
                result.append(e)

    return {
        "count": len(result),
        "anomalies": result
    }

# -----------------------------
# RUN (LOCAL ONLY)
# -----------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
