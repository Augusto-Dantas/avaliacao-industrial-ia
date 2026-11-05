"""Download and prepare public welding datasets with a configurable total size cap.

Only the CC0 YOLO dataset is wired into the current detector training pipeline.
Other datasets are downloaded into isolated source folders because their tasks,
annotation schemas, and splits are not interchangeable.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET_DIR = ROOT / "data/yolo"
SOURCES_DIR = TARGET_DIR / "sources"
CACHE_DIR = TARGET_DIR / ".download"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
SPLIT_ALIASES = {
    "train": "train", "valid": "val", "validation": "val",
    "val": "val", "test": "test",
}

# Public datasets with a visible license and a welding-inspection use case.
# Keep every source isolated; do not merge incompatible labels/tasks.
DATASETS = [
    {
        "id": "rikkarth/welding-defect-object-detection",
        "folder": "welding-defect-object-detection",
        "license": "CC0-1.0",
        "task": "object-detection",
        "description": "2,028 weld images; native YOLO boxes; 3 classes.",
        "train_yolo": True,
    },
    {
        "id": "AI4Manufacturing/217",
        "folder": "ai4manufacturing-217-smaw",
        "license": "CC BY 4.0 (upstream Mendeley Data)",
        "task": "object-detection-parquet",
        "description": "448 SMAW surface-defect images with pixel-coordinate boxes; parquet/schema conversion required.",
        "train_yolo": False,
    },
    {
        "id": "AI4Manufacturing/218",
        "folder": "ai4manufacturing-218-laser-weld",
        "license": "CC BY 4.0 (upstream Zenodo)",
        "task": "image-classification",
        "description": "61,670 laser-weld seam strips; image-level ok/defective labels, not bounding boxes.",
        "train_yolo": False,
    },
    {
        "id": "AI4Manufacturing/105",
        "folder": "ai4manufacturing-105-tig-ss304",
        "license": "CC BY-SA 4.0 (upstream Kaggle; gated research access)",
        "task": "run-level-image-classification",
        "description": "45,058 TIG SS304 frames from 58 runs; six run-level labels; about 9.93 GB; run-wise splits required.",
        "gated": True,
        "train_yolo": False,
    },
    {
        "id": "AI4Manufacturing/219",
        "folder": "ai4manufacturing-219-bam-hot-cracking",
        "license": "CC BY 4.0 (upstream Zenodo; gated access)",
        "task": "metallography-crack-inspection",
        "description": "609 metallographic weld cross-section images; hot-cracking microscopy; about 11.6 GB; specimen-wise splits required.",
        "gated": True,
        "train_yolo": False,
    },
]


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def install_dependencies() -> None:
    # Avoid pulling CUDA wheels onto CPU-only machines.
    torch_ok = False
    if importlib.util.find_spec("torch") is not None:
        check = subprocess.run(
            [sys.executable, "-c", "import torch"],
            cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        torch_ok = check.returncode == 0
    if not torch_ok:
        run([
            sys.executable, "-m", "pip", "install", "torch", "torchvision",
            "--index-url", "https://download.pytorch.org/whl/cpu",
        ])
    run([sys.executable, "-m", "pip", "install", "-r", "requirements-vision.txt"])


def dataset_size_bytes(api, repo_id: str) -> int:
    info = api.dataset_info(repo_id, files_metadata=True)
    siblings = info.siblings or []
    sizes = [getattr(item, "size", None) for item in siblings]
    if not siblings or any(size is None for size in sizes):
        raise RuntimeError(
            f"Could not reliably calculate the size of {repo_id}; "
            "refusing to download it under a strict disk quota."
        )
    return sum(int(size) for size in sizes)


def download_catalog(max_gb: float, selected: list[str], force: bool = False) -> list[dict]:
    from huggingface_hub import HfApi, snapshot_download

    api = HfApi()
    chosen = [item for item in DATASETS if item["id"] in selected]
    if not chosen:
        raise RuntimeError("No valid datasets selected.")

    planned = []
    total = 0
    for item in chosen:
        try:
            size = dataset_size_bytes(api, item["id"])
        except Exception as exc:
            print(f"SKIP {item['id']}: cannot verify repository size ({exc}).")
            continue
        if total + size > max_gb * 1_000_000_000:
            print(
                f"SKIP {item['id']}: {size / 1_000_000_000:.2f} GB would exceed "
                f"the {max_gb:.2f} GB total limit."
            )
            continue
        planned.append((item, size))
        total += size

    print(f"Selected download budget: {total / 1_000_000_000:.2f} GB / {max_gb:.2f} GB")
    manifest = []
    for item, size in planned:
        destination = SOURCES_DIR / item["folder"]
        marker = destination / ".download-complete.json"
        status = "downloaded"
        if marker.exists() and not force:
            print(f"Already downloaded: {item['id']} (use --force to refresh)")
            status = "already-present"
        else:
            print(
                f"Downloading {item['id']} ({size / 1024**2:.1f} MiB) "
                f"[{item['license']}]"
            )
            try:
                snapshot_download(
                    repo_id=item["id"], repo_type="dataset",
                    local_dir=str(destination),
                )
                marker.write_text(json.dumps({
                    "repo_id": item["id"], "license": item["license"],
                    "size_bytes_at_download": size,
                }, indent=2), encoding="utf-8")
            except Exception as exc:
                status = "skipped-access-or-download-error"
                print(
                    f"SKIP {item['id']}: download unavailable. If gated, open "
                    f"https://huggingface.co/datasets/{item['id']}, request/accept "
                    f"access, then rerun. Details: {exc}"
                )
                if destination.exists() and not marker.exists():
                    shutil.rmtree(destination, ignore_errors=True)
        manifest.append({
            **item, "size_bytes": size, "status": status,
            "local_path": str(destination.relative_to(ROOT)),
        })

    (TARGET_DIR / "datasets-manifest.json").write_text(
        json.dumps({
            "max_gib": max_gb,
            "planned_bytes": total,
            "downloaded_bytes": sum(
                item["size_bytes"] for item in manifest
                if item["status"] in {"downloaded", "already-present"}
            ),
            "datasets": manifest,
            "note": "Downloaded datasets remain isolated; only the CC0 native-YOLO source is prepared for the current detector.",
        }, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return manifest


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
            "Unexpected YOLO dataset layout. Missing splits: "
            f"{', '.join(sorted(missing))}. Inspect {download_dir}"
        )
    return found


def prepare_yolo_dataset(download_dir: Path, force: bool = False) -> Path:
    yaml_path = TARGET_DIR / "data.yaml"
    image_root, label_root = TARGET_DIR / "images", TARGET_DIR / "labels"
    if not force and yaml_path.is_file() and all(
        (image_root / split).is_dir() and (label_root / split).is_dir()
        for split in ("train", "val")
    ):
        print("Prepared YOLO dataset exists; keeping it (use --force to rebuild).")
        return yaml_path

    source_splits = locate_source_splits(download_dir)
    if force:
        for directory in (image_root, label_root):
            if directory.exists():
                shutil.rmtree(directory)

    for split, (source_images, source_labels) in source_splits.items():
        target_images, target_labels = image_root / split, label_root / split
        target_images.mkdir(parents=True, exist_ok=True)
        target_labels.mkdir(parents=True, exist_ok=True)
        image_count = label_count = 0
        for image_path in source_images.rglob("*"):
            if not image_path.is_file() or image_path.suffix.lower() not in IMAGE_SUFFIXES:
                continue
            relative = image_path.relative_to(source_images)
            out_image = target_images / relative
            out_image.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(image_path, out_image)
            image_count += 1
            source_label = source_labels / relative.with_suffix(".txt")
            if source_label.is_file():
                out_label = target_labels / relative.with_suffix(".txt")
                out_label.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_label, out_label)
                label_count += 1
        if image_count == 0 or label_count == 0:
            raise RuntimeError(
                f"Split {split!r} incomplete: {image_count} images, {label_count} labels."
            )
        print(f"{split}: {image_count} images, {label_count} annotation files")

    yaml_path.write_text(
        "path: data/yolo\ntrain: images/train\nval: images/val\ntest: images/test\n"
        "names:\n  0: bad_weld\n  1: good_weld\n  2: defect\n",
        encoding="utf-8",
    )
    return yaml_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Install YOLO dependencies and download welding datasets within a disk quota."
    )
    parser.add_argument("--max-gb", type=float, default=25.0,
                        help="Maximum combined dataset download size in GB (default: 25).")
    parser.add_argument("--datasets", nargs="+", choices=[d["id"] for d in DATASETS],
                        default=[d["id"] for d in DATASETS],
                        help="Dataset IDs to download (default: all catalog entries).")
    parser.add_argument("--force", action="store_true",
                        help="Refresh selected downloads and rebuild the YOLO dataset.")
    parser.add_argument("--no-install", action="store_true",
                        help="Do not install Python/PyTorch/Ultralytics dependencies.")
    parser.add_argument("--train", action="store_true",
                        help="Train after downloading and preparing the native YOLO dataset.")
    parser.add_argument("--weights", default="yolo26n.pt")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--device", default="cpu",
                        help="Use cpu by default; use 0 only with compatible CUDA PyTorch.")
    args = parser.parse_args()

    if args.max_gb <= 0 or args.epochs < 1 or args.imgsz < 32 or args.batch < 1:
        parser.error("--max-gb, --epochs and --batch must be positive; --imgsz must be >= 32.")
    if not args.no_install:
        install_dependencies()

    manifest = download_catalog(args.max_gb, args.datasets, force=args.force)
    primary = next(
        (item for item in manifest if item["train_yolo"]), None
    )
    if primary is None:
        raise RuntimeError(
            "The selected datasets do not include the native YOLO detection dataset. "
            "Include rikkarth/welding-defect-object-detection to prepare/train YOLO."
        )

    source_dir = SOURCES_DIR / primary["folder"]
    yaml_path = prepare_yolo_dataset(source_dir, force=args.force)
    print(f"YOLO dataset ready: {yaml_path}")
    print("Other datasets were downloaded separately; their labels/tasks are not mixed.")

    if args.train:
        run([
            sys.executable, "src/train_yolo.py", "--data", str(yaml_path),
            "--weights", args.weights, "--epochs", str(args.epochs),
            "--imgsz", str(args.imgsz), "--batch", str(args.batch),
            "--device", args.device,
        ])
    else:
        print("Dataset preparation complete. Add --train to start YOLO training.")


if __name__ == "__main__":
    main()
