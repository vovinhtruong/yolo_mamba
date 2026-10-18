# context.md — background

**Thesis.** Master's thesis (NTPU, SHAIL Lab) by Vo Vinh Truong: pediatric wrist fracture detection on X-rays. Dataset **GRAZPEDWRI-DX**, 1 class `fracture`, patient-level split 70/20/10 (seed 42). Baseline **YOLO26** (Ultralytics 8.4.127), `imgsz=640`.
Two contributions: (1) integrate **Mamba (SSM)** into YOLO26 → YOLO-Mamba; (2) **Approach B**, an input-rescaling method that keeps useful information when X-rays of different native resolutions are downscaled to 640.

**Status** (2026-10-14, may be out of date; newest details are in `05_Notes/`). YOLO26 n/s/m/l/x trained (50 epochs, 640). Reproducing reference paper Mamba-YOLO (#11) on the lab: env and CUDA kernel verified, 2-epoch test run in progress. Writing Proposal v2 (`07_Thesis/Proposal/`).

**Compute.** `lps_phuong`: 1 × RTX 3080 (10 GB, ~2 GB used by the desktop), via Cloudflare Tunnel; main machine. `fa_server`: 4 × A40 (48 GB), borrowed, through `lps_phuong`: check GPU and disk first. Training runs in tmux; eval and other scripts run in the terminal.
Env `yolo26` (checked 2026-10-15): driver 570.172.08 (up to CUDA 12.8), `nvcc` 12.4.131, PyTorch 2.5.1+cu121. Each reference paper gets its own env under `mamba_yolo_ref/<PaperName>/`; a script states the versions it expects and the lead checks them.

**Lab layout.** `~/VINH_TRUONG/yolo26/` (baseline, `dataset/graz`, `runs/`); `~/VINH_TRUONG/yolo_mamba/` (contents not confirmed); `~/VINH_TRUONG/mamba_yolo_ref/<PaperName>/env_<PaperName>/`. Runs are named `runs/<experiment>_<YYMMDD>`.

**GRAZ on the lab.** `~/VINH_TRUONG/yolo26/dataset/graz/` has `data.yaml`, `dataset.csv`, `original_dataset/`, `processed_dataset/`, `percentile_groups/`, `split/`. `data.yaml` points to `split/{train,val,test}/images`, `nc: 1`, `names: ['fracture']`; the label folders have not been checked.

**Study notes.** (empty — the lead's notes on Mamba, YOLO26 and the reference papers go here.)
