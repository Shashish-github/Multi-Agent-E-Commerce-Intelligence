#!/bin/bash
# Run all benchmarks for the surveillance platform

set -e

echo "=========================================="
echo "Surveillance Platform Benchmark Suite"
echo "=========================================="

# Check if sample video exists
SAMPLE_VIDEO="${1:-sample_video.mp4}"
if [ ! -f "$SAMPLE_VIDEO" ]; then
    echo "Usage: $0 <video_file>"
    echo "Please provide a sample video file for benchmarking."
    exit 1
fi

echo ""
echo "1. Detection Benchmark (YOLOv8n)"
echo "----------------------------------"
python -m vision.detection.benchmark \
    --source "$SAMPLE_VIDEO" \
    --model yolov8n.pt \
    --device cpu \
    --max-frames 300 \
    --output docs/benchmark_detection_yolov8n.json

echo ""
echo "2. Detection Benchmark (YOLOv8s)"
echo "----------------------------------"
python -m vision.detection.benchmark \
    --source "$SAMPLE_VIDEO" \
    --model yolov8s.pt \
    --device cpu \
    --max-frames 300 \
    --output docs/benchmark_detection_yolov8s.json

echo ""
echo "3. Full Pipeline Benchmark"
echo "----------------------------------"
python scripts/run_pipeline.py \
    --source "$SAMPLE_VIDEO" \
    --model yolov8n.pt \
    --device cpu \
    --max-frames 300 \
    --output-json docs/benchmark_pipeline.json

echo ""
echo "=========================================="
echo "All benchmarks complete!"
echo "Results saved to docs/"
echo "=========================================="
