# 🛍️ Store Intelligence System

End-to-end pipeline that processes CCTV footage, detects customer movement,
tracks zones, calculates dwell time, and exposes a deployed FastAPI service
with real-time analytics and dashboard visualization.

Built for the **Purplle Engineering Challenge** using **YOLOv8 + OpenCV**
for computer vision, **FastAPI + Pydantic** for APIs, and a **web dashboard**
for analytics visualization.

---

## 📦 Prerequisites

| Dependency       | Why                                                |
|------------------|----------------------------------------------------|
| Python 3.9+      | Runs pipeline + FastAPI                            |
| OpenCV           | Video processing                                  |
| Ultralytics YOLO | Object detection                                  |
| FastAPI + Uvicorn| API server                                        |
| Git              | Version control                                   |

---

## ⚡ Quickstart (5 commands)

```bash
git clone https://github.com/sripranay/store-intelligence_id.git
cd store-intelligence_id

pip install -r requirements.txt

# Run API
uvicorn app.main:app --reload

# Run pipeline
cd pipeline
python detect_entry_exit.py
```
\## Demo Videos

https://drive.google.com/drive/folders/1mU1\_RImrr658sIXeoyrtHXjVE4hhBoP8?usp=sharing
---

## 🌐 Live API

👉 https://store-intelligence-id.onrender.com

---

## 🧠 Architecture

```
 ┌────────────────┐     ┌──────────────────┐     ┌──────────────┐
 │ CCTV Feed      │ ──▶ │ pipeline/        │ ──▶ │ Events JSON  │
 │ (Video Input)  │     │ YOLO + Tracking  │     │ events.jsonl │
 └────────────────┘     └──────────────────┘     └──────┬───────┘
                                                       │
                                                       ▼
                                              ┌──────────────────┐
                                              │ FastAPI (app/)   │
                                              │ In-memory DB     │
                                              └──────┬───────────┘
                                                     │
                    ┌────────────────────────────────┼──────────────────┐
                    ▼                ▼               ▼                  ▼
                /metrics         /heatmap      /generate-dummy     /health
                    │
                    ▼
             ┌──────────────────┐
             │ dashboard.html   │
             └──────────────────┘
```

---

## 📡 API Endpoints

| Method | Path                              | Purpose |
|--------|-----------------------------------|--------|
| GET    | `/`                               | Root check |
| GET    | `/health`                         | API status |
| POST   | `/events/ingest`                  | Ingest events |
| GET    | `/stores/{store_id}/metrics`      | Store analytics |
| GET    | `/stores/{store_id}/heatmap`      | Zone heatmap |
| GET    | `/generate-dummy`                 | Generate test data |

---

## 🎯 Features

- Entry / Exit detection  
- Zone tracking (RACK-based zones)  
- Dwell time calculation  
- Visitor analytics  
- Conversion metrics  
- Heatmap visualization  
- Dummy data generator  
- Deployable API (Render)  

---

## 🎥 Pipeline Flow

1. Detect persons using YOLOv8  
2. Assign unique IDs (tracking)  
3. Detect ENTRY / EXIT events  
4. Track zone (RACK_1, RACK_2, etc.)  
5. Calculate dwell time per zone  
6. Store events in JSONL  
7. Send to API  

---

## 📊 Dashboard

Open locally:

```bash
dashboard.html
```

Features:
- Store metrics view  
- Heatmap visualization  
- API integration  
- Simple UI for demo  

---

## 🗂️ Project Structure

```
store-intelligence_id/
├── app/                 # FastAPI backend
│   └── main.py
├── pipeline/            # Detection + tracking
│   └── detect_entry_exit.py
├── dashboard.html       # Frontend UI
├── requirements.txt
└── README.md
```

---

## 🧪 Testing API

Open Swagger UI:

```
http://127.0.0.1:8000/docs
```

Try:
- `/generate-dummy`
- `/stores/STORE_001/metrics`
- `/stores/STORE_001/heatmap`

---

## 🚀 Deployment

Deployed using **Render**

Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 10000
```

---

## 💡 Notes

- Uses **in-memory DB** (no Postgres for simplicity)  
- Dummy data used for demonstration  
- Lightweight and easy to deploy  

---

## 🏆 Highlights

Simulates real-world retail analytics including visitor tracking,
dwell time analysis, and heatmap-based store insights.

---

## 👤 Author

**Pranay (AI Engineer)**
