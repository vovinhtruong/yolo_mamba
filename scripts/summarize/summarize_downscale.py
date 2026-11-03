"""Put the 640 area runs beside the old 640 linear and 1120 linear runs in one Excel file.

Reads metrics.yaml from runs/eval/input_size/ (old runs, linear) and runs/eval/downscale/
(written by eval/eval_downscale.py) and writes excel_output/eval_downscale.xlsx:

    all_runs           one row per (configuration, seed, image set), the raw table
    compare_<metric>   rows = All, P10..P90; columns = mean of 640 linear, 640 area, 1120 linear,
                       difference 640 area - 640 linear, improvement (% of 1120 gain);
                       SD block below

Usage:
    python summarize_downscale.py
"""

from __future__ import annotations

import logging
from pathlib import Path

import yaml
from openpyxl import Workbook
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter

from summarize_input_size_effect import header, mean_sd, note, put

# ===== SETTINGS (edit here) =====
ROOT = Path.home() / "VINH_TRUONG" / "yolo26"
OLD_EVAL_DIR = ROOT / "runs" / "eval" / "input_size"   # old runs, linear
NEW_EVAL_DIR = ROOT / "runs" / "eval" / "downscale"    # 640 area runs
OLD_SIZES = [640, 1120]  # input sizes taken from the old runs
OUTPUT_XLSX = ROOT / "excel_output" / "eval_downscale.xlsx"
DECIMALS = 3     # metrics and means
SD_DECIMALS = 4  # standard deviations are small

LOGGER = logging.getLogger("summarize_downscale")
METRICS = ["precision", "recall", "mAP50", "mAP50-95"]
SET_ORDER = ["All", "P10", "P30", "P50", "P70", "P90"]
CONFIG_ORDER = ["640 linear", "640 area", "1120 linear"]
WRAP = Alignment(horizontal="center", vertical="center", wrap_text=True)


def config_name(row: dict) -> str:
    """Configuration label of one result, e.g. "640 area"."""
    return f"{row['imgsz']} {row.get('interp', 'linear')}"


def read_results() -> list[dict]:
    """Read the metrics.yaml files of the three configurations.

    Old runs (runs/eval/input_size) have no interp entry and count as linear;
    only the input sizes in OLD_SIZES are kept from them.

    Returns:
        One dict per (run, image set) with a "config" entry, sorted by configuration, seed and image set.
    """
    rows = []
    for f in OLD_EVAL_DIR.glob("*/*/metrics.yaml"):
        r = yaml.safe_load(f.read_text())
        if r["imgsz"] in OLD_SIZES:
            rows.append(r)
    rows += [yaml.safe_load(f.read_text()) for f in NEW_EVAL_DIR.glob("*/*/metrics.yaml")]
    for r in rows:
        r["config"] = config_name(r)
    rows = [r for r in rows if r["config"] in CONFIG_ORDER]  # keep only the three configurations
    return sorted(rows, key=lambda r: (CONFIG_ORDER.index(r["config"]), r["seed"], SET_ORDER.index(r["image_set"])))


def wrap_header(ws, row: int, n_cols: int) -> None:
    """Let the header cells of one row wrap onto several lines."""
    for j in range(1, n_cols + 1):
        ws.cell(row, j).alignment = WRAP
    ws.row_dimensions[row].height = 45  # room for 3 lines


def write_all_runs(ws, rows: list[dict]) -> None:
    """Raw table: one row per (configuration, seed, image set).

    Settings that are the same for every run, and the number of images in each
    image set, are written once in the note lines; a setting that differs
    between runs gets its own column.
    """
    settings = ["model", "train_batch", "epochs", "split", "val_batch"]
    same = {k: rows[0][k] for k in settings if len({r[k] for r in rows}) == 1}
    varying = [k for k in settings if k not in same]
    if varying:
        LOGGER.warning("Settings differ between runs: %s", ", ".join(varying))
    n_images = {r["image_set"]: r["n_images"] for r in rows}
    cols = ["config", "seed", "image_set", *varying, *METRICS]
    note(ws, 1, "One row per (configuration, seed, image set). best.pt evaluated with model.val; "
                "source: runs/eval/{input_size,downscale}/<run>/<image_set>/metrics.yaml")
    note(ws, 2, "Same for all runs: " + ", ".join(f"{k} = {v}" for k, v in same.items()))
    note(ws, 3, "Images per set: " + ", ".join(f"{k} = {v} samples" for k, v in n_images.items()))
    header(ws, 5, cols)
    for i, r in enumerate(rows, start=6):
        for j, name in enumerate(cols, start=1):
            put(ws, i, j, r.get(name), decimals=DECIMALS if name in METRICS else None)
    ws.auto_filter.ref = f"A5:{get_column_letter(len(cols))}{5 + len(rows)}"


