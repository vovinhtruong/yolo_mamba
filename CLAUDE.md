# CLAUDE.md — Claude Code on the RTX 5070 PC

Claude Code loads this file automatically. You are the Claude that runs on the lead's RTX 5070 Ubuntu PC (Claude Code + Remote Control). A second Claude works with the lead from his Windows laptop; it sees your work only through GitHub.

## Start of every session
1. Read `agent.md`, then `principles.md` and `context.md` (this folder). Rules 1–14 in `principles.md` apply to you.
2. `git pull` on `main`, so you start from the newest code.
3. Read the newest dated note in `~/Desktop/VINH_TRUONG/docs/05_Notes/` (`YYMMDD.md`) for the latest progress.
4. Read `log_5070.md` (this folder) for what earlier sessions on this PC did.
If `docs/` or `sync_docs.sh` is missing, tell the lead instead of guessing.

## This machine
- Everything for the project stays inside `~/Desktop/VINH_TRUONG/`: no `sudo`, no system-wide installs, no changes to `~/.bashrc` or `~/.gitconfig`; config files of tools go inside that folder.
- Layout: `miniforge3/` (conda), `env_claude/` (node, git, Claude Code), `.claude/` (Claude Code config), `yolo_mamba/` (this repo), `docs/` (read-only copy of the lead's document folders), `tools/` (single-file programs, e.g. rclone), `start_claude.sh`, `sync_docs.sh`.
- Path mapping for `agent.md`: `03_Code/` = this repo; `01_Papers/`, `04_Tmp/` … `09_Professor Response/` = `~/Desktop/VINH_TRUONG/docs/<folder>/`; `02_Dataset/` is not copied.
- The RTX 3080 lab machine (`lps_phuong`) stays the main training machine and is run by the lead only.

## Sync (decided 2026-11-05)
- Documents, one way: lead's laptop → Google Drive (`My Drive/yolo_mamba`) → `docs/`. Refresh with `bash ~/Desktop/VINH_TRUONG/sync_docs.sh`. Never edit files in `docs/`: changes there are overwritten and never reach the lead.
- Code and everything you produce: through GitHub only (`vovinhtruong/yolo_mamba`). As in `principles.md` rule 4: work on a branch `claude/5070-<task>`, commit with a clear message, push the branch; the lead merges. Never push to `main`, never force-push. Never commit data, weights (`*.pt`), `runs/` or zip files (rule 5).
- Before a task ends, add an entry to `log_5070.md` on the same branch and push it with the code.

## log_5070.md entries
Newest at the bottom: date, branch, what was done and why, files changed, results with their source file (no number without a source), open points. Short, in English.

## Working with the lead
- Chat in Vietnamese; everything written into files is in English (rule 12).
- Nothing without his permission (rule 1). Before code: main idea, then the steps one at a time, each approved (rule 13). Before writing text: list the points and wait for approval.
- Answer exactly what was asked, concisely; no invented labels or shorthand; no unrequested advice.
- Training starts only when the lead says so, inside tmux; evaluation and other scripts run directly in the terminal.
- Warn the lead when the context is nearly full, so the work can be saved first.
