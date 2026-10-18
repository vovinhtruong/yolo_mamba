# context.md — background of the project

## The thesis
- Master's thesis (NTPU, SHAIL Lab) by **Vo Vinh Truong**: pediatric wrist fracture detection on X-ray images.
- Main dataset: **GRAZPEDWRI-DX**, 1 class `fracture`, patient-level split 70/20/10 (seed 42).
- Baseline: **YOLO26** (Ultralytics 8.4.127), `imgsz=640`.
- Two main contributions:
  1. **Integrating Mamba (SSM) into YOLO26** → YOLO-Mamba.
  2. **Approach B — an input-rescaling method**: preserve useful information when X-rays with different native resolutions are downscaled to 640.

## Current status (updated 2026-10-14; may be out of date)
- YOLO26 baselines n/s/m/l/x: trained (50 epochs, `imgsz=640`).
- Reproducing reference paper **Mamba-YOLO** (#11) on the lab machine: env + CUDA kernel verified; 2-epoch test run in progress.
- Writing **Proposal v2** (`07_Thesis/Proposal/`).
- The latest details are always in the newest note in `05_Notes/`.

## Compute
- `lps_phuong`: 1 × RTX 3080 (~7.9 GB free VRAM), via Cloudflare Tunnel. Main machine.
- `fa_server`: 4 × A40 (48 GB), reached through `lps_phuong`. Borrowed — **check GPU/disk before running**.
- Training runs go in **tmux**; eval/val and other scripts run directly in the terminal.
- **Lab environment** (checked by the lead on 2026-10-15, env `yolo26` on `lps_phuong`): RTX 3080 with 10 GB total (about 2 GB is used by the desktop); NVIDIA driver 570.172.08 (supports up to CUDA 12.8); CUDA toolkit (`nvcc`) 12.4.131; PyTorch 2.5.1+cu121. These are the baseline env's versions. Each reference paper gets its own env under `mamba_yolo_ref/<PaperName>/`, so a script should state which versions it expects and the lead checks them.

## Lab layout (`lps_phuong`)
```
~/VINH_TRUONG/yolo26/            baseline, dataset/graz, runs/
~/VINH_TRUONG/yolo_mamba/        (contents not yet confirmed — lead to fill in)
~/VINH_TRUONG/mamba_yolo_ref/<PaperName>/env_<PaperName>/   one folder + own env per reference paper
```

## Dataset on the lab
`~/VINH_TRUONG/yolo26/dataset/graz/` contains `data.yaml`, `dataset.csv`, `original_dataset/`, `processed_dataset/`, `percentile_groups/` and `split/`. `data.yaml` points to `split/{train,val,test}/images`, `nc: 1`, `names: ['fracture']` (Ultralytics layout; the label folders have not been checked).

## Study notes
(Empty for now. The lead's learning notes about Mamba, YOLO26 and the reference papers go here.)
