# principles.md — the lead's rules

Claude follows these and never changes them on its own.

## Rules
1. Do nothing without the lead's permission. Push back when there is a real problem or a better way, with reasons.
2. Never fabricate numbers, citations or links. Every number traces to a source file (`runs/.../results.csv`, logs); every citation to a real paper. Say when unsure.
3. Do only the task given, step by step, concisely.
4. Git: work on `claude/<task>`, open a PR, the lead merges; never push to `main` (except approved edits to the instruction files).
5. Never commit datasets, weights (`*.pt`), `runs/` or zip files.
6. Write to `05_Notes/` only when the lead asks.
7. Keep actual results and expected results clearly separate in the proposal/paper.
8. Send datasets, unpublished results and full thesis text to no service the lead has not chosen.
9. Check every file you produce before handing it over: it opens without error, with no placeholders, broken numbering, stale table of contents or overflowing text.
10. No section cross-references in thesis text ("see Section 3.3.3"); state the point directly.
11. One document = one file. Edit the existing file; no extra copies or `_v2`. If it is locked, ask the lead to close it.
12. Chat with the lead in Vietnamese; everything written into a file is in English. If something is unclear or contradicts another file, say so right away instead of guessing.

## Lab and secrets
- Never write passwords, IPs or tokens into the repo or any project file.
- Only the lead touches the lab machines. Claude puts code or commands in `scripts/` and sends them to the lead, who runs them and copies logs and `results.csv` back.
- No training starts until the lead says so.
