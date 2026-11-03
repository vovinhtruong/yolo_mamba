"""Train YOLO26n at 640 px with a chosen downscaling interpolation (detail-preserving downscaling, step 2)."""

from __future__ import annotations

import logging
import os
from pathlib import Path

import cv2
import yaml

# ===== SETTINGS (edit here) =====
ROOT = Path.home() / "VINH_TRUONG" / "yolo26"
MODEL = ROOT / "base_models" / "yolo26n.pt"
DATA = ROOT / "dataset" / "graz" / "data.yaml"
PROJECT = ROOT / "runs" / "train" / "downscale"
INTERP = "area"  # area, linear, cubic or lanczos
IMGSZ = 640
SEEDS = [0, 1, 2]
BATCH = 4
EPOCHS = 50
DEVICE = 0

INTERP_FLAGS = {
    "linear": cv2.INTER_LINEAR,
    "area": cv2.INTER_AREA,
    "cubic": cv2.INTER_CUBIC,
    "lanczos": cv2.INTER_LANCZOS4,
}
LOGGER = logging.getLogger("train_downscale")

class Cv2Downscale:
    """Stand-in for the cv2 module inside ultralytics/data/base.py.

    Every cv2 name is passed through unchanged, except resize: when the output is
    smaller than the input, the interpolation is replaced by the chosen flag.

    Args:
        flag: OpenCV interpolation flag used when an image is shrunk.
    """

    def __init__(self, flag: int) -> None:
        self.flag = flag

    def __getattr__(self, name: str):
        return getattr(cv2, name)

    def resize(self, img, dsize, *args, **kwargs):
        """cv2.resize, with the chosen interpolation when the image gets smaller."""
        h, w = img.shape[:2]
        if dsize[0] * dsize[1] < w * h:
            kwargs["interpolation"] = self.flag
        return cv2.resize(img, dsize, *args, **kwargs)
    
def use_downscale_interp(interp: str) -> None:
    """Make Ultralytics shrink images with the given interpolation.

    Args:
        interp: Key of INTERP_FLAGS, e.g. "area".
    """
    import ultralytics.data.base as base

    base.cv2 = Cv2Downscale(INTERP_FLAGS[interp])
    LOGGER.info("load_image now shrinks with %s", interp)

def train_seed(seed: int) -> None:
    """Train one seed with the same settings as the 640 baseline.

    Args:
        seed: Random seed for this run.
    """
    import ultralytics
    from ultralytics import YOLO

    name = f"imgsz{IMGSZ}_{INTERP}_seed{seed}"  # e.g. imgsz640_area_seed0
    model = YOLO(str(MODEL))
    model.train(data=str(DATA), epochs=EPOCHS, imgsz=IMGSZ, batch=BATCH, seed=seed,
                device=DEVICE, project=str(PROJECT), name=name)

    info = {
        "interp": INTERP,
        "applies_to": "BaseDataset.load_image when an image is shrunk (train and val); enlarging stays linear",
        "ultralytics": ultralytics.__version__,
    }
    (Path(model.trainer.save_dir) / "downscale.yaml").write_text(yaml.safe_dump(info, sort_keys=False))

def main() -> None:
    """Train every seed with the chosen interpolation."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    os.environ["YOLO_CONFIG_DIR"] = str(ROOT / ".ultralytics_config")  # same as train.sh
    use_downscale_interp(INTERP)
    for seed in SEEDS:
        LOGGER.info("Training %s seed %d", INTERP, seed)
        train_seed(seed)

if __name__ == "__main__":
    main()