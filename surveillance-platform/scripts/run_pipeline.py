#!/usr/bin/env python3
"""
Run the full processing pipeline on a video source.

Usage:
    python scripts/run_pipeline.py --source sample_video.mp4
    python scripts/run_pipeline.py --source 0  # webcam
    python scripts/run_pipeline.py --source rtsp://... --model yolov8s.pt
"""
import argparse
import time
import json
import sys

import cv2

from vision.detection.yolo_detector import YOLODetector
from vision.detection.preprocessor import FramePreprocessor
from vision.detection.pipeline import ProcessingPipeline
from vision.anomaly.event_engine import ZoneConfig, RuleConfig


def main():
    parser = argparse.ArgumentParser(description="Run surveillance processing pipeline")
    parser.add_argument("--source", type=str, required=True, help="Video source (file, camera index, RTSP URL)")
    parser.add_argument("--model", type=str, default="yolov8n.pt", help="YOLO model path")
    parser.add_argument("--device", type=str, default="cpu", help="Device: cpu or cuda")
    parser.add_argument("--confidence", type=float, default=0.5, help="Detection confidence threshold")
    parser.add_argument("--frame-skip", type=int, default=2, help="Process detection every N frames")
    parser.add_argument("--max-frames", type=int, default=0, help="Max frames to process (0 = unlimited)")
    parser.add_argument("--output-json", type=str, default=None, help="Save results to JSON file")
    parser.add_argument("--show", action="store_true", help="Show visualization window")
    args = parser.parse_args()

    # Initialize detector
    print(f"Loading model: {args.model} on {args.device}")
    detector = YOLODetector(
        model_path=args.model,
        confidence_threshold=args.confidence,
        device=args.device,
    )

    # Initialize pipeline
    pipeline = ProcessingPipeline(
        camera_id="demo",
        detector=detector,
        frame_skip_interval=args.frame_skip,
    )

    # Add sample zone and rule for demo
    pipeline.event_engine.add_zone(ZoneConfig(
        zone_id="demo_zone",
        name="Demo Restricted Zone",
        zone_type="restricted",
        polygon=[
            {"x": 100, "y": 100},
            {"x": 500, "y": 100},
            {"x": 500, "y": 400},
            {"x": 100, "y": 400},
        ],
    ))
    pipeline.event_engine.add_rule(RuleConfig(
        rule_id="demo_rule",
        rule_type="restricted_entry",
        zone_id="demo_zone",
        confidence_threshold=0.3,
    ))

    # Open video source
    source = int(args.source) if args.source.isdigit() else args.source
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"Error: Could not open video source: {args.source}")
        sys.exit(1)

    print(f"Processing: {args.source}")
    print(f"Frame skip: {args.frame_skip}, Confidence: {args.confidence}")
    print("Press 'q' to quit\n")

    results_log = []
    frame_count = 0
    start_time = time.time()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("End of video stream")
                break

            frame_count += 1
            if args.max_frames > 0 and frame_count > args.max_frames:
                break

            timestamp = time.time()
            result = pipeline.process_frame(frame, timestamp)

            if result:
                results_log.append(result)

                # Print events
                for event in result["events"]:
                    print(f"[EVENT] {event['event_type']} "
                          f"(confidence: {event['confidence']:.2f}) "
                          f"- {event['explanation']}")

                # Show visualization
                if args.show and result["detections"]:
                    from vision.detection.preprocessor import FramePreprocessor
                    preprocessor = FramePreprocessor()
                    vis = frame.copy()
                    # Draw detection boxes
                    for det in result["detections"]:
                        if hasattr(det, 'bbox'):
                            bbox = det.bbox
                        elif isinstance(det, dict) and 'bbox' in det:
                            import numpy as np
                            bbox = np.array(det['bbox'])
                        else:
                            continue
                        x1, y1, x2, y2 = bbox.astype(int) if hasattr(bbox, 'astype') else [int(b) for b in bbox]
                        cv2.rectangle(vis, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.imshow("Surveillance Pipeline", vis)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break

            # Print stats periodically
            if frame_count % 100 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed
                stats = pipeline.stats.to_dict()
                print(f"[STATS] Frame: {frame_count} | FPS: {fps:.1f} | "
                      f"Tracks: {stats['active_tracks']} | "
                      f"Events: {stats['total_events']} | "
                      f"Det Latency: {stats['avg_detection_latency_ms']:.1f}ms")

    except KeyboardInterrupt:
        print("\nInterrupted")
    finally:
        cap.release()
        if args.show:
            cv2.destroyAllWindows()

    # Final report
    elapsed = time.time() - start_time
    stats = pipeline.stats.to_dict()

    print(f"\n{'='*60}")
    print(f"Processing Complete")
    print(f"{'='*60}")
    print(f"Frames processed: {frame_count}")
    print(f"Total time: {elapsed:.1f}s")
    print(f"Average FPS: {frame_count/elapsed:.1f}")
    print(f"Total detections: {stats['total_detections']}")
    print(f"Total events: {stats['total_events']}")
    print(f"Avg detection latency: {stats['avg_detection_latency_ms']:.1f}ms")
    print(f"Avg tracking latency: {stats['avg_tracking_latency_ms']:.1f}ms")
    print(f"Active tracks at end: {stats['active_tracks']}")

    # Save results
    if args.output_json:
        output = {
            "stats": stats,
            "config": {
                "source": args.source,
                "model": args.model,
                "device": args.device,
                "confidence": args.confidence,
                "frame_skip": args.frame_skip,
            },
            "frames_processed": frame_count,
            "total_time_seconds": elapsed,
        }
        with open(args.output_json, "w") as f:
            json.dump(output, f, indent=2)
        print(f"\nResults saved to {args.output_json}")


if __name__ == "__main__":
    main()
