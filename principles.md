# principles.md — the lead's decisions and rules

Claude follows these and never changes them on its own.

## Decided
- Main experiments use `imgsz=640` (`1120` is Approach A, only a control if the lead says so).
- Ablation 2 × 2 at `imgsz=640`: {with/without rescaling method B} × {with/without Mamba}.
- Mamba workflow: (1) reproduce **every** reference Mamba+YOLO paper with public code on GRAZ, to learn how others customise YOLO and to get baselines (their model on our data, not directly comparable to YOLO26); (2) discuss candidate Mamba positions with Claude; (3) try candidates one by one; the one that works goes into the 2 × 2 ablation.
- Choose models on the validation set only; run the test set once, at the very end.
- Four block types: MLP, CNN, Attention, SSM — no RNN.
- 3 random seeds; no Wilcoxon test in the current proposal.
- Approach B is a main contribution, presented as such only in the Methodology chapter of Proposal v2.

## Not decided (Claude may only propose, with reasons)
- Where Mamba goes in YOLO26 (candidate layers 2, 4, 6, 8, 10, 13, 16, 19, 22 — see `05_Notes/261013.md`).
- Whether to add Wilcoxon or another test (the lead will ask the professor).
- The concrete algorithm for Approach B.
- Epochs, batch size and machine for the full Mamba-YOLO-T run.

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
