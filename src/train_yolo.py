"""Train an Ultralytics YOLO detector on an annotated welding dataset.

The dataset itself is intentionally not committed. See docs/dataset_yolo.md.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from ultralytics import YOLO


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a YOLO welding-defect detector")
    parser.add_argument("--data", type=Path, default=ROOT / "data/yolo/data.yaml",
                        help="Ultralytics dataset YAML")
    parser.add_argument("--weights", default="yolo26n.pt",
                        help="Pretrained model or model YAML (default: yolo26n.pt)")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--device", default=None,
                        help="Examples: 0, cpu. Omit for automatic selection.")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--name", default="welding-yolo")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data_yaml = args.data.resolve()
    if not data_yaml.is_file():
        raise FileNotFoundError(
            f"Dataset YAML not found: {data_yaml}. Follow docs/dataset_yolo.md first."
        )
    if args.epochs < 1 or args.imgsz < 32 or args.batch < 1:
        raise ValueError("epochs, imgsz and batch must be positive (imgsz >= 32).")

    model = YOLO(args.weights)
    train_args = {
        "data": str(data_yaml),
        "epochs": args.epochs,
        "imgsz": args.imgsz,
        "batch": args.batch,
        "workers": args.workers,
        "project": str(ROOT / "runs/detect"),
        "name": args.name,
        "exist_ok": True,
        "plots": True,
        "seed": 42,
    }
    if args.device:
        train_args["device"] = args.device

    results = model.train(**train_args)
    best = Path(model.trainer.best).resolve()
    print(f"Training complete. Best weights: {best}")
    print(f"Results directory: {Path(results.save_dir).resolve()}")


if __name__ == "__main__":
    main()
