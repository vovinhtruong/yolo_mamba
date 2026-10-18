# memory.md — the lead's principles

These are the lead's decisions and rules. Claude follows them and never changes them on its own.

## DECIDED — do not change on your own
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

## NOT YET DECIDED — Claude may only propose (with reasons), never decide
- Where to place Mamba in YOLO26 — candidates are chosen after phase 1 (possible layers: 2, 4, 6, 8, 10, 13, 16, 19, 22 — see `05_Notes/261013.md` §1).
- Whether to add Wilcoxon (or another statistical test), e.g. when comparing Mamba positions whose differences may be smaller than seed-to-seed variation — the lead will discuss with the professor.
- The concrete algorithm for Approach B.
- Epochs/batch size and which machine to use for the full Mamba-YOLO-T training run.

## Working rules
1. **Do nothing without the lead's permission.** Push back when there is a real problem or a better way — always with reasons.
2. **Never fabricate numbers, citations or links.** Every number must trace back to its source file (`runs/.../results.csv`, logs) and every citation to a real paper. Say clearly when unsure.
3. Be concise and focused; do only the task given; work step by step.
4. **Git:** work on a branch `claude/<task>`, open a PR, the lead merges. Never push directly to `main`, except edits to the instruction files that the lead has approved.
5. Never commit datasets, weights (`*.pt`), `runs/`, or zip files.
6. Write to `05_Notes/` only when the lead asks.
7. Keep **actual results** and **expected results** clearly separate when writing the proposal/paper.
8. Never send datasets, unpublished results, or full thesis/proposal text to any service the lead has not chosen.
9. **Files are reader-facing.** Any file Claude produces or renders (docx, pptx, pdf, xlsx, figure) must be checked before handing it over: it opens with no error or prompt, and has no leftover placeholders, broken numbering, stale table of contents, overflowing text or other visible defects.
10. **No section cross-references in thesis/proposal text** (e.g. "described in Section 3.3.3", "(Section 4.3)"). State the point directly so the reader does not have to look it up.
11. **One document = one file.** Edit the existing file; never save extra copies or new versions (`_v3`, `_new`, …) on your own. If the file is open or locked, ask the lead to close it instead of saving under another name.
12. **Language and problems.** Chat with the lead in Vietnamese. Everything written into a file or page (html, docx, pptx, xlsx, figures, notes, code comments, these files) is in English. When something is unclear or contradicts another file, do not guess and do not silently work around it: tell the lead right away, with what is wrong and where.

## Lab and secrets
- **Never write passwords, IPs or tokens into the repo or any project file.**
- **The lab machines are managed by the lead only.** Claude never accesses or runs anything on them. Any code or command meant for the lab goes into the repo (`scripts/`) and is **sent to the lead**, who reviews and runs it. Lab outputs (logs, `results.csv`) are copied back by the lead; Claude then reads and analyses them.
- **No training run starts until the lead says so.**
