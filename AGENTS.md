# WeightCourt: agent instructions (Codex and Claude Code)

Universal rules live in the global configs (`~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`) and the installed skills. This file adds only what is specific to this repo. `CLAUDE.md` imports this file, so edit rules here.

## Project

- **Status:** Phase 0, research definition and novelty review. No hypothesis, dataset, model choice or protocol is frozen, and nothing has been run.
- **Foundation:** Takehi, Teoh, Zhang and Khattab, "Sparks of Weight-Space Programming: LLMs can natively read & write neural network weights" (MIT CSAIL, 2 Nov 2026), https://rikiyat.github.io/blog/weight-space-programming/, and its released logs, https://github.com/RikiyaT/lm_understand-logs. WeightCourt starts from that post's "recursive self-improvement" future direction.
- **Candidate direction (not frozen):** when an AI agent proposes a persistent edit to another model's weights, can an independent verifier decide whether to accept it, especially when the agent's diagnosis is wrong, incomplete or misleading, and as accepted edits accumulate?
- **Owner / reviewer:** @omoissy
- **Repo:** https://github.com/omoissy/WeightCourt (public). Primary branch `main`; work on feature branches and merge through PRs.

## Research boundaries

- Freeze the research question, hypotheses, splits and analysis plan in a committed, versioned protocol before any confirmatory run. Until then, every result is exploratory.
- WeightCourt is not a sequel to the owner's SAE-MAS capstone. Do not copy that project's code, data or results. The core study needs no SAE training, probes or replication of the capstone's activation interventions. Acknowledge shared ideas in the paper.
- Do not claim weight editing, verification or acceptance gates, adversarial edits or sequential editing as novel on their own. The contribution must be a specific gap that the Phase 0 review confirms.
- MIT's editor ("GPT-6 Astra") may not be available to us. Keep "re-evaluating MIT's published edit" separate from "generating new edits with a model we can run", and never present one as the other.
- Check every citation, number and arXiv ID in docs or the paper against the source itself. Do not carry them over unchecked from chat summaries or AI-generated plans.
- Licenses for MIT's logs: their scripts are MIT; logs, data and networks are CC BY 4.0 (credit them); quoted benchmark content keeps its own license. `exp5_write_from_scratch/` quotes GPL-3.0 MinAtar code, so do not copy from it.

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
