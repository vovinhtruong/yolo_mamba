"""Collect the input size evaluation results into Excel tables.

Reads runs/eval/input_size/<run>/<image_set>/metrics.yaml (written by
eval/eval_input_size_effect.py) and writes excel_output/eval_input_size_effect.xlsx:

    all_runs          one row per (input size, seed, image set), the raw table
    overall_by_size   is performance at 640 lower than at larger input sizes? (all images)
                      rows = input size, columns = seed 0..2, mean, SD; one block per metric
    group_<metric>    in which image size group is the gap?
                      rows = group P10..P90, columns = input size; mean and SD over seeds
    resize_scale      input size / median longest side of each group (<1 shrunk, >1 enlarged)

Usage:
    python summarize_input_size_effect.py
"""

from __future__ import annotations

import logging
import statistics
from pathlib import Path

import yaml
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from PIL import Image

# ===== SETTINGS (edit here) =====
ROOT = Path.home() / "VINH_TRUONG" / "yolo26"
EVAL_DIR = ROOT / "runs" / "eval" / "input_size"
GROUP_DIR = ROOT / "dataset" / "graz" / "percentile_groups"
GROUPS = {  # group name -> image list used by the evaluation
    "P10": GROUP_DIR / "val_768.txt",   # smallest images
    "P30": GROUP_DIR / "val_896.txt",
    "P50": GROUP_DIR / "val_992.txt",
    "P70": GROUP_DIR / "val_1120.txt",
    "P90": GROUP_DIR / "val_1280.txt",  # largest images
}
OUTPUT_XLSX = ROOT / "excel_output" / "eval_input_size_effect.xlsx"
DECIMALS = 3     # metrics and means
SD_DECIMALS = 4  # standard deviations are small, 3 decimals would often show 0.000

LOGGER = logging.getLogger("summarize_input_size_effect")
METRICS = ["precision", "recall", "mAP50", "mAP50-95"]
SET_ORDER = ["All", *GROUPS]
FONT = "Times New Roman"
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(top=THIN, bottom=THIN, left=THIN, right=THIN)
CENTER = Alignment(horizontal="center")
HEADER_FILL = PatternFill("solid", fgColor="D9E1F2")
SHRUNK_FILL = PatternFill("solid", fgColor="FCE4D6")    # orange: images shrunk (scale < 0.95)
MATCHED_FILL = PatternFill("solid", fgColor="BDD7EE")   # blue: scale about 1
ENLARGED_FILL = PatternFill("solid", fgColor="FFF2CC")  # yellow: images enlarged (scale > 1.05)


def read_results(eval_dir: Path) -> list[dict]:
    """Read every metrics.yaml under the evaluation folder.

    Args:
        eval_dir: Folder with <run>/<image_set>/metrics.yaml files.

    Returns:
        One dict per (run, image set), sorted by input size, seed and image set.
    """
    rows = [yaml.safe_load(f.read_text()) for f in eval_dir.glob("*/*/metrics.yaml")]
    return sorted(rows, key=lambda r: (r["imgsz"], r["seed"], SET_ORDER.index(r["image_set"])))


def median_longest_side(image_list: Path) -> float:
    """Median longest image side (pixels) of the images listed in a .txt file.

    Args:
        image_list: Text file with one image path per line.

    Returns:
        Median of max(width, height) over the listed images.
    """
    sides = []
    for line in image_list.read_text().splitlines():
        if line.strip():
            with Image.open(line.strip()) as img:  # reads the header only
                sides.append(max(img.size))
    return statistics.median(sides)


def mean_sd(values: list[float]) -> tuple[float, float | None]:
    """Mean and sample standard deviation (ddof = 1).

    Args:
        values: Values from the different seeds.

    Returns:
        Mean, and SD (None when fewer than two values).
    """
    sd = statistics.stdev(values) if len(values) > 1 else None
    return statistics.mean(values), sd


