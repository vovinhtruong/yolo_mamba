"""Evaluate every downscale run on all validation images and on each image size group.

Same evaluation as eval_input_size_effect.py (val split, All + P10 to P90, batch 4),
except that each run's validation images are shrunk with the interpolation written in
its downscale.yaml, the same one used in training.

Usage:
    python eval_downscale.py
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "train"))  # scripts/train
from train_downscale import use_downscale_interp  # noqa: E402
from eval_input_size_effect import count_images, find_runs, read_train_args  # noqa: E402

# ===== SETTINGS (edit here) =====
ROOT = Path.home() / "VINH_TRUONG" / "yolo26"
TRAIN_DIR = ROOT / "runs" / "train" / "downscale"
EVAL_DIR = ROOT / "runs" / "eval" / "downscale"
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

LOGGER = logging.getLogger("eval_downscale")

def evaluate_run(run_dir: Path, n_images: dict[str, int]) -> None:
    """Validate the best.pt of one run on every image set and save each metrics.yaml.

    The validation images are shrunk with the interpolation written in the run's downscale.yaml.

    Args:
        run_dir: One training run folder.
        n_images: Number of images per image set name.
    """
    from ultralytics import YOLO  # imported here so YOLO_CONFIG_DIR is set first

    interp = yaml.safe_load((run_dir / "downscale.yaml").read_text())["interp"]
    use_downscale_interp(interp)

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
            "run": run_dir.name, **info, "interp": interp,
            "image_set": name, "data": str(data_yaml),
            "split": SPLIT, "val_batch": BATCH, "n_images": n_images[name],
            "precision": float(metrics.box.mp), "recall": float(metrics.box.mr),
            "mAP50": float(metrics.box.map50), "mAP50-95": float(metrics.box.map),
        }
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "metrics.yaml").write_text(yaml.safe_dump(result, sort_keys=False))

def main() -> None:
    """Evaluate all downscale runs on every image set."""
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