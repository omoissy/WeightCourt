import tomllib
from pathlib import Path

import weightcourt

ROOT = Path(__file__).resolve().parents[1]


def test_package_imports_and_version_matches_pyproject():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())
    assert weightcourt.__version__ == pyproject["project"]["version"]