def put(ws, row: int, col: int, value, bold: bool = False, fill: PatternFill | None = None,
        decimals: int | None = None) -> None:
    """Write one formatted cell, rounding floats to the given decimals."""
    if isinstance(value, float) and decimals is not None:
        value = round(value, decimals)
    c = ws.cell(row, col, value)
    c.font = Font(name=FONT, bold=bold)
    c.alignment = CENTER
    c.border = BORDER
    if fill is not None:
        c.fill = fill
    if isinstance(value, float) and decimals is not None:
        c.number_format = "0." + "0" * decimals


def header(ws, row: int, labels: list) -> None:
    """Write a header row."""
    for j, label in enumerate(labels, start=1):
        put(ws, row, j, label, bold=True, fill=HEADER_FILL)


def note(ws, row: int, text: str, bold: bool = False) -> None:
    """Write a grey italic note (or a bold italic block title)."""
    ws.cell(row, 1, text).font = Font(name=FONT, italic=True, bold=bold, color=None if bold else "595959")


def scale_fill(scale: float) -> PatternFill:
    """Colour for a scale value: shrunk, about 1, or enlarged."""
    if scale < 0.95:
        return SHRUNK_FILL
    if scale > 1.05:
        return ENLARGED_FILL
    return MATCHED_FILL

def write_all_runs(ws, rows: list[dict]) -> None:
    """Raw table: one row per (input size, seed, image set).

    Settings that are the same for every run, and the number of images in each
    image set, are written once in the note lines instead of repeating them in
    every row; a setting that differs between runs gets its own column.
    """
    settings = ["model", "train_batch", "epochs", "split", "val_batch"]
    same = {k: rows[0][k] for k in settings if len({r[k] for r in rows}) == 1}
    varying = [k for k in settings if k not in same]
    if varying:
        LOGGER.warning("Settings differ between runs: %s", ", ".join(varying))
    n_images = {r["image_set"]: r["n_images"] for r in rows}
    cols = ["imgsz", "seed", "image_set", *varying, *METRICS]
    note(ws, 1, "One row per (input size, seed, image set). best.pt evaluated with model.val; "
                "source: runs/eval/input_size/<run>/<image_set>/metrics.yaml")
    note(ws, 2, "Same for all runs: " + ", ".join(f"{k} = {v}" for k, v in same.items()))
    note(ws, 3, "Images per set: " + ", ".join(f"{k} = {v} samples" for k, v in n_images.items()))
    header(ws, 5, cols)
    for i, r in enumerate(rows, start=6):
        for j, name in enumerate(cols, start=1):
            put(ws, i, j, r.get(name), decimals=DECIMALS if name in METRICS else None)
    ws.auto_filter.ref = f"A5:{get_column_letter(len(cols))}{5 + len(rows)}"

def write_overall(ws, rows: list[dict], sizes: list[int], seeds: list[int]) -> None:
    """Table on all images: input size x seed, with mean and SD, one block per metric."""
    note(ws, 1, "Is performance at 640 lower than at larger input sizes? All validation images, "
                "best.pt of each run. SD = sample standard deviation over seeds (ddof = 1).")
    lookup = {(r["imgsz"], r["seed"]): r for r in rows if r["image_set"] == "All"}
    row = 3
    for metric in METRICS:
        note(ws, row, metric, bold=True)
        header(ws, row + 1, ["imgsz", *[f"seed {s}" for s in seeds], "mean", "SD", "mean - mean(640)"])
        base = mean_sd([lookup[(640, s)][metric] for s in seeds if (640, s) in lookup])[0] if 640 in sizes else None
        for i, size in enumerate(sizes, start=row + 2):
            values = [lookup[(size, s)][metric] for s in seeds if (size, s) in lookup]
            mean, sd = mean_sd(values)
            put(ws, i, 1, size, bold=True)
            for j, s in enumerate(seeds, start=2):
                put(ws, i, j, lookup[(size, s)][metric] if (size, s) in lookup else None, decimals=DECIMALS)
            put(ws, i, 2 + len(seeds), mean, decimals=DECIMALS)
            put(ws, i, 3 + len(seeds), sd, decimals=SD_DECIMALS)
            put(ws, i, 4 + len(seeds), None if base is None else mean - base, decimals=DECIMALS)
        row += len(sizes) + 3


