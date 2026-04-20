from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import json
import os

app = FastAPI()

events_db = []

class Event(BaseModel):
    event_id: str
    store_id: str
    camera_id: str
    visitor_id: str
    event_type: str
    timestamp: str
    zone_id: str | None
    dwell_ms: int
    is_staff: bool
    confidence: float
    metadata: dict

# -----------------------------
# LOAD EVENTS
# -----------------------------
def load_events_from_file():
    file_path = os.path.join(os.path.dirname(__file__), "..", "pipeline", "events.jsonl")

    if not os.path.exists(file_path):
        print("⚠ events.jsonl not found")
        return

    with open(file_path, "r") as f:
        for line in f:
            try:
                event = json.loads(line.strip())
                events_db.append(event)
            except:
                pass

    print(f"✅ Loaded {len(events_db)} events from file")

@app.on_event("startup")
def startup_event():
    load_events_from_file()

# -----------------------------
# INGEST
# -----------------------------
@app.post("/events/ingest")
def ingest_events(events: List[Event]):
    for event in events:
        events_db.append(event.dict())

    return {"status": "success", "count": len(events)}

# -----------------------------
# METRICS
# -----------------------------
@app.get("/stores/{store_id}/metrics")
def get_metrics(store_id: str):
    visitors = set()
    entry_count = 0

    for e in events_db:
        if e["store_id"] == store_id:
            if e["event_type"] == "ENTRY":
                entry_count += 1
                visitors.add(e["visitor_id"])

    return {
        "store_id": store_id,
        "total_entries": entry_count,
        "unique_visitors": len(visitors),
        "conversion_rate": 0
    }

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)