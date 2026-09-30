# Real-Time Multi-Object Surveillance and Anomalous Behavior Detection Platform

A real-time computer-vision system that detects, tracks, analyzes, and explains abnormal activity across video streams.

## Architecture

```
Camera / Video File
       ↓
Stream Manager
       ↓
Frame Buffer
       ↓
Preprocessor
       ↓
GPU/CPU Inference Worker
       ↓
YOLO Detection
       ↓
ByteTrack
       ↓
Trajectory Store
       ↓
Behavior/Event Engine
       ├── Zone Rules
       ├── Dwell Analysis
       ├── Counting
       ├── Crowd Analysis
       └── Anomaly Model
       ↓
Event Manager
       ├── PostgreSQL
       ├── Evidence Storage
       └── Alert Service
       ↓
FastAPI
       ↓
Next.js Dashboard
       ↕
WebSocket
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python + FastAPI |
| Frontend | Next.js + TypeScript |
| Detection | Ultralytics YOLO |
| Tracking | ByteTrack |
| Database | PostgreSQL |
| Cache | Redis |
| Video | OpenCV + FFmpeg |
| Deployment | Docker |

## Quick Start

```bash
# Clone and setup
cp .env.example .env
docker-compose up -d

# Or run locally
cd backend && pip install -r requirements.txt
cd frontend && npm install
```

## Development Phases

1. **Foundation** — Docker, database, auth, CI
2. **Video Ingestion** — Stream manager, frame buffer, health
3. **Detection** — YOLO integration, preprocessing, benchmarking
4. **Tracking** — ByteTrack, track lifecycle, trajectories
5. **Rule Engine** — Zones, line crossing, dwell, crowd events
6. **Dashboard** — Live stream, overlays, event timeline, zone editor
7. **Anomaly Detection** — Temporal features, anomaly model
8. **Performance** — Profiling, GPU optimization, queue tuning
9. **Productionization** — Security, monitoring, deployment
10. **Polish** — Accessibility, UX, documentation, demo

## License

Private — Internal use only
