# principles.md — the lead's rules

Claude follows these and never changes them on its own.

## Rules
1. Do nothing without the lead's permission. Push back when there is a real problem or a better way, with reasons.
2. Never fabricate numbers, citations or links. Every number traces to a source file (`runs/.../results.csv`, logs); every citation to a real paper. Say when unsure.
3. Answer exactly what was asked, step by step, concisely. Do not guess motives or a bigger plan, and do not add unrequested advice or warnings. If a request has two readings, ask one short question first. A real risk gets one sentence, then the answer.
4. Git: work on `claude/<task>`, open a PR, the lead merges; never push to `main` (except approved edits to the instruction files).
5. Never commit datasets, weights (`*.pt`), `runs/` or zip files.
6. Write to `05_Notes/` only when the lead asks.
7. Keep actual results and expected results clearly separate in the proposal/paper.
8. Send datasets, unpublished results and full thesis text to no service the lead has not chosen.
9. Check every file you produce before handing it over: it opens without error, with no placeholders, broken numbering, stale table of contents or overflowing text.
10. No section cross-references in thesis text ("see Section 3.3.3"); state the point directly.
11. One document = one file. Edit the existing file; no extra copies or `_v2`. If it is locked, ask the lead to close it.
12. Chat with the lead in Vietnamese; everything written into a file is in English. If something is unclear or contradicts another file, say so right away instead of guessing.
13. Before writing code, give the main idea, then the steps one at a time: which file, where, what code and why. The lead approves each step before the next. Each step shows its full code block; when a step changes code from an earlier step, show the whole function and name the changed lines. Before saying code is correct, check the whole file against the agreed steps.
14. Do not update the dashboard (the Thesis tracker artifact) without the lead's permission.
15. RTX 5070 PC (Ubuntu, shared with the account `aiuser`): install everything inside the lead's account `vinhtruong`, under `~/VINH_TRUONG/` and without `sudo` (conda, envs, Python packages, git). Install system-wide with `sudo` (which also affects `aiuser`) only when there is no other way, e.g. Tailscale, AnyDesk or the NVIDIA driver, and only after asking the lead.

## Lab and secrets
- Never write passwords, IPs or tokens into the repo or any project file.
- Only the lead touches the lab machines. Claude puts code or commands in `scripts/` and sends them to the lead, who runs them and copies logs and `results.csv` back.
- No training starts until the lead says so.
