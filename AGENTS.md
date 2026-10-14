# AGENTS.md — Shared context for all agents

> Every agent (Claude, Antigravity, Cursor, GitHub Copilot, Gemini, ChatGPT, Microsoft Copilot) **must read this file before doing anything**.
> Only the deputy lead (Claude) edits this file, and only after the lead approves.

## 1. Project
- Master's thesis (NTPU, SHAIL Lab) by **Vo Vinh Truong**: pediatric wrist fracture detection on X-ray images.
- Main dataset: **GRAZPEDWRI-DX**, 1 class `fracture`, patient-level split 70/20/10 (seed 42).
- Baseline: **YOLO26** (Ultralytics 8.4.127), `imgsz=640`.
- Two main contributions:
  1. **Integrating Mamba (SSM) into YOLO26** → YOLO-Mamba.
  2. **Approach B — an input-rescaling method**: preserve useful information when X-rays with different native resolutions are downscaled to 640.

## 2. DECIDED — do not change on your own
- Target input size for the main experiments: `imgsz=640`. (`1120` belongs to Approach A and is only a control if the lead decides so.)
- Ablation is **2 × 2** at `imgsz=640`: {with/without rescaling method B} × {with/without Mamba}.
- No ablation over multiple Mamba positions: the lead will choose **one** position.
- The model uses 4 block types: MLP, CNN, Attention, SSM — no RNN.
- Statistics: 3 random seeds; no Wilcoxon test in the current proposal.
- Approach B is a main contribution; in Proposal v2 it is presented as a main contribution only in the Methodology chapter.

## 3. NOT YET DECIDED — agents may only propose (with reasons), never decide
- Where to place Mamba in YOLO26 (candidates: layers 2, 4, 6, 8, 10, 13, 16, 19, 22 — see `05_Notes/261013.md` §1).
- The concrete algorithm for Approach B.
- Epochs/batch size and which machine to use for the full Mamba-YOLO-T training run.

## 4. Current status (updated 2026-10-14)
- YOLO26 baselines n/s/m/l/x: trained (50 epochs, `imgsz=640`).
- Reproducing reference paper **Mamba-YOLO** (#11) on the lab machine: env + CUDA kernel verified; 2-epoch test run in progress.
- Writing **Proposal v2** (`07_Thesis/Proposal/`).
- The latest details are always in the newest note in `05_Notes/`.

## 5. Folder structure
**Lead's Windows machine** — `Desktop\yolo_mamba\`:
```
01_Papers/    papers by topic (A, Basic Models, CNN-VIT, Dataset, Mamba, ...) + Summary.xlsx
02_Dataset/   GRAZ, FracAtlas, MURA (never in git)
03_Code/      ← this git repo (github.com/vovinhtruong/yolo_mamba, private)
04_Results/   result tables (xlsx), charts
05_Notes/     progress notes (YYMMDD.md); older notes in archive/
06_Reports/   weekly report slides
07_Thesis/    Thesis, Draft/, Proposal/
08_Teaching/  teaching slides for new students
```
**This repo (`03_Code/`)**:
```
scripts/      train/eval/analysis scripts (paths point to the lab machine: ~/VINH_TRUONG/yolo26/)
env_backup/   environment.yml, requirements of the yolo26 env
repos/        (git-ignored) third-party source: ultralytics, mamba, yolo26
```
**Lab machine (`lps_phuong`)**:
```
~/VINH_TRUONG/yolo26/            baseline, dataset/graz, runs/
~/VINH_TRUONG/yolo_mamba/        (contents not yet confirmed — lead to fill in)
~/VINH_TRUONG/mamba_yolo_ref/<PaperName>/env_<PaperName>/   one folder + own env per reference paper
```

## 6. Compute
- `lps_phuong`: 1 × RTX 3080 (~7.9 GB free VRAM), via Cloudflare Tunnel. Main machine.
- `fa_server`: 4 × A40 (48 GB), reached through `lps_phuong`. Borrowed — **check GPU/disk before running**.
- Training runs go in **tmux**; eval/val and other scripts run directly in the terminal.
- **Never write passwords, IPs or tokens into the repo or any project file.**

## 7. Roles (all tools on free plans unless noted)
| Agent | Role | Allowed to |
|---|---|---|
| Lead (human) | Makes every decision, merges into `main` | Everything |
| **Claude** | Deputy lead: coordination, model architecture, experiment design, analysis, writing the proposal/paper; reviews PRs | Edit `AGENTS.md`; write model code together with the lead |
| **Antigravity** | Reproduces reference papers (env setup, fixing dependencies, test runs) | Only inside `mamba_yolo_ref/<PaperName>/` |
| **Cursor** (Free) | Main IDE: editing code, refactoring | Work on its own branch |
| **GitHub Copilot** (Free) | Backup when Cursor runs out of requests; code suggestions in VS Code when SSH-ing into the lab machine | Work on its own branch |
| **Gemini** | Reads many papers at once, related work, citation checks | Documents only, no code changes |
| **ChatGPT** | Critic: challenges ideas and wording, **independently checks Claude's math/logic/analysis**, reviews PRs, drafts teaching material | Documents and reviews only, no code changes |
| **Microsoft Copilot** | Backup when ChatGPT runs out of requests | Same as ChatGPT |

Cross-review: work produced by one agent is reviewed by another (e.g. Claude's code → ChatGPT reviews; Cursor's code → Claude reviews). No agent grades its own work.

Not used: DeepSeek (data-security concerns; Taiwan restricts it in the public sector).

## 8. Working rules
1. **Do nothing without the lead's permission.** Push back when there is a real problem or a better way — always with reasons.
2. **Never fabricate numbers or evidence.** Every number must trace back to its source file (`runs/.../results.csv`, logs). Say clearly when unsure; cite sources for outside information.
3. Be concise and focused; work step by step; do not go beyond the assigned scope.
4. **Git:** each agent works on a branch `<agent>/<task>` (e.g. `cursor/fix-eval`), opens a PR → cross-review → the lead merges. Never push directly to `main`.
5. Never commit datasets, weights (`*.pt`), `runs/`, or zip files.
6. Write to `05_Notes/` only when the lead asks; write so that another agent can read it and understand what was done.
7. Keep **actual results** and **expected results** clearly separate when writing the proposal/paper.
8. Never send datasets, unpublished results, or full thesis/proposal text to services outside this team.
