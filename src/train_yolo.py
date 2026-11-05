"""Train an Ultralytics YOLO detector on an annotated welding dataset.

The dataset is not committed. Prepare it locally as described in
docs/dataset_yolo.md before starting a training run.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a YOLO welding-defect detector")
    parser.add_argument("--data", type=Path, default=ROOT / "data/yolo/data.yaml",
                        help="Ultralytics dataset YAML")
    parser.add_argument("--weights", default="yolo26n.pt",
                        help="Pretrained model or model YAML (default: yolo26n.pt)")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--device", default=None,
                        help="Examples: 0, cpu. Omit for automatic selection.")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--name", default="welding-yolo")
    return parser.parse_args()


def validate_dataset(data_yaml: Path) -> None:
    if not data_yaml.is_file():
        raise FileNotFoundError(
            f"Dataset configuration not found: {data_yaml}\n"
            "Create it from data/yolo/data.yaml and follow docs/dataset_yolo.md."
        )

    try:
        config = yaml.safe_load(data_yaml.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in {data_yaml}: {exc}") from exc

    configured_root = Path(config.get("path", data_yaml.parent))
    dataset_root = configured_root if configured_root.is_absolute() else (ROOT / configured_root).resolve()

    missing = []
    empty = []
    for split in ("train", "val"):
        split_value = config.get(split)
        if not split_value:
            missing.append(f"{split}: not configured in {data_yaml}")
            continue

        split_path = Path(split_value)
        split_path = split_path if split_path.is_absolute() else dataset_root / split_path
        if not split_path.is_dir():
            missing.append(f"{split}: {split_path}")
            continue

        images = [
            path for path in split_path.rglob("*")
            if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
        ]
        if not images:
            empty.append(f"{split}: {split_path} (no supported image files)")

    if missing or empty:
        details = "\n".join([*(f"- Missing: {item}" for item in missing),
                              *(f"- Empty: {item}" for item in empty)])
        raise FileNotFoundError(
            "YOLO dataset is not ready; training was not started.\n"
            f"{details}\n"
            "Download/prepare the images and YOLO labels first. See docs/dataset_yolo.md "
            "and data/yolo/README.md. The CSV in data/ is tabular and cannot be used "
            "as an image dataset."
        )

    if not config.get("names"):
        raise ValueError(f"No class names found in {data_yaml} (expected 'names').")


def main() -> None:
    args = parse_args()
    data_yaml = args.data.expanduser().resolve()
    if args.epochs < 1 or args.imgsz < 32 or args.batch < 1 or args.workers < 0:
        raise ValueError("epochs/batch must be positive, imgsz >= 32 and workers >= 0.")

    # Fail early with an actionable message, before downloading weights or importing torch.
    validate_dataset(data_yaml)

    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise SystemExit(
            "YOLO dependencies are not installed. Run: pip install -r requirements-vision.txt"
        ) from exc

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
