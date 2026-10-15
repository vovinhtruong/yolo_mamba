# AGENTS.md — Shared context for the lead and the AI agents

> Every agent (Claude, Antigravity, Cursor, Gemini, Codex, Perplexity) **must read this file before doing anything**.
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
  2. Discuss with Claude (and the other agents) to pick candidate Mamba positions.
  3. Try candidates one by one until a suitable position is found; that **one** position is used in the 2 × 2 ablation.
- **Model selection uses the validation set only. The test set is run once, at the very end.**
- The model uses 4 block types: MLP, CNN, Attention, SSM — no RNN.
- Statistics: 3 random seeds; no Wilcoxon test in the current proposal.
- Approach B is a main contribution; in Proposal v2 it is presented as a main contribution only in the Methodology chapter.

## 3. NOT YET DECIDED — agents may only propose (with reasons), never decide
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
nhóm công việc.txt   the lead's own notes: the work groups and which tool fits which (the lead's file; agents only read it)
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
- **The lab machines are managed by the lead only.** No agent accesses or runs anything on them. Any code or command meant for the lab goes into the repo (`scripts/`) and is **sent to the lead**, who reviews and runs it. Lab outputs (logs, `results.csv`) are copied back by the lead; agents then read and analyse them.
- **No training run starts until the lead says so.**

## 7. Roles (all tools on free plans; one job each, one task at a time)
| Who | Job | Allowed to |
|---|---|---|
| Lead (human) | Makes every decision, reviews every result, merges into `main`, runs everything on the lab. Works on one job at a time and moves on only when the result is understood | Everything |
| **Claude** | Planning and questions: keeps this file, discusses options, cross-checks results when the lead asks. Not one of the five jobs | Edit `AGENTS.md` (with approval); code on a `claude/<task>` branch via PR |
| **Antigravity** | **1. File management**: organise, rename, extract metadata from the files and folders the lead names. Has local file access | Write only in the files/folders named in the task; never delete |
| **Cursor** | **2. Writing code**: YOLO-Mamba code, shape tests, refactoring, setup scripts for the lab | Code in `03_Code/` on a `cursor/<task>` branch via PR |
| **Gemini** | **3. Analyse a paper and explain it to the lead** (in Vietnamese, in chat) | Chat only |
| **Codex** | **4. Writing**: English academic text. The lead writes the main ideas first; Codex polishes the wording | Drafts go to the lead in chat or as a separate file, never into `07_Thesis/*.docx` |
| **Perplexity** | **5. Find paper sources**: candidate papers, repos, citations. The lead opens every link and downloads the paper into `01_Papers/` before it is used | Chat only |

Agents without local file access (Codex, Gemini, Perplexity) can be set up as a project or chat with this file and `nhóm công việc.txt` attached. GitHub Copilot and VS Code are editor helpers for the lead, not a job.

Not used: Microsoft Copilot; DeepSeek (data-security concerns; Taiwan restricts it in the public sector). Review: the lead reviews every result before using it; Claude cross-checks when asked.

## 8. Write zones
| Where | Who writes |
|---|---|
| `01_Papers/` … `08_Teaching/` (Windows) | Lead only. Agents propose; files agents produce are given to the lead, who places them. Exception: Antigravity, only inside what a file-management task names |
| `07_Thesis/*.docx` | **Lead only** — Word files cannot be merged; drafts come as separate files or chat text |
| `03_Code/` repo | Cursor and Claude, each on its own branch `<agent>/<task>` + PR |
| Lab machines (everything: `yolo26/`, `yolo_mamba/`, `mamba_yolo_ref/`, GPU) | **Lead only** — agents send code/commands to the lead |

Lab runs are named `runs/<experiment>_<YYMMDD>` so nothing is overwritten.

## 9. Working rules
1. **Do nothing without the lead's permission.** Push back when there is a real problem or a better way — always with reasons.
2. **Never fabricate numbers, citations or links.** Every number must trace back to its source file (`runs/.../results.csv`, logs) and every citation to a real paper. Say clearly when unsure.
3. Be concise and focused; do only the job and task you were given; work step by step.
4. **Git:** each agent works on a branch `<agent>/<task>` (e.g. `cursor/fix-eval`), opens a PR, and the lead merges. Never push directly to `main`, except edits to `AGENTS.md` that the lead has approved.
5. Never commit datasets, weights (`*.pt`), `runs/`, or zip files.
6. Write to `05_Notes/` only when the lead asks.
7. Keep **actual results** and **expected results** clearly separate when writing the proposal/paper.
8. Never send datasets, unpublished results, or full thesis/proposal text to a service that is not one of the agents listed above.
9. **Files are reader-facing.** Any file an agent produces or renders (docx, pptx, pdf, xlsx, figure) must be checked before handing it over: it opens with no error or prompt, and has no leftover placeholders, broken numbering, stale table of contents, overflowing text or other visible defects.
10. **No section cross-references in thesis/proposal text** (e.g. "described in Section 3.3.3", "(Section 4.3)"). State the point directly so the reader does not have to look it up.
11. **One document = one file.** Edit the existing file; never save extra copies or new versions (`_v3`, `_new`, …) on your own. If the file is open or locked, ask the lead to close it instead of saving under another name.
12. **Language and problems.** Chat with the lead in Vietnamese. Everything written into a file or page (html, docx, pptx, xlsx, figures, notes, code comments, this file) is in English. When something is unclear or contradicts another file, do not guess and do not silently work around it: tell the lead right away, with what is wrong and where.

## 10. Workflow
The lead works on **one job at a time**, with the one agent that owns that job, until the result is understood. If something is unclear, the lead asks the same agent, or Claude.

1. **Lead** picks a job and gives the agent one concrete task (the shared prompt: read this file, do only your job).
2. **Agent** does that task and replies. It states what it is unsure about.
3. **Lead** reads, checks the sources, decides. Only the lead touches the lab. Claude cross-checks when asked.

Workstreams (LOCKED = waits for the lead's go-ahead):

| Stream | Steps (agent) | Lead decides |
|---|---|---|
| B. Reference papers | B1 find 1–2 Mamba+YOLO papers with public code (Perplexity; start from `01_Papers/Mamba`) → B2 explain each paper (Gemini) → B3 setup script + test-run guide (Cursor) → B4 run on the lab (LOCKED) | Paper order; B4 |
| C. YOLO-Mamba code | C1 explain how each paper adds Mamba (Gemini) → C2 lead + Claude propose candidate positions → C3 Mamba block + shape tests (Cursor) → C4 train (LOCKED) | Positions; C4 |
| D. Approach B | D1 find literature on handling different image sizes (Perplexity) → D2 explain it (Gemini) → D3 lead + Claude propose 2–3 options → D4 code + train (Cursor; LOCKED) | Option; D4 |
| E. Documents | Lead writes the ideas; Codex polishes the English (proposal, weekly reports, teaching slides) | — |
