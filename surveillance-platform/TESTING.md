# Testing Strategy

## Test Types

### 1. Unit Tests
Test individual components in isolation:
- Zone geometry (point-in-polygon, line crossing)
- Trajectory calculations (velocity, direction, dwell time)
- Event threshold logic
- Confidence handling
- Database models

### 2. Vision Pipeline Tests
Use fixed frames/video clips:
- Detection accuracy on sample frames
- Tracking identity consistency
- Event engine rule evaluation
- Explainability output validation

### 3. Integration Tests
- Stream manager → Detection → Tracking pipeline
- Event engine → Persistence → WebSocket
- Camera management → Processing lifecycle

### 4. API Tests
- Authentication flow (register, login, token)
- Authorization (role-based access)
- CRUD operations (cameras, zones, rules)
- Event search and filtering
- Pagination and validation
- Error responses

### 5. E2E Scenario
```
Login
  ↓
Dashboard
  ↓
Add Camera
  ↓
Configure Restricted Zone
  ↓
Configure Dwell Rule
  ↓
Start Stream
  ↓
Object Enters Zone
  ↓
Event Generated
  ↓
Alert Appears in Dashboard
  ↓
Operator Acknowledges Event
  ↓
Analytics Updated
```

## Running Tests

```bash
# All backend tests
pytest -v

# Specific test file
pytest backend/tests/test_vision.py -v

# With coverage
pytest --cov=backend --cov=vision -v

# Frontend tests
cd frontend && npm test
```

## Benchmarking

```bash
# Detection FPS benchmark
python -m vision.detection.benchmark \
  --source sample_video.mp4 \
  --model yolov8n.pt \
  --device cpu \
  --max-frames 300
```

## Metrics to Report

### Detection
- Precision, Recall, mAP50, mAP50-95

### Tracking
- IDF1, MOTA/HOTA, ID Switches

### Event Detection
- Precision, Recall, F1, False Positive Rate, Mean Detection Latency

### System
- Average FPS, P95 Inference Latency, CPU/GPU Usage, Memory, Dropped Frame Rate
