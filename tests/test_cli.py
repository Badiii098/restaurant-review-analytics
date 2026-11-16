"""Pengujian kotak hitam antarmuka baris perintah.

Pengujian ini tidak memanggil fungsi Python secara langsung, melainkan
menjalankan perintah sebagaimana yang akan dilakukan pengguna. Tujuannya
memastikan seluruh jalur pemakaian benar-benar berfungsi dari luar.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


@pytest.fixture()
def cli_root(tmp_path: Path) -> Path:
    """Direktori proyek sementara berisi salinan berkas konfigurasi."""
    shutil.copytree(ROOT / "config", tmp_path / "config")
    return tmp_path


def run_cli(root: Path, *args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(SRC)
    return subprocess.run(
        [sys.executable, "-m", "rra.cli", "--root", str(root), *args],
        capture_output=True, text=True, env=env, timeout=900, check=False,
    )


def test_help_is_available(cli_root: Path) -> None:
    result = run_cli(cli_root, "--help")
    assert result.returncode == 0
    for command in ("run", "evaluate", "benchmark", "models", "sample-data", "explain"):
        assert command in result.stdout


def test_models_lists_only_svm(cli_root: Path) -> None:
    result = run_cli(cli_root, "models")
    assert result.returncode == 0
    assert "svm" in result.stdout
    assert "Naive Bayes" not in result.stdout


def test_sample_data_creates_files(cli_root: Path) -> None:
    result = run_cli(cli_root, "sample-data", "--n", "60")
    assert result.returncode == 0
    assert (cli_root / "data" / "raw" / "reviews.csv").exists()
    assert (cli_root / "data" / "reference" / "labels.csv").exists()
    assert (cli_root / "data" / "reference" / "gold_phrases.json").exists()


def test_run_produces_priorities_and_reports(cli_root: Path) -> None:
    run_cli(cli_root, "sample-data", "--n", "80")
    result = run_cli(cli_root, "run", "--json")
    assert result.returncode == 0, result.stderr
    assert "Peringkat prioritas" in result.stdout
    assert (cli_root / "data" / "processed" / "rra.sqlite").exists()
    assert list((cli_root / "reports").glob("laporan-*.md"))


def test_run_without_data_fails_with_guidance(cli_root: Path) -> None:
    result = run_cli(cli_root, "run")
    assert result.returncode != 0
    assert "sample-data" in (result.stderr + result.stdout)


def test_unknown_model_gives_clear_error(cli_root: Path) -> None:
    """Nama model yang tidak terdaftar ditolak dengan pesan, bukan traceback."""
    run_cli(cli_root, "sample-data", "--n", "60")
    result = run_cli(cli_root, "run", "--no-report", "--set", "model.name=nb")
    assert result.returncode != 0
    assert "tidak terdaftar" in result.stderr
    assert "Traceback" not in result.stderr


def test_explain_requires_a_previous_run(cli_root: Path) -> None:
    result = run_cli(cli_root, "explain")
    assert result.returncode != 0
    assert "rra run" in (result.stderr + result.stdout)


def test_explain_shows_audit_trail(cli_root: Path) -> None:
    run_cli(cli_root, "sample-data", "--n", "80")
    run_cli(cli_root, "run", "--no-report")
    result = run_cli(cli_root, "explain")
    assert result.returncode == 0
    assert "Volume" in result.stdout
    assert "Keparahan" in result.stdout
    assert "Keragaman" in result.stdout


def test_benchmark_writes_summary(cli_root: Path) -> None:
    run_cli(cli_root, "sample-data", "--n", "60")
    result = run_cli(cli_root, "benchmark", "--repeat", "2")
    assert result.returncode == 0, result.stderr
    assert (cli_root / "reports" / "benchmark.json").exists()


def test_unknown_model_name_is_rejected(cli_root: Path) -> None:
    run_cli(cli_root, "sample-data", "--n", "40")
    result = run_cli(cli_root, "run", "--no-report", "--set", "model.name=tidak_ada")
    assert result.returncode != 0
    assert "tidak terdaftar" in (result.stderr + result.stdout)


def test_invalid_set_syntax_is_rejected(cli_root: Path) -> None:
    result = run_cli(cli_root, "models", "--set", "tanpa_sama_dengan")
    assert result.returncode != 0
