"""EigenCAM visualization for the YOLO26 fracture detection model.

Idea:
    Hook a forward hook into one backbone layer, run one forward pass, take
    the activations at that layer, then run PCA (principal component
    analysis) on them to build a heatmap. No class/box target is backpropped
    (unlike vanilla Grad-CAM) -> avoids the multi-box/NMS/multi-scale mess of
    object detection, robust default choice for YOLO-style models.
"""

import os
import cv2
import numpy as np
import torch
from ultralytics import YOLO
from pytorch_grad_cam import EigenCAM
from pytorch_grad_cam.utils.image import show_cam_on_image
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget

# ============================================================
# CONFIG
# ============================================================

MODEL_PATH = "/home/phuong/VINH_TRUONG/yolo26/runs/baseline/yolo26n_640/weights/best.pt"

TEST_IMAGES_DIR = os.path.expanduser(
    "~/VINH_TRUONG/yolo26/dataset/graz/split/test/images"
)

OUTPUT_DIR = os.path.expanduser(
    "~/VINH_TRUONG/yolo26/gradcam_output"
)

# Which layer to hook (model.model.model[TARGET_LAYER_INDEX]).
# yolo26n layer map (backbone -> neck):
#   9  = SPPF        (last pooling, right before attention)
#   10 = C2PSA        <- default hook, end of backbone, before neck
#   16 = last layer before Detect@P3 (small objects)
#   19 = last layer before Detect@P4 (medium objects)
#   22 = last layer before Detect@P5 (large objects)
# Idea for picking 10 (C2PSA): deep enough to be semantic, but feature map is
# still P5 resolution (20x20 @ imgsz=640) -> heatmap upsample still meaningful.
# Too shallow -> just edges/contrast, not "fracture" concept.
# Too deep/small feature map -> heatmap too blurry/blocky when upsampled.
TARGET_LAYER_INDEX = 10

IMGSZ = 640  # must match training imgsz

LIMIT = None  # test with small number first, e.g. 20, before full ~1938 run


# ============================================================
# HELPERS
# ============================================================

def letterbox(img, new_size=640, color=(114, 114, 114)):
    """Aspect-ratio resize + gray pad to a square canvas (YOLO-style preprocessing).

    Args:
        img (np.ndarray): Input BGR image.
        new_size (int): Target square size.
        color (tuple): Padding color (BGR).

    Returns:
        (np.ndarray): Letterboxed square image, shape (new_size, new_size, 3).
    """
    h, w = img.shape[:2]
    scale = min(new_size / h, new_size / w)
    nh, nw = int(round(h * scale)), int(round(w * scale))
    resized = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_LINEAR)

    canvas = np.full((new_size, new_size, 3), color, dtype=np.uint8)
    top = (new_size - nh) // 2
    left = (new_size - nw) // 2
    canvas[top:top + nh, left:left + nw] = resized
    return canvas


def load_image_as_tensor(image_path, imgsz):
    """Read an image and convert it into the model's input tensor format.

    Args:
        image_path (str): Path to the image file.
        imgsz (int): Target square input size.

    Returns:
        (torch.Tensor | None): Input tensor, shape (1, 3, imgsz, imgsz), RGB, [0,1].
        (np.ndarray | None): Same image as float RGB array, reused for the overlay draw.
    """
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        return None, None
    if img_bgr.ndim == 2:  # grayscale -> 3ch
        img_bgr = cv2.cvtColor(img_bgr, cv2.COLOR_GRAY2BGR)

    img_letterboxed = letterbox(img_bgr, imgsz)
    img_rgb = cv2.cvtColor(img_letterboxed, cv2.COLOR_BGR2RGB)
    img_float = img_rgb.astype(np.float32) / 255.0

    tensor = torch.from_numpy(img_float).permute(2, 0, 1).unsqueeze(0)
    return tensor, img_float


# ============================================================
# MAIN
# ============================================================

def main():
    """Run EigenCAM over every image in TEST_IMAGES_DIR, save overlays to OUTPUT_DIR."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Loading: {MODEL_PATH}")
    yolo = YOLO(MODEL_PATH)
    model = yolo.model  # real nn.Module (DetectionModel)
    model.eval()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)

    target_layer = model.model[TARGET_LAYER_INDEX]
    print(f"Target layer {TARGET_LAYER_INDEX}: {type(target_layer).__name__}")

    cam = EigenCAM(model=model, target_layers=[target_layer])

    image_files = sorted(
        f for f in os.listdir(TEST_IMAGES_DIR)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    )
    if LIMIT is not None:
        image_files = image_files[:LIMIT]

    print(f"Total: {len(image_files)} images")

    for i, filename in enumerate(image_files):
        image_path = os.path.join(TEST_IMAGES_DIR, filename)
        tensor, img_float = load_image_as_tensor(image_path, IMGSZ)
        if tensor is None:
            print(f"  [skip] unreadable: {filename}")
            continue

        tensor = tensor.to(device)

        # Dummy target — EigenCAM never backprops through it, it's only here
        # to skip pytorch-grad-cam's auto-argmax on a detection output shape
        # it can't parse as a classification output.
        targets = [ClassifierOutputTarget(0)]

        grayscale_cam = cam(input_tensor=tensor, targets=targets)[0]

        overlay = show_cam_on_image(img_float, grayscale_cam, use_rgb=True)
        overlay_bgr = cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR)
        cv2.imwrite(os.path.join(OUTPUT_DIR, filename), overlay_bgr)

        if (i + 1) % 50 == 0 or (i + 1) == len(image_files):
            print(f"  {i + 1}/{len(image_files)}")

    print(f"\nDone -> {OUTPUT_DIR}")


if __name__ == "__main__":
    main()