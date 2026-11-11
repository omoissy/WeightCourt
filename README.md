# WeightCourt

> **Status: Phase 0, research definition.** The direction below is a candidate under novelty review. No hypothesis, dataset, model choice or protocol is frozen, and nothing has been run.

## Starting point

WeightCourt extends [Sparks of Weight-Space Programming: LLMs can natively read & write neural network weights](https://rikiyat.github.io/blog/weight-space-programming/) (Takehi, Teoh, Zhang and Khattab, MIT CSAIL, 2 November 2026). In selected experiments, that work showed a general-purpose LLM inspecting neural-network weights and editing them directly, without gradient descent. Its authors released [complete logs and a harness](https://github.com/RikiyaT/lm_understand-logs). Its "What Comes Next" section proposes **recursive self-improvement** as future work: an LLM inspecting and improving its own weights or another model's. WeightCourt starts from that direction.

## Candidate research question

> When an AI agent proposes a persistent edit to another model's weights, can an independent verifier decide whether the edit should be accepted, especially when the agent's diagnosis is wrong, incomplete or misleading, and as accepted edits accumulate?

Working title (not final): *WeightCourt: Reliable Agent-to-Agent Weight-Space Programming for Recursive Model Improvement.*

## Phase 0 plan

Nothing below Phase 0 is built until these steps are done:

1. Study MIT experiments 7 (sycophancy detection in Gemma 3 270M) and 8 (editing Qwen3.5-0.8B to stop reasoning loops) from the released code, prompts, evaluations and stated limitations.
2. Review work that extends weight-space programming, plus model editing, sequential editing, malicious-edit benchmarks and acceptance gates. Check every citation against its source.
3. Separate what MIT demonstrated, what it only proposed, and what later work already covers.
4. Pick one testable gap that differs from both MIT's experiments and the author's earlier SAE-MAS capstone.
5. Freeze the hypothesis, baselines, splits and analysis plan before any confirmatory experiment.

## Out of scope for the core study

- Training SAEs or probes, or replicating the SAE-MAS capstone's activation interventions.
- Claiming weight editing, acceptance gates, adversarial edits or sequential editing as novel on their own.

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

MIT for this repository's code. MIT's released logs carry their own terms: scripts are MIT, logs and data are CC BY 4.0, and quoted benchmark content keeps its original license.
