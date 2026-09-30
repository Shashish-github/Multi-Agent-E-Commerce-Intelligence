# Architecture

## System Overview

The Real-Time Surveillance Platform is a distributed system with the following major subsystems:

```
┌─────────────────────────────────────────────────────┐
│                   Frontend (Next.js)                │
│  Dashboard │ Camera View │ Events │ Analytics       │
└──────────────────────┬──────────────────────────────┘
                       │ WebSocket + REST API
┌──────────────────────┴──────────────────────────────┐
│                 Backend (FastAPI)                    │
│  Auth │ Camera API │ Events │ Analytics │ WebSocket │
└──────┬──────────────────────────────────────────────┘
       │
┌──────┴──────────────────────────────────────────────┐
│              Vision Pipeline (Python)                │
│  Stream │ Detect │ Track │ Features │ Event Engine   │
└──────┬──────────────────────────────────────────────┘
       │
┌──────┴──────────────────────────────────────────────┐
│                   Storage Layer                      │
│  PostgreSQL │ Redis │ Evidence Store (filesystem)    │
└─────────────────────────────────────────────────────┘
```

## Processing Pipeline

```
Camera / Video File
       ↓
Stream Manager (capture, reconnect, health)
       ↓
Frame Buffer (bounded, FIFO)
       ↓
Preprocessor (resize, normalize)
       ↓
YOLO Detector (every N frames)
       ↓
ByteTrack (every frame)
       ↓
Trajectory Analyzer (velocity, direction, dwell)
       ↓
Event Engine (zone rules, crowd, anomaly)
       ↓
Event Manager (persistence, evidence)
       ↓
WebSocket → Dashboard
```

## Key Design Decisions

1. **Bounded queues** — Frame buffers prevent unbounded memory growth
2. **Non-blocking persistence** — Database writes never block the frame loop
3. **Frame skipping** — Detection runs every N frames; tracking runs every frame
4. **Deterministic rules first** — Rule engine before learned anomaly detection
5. **Replaceable components** — Detector and tracker are pluggable
6. **Explainable events** — Every event includes a human-readable explanation

## Security

- JWT-based authentication
- Role-based access (ADMIN, OPERATOR)
- No facial recognition or biometric identification
- Encrypted camera credentials
- Evidence access control
