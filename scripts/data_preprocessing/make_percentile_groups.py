"""Write the five validation image-size groups used by the evaluation scripts.

Reads the 'design' and 'resolution' sheets written by analyze_resolution.py and puts
every validation image into the group whose bounds contain its longest side (max_dim).
Same rule as the old eval_by_resolution.py (removed from scripts/ on 2026-10-19).
For each group it writes:

    dataset/graz/percentile_groups/val_<imgsz>.txt    one image path per line
    dataset/graz/percentile_groups/val_<imgsz>.yaml   data file for model.val()

Run analyze_resolution.py first.

Usage:
    python make_percentile_groups.py
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

# ===== SETTINGS (edit here) =====
ROOT = Path.home() / "VINH_TRUONG" / "yolo26"
RES_XLSX = ROOT / "resolution_outputs" / "resolution_per_image_train.xlsx"  # sheets: resolution, design
SPLIT_DIR = ROOT / "dataset" / "graz" / "split"
GROUP_DIR = ROOT / "dataset" / "graz" / "percentile_groups"  # output folder

LOGGER = logging.getLogger("make_percentile_groups")


def load_design() -> tuple[list[int], list[float]]:
    """Read the group design written by analyze_resolution.py.

    Returns:
        imgsz values (ascending) and the group bin edges (one more than the imgsz values).
    """
    design = pd.read_excel(RES_XLSX, sheet_name="design")
    return design["imgsz"].tolist(), [design["lower"].iloc[0]] + design["upper"].tolist()


def load_val_resolutions() -> pd.DataFrame:
    """Read the longest side of every validation image.

    Returns:
        Validation images only, with columns filestem and max_dim.
    """
    df = pd.read_excel(RES_XLSX, sheet_name="resolution")
    return df.loc[df["split"] == "val", ["filestem", "max_dim"]].reset_index(drop=True)


def assign_groups(df: pd.DataFrame, imgsz_list: list[int], edges: list[float]) -> pd.DataFrame:
    """Add a 'group' column: the imgsz whose bin contains the image's max_dim.

    Args:
        df: Validation images with a max_dim column.
        imgsz_list: Group names (the matching imgsz values).
        edges: Bin edges from load_design().

    Returns:
        The input table with the extra 'group' column (int).
    """
    df["group"] = pd.cut(df["max_dim"], bins=edges, labels=imgsz_list, include_lowest=True).astype(int)
    LOGGER.info("%s", df.groupby("group")["max_dim"].agg(["count", "min", "median", "max"]).to_string())
    return df


def write_group_yamls(df: pd.DataFrame, groups: list[int]) -> dict[int, Path]:
    """Write one image-list .txt and one data .yaml per group.

    Args:
        df: Output of assign_groups().
        groups: Group names to write.

    Returns:
        Group name -> path of its .yaml file.
    """
    GROUP_DIR.mkdir(parents=True, exist_ok=True)
    yamls = {}
    for g in groups:
        stems = df.loc[df["group"] == g, "filestem"]
        txt_path = GROUP_DIR / f"val_{g}.txt"
        txt_path.write_text("".join(f"{SPLIT_DIR / 'val' / 'images' / f'{s}.png'}\n" for s in stems))

        yaml_path = GROUP_DIR / f"val_{g}.yaml"
        yaml_path.write_text(
            f"train: {SPLIT_DIR / 'train' / 'images'}\n"  # required key, not used by val
            f"val: {txt_path}\n"
            f"nc: 1\n"
            f"names: ['fracture']\n"
        )
        yamls[g] = yaml_path
    return yamls


def main() -> None:
    """Build dataset/graz/percentile_groups/ from the resolution Excel file."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    if not RES_XLSX.is_file():
        LOGGER.error("Not found: %s (run analyze_resolution.py first)", RES_XLSX)
        return
    imgsz_list, edges = load_design()
    df = assign_groups(load_val_resolutions(), imgsz_list, edges)
    for g, yaml_path in write_group_yamls(df, imgsz_list).items():
        LOGGER.info("val_%d: %d images -> %s", g, int((df["group"] == g).sum()), yaml_path)
    LOGGER.info("Total: %d validation images", len(df))


if __name__ == "__main__":
    main()