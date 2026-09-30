"""Detection benchmark: measure FPS, latency, and accuracy."""
import time
import json
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from vision.detection.yolo_detector import YOLODetector


def benchmark_fps(
    detector: YOLODetector,
    source: str,
    max_frames: int = 300,
    warmup_frames: int = 30,
) -> dict:
    """
    Benchmark detection FPS on a video source.

    Args:
        detector: Initialized YOLODetector
        source: Video file path or camera index
        max_frames: Max frames to process
        warmup_frames: Frames to discard for warmup

    Returns:
        Benchmark results dict
    """
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise ValueError(f"Could not open video source: {source}")

    fps_stats = []
    latencies = []
    frame_count = 0

    print(f"Benchmarking detection on: {source}")
    print(f"Max frames: {max_frames}, Warmup: {warmup_frames}")

    start_total = time.perf_counter()

    while frame_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        timestamp = time.perf_counter()

        result = detector.detect(frame, timestamp=timestamp)

        if frame_count > warmup_frames:
            latencies.append(result.inference_time_ms)
            fps_stats.append(1000.0 / max(result.inference_time_ms, 0.001))

    total_time = time.perf_counter() - start_total
    cap.release()

    # Filter out warmup frames
    benchmark_frames = frame_count - warmup_frames

    stats = {
        "source": source,
        "total_frames": frame_count,
        "benchmark_frames": benchmark_frames,
        "total_time_seconds": round(total_time, 3),
        "avg_fps": round(benchmark_frames / total_time, 2) if total_time > 0 else 0,
        "avg_latency_ms": round(np.mean(latencies), 2) if latencies else 0,
        "p95_latency_ms": round(np.percentile(latencies, 95), 2) if latencies else 0,
        "p99_latency_ms": round(np.percentile(latencies, 99), 2) if latencies else 0,
        "min_latency_ms": round(np.min(latencies), 2) if latencies else 0,
        "max_latency_ms": round(np.max(latencies), 2) if latencies else 0,
        "std_latency_ms": round(np.std(latencies), 2) if latencies else 0,
        "detections_per_frame": 0,
        "model_path": detector.model_path,
        "device": detector.device,
        "confidence_threshold": detector.confidence_threshold,
        "target_classes": detector.target_classes,
    }

    print(json.dumps(stats, indent=2))
    return stats


def save_benchmark(results: dict, output_path: str = "docs/benchmark_detection.json"):
    """Save benchmark results to JSON."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {output_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Benchmark YOLO detection")
    parser.add_argument("--source", type=str, required=True, help="Video file or camera index")
    parser.add_argument("--model", type=str, default="yolov8n.pt", help="YOLO model path")
    parser.add_argument("--device", type=str, default="cpu", help="Device: cpu or cuda")
    parser.add_argument("--max-frames", type=int, default=300)
    parser.add_argument("--warmup-frames", type=int, default=30)
    parser.add_argument("--output", type=str, default="docs/benchmark_detection.json")
    args = parser.parse_args()

    detector = YOLODetector(model_path=args.model, device=args.device)
    detector.warmup()
    results = benchmark_fps(detector, args.source, args.max_frames, args.warmup_frames)
    save_benchmark(results, args.output)