def write_compare(ws, rows: list[dict], metric: str) -> None:
    """Table for one metric: image set x configuration, mean and SD over seeds.

    The difference and the improvement use the first, second and third entry of
    CONFIG_ORDER as the old 640 run, the new 640 run and the 1120 reference.
    """
    base, new, ref = CONFIG_ORDER  # "640 linear", "640 area", "1120 linear"
    note(ws, 1, f"{metric}: mean over seeds per image set. improvement (% of {ref.split()[0]} gain) = "
                f"100 x ({new} - {base}) / ({ref} - {base}): 0 = no better than {base}, 100 = as good as {ref}, "
                f'negative = worse than {base}; unstable where the {ref} gain is small (e.g. P10), '
                f'"no gain" where {ref} is not better than {base}.')
    values: dict[tuple[str, str], list[float]] = {}
    for r in rows:
        values.setdefault((r["image_set"], r["config"]), []).append(r[metric])
    n_images = {r["image_set"]: r["n_images"] for r in rows}

    note(ws, 3, "Mean over seeds", bold=True)
    header(ws, 4, ["image set (n images)", *CONFIG_ORDER, f"{new} - {base}",
                   f"improvement (% of {ref.split()[0]} gain)"])
    wrap_header(ws, 4, 3 + len(CONFIG_ORDER))
    for i, s in enumerate(SET_ORDER, start=5):
        means = {c: mean_sd(values[(s, c)])[0] if (s, c) in values else None for c in CONFIG_ORDER}
        put(ws, i, 1, f"{s} ({n_images.get(s, '?')})", bold=True)
        for j, c in enumerate(CONFIG_ORDER, start=2):
            put(ws, i, j, means[c], decimals=DECIMALS)
        diff = None if means[base] is None or means[new] is None else means[new] - means[base]
        gain = None if means[base] is None or means[ref] is None else means[ref] - means[base]
        improvement = 100 * diff / gain if diff is not None and gain is not None and gain > 0 else "no gain"
        put(ws, i, 2 + len(CONFIG_ORDER), diff, decimals=DECIMALS)
        put(ws, i, 3 + len(CONFIG_ORDER), improvement, decimals=1)

    start = 5 + len(SET_ORDER) + 1
    note(ws, start, "SD over seeds (ddof = 1)", bold=True)
    header(ws, start + 1, ["image set (n images)", *CONFIG_ORDER])
    wrap_header(ws, start + 1, 1 + len(CONFIG_ORDER))
    for i, s in enumerate(SET_ORDER, start=start + 2):
        put(ws, i, 1, f"{s} ({n_images.get(s, '?')})", bold=True)
        for j, c in enumerate(CONFIG_ORDER, start=2):
            put(ws, i, j, mean_sd(values[(s, c)])[1] if (s, c) in values else None, decimals=SD_DECIMALS)


def main() -> None:
    """Build excel_output/eval_downscale.xlsx from the evaluation results."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    rows = read_results()
    if not rows:
        LOGGER.error("No metrics.yaml found in %s or %s", OLD_EVAL_DIR, NEW_EVAL_DIR)
        return
    seeds = {c: sorted({r["seed"] for r in rows if r["config"] == c}) for c in CONFIG_ORDER}
    LOGGER.info("Seeds per configuration: %s", seeds)

    wb = Workbook()
    write_all_runs(wb.active, rows)
    wb.active.title = "all_runs"
    for metric in METRICS:
        write_compare(wb.create_sheet(f"compare_{metric}"), rows, metric)
    for ws in wb.worksheets:
        for j in range(1, ws.max_column + 1):
            ws.column_dimensions[get_column_letter(j)].width = 15
    OUTPUT_XLSX.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUTPUT_XLSX)
    LOGGER.info("Saved %s", OUTPUT_XLSX)


if __name__ == "__main__":
    main()