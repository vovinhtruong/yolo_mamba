"""Evaluate every baseline run on the validation set with its best.pt.

Every run folder in runs/train/baseline/ that has weights/best.pt is validated
once with model.val(), using the same data, split and batch for all runs.
Each run gets its own folder runs/eval/baseline/<run>/ with the Ultralytics
plots and a metrics.yaml file. Building tables is done by scripts/summarize/.

Usage:
    python eval_baseline.py
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

import yaml

# ===== SETTINGS (edit here) =====
ROOT = Path.home() / "VINH_TRUONG" / "yolo26"
TRAIN_DIR = ROOT / "runs" / "train" / "baseline" # take model
EVAL_DIR = ROOT / "runs" / "eval" / "baseline"   # output place
DATA = ROOT / "dataset" / "graz" / "data.yaml"
SPLIT = "val"
BATCH = 4  # same validation batch for every run
DEVICE = 0

LOGGER = logging.getLogger("eval_baseline")
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
    """Count the images of one split listed in a YOLO data.yaml.

    Args:
        data_yaml: Path to data.yaml.
        split: Split name, e.g. "val".

    Returns:
        Number of image files in that split folder.
    """
    data = yaml.safe_load(data_yaml.read_text())
    folder = Path(data[split])
    if not folder.is_absolute():
        folder = Path(data.get("path", data_yaml.parent)) / folder
    return sum(1 for p in folder.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES)


def evaluate_run(run_dir: Path, n_images: int) -> None:
    """Validate the best.pt of one run and save its metrics.yaml.

    Args:
        run_dir: One training run folder.
        n_images: Number of images in the evaluated split.
    """
    from ultralytics import YOLO  # imported here so YOLO_CONFIG_DIR is set first

    info = read_train_args(run_dir)
    model = YOLO(str(run_dir / "weights" / "best.pt"))
    yaml_file = model.model.yaml.get("yaml_file", "")  # e.g. yolo26n.yaml, stays correct after a resume
    if yaml_file:
        info["model"] = Path(yaml_file).stem
    metrics = model.val(data=str(DATA), split=SPLIT, imgsz=info["imgsz"], batch=BATCH, device=DEVICE,
                        project=str(EVAL_DIR), name=run_dir.name, exist_ok=True)
    result = {
        "run": run_dir.name, **info,
        "split": SPLIT, "val_batch": BATCH, "n_images": n_images,
        "precision": float(metrics.box.mp), "recall": float(metrics.box.mr),
        "mAP50": float(metrics.box.map50), "mAP50-95": float(metrics.box.map),
    }
    (EVAL_DIR / run_dir.name / "metrics.yaml").write_text(yaml.safe_dump(result, sort_keys=False))


def main() -> None:
    """Evaluate all baseline runs."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    os.environ["YOLO_CONFIG_DIR"] = str(ROOT / ".ultralytics_config")

    runs = find_runs(TRAIN_DIR)
    if not runs:
        LOGGER.error("No run with weights/best.pt found in %s", TRAIN_DIR)
        return
    n_images = count_images(DATA, SPLIT)
    for run_dir in runs:
        LOGGER.info("Evaluating %s", run_dir.name)
        evaluate_run(run_dir, n_images)
    LOGGER.info("Done: %d runs, results in %s", len(runs), EVAL_DIR)


if __name__ == "__main__":
    main()