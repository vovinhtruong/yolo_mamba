# AGENTS.md — Shared context for the lead and Claude

> Claude **must read this file before doing anything** in a new session.
> Only Claude edits this file, and only after the lead approves.

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
- **Mamba workflow (3 phases):**
  1. Reproduce **every** reference Mamba+YOLO paper that has public code, on GRAZ — goals: learn how others customize YOLO, and get baselines for later comparison. (Results only show "their model on our data"; not directly comparable to YOLO26 because of different Ultralytics versions, pretraining and heads.)
  2. Discuss with Claude to pick candidate Mamba positions.
  3. Try candidates one by one until a suitable position is found; that **one** position is used in the 2 × 2 ablation.
- **Model selection uses the validation set only. The test set is run once, at the very end.**
- The model uses 4 block types: MLP, CNN, Attention, SSM — no RNN.
- Statistics: 3 random seeds; no Wilcoxon test in the current proposal.
- Approach B is a main contribution; in Proposal v2 it is presented as a main contribution only in the Methodology chapter.

## 3. NOT YET DECIDED — Claude may only propose (with reasons), never decide
- Where to place Mamba in YOLO26 — candidates are chosen after phase 1 (possible layers: 2, 4, 6, 8, 10, 13, 16, 19, 22 — see `05_Notes/261013.md` §1).
- Whether to add Wilcoxon (or another statistical test), e.g. when comparing Mamba positions whose differences may be smaller than seed-to-seed variation — the lead will discuss with the professor.
- The concrete algorithm for Approach B.
- Epochs/batch size and which machine to use for the full Mamba-YOLO-T training run.

