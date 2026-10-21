"""
Phase 0: measure native resolution distribution of GRAZPEDWRI-DX before any
architecture change.
"""

import pathlib
import sys

import pandas as pd
import numpy as np
from PIL import Image

# ===== CONFIG =====
ROOT = pathlib.Path("~/VINH_TRUONG/yolo26/dataset/graz").expanduser()
CSV_PATH = ROOT / "dataset.csv"
IMAGES_DIR = ROOT / "processed_dataset" / "images"
SPLIT_DIR = ROOT / "split"
OUTPUT_DIR = pathlib.Path("~/VINH_TRUONG/yolo26/resolution_outputs").expanduser()
PERCENTILES = [0.10, 0.30, 0.50, 0.70, 0.90]  # imgsz candidates = these quantiles of train max_dim
STRIDE = 32                                   # imgsz must be a multiple of the model max stride

SPLIT_TITLES = {"train": "Training", "val": "Validation", "test": "Test"}  # split -> word used in the plot title
# PIL mode -> channel count
MODE_TO_CHANNELS = {
    "1": 1, "L": 1, "P": 1, "I": 1, "F": 1,
    "LA": 2, "PA": 2,
    "RGB": 3, "YCbCr": 3, "HSV": 3,
    "RGBA": 4, "CMYK": 4,
}


def check_paths():
    problems = []
    if not CSV_PATH.exists():
        problems.append(f"dataset.csv not found at: {CSV_PATH}")
    if not IMAGES_DIR.exists():
        problems.append(f"images dir not found at: {IMAGES_DIR}")
    if problems:
        print("\n[analyze_resolution.py] ERROR: expected dataset files not found.")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_image_stems():
    # all rows, not just fracture_visible==1 (all images go through letterbox at train time)
    df = pd.read_csv(CSV_PATH)
    return df[["filestem", "patient_id", "fracture_visible"]].reset_index(drop=True)


def load_split_membership():
    # split_dataset.py symlinks into SPLIT_DIR/{train,val,test}/images/, no .txt lists
    membership = {}
    for split_name in ("train", "val", "test"):
        split_images_dir = SPLIT_DIR / split_name / "images"
        if not split_images_dir.exists():
            continue
        for entry in split_images_dir.iterdir():
            membership[entry.stem] = split_name
    return membership


def find_image_path(stem):
    return IMAGES_DIR / f"{stem}.png"


def compute_resolutions(stems_df, split_membership):
    records = []
    missing = 0
    for _, row in stems_df.iterrows():
        stem = row["filestem"]
        img_path = find_image_path(stem)
        if not img_path.exists():
            missing += 1
            continue

        with Image.open(img_path) as im:
            w, h = im.size
            mode = im.mode

        records.append({
            "filestem": stem,
            "patient_id": row["patient_id"],
            "fracture_visible": row["fracture_visible"],
            "split": split_membership.get(stem, "unknown"),
            "height": h,
            "width": w,
            "channels": MODE_TO_CHANNELS.get(mode),
            "max_dim": max(w, h),  # scale = imgsz / max_dim under letterbox resize
            "aspect_ratio": round(w / h, 4) if h else None,
        })

    if missing:
        print(f"[analyze_resolution.py] WARNING: {missing} images not found in {IMAGES_DIR}",
              file=sys.stderr)

    return pd.DataFrame.from_records(records)


def compute_imgsz_design(res_df):
    """Derive candidate imgsz values and matching resolution groups from the data.

    Idea:
        imgsz = quantiles of train max_dim (equal-frequency), rounded to STRIDE.
        Each image belongs to the imgsz closest to its max_dim in RATIO terms,
        so group boundaries are geometric means sqrt(a*b) of neighbouring imgsz.

    Args:
        res_df (pd.DataFrame): per-image table with columns split, max_dim.

    Returns:
        (pd.DataFrame): one row per imgsz with percentile value, imgsz, group bounds, counts.
    """
    train_dim = res_df.loc[res_df["split"] == "train", "max_dim"]
    q = train_dim.quantile(PERCENTILES).to_numpy()
    imgsz = (np.round(q / STRIDE) * STRIDE).astype(int)
    bounds = [res_df["max_dim"].min()] + [np.sqrt(a * b) for a, b in zip(imgsz[:-1], imgsz[1:])] + [res_df["max_dim"].max()]
    group = pd.cut(res_df["max_dim"], bins=bounds, labels=False, include_lowest=True)  # include_lowest keeps the smallest image

    rows = []
    for i, p in enumerate(PERCENTILES):
        in_group = group == i
        rows.append({
            "percentile": f"P{round(p * 100)}",
            "max_dim_train": round(q[i], 1),
            "imgsz": int(imgsz[i]),
            "lower": round(bounds[i], 1),
            "upper": round(bounds[i + 1], 1),
            "n_train": int((in_group & (res_df["split"] == "train")).sum()),
            "n_val": int((in_group & (res_df["split"] == "val")).sum()),
        })
    return pd.DataFrame(rows)


