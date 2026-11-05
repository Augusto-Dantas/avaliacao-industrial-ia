"""Run YOLO inference on an image, video, directory or camera source."""
from __future__ import annotations

import argparse
from pathlib import Path
from ultralytics import YOLO


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect visible welding defects")
    parser.add_argument("--weights", type=Path, required=True,
                        help="Path to trained best.pt")
    parser.add_argument("--source", required=True,
                        help="Image, video, directory, URL or camera index")
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", default=None)
    parser.add_argument("--name", default="welding-predictions")
    args = parser.parse_args()

    weights = args.weights.resolve()
    if not weights.is_file():
        raise FileNotFoundError(f"Model weights not found: {weights}")
    if not 0.0 <= args.conf <= 1.0:
        raise ValueError("--conf must be between 0 and 1.")

    model = YOLO(str(weights))
    predict_args = {
        "source": args.source,
        "conf": args.conf,
        "imgsz": args.imgsz,
        "project": str(ROOT / "runs/predict"),
        "name": args.name,
        "save": True,
    }
    if args.device:
        predict_args["device"] = args.device

    results = model.predict(**predict_args)
    print(f"Processed {len(results)} input item(s).")
    print(f"Predictions saved under {ROOT / 'runs/predict' / args.name}")


if __name__ == "__main__":
    main()
