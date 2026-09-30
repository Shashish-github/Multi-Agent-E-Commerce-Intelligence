# ML Pipeline Documentation

## Object Detection

### Model
- **Architecture:** YOLOv8 (Ultralytics)
- **Baseline:** `yolov8n.pt` (nano, fastest)
- **Target Classes:** person, car, truck, bus, motorcycle, bicycle
- **Input:** 640x640 BGR frame
- **Output:** Bounding boxes with class labels and confidence scores

### Pipeline
```
Frame → Resize/Letterbox → YOLO Inference → Confidence Filter → Class Filter → Detections
```

### Configuration
| Parameter | Default | Description |
|-----------|---------|-------------|
| Confidence threshold | 0.5 | Minimum detection confidence |
| Model size | yolov8n | Trade-off: speed vs accuracy |
| Device | cpu | cpu, cuda, mps |

### Evaluation Metrics
- Precision, Recall
- mAP50, mAP50-95
- Per-class performance
- Inference latency (ms)

---

## Multi-Object Tracking

### Model
- **Algorithm:** ByteTrack-inspired IoU-based tracker
- **Matching:** Two-stage IoU greedy matching
- **ID Management:** Incremental integer IDs

### Track Lifecycle
```
New Detection → Tentative Track (hits < 3)
                 ↓
             Confirmed Track (hits >= 3)
                 ↓
             Lost Track (time_since_update > max_time_lost)
                 ↓
             Removed
```

### Features Computed Per Track
- Position (center of bounding box)
- Velocity (frame-to-frame displacement)
- Speed (velocity magnitude)
- Direction (cardinal: up/down/left/right/static)
- Displacement (total movement from start)
- Path length (total distance traveled)
- Dwell time (time in current zone)
- Zone transitions
- Acceleration proxy

---

## Anomaly Detection

### Architecture
```
Track Trajectories
      ↓
Windowing (sequence of N frames)
      ↓
Feature Normalization
      ↓
LSTM Autoencoder (or statistics-based fallback)
      ↓
Reconstruction Error → Anomaly Score
```

### Feature Vector (10 dimensions)
1. Position X
2. Position Y
3. Velocity X
4. Velocity Y
5. Speed
6. Displacement
7. Path length
8. Dwell time
9. Acceleration
10. Direction (encoded)

### Training
- Train on normal behavior data from the target deployment
- Reconstruction error threshold determines anomaly sensitivity
- Must be evaluated separately from the rule engine

### Evaluation Metrics
- Precision, Recall, F1
- False Positive Rate
- Event detection latency
- ROC-AUC

---

## Model Optimization

### Current Optimizations
- Frame skipping (detect every N frames)
- Class filtering (skip irrelevant objects)
- Confidence thresholding
- Bounded frame buffers

### Future Optimizations
- FP16 inference (GPU)
- ONNX/TensorRT export
- Region-of-interest processing
- Batch inference
- Detector/tracker frequency separation

### Benchmarking
Always measure before and after optimization:
```bash
python -m vision.detection.benchmark --source <video> --model <model>
```
