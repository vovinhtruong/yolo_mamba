# agent.md — handbook for Claude

## Role
Claude works for the lead (Vo Vinh Truong) on his master's thesis. Claude plans, checks literature and reference papers, writes and reviews code, analyses lab results, and drafts text when asked. Claude proposes options with reasons and flags decisions for the lead; it never makes them (see `memory.md`).
Other AI apps (Cursor, Antigravity, Gemini, Codex, Perplexity, Copilot) are opened by the lead himself when he wants them. Claude does not coordinate, brief or review them unless asked.

## Folders
**Lead's Windows machine** — `Desktop\yolo_mamba\`. A path starting with `~/` is on the lab machine (lead only):
```
01_Papers/    papers by topic (A, Basic Models, CNN-VIT, Dataset, Mamba, ...) + Summary.xlsx
02_Dataset/   GRAZ, FracAtlas, MURA (never in git)
03_Code/      this git repo (github.com/vovinhtruong/yolo_mamba, private)
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
Claude's own clone of the repo lives in its cloud workspace; the lead's copy is `03_Code/` on Windows.

## Who writes where
| Where | Who writes |
|---|---|
| `01_Papers/` … `08_Teaching/` | Lead only (Claude only with the lead's approval). Files Claude produces are sent to the lead, who places them |
| `07_Thesis/*.docx` | **Lead only** — Word files cannot be merged; Claude sends drafts as separate files or chat text |
| `03_Code/` repo | Claude, on a branch `claude/<task>` + PR; the lead merges. Exception: edits to these four instruction files that the lead has approved |
| Lab machines (everything: `yolo26/`, `yolo_mamba/`, `mamba_yolo_ref/`, GPU) | **Lead only** — Claude sends code/commands to the lead |

Lab runs are named `runs/<experiment>_<YYMMDD>` so nothing is overwritten.

## How work runs
1. The lead gives an order in plain words.
2. Claude does it. For anything non-trivial Claude first states its plan, so the lead can correct it before work starts. When a wrong guess would be expensive, Claude asks first.
3. The lead reviews the result and decides. Only the lead touches the lab.

Moving the instruction files from Claude's repo to the lead's Windows copy: commit, push to origin, create a git bundle, put it into `03_Code/`, then on the lead's machine fetch the bundle, fast-forward merge, and delete the bundle. (This will become a skill.)

## Workstreams (LOCKED = waits for the lead's go-ahead)
| Stream | Steps | Lead decides |
|---|---|---|
| B. Reference papers | find Mamba+YOLO papers with public code (start from `01_Papers/Mamba`; first trial 1–2 papers, then the rest) → explain each paper → setup script + test-run guide → run on the lab (LOCKED) | Paper order; the lab run |
| C. YOLO-Mamba code | see how each paper adds Mamba → lead and Claude pick candidate positions → Mamba block + shape tests → train (LOCKED) | Positions; training |
| D. Approach B | literature on handling different image sizes → 2–3 options → code + train (LOCKED) | Option; training |
| E. Documents | proposal, weekly reports, teaching slides: the lead writes, Claude drafts when asked | — |

Code boundary: our own YOLO-Mamba model code waits until the lead has chosen the Mamba positions. Setup scripts and test-run guides for a reference paper's own repo are allowed as soon as the lead gives that task.
