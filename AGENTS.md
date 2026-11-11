# WeightCourt: agent instructions (Codex and Claude Code)

Universal rules live in the global configs (`~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`) and the installed skills. This file adds only what is specific to this repo. `CLAUDE.md` imports this file, so edit rules here.

## Project

- **Status:** scaffolding only. Nothing has been run.
- **Research question, data, models, evaluation protocol:** TBD. Do not invent them; ask the owner.
- **Owner / reviewer:** @omoissy
- **Repo:** https://github.com/omoissy/WeightCourt (public). Primary branch `main`; work on feature branches and merge through PRs.

## Runtime and commands

- Python >= 3.11 (developed on 3.13). Package `weightcourt` lives in `src/` and is installed editable.
- Install: `pip install -e ".[dev]"` (or `make install`)
- Test: `pytest -q --cov=weightcourt` (coverage floor 80%; `make test`)
- Lint: `ruff check src tests` (`make lint`)
- CI: `.github/workflows/ci.yml` runs lint and tests on Python 3.11 and 3.13 for every push to `main` and every PR.

## Layout

- `src/weightcourt/`: all reusable logic. `provenance.py` is the single source of truth for run IDs, run directories and manifests; extend it rather than writing new run-metadata code.
- `tests/`: unit, contract and repo-hygiene tests.
- `scripts/` (thin entry points) and `configs/` (run configs): create when first needed.
- `data/` (gitignored): `data/raw/` is read-only once downloaded.
- `runs/` (gitignored): one directory per run, created by `provenance.create_run_dir`.

## Protected paths and data

- `data/raw/` and every `runs/<run_id>/` are read-only. Never overwrite or delete a run; start a new run ID instead.
- The holdout/test split is TBD. It must be frozen (committed and hashed) before any confirmatory run, and never used for tuning.
- `.env`, keys and `*.pem` are never committed; `tests/test_repo_hygiene.py` enforces this.

## Needs owner approval

- Pushing, merging PRs, releases, enabling GitHub Pages (the repo is public).
- Paid API calls, GPU rental, large downloads, adding dependencies.

## Run conventions

- Every run: `new_run_id(kind)` -> `create_run_dir` -> `build_manifest` + `write_manifest` before writing outputs. `kind` is one of `smoke | pilot | exploratory | confirmatory | production`.
- Every number in a figure, table or the README must trace to a run directory and its `manifest.json`.
