"""Evaluate every input size run on all validation images and on each image size group.

Every run folder in runs/train/input_size/ that has weights/best.pt is validated
with model.val() at its training imgsz, once on all validation images (All) and
once on each of the five image size groups (P10 to P90). All evaluations use the
same split and batch. Each (run, image set) pair gets its own folder
runs/eval/input_size/<run>/<image_set>/ with the Ultralytics plots and a
metrics.yaml file. Building tables is done by scripts/summarize/.

Usage:
    python eval_input_size_effect.py
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

import yaml

# ===== SETTINGS (edit here) =====
ROOT = Path.home() / "VINH_TRUONG" / "yolo26"
TRAIN_DIR = ROOT / "runs" / "train" / "input_size"
EVAL_DIR = ROOT / "runs" / "eval" / "input_size"
GROUP_DIR = ROOT / "dataset" / "graz" / "percentile_groups"
IMAGE_SETS = {  # image set name -> data yaml
    "All": ROOT / "dataset" / "graz" / "data.yaml",
    "P10": GROUP_DIR / "val_768.yaml",   # smallest images
    "P30": GROUP_DIR / "val_896.yaml",
    "P50": GROUP_DIR / "val_992.yaml",
    "P70": GROUP_DIR / "val_1120.yaml",
    "P90": GROUP_DIR / "val_1280.yaml",  # largest images
}
SPLIT = "val"
BATCH = 4  # same validation batch for every evaluation
DEVICE = 0

LOGGER = logging.getLogger("eval_input_size_effect")
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


def find_runs(train_dir: Path) -> list[Path]:
    """Find run folders that contain weights/best.pt.

    Args:
        train_dir: Folder that holds one sub-folder per training run.

    Returns:
        Run folders sorted by name.
    """
    return sorted(p for p in train_dir.iterdir() if (p / "weights" / "best.pt").is_file())


def read_train_args(run_dir: Path) -> dict:
    """Read the training settings that Ultralytics saved in args.yaml.

    Args:
        run_dir: One training run folder.

    Returns:
        Model file stem, imgsz, batch, seed and epochs used for training.
    """
    args = yaml.safe_load((run_dir / "args.yaml").read_text())
    return {
        "model": Path(str(args["model"])).stem,
        "imgsz": args["imgsz"],
        "train_batch": args["batch"],
        "seed": args["seed"],
        "epochs": args["epochs"],
    }


def count_images(data_yaml: Path, split: str) -> int:
    """Count the images of one split in a YOLO data yaml.

    The split entry may be an image folder (data.yaml) or a .txt list of
    image paths (the group yamls).

    Args:
        data_yaml: Path to the data yaml.
        split: Split name, e.g. "val".

    Returns:
        Number of images in that split.
    """
    data = yaml.safe_load(data_yaml.read_text())
    source = Path(data[split])
    if not source.is_absolute():
        source = Path(data.get("path", data_yaml.parent)) / source
    if source.is_file():
        return sum(1 for line in source.read_text().splitlines() if line.strip())
    return sum(1 for p in source.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES)


def evaluate_run(run_dir: Path, n_images: dict[str, int]) -> None:
    """Validate the best.pt of one run on every image set and save each metrics.yaml.

    Args:
        run_dir: One training run folder.
        n_images: Number of images per image set name.
    """
    from ultralytics import YOLO  # imported here so YOLO_CONFIG_DIR is set first

    info = read_train_args(run_dir)
    model = YOLO(str(run_dir / "weights" / "best.pt"))
    yaml_file = model.model.yaml.get("yaml_file", "")  # e.g. yolo26n.yaml, stays correct after a resume
    if yaml_file:
        info["model"] = Path(yaml_file).stem

    for name, data_yaml in IMAGE_SETS.items():
        LOGGER.info("  %s | %s", run_dir.name, name)
        out_dir = EVAL_DIR / run_dir.name / name
        metrics = model.val(data=str(data_yaml), split=SPLIT, imgsz=info["imgsz"], batch=BATCH, device=DEVICE,
                            project=str(out_dir.parent), name=name, exist_ok=True)
        result = {
            "run": run_dir.name, **info,
            "image_set": name, "data": str(data_yaml),
            "split": SPLIT, "val_batch": BATCH, "n_images": n_images[name],
            "precision": float(metrics.box.mp), "recall": float(metrics.box.mr),
            "mAP50": float(metrics.box.map50), "mAP50-95": float(metrics.box.map),
        }
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "metrics.yaml").write_text(yaml.safe_dump(result, sort_keys=False))


def main() -> None:
    """Evaluate all input size runs on every image set."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    os.environ["YOLO_CONFIG_DIR"] = str(ROOT / ".ultralytics_config")

    runs = find_runs(TRAIN_DIR)
    if not runs:
        LOGGER.error("No run with weights/best.pt found in %s", TRAIN_DIR)
        return
    missing = [str(p) for p in IMAGE_SETS.values() if not p.is_file()]
    if missing:
        LOGGER.error("Data yaml not found: %s", ", ".join(missing))
        return
    n_images = {name: count_images(path, SPLIT) for name, path in IMAGE_SETS.items()}
    LOGGER.info("Images per set: %s", n_images)

    for run_dir in runs:
        LOGGER.info("Evaluating %s", run_dir.name)
        evaluate_run(run_dir, n_images)
    LOGGER.info("Done: %d runs x %d image sets, results in %s", len(runs), len(IMAGE_SETS), EVAL_DIR)


if __name__ == "__main__":
    main()