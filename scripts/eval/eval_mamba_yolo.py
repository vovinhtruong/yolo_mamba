"""Evaluate every Mamba-YOLO run on all validation images and on each image size group.

Same evaluation as eval_input_size_effect.py (val split, All + P10 to P90, batch 4, the
training imgsz), for the reference model Mamba-YOLO-T trained in
~/VINH_TRUONG/mamba_yolo_ref/Mamba-YOLO/runs/. Every run folder there that has
weights/best.pt is validated with model.val(); each (run, image set) pair gets its own
folder runs/eval/mamba_yolo/<run>/<image_set>/ with the Ultralytics plots and a
metrics.yaml file (same fields as eval_input_size_effect.py).

Run it with the python of env_MambaYOLO (the Mamba-YOLO copy of Ultralytics 8.2.29),
not with the yolo26 env, because the model needs the Mamba-YOLO code.

Usage:
    ~/VINH_TRUONG/mamba_yolo_ref/Mamba-YOLO/env_MambaYOLO/bin/python eval_mamba_yolo.py
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

import yaml

from eval_input_size_effect import count_images, find_runs, read_train_args

# ===== SETTINGS (edit here) =====
ROOT = Path.home() / "VINH_TRUONG" / "yolo26"
MAMBA_ROOT = Path.home() / "VINH_TRUONG" / "mamba_yolo_ref" / "Mamba-YOLO"
TRAIN_DIR = MAMBA_ROOT / "runs"                     # Mamba-YOLO runs
EVAL_DIR = ROOT / "runs" / "eval" / "mamba_yolo"    # next to eval/input_size and eval/downscale
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

LOGGER = logging.getLogger("eval_mamba_yolo")


def evaluate_run(run_dir: Path, n_images: dict[str, int]) -> None:
    """Validate the best.pt of one run on every image set and save each metrics.yaml.

    Args:
        run_dir: One training run folder.
        n_images: Number of images per image set name.
    """
    from ultralytics import YOLO  # imported here so YOLO_CONFIG_DIR is set first

    info = read_train_args(run_dir)  # model = yaml file stem, e.g. Mamba-YOLO-T
    model = YOLO(str(run_dir / "weights" / "best.pt"))

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
    """Evaluate all Mamba-YOLO runs on every image set."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    os.environ["YOLO_CONFIG_DIR"] = str(MAMBA_ROOT / ".ultralytics_config")  # same as train.sh

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