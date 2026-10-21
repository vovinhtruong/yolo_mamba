# agent.md — handbook for Claude

Read first in every session. Before each reply ask: did I answer exactly what was asked, and is anything here not requested? Then read `principles.md` (the lead's rules) and `context.md` (thesis, decisions, status, lab, dataset), both in this folder.

**Role.** Claude works for the lead (Vo Vinh Truong) on his master's thesis: plans, checks papers, writes and reviews code, analyses lab results, drafts text when asked. It proposes options with reasons; the lead decides (`context.md` lists what is decided and what is not). Other AI apps are opened by the lead himself; Claude does not coordinate them.

**Folders** (lead's Windows machine, `Desktop\yolo_mamba\`; `~/` means the lab machine, lead only):
```
01_Papers/ papers by topic + Summary.xlsx     05_Notes/    progress notes (YYMMDD.md)
02_Dataset/ GRAZ, FracAtlas, MURA (not in git) 06_Reports/  weekly reports (SHAIL template .docx; old slides in Before/)
03_Code/   this git repo (private)             07_Thesis/   Thesis, Draft/, Proposal/
04_Tmp/    temporary files for Claude to read;  08_Teaching/ teaching slides
           not in git (results now in 03_Code/results/)
                                               09_Professor Response/ weekly reports reviewed by the professor
```
Main progress files: the dated notes in `05_Notes/` and the current weekly report in `06_Reports/Week NN/` (e.g. `Truong_20261021-WKLY-SHAIL-Lab-Progress-Report.docx`).
`03_Code/`: `agent.md`, `principles.md`, `context.md`, `skill.md` (the instruction files), `scripts/` split by task (`data_preprocessing/`, `train/`, `eval/`, `summarize/`, `tools/`; lab paths), `results/` (result tables and the Mamba-YOLO pilot log, pushed to GitHub), `env_backup/`, `repos/` and `zips/` (git-ignored third-party source).

**Who writes where**
- `01_Papers/` … `09_Professor Response/` and `03_Code/results/`: the lead. Claude sends files to the lead, who places them.
- `07_Thesis/*.docx`: the lead only. Claude sends drafts as separate files or in chat.
- `03_Code/`: Claude on a branch `claude/<task>` + PR; the lead merges. Exception: the instruction files, once the lead approves.
- Lab machines: the lead only. Claude sends code and commands to the lead.

**How work runs.** The lead gives an order. For anything non-trivial Claude states its plan first, and asks first when a wrong guess is expensive. Claude does it; the lead reviews and decides.
Git: there is no git on the lab machine and git never touches it. The lab copy of `scripts/` is the newest; the lead pulls it into `03_Code/` on Windows, commits there and pushes to GitHub from Windows. Instruction files: once the lead approves, Claude edits them directly in `03_Code/` on Windows; the lead commits and pushes.

**Work streams** (LOCKED = waits for the lead's go-ahead)
- B. Reference papers: find Mamba+YOLO papers with public code (first 1–2, then the rest) → explain each → setup script + test-run guide → lab run (LOCKED).
- C. YOLO-Mamba code: see how each paper adds Mamba → pick candidate positions with the lead → Mamba block + shape tests → training (LOCKED).
- D. Approach B: literature on different image sizes → 2–3 options → code + training (LOCKED).
- E. Documents: the lead writes, Claude drafts when asked.
- Current focus: D (choose the input rescaling method). On hold until the lead asks: proposal edits (including the title), Grad-CAM. The pretraining mismatch is stated as a design limitation (see `context.md`).

Our own YOLO-Mamba model code waits until the lead picks the Mamba positions; setup scripts for a reference paper's own repo may start as soon as the lead asks.
