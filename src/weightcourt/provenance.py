"""Run provenance: immutable run IDs, run directories and manifests.

Every run gets a fresh ID and its own directory, and its manifest is written
before any outputs, so each result can be traced to the exact code, inputs and
environment that produced it.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import secrets
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = ROOT / "runs"
MANIFEST_SCHEMA_VERSION = "1.0"
RUN_KINDS = ("smoke", "pilot", "exploratory", "confirmatory", "production")


def _git(*args: str, strip: bool = True) -> str | None:
    try:
        out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return out.strip() if strip else out


def sha256_file(path: str | Path, chunk_size: int = 1 << 20) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        while block := f.read(chunk_size):
            digest.update(block)
    return digest.hexdigest()


def new_run_id(kind: str, now: datetime | None = None) -> str:
    """``<UTC time>-<kind>-<short git sha or nogit>-<random hex>``, unique per call."""
    if kind not in RUN_KINDS:
        raise ValueError(f"unknown run kind {kind!r}; expected one of {RUN_KINDS}")
    now = now or datetime.now(UTC)
    sha = _git("rev-parse", "--short=7", "HEAD") or "nogit"
    return f"{now:%Y%m%dT%H%M%SZ}-{kind}-{sha}-{secrets.token_hex(3)}"


def create_run_dir(run_id: str, runs_dir: Path = RUNS_DIR) -> Path:
    """Create the run's directory. Raises FileExistsError rather than reuse one: runs are immutable."""
    path = runs_dir / run_id
    path.mkdir(parents=True, exist_ok=False)
    return path


def collect(packages: tuple[str, ...] = (), inputs: dict[str, str | Path] | None = None,
            seeds: dict | None = None) -> dict:
    """Git state, environment, input checksums and seeds for a manifest.

    Missing input files and uninstalled packages raise instead of being skipped,
    so a manifest never silently omits what a run depended on."""
    status = _git("status", "--porcelain", "--untracked-files=all", strip=False)
    dirty_paths = [line[3:] for line in status.splitlines()] if status is not None else None
    diff = _git("diff", "HEAD", strip=False) if dirty_paths else None
    return {
        "code": {
            "commit_sha": _git("rev-parse", "HEAD"),
            "branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
            "is_dirty": bool(dirty_paths) if dirty_paths is not None else None,
            "dirty_paths": dirty_paths or [],
            "dirty_diff_sha256": hashlib.sha256(diff.encode()).hexdigest() if diff else None,
            "command": sys.argv,
        },
        "environment": {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "packages": {p: metadata.version(p) for p in packages},
        },
        "inputs": {name: {"path": str(path), "sha256": sha256_file(path)} for name, path in (inputs or {}).items()},
        "seeds": seeds or {},
    }


def build_manifest(run_id: str, kind: str, config: dict, *, status: str = "planned", **collect_kwargs) -> dict:
    return {
        "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
        "run": {
            "run_id": run_id,
            "kind": kind,
            "status": status,
            "created_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        },
        "config": config,
        **collect(**collect_kwargs),
    }


def write_manifest(run_dir: Path, manifest: dict) -> Path:
    """Atomically write ``manifest.json``: readers see the old file or the new one, never a partial write."""
    target = run_dir / "manifest.json"
    fd, tmp = tempfile.mkstemp(dir=run_dir, prefix=".manifest-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(manifest, f, indent=2, sort_keys=True)
            f.write("\n")
        os.replace(tmp, target)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
    return target
