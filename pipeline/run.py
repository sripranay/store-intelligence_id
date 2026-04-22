import time
import requests
import json

API = "http://127.0.0.1:8000/events/ingest"

with open("events.jsonl") as f:

    for line in f:
        event = json.loads(line)

        requests.post(API, json=[event])

        print("Sent:", event["event_id"])

        time.sleep(1)