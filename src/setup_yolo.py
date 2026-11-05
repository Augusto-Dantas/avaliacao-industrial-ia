"""Prepare the welding YOLO dataset and optionally train the detector.

Downloads the public Hugging Face dataset, maps train/valid/test to this
project's images/{train,val,test} and labels/{train,val,test}, writes data.yaml,
and can start training.
"""
from __future__ import annotations

import argparse
import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASET_ID = "rikkarth/welding-defect-object-detection"
DATASET_DIR = ROOT / "data/yolo/.download/welding-defect-object-detection"
TARGET_DIR = ROOT / "data/yolo"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
SPLIT_ALIASES = {
    "train": "train",
    "valid": "val",
    "validation": "val",
    "val": "val",
    "test": "test",
}


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def install_dependencies() -> None:
    # Preserve a working CPU/CUDA PyTorch. If missing or broken, use CPU wheels.
    torch_ok = False
    if importlib.util.find_spec("torch") is not None:
        check = subprocess.run(
            [sys.executable, "-c", "import torch"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        torch_ok = check.returncode == 0
    if not torch_ok:
        run([
            sys.executable, "-m", "pip", "install", "torch", "torchvision",
            "--index-url", "https://download.pytorch.org/whl/cpu",
        ])
    run([sys.executable, "-m", "pip", "install", "-r", "requirements-vision.txt"])


def download_dataset(force_download: bool = False) -> Path:
    from huggingface_hub import snapshot_download

    if force_download and DATASET_DIR.exists():
        shutil.rmtree(DATASET_DIR)
    DATASET_DIR.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading dataset {DATASET_ID} (approximately 104 MB)...", flush=True)
    downloaded = snapshot_download(
        repo_id=DATASET_ID,
        repo_type="dataset",
        local_dir=str(DATASET_DIR),
        allow_patterns=[
            "*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp",
            "*.txt", "*.yaml", "*.yml", "README.md",
        ],
    )
    return Path(downloaded)


def locate_source_splits(download_dir: Path) -> dict[str, tuple[Path, Path]]:
    found: dict[str, tuple[Path, Path]] = {}
    for images_dir in download_dir.rglob("images"):
        if not images_dir.is_dir():
            continue
        split_name = SPLIT_ALIASES.get(images_dir.parent.name.lower())
        labels_dir = images_dir.parent / "labels"
        if split_name and labels_dir.is_dir() and split_name not in found:
            found[split_name] = (images_dir, labels_dir)
    missing = {"train", "val"} - found.keys()
    if missing:
        raise RuntimeError(
            "Unexpected Hugging Face dataset layout. Missing image/label splits: "
            f"{', '.join(sorted(missing))}. Inspect: {download_dir}"
        )
    return found


def prepare_dataset(download_dir: Path, force: bool = False) -> Path:
    yaml_path = TARGET_DIR / "data.yaml"
    image_root = TARGET_DIR / "images"
    label_root = TARGET_DIR / "labels"

    if not force and yaml_path.is_file() and all(
        (image_root / split).is_dir() and (label_root / split).is_dir()
        for split in ("train", "val")
    ):
        print("A prepared YOLO dataset already exists; keeping it (use --force to replace).")
        return yaml_path

    source_splits = locate_source_splits(download_dir)
    if force:
        for directory in (image_root, label_root):
            if directory.exists():
                shutil.rmtree(directory)

    for split, (source_images, source_labels) in source_splits.items():
        target_images = image_root / split
        target_labels = label_root / split
        target_images.mkdir(parents=True, exist_ok=True)
        target_labels.mkdir(parents=True, exist_ok=True)
        image_count = 0
        label_count = 0

        for image_path in source_images.rglob("*"):
            if not image_path.is_file() or image_path.suffix.lower() not in IMAGE_SUFFIXES:
                continue
            relative = image_path.relative_to(source_images)
            destination_image = target_images / relative
            destination_image.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(image_path, destination_image)
            image_count += 1

            source_label = source_labels / relative.with_suffix(".txt")
            if source_label.is_file():
                destination_label = target_labels / relative.with_suffix(".txt")
                destination_label.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_label, destination_label)
                label_count += 1

        if image_count == 0 or label_count == 0:
            raise RuntimeError(
                f"Split '{split}' is incomplete: {image_count} images and "
                f"{label_count} annotation files."
            )
        print(f"{split}: {image_count} images, {label_count} label files")

    yaml_path.write_text(
        "path: data/yolo\n"
        "train: images/train\n"
        "val: images/val\n"
        "test: images/test\n"
        "names:\n"
        "  0: bad_weld\n"
        "  1: good_weld\n"
        "  2: defect\n",
        encoding="utf-8",
    )
    return yaml_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Install YOLO dependencies, download/prepare welding images, and optionally train."
    )
    parser.add_argument("--force", action="store_true",
                        help="Replace the local dataset and download a fresh copy.")
    parser.add_argument("--train", action="store_true",
                        help="Start training after preparing the dataset.")
    parser.add_argument("--weights", default="yolo26n.pt")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--device", default="cpu",
                        help="Training device (default: cpu; use 0 for an NVIDIA GPU).")
    args = parser.parse_args()

    if args.epochs < 1 or args.imgsz < 32 or args.batch < 1:
        parser.error("--epochs and --batch must be positive; --imgsz must be >= 32.")

    install_dependencies()
    download_dir = download_dataset(force_download=args.force)
    yaml_path = prepare_dataset(download_dir, force=args.force)
    print(f"YOLO dataset ready: {yaml_path}")
    print("The downloaded dataset is CC0; preserve source attribution in research outputs.")

    if args.train:
        run([
            sys.executable, "src/train_yolo.py",
            "--data", str(yaml_path),
            "--weights", args.weights,
            "--epochs", str(args.epochs),
            "--imgsz", str(args.imgsz),
            "--batch", str(args.batch),
            "--device", args.device,
        ])
    else:
        print("To train now, rerun with --train.")


if __name__ == "__main__":
    main()