def export_excel(res_df, design_df):
    excel_path = OUTPUT_DIR / "resolution_per_image_train.xlsx"
    with pd.ExcelWriter(excel_path) as writer:
        res_df.to_excel(writer, index=False, sheet_name="resolution")
        design_df.to_excel(writer, index=False, sheet_name="design")
    return excel_path


def plot_histogram(res_df, design_df, split):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    BIN_WIDTH = 26  # px; matches the bin width Excel picks automatically

    dim = res_df.loc[res_df["split"] == split, "max_dim"]
    bin_edges = np.arange(dim.min(), dim.max() + BIN_WIDTH, BIN_WIDTH)

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.grid(axis="y", color="lightgray", linewidth=0.5, alpha=0.7, zorder=0)
    ax.hist(dim, bins=bin_edges, color="#3B6EA5", edgecolor="white")

    edges = [design_df["lower"].iloc[0]] + design_df["upper"].tolist()
    counts = pd.cut(dim, bins=edges, labels=False, include_lowest=True).value_counts()  # images per design group in this split

    y_top = ax.get_ylim()[1]
    for i, d in design_df.iterrows():  # percentile imgsz (always from TRAIN), labelled at the top
        ax.axvline(d["imgsz"], color="#C0392B", linestyle="--", linewidth=1.2)
        ax.text(d["imgsz"], y_top, f'{d["percentile"]}\n{d["imgsz"]}\nn = {counts.get(i, 0):,}',
                ha="center", va="bottom", fontsize=8, color="#C0392B")

    ax.axvline(640, color="#27AE60", linewidth=1.5)  # YOLO default imgsz, reference only
    ax.text(640, y_top, "default\n640\n", ha="center", va="bottom", fontsize=8, color="#27AE60")

    tick_pos = bin_edges[:-1] + BIN_WIDTH / 2
    tick_labels = [f"{int(edge)}, {int(edge + BIN_WIDTH)}" for edge in bin_edges[:-1]]
    ax.set_xticks(tick_pos)
    ax.set_xticklabels(tick_labels, rotation=90, fontsize=6)
    ax.set_xlim(bin_edges[0], bin_edges[-1])

    ax.set_xlabel("max(width, height) in pixels")
    ax.set_ylabel("number of images")
    ax.set_title(f"Resolution Distribution of {SPLIT_TITLES[split]} Dataset", pad=28)
    fig.tight_layout()

    out_path = OUTPUT_DIR / f"resolution_histogram_{split}.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


if __name__ == "__main__":
    check_paths()

    stems_df = load_image_stems()
    n_fracture = int((stems_df["fracture_visible"] == 1).sum())
    print(f"[analyze_resolution.py] Loaded {len(stems_df)} rows "
          f"(fracture={n_fracture}, negative={len(stems_df) - n_fracture})")

    split_membership = load_split_membership()

    res_df = compute_resolutions(stems_df, split_membership)
    print(f"\nMeasured {len(res_df)} images")
    print(res_df["channels"].value_counts(dropna=False).to_string())
    print(res_df["split"].value_counts(dropna=False).to_string())
    print(res_df.head().to_string(index=False))

    design_df = compute_imgsz_design(res_df)
    print("\n" + design_df.to_string(index=False))

    excel_path = export_excel(res_df, design_df)
    print(f"\nSaved: {excel_path}")

    for split in SPLIT_TITLES:
        print(f"Saved: {plot_histogram(res_df, design_df, split)}")