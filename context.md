# context.md — background and decisions

**Thesis.** Master's thesis (NTPU, SHAIL Lab) by Vo Vinh Truong: pediatric wrist fracture detection on X-rays. Dataset **GRAZPEDWRI-DX**, 1 class `fracture`, patient-level split 70/20/10 (seed 42). Baseline **YOLO26 nano** (Ultralytics 8.4.127), `imgsz=640`.
Two contributions: (1) integrate **Mamba (SSM)** into YOLO26 → YOLO-Mamba; (2) **Approach B**, an input-rescaling method that keeps useful information when X-rays of different native resolutions are downscaled to 640.

## Decided — Claude never changes these on its own
- Main experiments use `imgsz=640` (`1120` is Approach A, only a control if the lead says so).
- Ablation 2 × 2 at `imgsz=640`: {with/without rescaling method B} × {with/without Mamba}.
- Mamba workflow: (1) reproduce **every** reference Mamba+YOLO paper with public code on GRAZ, to learn how others customise YOLO and to get baselines (their model on our data, not directly comparable to YOLO26); (2) discuss candidate Mamba positions with Claude; (3) try candidates one by one; the one that works goes into the 2 × 2 ablation.
- Choose models on the validation set only; run the test set once, at the very end.
- Four block types: MLP, CNN, Attention, SSM — no RNN.
- 3 random seeds: report each seed and mean ± SD, descriptive only; no Wilcoxon test (professor, 2026-10-18). If inference is needed: paired bootstrap CI over patient-level test cases.
- Approach B is a main contribution, presented as such only in the Methodology chapter of Proposal v2.
- YOLO26 nano is the base model (lightweight requirement; at most 1.2 mAP@0.5 points below l/x).
- Main reported metric: mAP@0.5; the full metric set goes to the professor in Excel.
- The input scale effect analysis is motivation for the rescaling method only, not a contribution.

## Not decided — Claude may only propose, with reasons
- Where Mamba goes in YOLO26 (candidate layers 2, 4, 6, 8, 10, 13, 16, 19, 22 — see `05_Notes/261013.md`).
- The concrete algorithm for Approach B.
- Epochs, batch size and machine for the full Mamba-YOLO-T run.
- Pretraining mismatch (Mamba-YOLO-T from scratch on Ultralytics 8.2.29 vs YOLO26 pretrained on 8.4.127): match the settings or state it as a limitation. Waits until the lead has met the professor.

**Status** (2026-10-21, may be out of date; newest details are in `05_Notes/` and the current weekly report in `06_Reports/`). YOLO26 n/s/m/l/x baselines re-evaluated (batch 4, best.pt, val). Input scale effect study rebuilt: 6 input sizes × 3 seeds; 640 is lowest, the gap is mainly in the largest images (P90). Mamba-YOLO (#11) on the lab: env and CUDA kernel verified, peak GPU memory 2.55 GB at batch 4, two-epoch pilot log not yet collected. Progress goes into the professor's weekly SHAIL template (`06_Reports/`); the proposal is not resubmitted for now. Current focus: discuss and choose the input rescaling method (Approach B). On hold until the lead asks: proposal edits (including the title), Grad-CAM.

**Compute.** `lps_phuong`: 1 × RTX 3080 (10 GB, ~2 GB used by the desktop), via Cloudflare Tunnel; main machine. `fa_server`: 4 × A40 (48 GB), borrowed, through `lps_phuong`: check GPU and disk first. Training runs in tmux; eval and other scripts run in the terminal.
IDEs: on Windows the lead reads code only in Antigravity; VS Code (Remote-SSH) is used only for the lab, to avoid mixing them up.
Env `yolo26` (checked 2026-10-15): driver 570.172.08 (up to CUDA 12.8), `nvcc` 12.4.131, PyTorch 2.5.1+cu121. Each reference paper gets its own env under `mamba_yolo_ref/<PaperName>/`; a script states the versions it expects and the lead checks them.

**Lab layout.** `~/VINH_TRUONG/yolo26/` (baseline, `dataset/graz`, `runs/`); `~/VINH_TRUONG/yolo_mamba/` (contents not confirmed); `~/VINH_TRUONG/mamba_yolo_ref/<PaperName>/env_<PaperName>/`. In `yolo26/`: `runs/train/{baseline,input_size}/<run>` (e.g. `yolo26n_640`, `imgsz640_seed0`), `runs/eval/{baseline,input_size}/`, `runs/test/` (empty until the final test), `excel_output/` (one Excel per experiment), `scripts/{data_preprocessing,train,eval,summarize,tools}/`. No git on the lab; the lead pulls `scripts/` into `03_Code/` on Windows.

**GRAZ on the lab.** `~/VINH_TRUONG/yolo26/dataset/graz/` has `data.yaml`, `dataset.csv`, `original_dataset/`, `processed_dataset/`, `percentile_groups/`, `split/`. `data.yaml` points to `split/{train,val,test}/images`, `nc: 1`, `names: ['fracture']`. Labels checked 2026-09-30: `processed_dataset/labels` is rebuilt from `original_dataset/labels` by `modify_label.py` (13,550 with fracture, 6,777 negative); every split image has a label file (14,403 / 3,986 / 1,938). `percentile_groups/val_{768,896,992,1120,1280}.{txt,yaml}` hold the five validation size groups (785 / 757 / 838 / 856 / 750).

**Study notes.** (empty — the lead's notes on Mamba, YOLO26 and the reference papers go here.)
