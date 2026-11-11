"""Nothing that would be committed contains credentials, local data or run outputs."""
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    "Anthropic key": re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}"),
    "OpenAI key": re.compile(r"\bsk-(proj-)?[A-Za-z0-9]{32,}\b"),
    "Hugging Face token": re.compile(r"\bhf_[A-Za-z0-9]{30,}\b"),
}
FORBIDDEN_PATHS = re.compile(r"(^|/)\.env$|\.pem$|^data/raw/|^runs/")


def committable_files() -> list[str]:
    """Tracked files plus untracked files that .gitignore does not exclude."""
    try:
        out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                             cwd=ROOT, capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("git unavailable")
    return [p for p in out.splitlines() if (ROOT / p).is_file()]


def test_no_secrets_in_committable_files():
    hits = [f"{path}: {name}"
            for path in committable_files()
            for name, pattern in SECRET_PATTERNS.items()
            if pattern.search((ROOT / path).read_text(errors="ignore"))]
    assert not hits, hits


def test_no_env_keys_data_or_runs_committable():
    bad = [p for p in committable_files() if FORBIDDEN_PATHS.search(p)]
    assert not bad, bad


def test_gitignore_excludes_sensitive_paths():
    for path in (".env", "key.pem", "data/raw/x.csv", "runs/r1/manifest.json"):
        result = subprocess.run(["git", "check-ignore", "-q", path], cwd=ROOT)
        assert result.returncode == 0, f"{path} is not gitignored"
