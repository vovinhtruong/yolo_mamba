"""Put Mamba-YOLO-T beside the old YOLO26n 640 linear runs in one Excel file.

Reads metrics.yaml from runs/eval/input_size/ (YOLO26n, only imgsz 640) and
runs/eval/mamba_yolo/ (written by eval/eval_mamba_yolo.py) and writes
excel_output/eval_mamba_yolo.xlsx:

    all_runs           one row per (model, seed, image set), the raw table
    compare_<metric>   rows = All, P10..P90; columns = mean of YOLO26n 640, mean of
                       Mamba-YOLO-T 640, difference Mamba-YOLO-T - YOLO26n; SD block below

Usage:
    python summarize_mamba_yolo.py
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
YOLO_EVAL_DIR = ROOT / "runs" / "eval" / "input_size"    # old YOLO26n runs
MAMBA_EVAL_DIR = ROOT / "runs" / "eval" / "mamba_yolo"   # Mamba-YOLO-T runs
YOLO_IMGSZ = 640  # input size taken from the old runs
OUTPUT_XLSX = ROOT / "excel_output" / "eval_mamba_yolo.xlsx"
DECIMALS = 3     # metrics and means
SD_DECIMALS = 4  # standard deviations are small

LOGGER = logging.getLogger("summarize_mamba_yolo")
METRICS = ["precision", "recall", "mAP50", "mAP50-95"]
SET_ORDER = ["All", "P10", "P30", "P50", "P70", "P90"]
CONFIG_ORDER = ["YOLO26n 640", "Mamba-YOLO-T 640"]
WRAP = Alignment(horizontal="center", vertical="center", wrap_text=True)


def read_results() -> list[dict]:
    """Read the metrics.yaml files of both models.

    Returns:
        One dict per (run, image set) with a "config" entry, sorted by model, seed and image set.
    """
    rows = []
    for f in YOLO_EVAL_DIR.glob("*/*/metrics.yaml"):
        r = yaml.safe_load(f.read_text())
        if r["imgsz"] == YOLO_IMGSZ:
            r["config"] = f"YOLO26n {r['imgsz']}"
            rows.append(r)
    for f in MAMBA_EVAL_DIR.glob("*/*/metrics.yaml"):
        r = yaml.safe_load(f.read_text())
        r["config"] = f"Mamba-YOLO-T {r['imgsz']}"
        rows.append(r)
    rows = [r for r in rows if r["config"] in CONFIG_ORDER]  # keep only the two configurations
    return sorted(rows, key=lambda r: (CONFIG_ORDER.index(r["config"]), r["seed"], SET_ORDER.index(r["image_set"])))


def wrap_header(ws, row: int, n_cols: int) -> None:
    """Let the header cells of one row wrap onto several lines."""
    for j in range(1, n_cols + 1):
        ws.cell(row, j).alignment = WRAP
    ws.row_dimensions[row].height = 45  # room for 3 lines


def write_all_runs(ws, rows: list[dict]) -> None:
    """Raw table: one row per (model, seed, image set).

    Settings that are the same for every run are written once in a note line;
    a setting that differs between runs gets its own column.
    """
    settings = ["model", "train_batch", "epochs", "split", "val_batch"]
    same = {k: rows[0][k] for k in settings if len({r[k] for r in rows}) == 1}
    varying = [k for k in settings if k not in same]
    n_images = {r["image_set"]: r["n_images"] for r in rows}
    cols = ["config", "seed", "image_set", *varying, *METRICS]
    note(ws, 1, "One row per (model, seed, image set). best.pt evaluated with model.val; "
                "source: runs/eval/{input_size,mamba_yolo}/<run>/<image_set>/metrics.yaml")
    note(ws, 2, "Same for all runs: " + (", ".join(f"{k} = {v}" for k, v in same.items()) or "none"))
    note(ws, 3, "Images per set: " + ", ".join(f"{k} = {v} samples" for k, v in n_images.items()))
    header(ws, 5, cols)
    for i, r in enumerate(rows, start=6):
        for j, name in enumerate(cols, start=1):
            put(ws, i, j, r.get(name), decimals=DECIMALS if name in METRICS else None)
    ws.auto_filter.ref = f"A5:{get_column_letter(len(cols))}{5 + len(rows)}"


def write_compare(ws, rows: list[dict], metric: str) -> None:
    """Table for one metric: image set x model, mean and SD over seeds."""
    base, new = CONFIG_ORDER  # "YOLO26n 640", "Mamba-YOLO-T 640"
    values: dict[tuple[str, str], list[float]] = {}
    for r in rows:
        values.setdefault((r["image_set"], r["config"]), []).append(r[metric])
    n_images = {r["image_set"]: r["n_images"] for r in rows}
    seeds = {c: len({r["seed"] for r in rows if r["config"] == c}) for c in CONFIG_ORDER}
    note(ws, 1, f"{metric}: mean over seeds per image set ({base}: {seeds[base]} seeds, {new}: {seeds[new]} seed(s)). "
                f"{base} is pretrained (Ultralytics 8.4.127); {new} is trained from scratch (Ultralytics 8.2.29). "
                "With one Mamba-YOLO-T seed the difference is not yet a result.")

    note(ws, 3, "Mean over seeds", bold=True)
    header(ws, 4, ["image set (n images)", *CONFIG_ORDER, f"{new} - {base}"])
    wrap_header(ws, 4, 2 + len(CONFIG_ORDER))
    for i, s in enumerate(SET_ORDER, start=5):
        means = {c: mean_sd(values[(s, c)])[0] if (s, c) in values else None for c in CONFIG_ORDER}
        put(ws, i, 1, f"{s} ({n_images.get(s, '?')})", bold=True)
        for j, c in enumerate(CONFIG_ORDER, start=2):
            put(ws, i, j, means[c], decimals=DECIMALS)
        diff = None if means[base] is None or means[new] is None else means[new] - means[base]
        put(ws, i, 2 + len(CONFIG_ORDER), diff, decimals=DECIMALS)

    start = 5 + len(SET_ORDER) + 1
    note(ws, start, "SD over seeds (ddof = 1; empty with one seed)", bold=True)
    header(ws, start + 1, ["image set (n images)", *CONFIG_ORDER])
    wrap_header(ws, start + 1, 1 + len(CONFIG_ORDER))
    for i, s in enumerate(SET_ORDER, start=start + 2):
        put(ws, i, 1, f"{s} ({n_images.get(s, '?')})", bold=True)
        for j, c in enumerate(CONFIG_ORDER, start=2):
            put(ws, i, j, mean_sd(values[(s, c)])[1] if (s, c) in values else None, decimals=SD_DECIMALS)


def main() -> None:
    """Build excel_output/eval_mamba_yolo.xlsx from the evaluation results."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    rows = read_results()
    if not rows:
        LOGGER.error("No metrics.yaml found in %s or %s", YOLO_EVAL_DIR, MAMBA_EVAL_DIR)
        return
    seeds = {c: sorted({r["seed"] for r in rows if r["config"] == c}) for c in CONFIG_ORDER}
    LOGGER.info("Seeds per model: %s", seeds)

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