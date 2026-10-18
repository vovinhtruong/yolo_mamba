# Skill: clean-code-yolo-mamba

Copy of the skill saved in the lead's Claude account. Keep both in sync.

Use when writing or editing NEW Python code for the yolo-mamba thesis project (models, blocks, training or eval code). Not for refactoring existing scripts.

Applies to new code only. Do not refactor files already in `scripts/` unless the lead asks. Own YOLO-Mamba model code still waits until the lead picks the Mamba positions (see `context.md`).

## Rules (Ultralytics style)

1. Config: model and data settings live in YAML files; runtime overrides use `key=value` command-line arguments. No settings buried in code.
2. Paths: use `pathlib.Path`; never hard-code user, home or lab paths. Paths come from arguments or YAML. Never write passwords, IPs or tokens.
3. Layout: a package split by function, e.g. `nn/modules/` (one class per block, registered through the model YAML), `models/`, `utils/`. Thin entry scripts in `scripts/` only call package code.
4. Size: no hard line limit, but each function or class does one thing.
5. Names: `snake_case` for functions and variables, `CamelCase` for classes. Short names (`c1, c2, k, s`) are allowed inside network blocks, as in Ultralytics. Otherwise no cryptic abbreviations.
6. Docstrings: Google style with Args and Returns; add a short example on the main class of a module.
7. Type hints: required on public functions and methods.
8. Logging: use `logging` through one shared logger; no `print` in library code.
9. Reproducibility: fixed seed passed in; each run saves its full config (like `args.yaml`) next to its outputs.
10. Tests: small `pytest` tests for the main functions (shapes of a new block, split and label logic).

## Before handing over code

- Run the tests and the linter if they exist; say plainly what was and was not run.
- Work on a branch `claude/<task>` and open a PR; do not train or touch lab machines (see `principles.md`).
- Report actual results separately from expected results.