def write_group(ws, rows: list[dict], metric: str, sizes: list[int],
                scales: dict[tuple[str, int], float], n_images: dict[str, int]) -> None:
    """Table for one metric: group x input size, mean and SD over seeds, coloured by scale."""
    note(ws, 1, f"{metric} per image size group (rows) and input size (columns), mean over seeds. "
                "Orange = images shrunk, blue = scale about 1, yellow = images enlarged (see sheet 'resize_scale').")
    lookup: dict[tuple[str, int], list[float]] = {}
    for r in rows:
        if r["image_set"] in GROUPS:
            lookup.setdefault((r["image_set"], r["imgsz"]), []).append(r[metric])
    for title, start, use_sd in (("Mean over seeds", 3, False), ("SD over seeds (ddof = 1)", 5 + len(GROUPS) + 2, True)):
        note(ws, start, title, bold=True)
        header(ws, start + 1, ["group (n images)", *sizes])
        for i, group in enumerate(GROUPS, start=start + 2):
            put(ws, i, 1, f"{group} ({n_images.get(group, '?')})", bold=True)
            for j, size in enumerate(sizes, start=2):
                values = lookup.get((group, size), [])
                if not values:
                    put(ws, i, j, None)
                    continue
                mean, sd = mean_sd(values)
                put(ws, i, j, sd if use_sd else mean, decimals=SD_DECIMALS if use_sd else DECIMALS,
                    fill=scale_fill(scales[(group, size)]))


def write_scale(ws, scales: dict[tuple[str, int], float], medians: dict[str, float], sizes: list[int]) -> None:
    """Scale table: input size / median longest side of each group."""
    note(ws, 1, "scale = input size / median longest side of the group (validation images). "
                "< 1 images shrunk, about 1 kept, > 1 enlarged.")
    header(ws, 3, ["group", "median longest side (px)", *sizes])
    for i, (group, median) in enumerate(medians.items(), start=4):
        put(ws, i, 1, group, bold=True)
        put(ws, i, 2, median)
        for j, size in enumerate(sizes, start=3):
            put(ws, i, j, scales[(group, size)], decimals=2, fill=scale_fill(scales[(group, size)]))


def main() -> None:
    """Build excel_output/eval_input_rescale_affect.xlsx from the evaluation results."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    rows = read_results(EVAL_DIR)
    if not rows:
        LOGGER.error("No metrics.yaml found in %s; run eval/eval_input_size_effect.py first", EVAL_DIR)
        return
    sizes = sorted({r["imgsz"] for r in rows})
    seeds = sorted({r["seed"] for r in rows})
    n_images = {r["image_set"]: r["n_images"] for r in rows}
    LOGGER.info("Found %d results: %d input sizes, %d seeds", len(rows), len(sizes), len(seeds))

    medians = {group: median_longest_side(path) for group, path in GROUPS.items()}
    scales = {(g, s): s / medians[g] for g in GROUPS for s in sizes}

    wb = Workbook()
    write_all_runs(wb.active, rows)
    wb.active.title = "all_runs"
    write_overall(wb.create_sheet("overall_by_size"), rows, sizes, seeds)
    for metric in METRICS:
        write_group(wb.create_sheet(f"group_{metric}"), rows, metric, sizes, scales, n_images)
    write_scale(wb.create_sheet("resize_scale"), scales, medians, sizes)
    for ws in wb.worksheets:
        for j in range(1, ws.max_column + 1):
            ws.column_dimensions[get_column_letter(j)].width = 15
    OUTPUT_XLSX.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUTPUT_XLSX)
    LOGGER.info("Saved %s", OUTPUT_XLSX)


if __name__ == "__main__":
    main()