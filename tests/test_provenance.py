import json
import re
from datetime import UTC, datetime
from importlib import metadata

import pytest

from weightcourt import provenance

RUN_ID = re.compile(r"^\d{8}T\d{6}Z-(smoke|pilot|exploratory|confirmatory|production)-([0-9a-f]{7}|nogit)-[0-9a-f]{6}$")


def test_sha256_file_matches_known_digest(tmp_path):
    path = tmp_path / "abc.txt"
    path.write_bytes(b"abc")
    assert provenance.sha256_file(path) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_sha256_file_reads_across_chunks(tmp_path):
    path = tmp_path / "big.bin"
    path.write_bytes(b"x" * 10)
    assert provenance.sha256_file(path, chunk_size=3) == provenance.sha256_file(path)


def test_run_id_format_and_uniqueness():
    now = datetime(2026, 11, 11, 12, 0, 0, tzinfo=UTC)
    a, b = provenance.new_run_id("smoke", now=now), provenance.new_run_id("smoke", now=now)
    assert RUN_ID.match(a) and a.startswith("20261111T120000Z-smoke-")
    assert a != b


def test_run_id_rejects_unknown_kind():
    with pytest.raises(ValueError, match="unknown run kind"):
        provenance.new_run_id("final")


def test_run_dir_is_never_reused(tmp_path):
    run_dir = provenance.create_run_dir("r1", runs_dir=tmp_path)
    assert run_dir.is_dir()
    with pytest.raises(FileExistsError):
        provenance.create_run_dir("r1", runs_dir=tmp_path)


def test_manifest_records_inputs_seeds_and_config(tmp_path):
    data = tmp_path / "data.csv"
    data.write_text("a,b\n1,2\n")
    manifest = provenance.build_manifest(
        "r1", "smoke", {"lr": 0.1}, packages=("pytest",), inputs={"train": data}, seeds={"global": 7})
    assert manifest["manifest_schema_version"] == provenance.MANIFEST_SCHEMA_VERSION
    assert manifest["run"]["run_id"] == "r1" and manifest["run"]["status"] == "planned"
    assert manifest["config"] == {"lr": 0.1}
    assert manifest["inputs"]["train"]["sha256"] == provenance.sha256_file(data)
    assert manifest["seeds"] == {"global": 7}
    assert manifest["environment"]["packages"] == {"pytest": metadata.version("pytest")}
    assert set(manifest["code"]) >= {"commit_sha", "branch", "is_dirty", "dirty_paths", "dirty_diff_sha256", "command"}


def test_manifest_fails_on_missing_input(tmp_path):
    with pytest.raises(FileNotFoundError):
        provenance.build_manifest("r1", "smoke", {}, inputs={"train": tmp_path / "missing.csv"})


def test_manifest_fails_on_uninstalled_package():
    with pytest.raises(metadata.PackageNotFoundError):
        provenance.build_manifest("r1", "smoke", {}, packages=("not-a-real-package-xyz",))


def test_write_manifest_round_trips_without_leftover_temp_files(tmp_path):
    manifest = {"run": {"run_id": "r1"}, "config": {"k": [1, 2]}}
    target = provenance.write_manifest(tmp_path, manifest)
    assert json.loads(target.read_text()) == manifest
    assert [p.name for p in tmp_path.iterdir()] == ["manifest.json"]


def test_write_manifest_cleans_up_on_failure(tmp_path):
    with pytest.raises(TypeError):
        provenance.write_manifest(tmp_path, {"bad": object()})
    assert list(tmp_path.iterdir()) == []
