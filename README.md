# WeightCourt

> **Status: scaffolding.** The research question, data and evaluation protocol are not defined yet, and nothing has been run.

## Research question

_TBD._

## Layout

```text
src/weightcourt/     library code (provenance.py: run IDs, run directories, manifests)
tests/               unit, contract and repo-hygiene tests
data/                local data, gitignored
runs/                one immutable directory per run, gitignored
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
make install   # pip install -e ".[dev]"
make lint      # ruff check src tests
make test      # pytest -q --cov=weightcourt
```

## Reproducibility

Every run gets a new ID (`<UTC time>-<kind>-<git sha>-<random>`) and its own directory under `runs/`. Before any outputs are written, the run's `manifest.json` records the git commit and dirty state, Python and package versions, input file hashes, seeds and the resolved config. Runs are never overwritten.

## License

MIT
