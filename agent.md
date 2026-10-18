# agent.md — handbook for Claude

Read first in every session. Before each reply ask: did I answer exactly what was asked, and is anything here not requested? Then read `principles.md` (the lead's rules) and `context.md` (thesis, decisions, status, lab, dataset), both in this folder.

**Role.** Claude works for the lead (Vo Vinh Truong) on his master's thesis: plans, checks papers, writes and reviews code, analyses lab results, drafts text when asked. It proposes options with reasons; the lead decides (`context.md` lists what is decided and what is not). Other AI apps are opened by the lead himself; Claude does not coordinate them.

**Folders** (lead's Windows machine, `Desktop\yolo_mamba\`; `~/` means the lab machine, lead only):
```
01_Papers/ papers by topic + Summary.xlsx     05_Notes/    progress notes (YYMMDD.md)
02_Dataset/ GRAZ, FracAtlas, MURA (not in git) 06_Reports/  weekly report slides
03_Code/   this git repo (private)             07_Thesis/   Thesis, Draft/, Proposal/
04_Results/ result tables, charts              08_Teaching/ teaching slides
```
`03_Code/`: `agent.md`, `principles.md`, `context.md` (the instruction files), `scripts/` (train/eval/analysis, lab paths), `env_backup/`, `repos/` (git-ignored third-party source).

**Who writes where**
- `01_Papers/` … `08_Teaching/`: the lead. Claude sends files to the lead, who places them.
- `07_Thesis/*.docx`: the lead only. Claude sends drafts as separate files or in chat.
- `03_Code/`: Claude on a branch `claude/<task>` + PR; the lead merges. Exception: the instruction files, once the lead approves.
- Lab machines: the lead only. Claude sends code and commands to the lead.

**How work runs.** The lead gives an order. For anything non-trivial Claude states its plan first, and asks first when a wrong guess is expensive. Claude does it; the lead reviews and decides.
Syncing the instruction files to Windows: commit, push, make a git bundle, put it in `03_Code/`, fetch + fast-forward merge on the lead's machine, delete the bundle (to become a skill).

**Work streams** (LOCKED = waits for the lead's go-ahead)
- B. Reference papers: find Mamba+YOLO papers with public code (first 1–2, then the rest) → explain each → setup script + test-run guide → lab run (LOCKED).
- C. YOLO-Mamba code: see how each paper adds Mamba → pick candidate positions with the lead → Mamba block + shape tests → training (LOCKED).
- D. Approach B: literature on different image sizes → 2–3 options → code + training (LOCKED).
- E. Documents: the lead writes, Claude drafts when asked.

Our own YOLO-Mamba model code waits until the lead picks the Mamba positions; setup scripts for a reference paper's own repo may start as soon as the lead asks.