## 4. Current status (updated 2026-10-14)
- YOLO26 baselines n/s/m/l/x: trained (50 epochs, `imgsz=640`).
- Reproducing reference paper **Mamba-YOLO** (#11) on the lab machine: env + CUDA kernel verified; 2-epoch test run in progress.
- Writing **Proposal v2** (`07_Thesis/Proposal/`).
- The latest details are always in the newest note in `05_Notes/`.

## 5. Folder structure
**Lead's Windows machine** — `Desktop\yolo_mamba\`. Paths in files are relative to this folder; a path starting with `~/` is on the lab machine (lead only):
```
01_Papers/    papers by topic (A, Basic Models, CNN-VIT, Dataset, Mamba, ...) + Summary.xlsx
02_Dataset/   GRAZ, FracAtlas, MURA (never in git)
03_Code/      ← this git repo (github.com/vovinhtruong/yolo_mamba, private)
04_Results/   result tables (xlsx), charts
05_Notes/     progress notes (YYMMDD.md); older notes in archive/
06_Reports/   weekly report slides
07_Thesis/    Thesis, Draft/, Proposal/
08_Teaching/  teaching slides for new students
09_Agents/    Claude's working area (drafts, notes, scripts for the lab): claude/
11_Temp_Outputs/  scratch: task outputs, plus ISSUES.txt (problem log)
AGENTS.md     short pointer to this file + write-zone rules
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
- **Lab environment** (checked by the lead on 2026-10-15, env `yolo26` on `lps_phuong`): RTX 3080 with 10 GB total (about 2 GB is used by the desktop); NVIDIA driver 570.172.08 (supports up to CUDA 12.8); CUDA toolkit (`nvcc`) 12.4.131; PyTorch 2.5.1+cu121. These are the baseline env's versions. Each reference paper gets its own env under `mamba_yolo_ref/<PaperName>/`, so a script should state which versions it expects and the lead checks them.
- **GRAZ on the lab:** `~/VINH_TRUONG/yolo26/dataset/graz/` contains `data.yaml`, `dataset.csv`, `original_dataset/`, `processed_dataset/`, `percentile_groups/` and `split/`. `data.yaml` points to `split/{train,val,test}/images`, `nc: 1`, `names: ['fracture']` (Ultralytics layout; the label folders have not been checked).
- **Never write passwords, IPs or tokens into the repo or any project file.**
- **The lab machines are managed by the lead only.** Claude never accesses or runs anything on them. Any code or command meant for the lab goes into the repo or `09_Agents/claude/` and is **sent to the lead**, who reviews and runs it. Lab outputs (logs, `results.csv`) are copied back by the lead; Claude then reads and analyses them.
- **No training run starts until the lead says so.**

## 7. Roles
| Who | Role | Allowed to |
|---|---|---|
| Lead (human) | Makes every decision, reviews every result, merges into `main`, runs everything on the lab | Everything |
| **Claude** | Does the work the lead orders: literature and reference-paper checks, setup scripts and test-run guides for the lab, YOLO-Mamba code and shape tests, analysis of lab outputs, drafts of text. Flags decisions for the lead and proposes options with reasons | Edit `AGENTS.md` (with approval); write in `09_Agents/claude/`, `11_Temp_Outputs/`; code on a `claude/<task>` branch via PR |

Not used: Codex, Antigravity, Cursor, GitHub Copilot, Microsoft Copilot (dropped on 2026-10-15: every hand-off between apps had to be copied by hand, which made the workflow too slow); Gemini (dropped earlier the same day); DeepSeek (data-security concerns; Taiwan restricts it in the public sector).

The lead reviews every result before using it. Claude checks its own work before handing it over (rule 9).

## 8. Write zones
| Where | Who writes |
|---|---|
| `09_Agents/claude/` (Windows) | Claude: drafts, notes, lab scripts (`09_Agents/claude/<PaperName>/` for a reference paper) |
| `11_Temp_Outputs/<YYMMDD>_<task>/` | Claude: task outputs. `11_Temp_Outputs/ISSUES.txt` is the problem log (rule 12) |
| `01_Papers/` … `08_Teaching/` (Windows) | Lead only (Claude only with the lead's approval) |
| `07_Thesis/*.docx` | **Lead only** — Word files cannot be merged; Claude puts drafts in `09_Agents/claude/` |
| `03_Code/` repo | Claude, in its own cloud clone, via branch `claude/<task>` + PR |
| Lab machines (everything: `yolo26/`, `yolo_mamba/`, `mamba_yolo_ref/`, GPU) | **Lead only** — Claude sends code/commands to the lead |

The temp folders are scratch: once the lead accepts a result, the lead moves it to its final place and clears the task folder.
Lab runs are named `runs/<experiment>_<YYMMDD>` so nothing is overwritten.

## 9. Working rules
1. **Do nothing without the lead's permission.** Push back when there is a real problem or a better way — always with reasons.
2. **Never fabricate numbers or evidence.** Every number must trace back to its source file (`runs/.../results.csv`, logs). Say clearly when unsure; cite sources for outside information.
3. Be concise and focused; work step by step; do not go beyond the assigned scope.
4. **Git:** Claude works on a branch `claude/<task>`, opens a PR, and the lead merges. Never push directly to `main`, except edits to `AGENTS.md` that the lead has approved.
5. Never commit datasets, weights (`*.pt`), `runs/`, or zip files.
6. Write to `05_Notes/` only when the lead asks; write so that a later session can read it and understand what was done.
7. Keep **actual results** and **expected results** clearly separate when writing the proposal/paper.
8. Never send datasets, unpublished results, or full thesis/proposal text to services outside the lead and Claude.
9. **Files are reader-facing.** Any file Claude produces or renders (docx, pptx, pdf, xlsx, figure) must be checked before handing it over: it opens with no error or prompt, and has no leftover placeholders, broken numbering, stale table of contents, overflowing text or other visible defects.
10. **No section cross-references in thesis/proposal text** (e.g. "described in Section 3.3.3", "(Section 4.3)"). State the point directly so the reader does not have to look it up.
11. **One document = one file.** Edit the existing file; never save extra copies or new versions (`_v3`, `_new`, …) on your own. If the file is open or locked, ask the lead to close it instead of saving under another name.
12. **Language and problems.** Chat with the lead in Vietnamese. Everything written into a file or page (html, docx, pptx, xlsx, figures, notes, code comments, this file) is in English. When a problem or contradiction turns up (in `AGENTS.md`, in files or results), do not guess and do not silently work around it: append one entry to `11_Temp_Outputs/ISSUES.txt` (date, who, task, what is wrong, where) and tell the lead. Append only; the lead marks entries resolved.

## 10. Workflow
1. **Lead** gives an order in plain words.
2. **Claude** does it, checks it against this file, and asks first when a wrong guess would be expensive. For anything non-trivial Claude states its plan before starting, so the lead can correct it.
3. **Lead** reviews the result and decides. Only the lead touches the lab.

Workstreams (LOCKED = waits for the lead's go-ahead):

| Stream | Steps | Lead decides |
|---|---|---|
| B. Reference papers | B1 Claude: find 1–2 Mamba+YOLO papers with public code (start with the papers in `01_Papers/Mamba`) → B2 Claude: setup script + test-run guide, one paper at a time → B3 run on the lab (LOCKED) | Paper order; B3 |
| C. YOLO-Mamba code | C1 Claude: ways to add Mamba to Ultralytics 8.4.127 → C2–C3 Claude + Lead: repo skeleton, Mamba block + shape tests → C4 train (LOCKED) | C1 choice; C4 |
| D. Approach B | D1 Claude: literature on handling different image sizes → D2 Claude: 2–3 options → D3 code + train (LOCKED) | Option; D3 |
| E. Documents | Lead: proposal, weekly reports, teaching slides (Claude drafts when asked) | — |

Suggested order: B1, then D1 → C1 decision → B2 one paper at a time → C2–C3.
