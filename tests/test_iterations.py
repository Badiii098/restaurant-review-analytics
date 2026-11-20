"""Catatan iterasi prototipe (SDLC Prototipe, iterasi 1–2) dan selisih Macro-F1."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from rra.iterations import bandingkan, muat_iterasi, simpan_iterasi

pytestmark = pytest.mark.kasus("U-11")

LAPORAN = {
    "summary": {"aspect_macro_f1_mean": 0.71, "aspect_macro_f1_std": 0.02,
                "sentiment_macro_f1_mean": 0.64, "sentiment_macro_f1_std": 0.03},
    "per_fold": [{"fold": 1, "aspect": {"macro_f1": 0.7, "per_aspect": {"makanan": {"f1": 0.8}}},
                  "sentiment": {"macro_f1": 0.63}}],
}


def test_simpan_lalu_muat(tmp_path: Path) -> None:
    berkas = simpan_iterasi(LAPORAN, 1, "awal", tmp_path, data_contoh=True, commit="abc1234")
    assert berkas.name == "iterasi-1.json"
    isi = json.loads(berkas.read_text(encoding="utf-8"))
    assert isi["nomor"] == 1 and isi["data_contoh"] is True and isi["commit"] == "abc1234"
    assert isi["catatan"] == "awal"
    assert isi["ringkasan"]["aspect_macro_f1_mean"] == 0.71
    assert [i["nomor"] for i in muat_iterasi(tmp_path)] == [1]


def test_muat_urut_nomor_dan_folder_kosong(tmp_path: Path) -> None:
    assert muat_iterasi(tmp_path / "tidak-ada") == []
    simpan_iterasi(LAPORAN, 2, "perbaikan", tmp_path, data_contoh=False, commit=None)
    simpan_iterasi(LAPORAN, 1, "awal", tmp_path, data_contoh=False, commit=None)
    assert [i["nomor"] for i in muat_iterasi(tmp_path)] == [1, 2]


def test_bandingkan_selisih_empat_desimal() -> None:
    a = {"ringkasan": {"aspect_macro_f1_mean": 0.71, "sentiment_macro_f1_mean": 0.64}}
    b = {"ringkasan": {"aspect_macro_f1_mean": 0.7456, "sentiment_macro_f1_mean": 0.6}}
    assert bandingkan(a, b) == {"aspek_macro_f1": 0.0356, "sentimen_macro_f1": -0.04}


def test_nomor_iterasi_harus_positif(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        simpan_iterasi(LAPORAN, 0, "", tmp_path, data_contoh=True, commit=None)


def test_cli_evaluate_menulis_iterasi(tmp_path: Path) -> None:
    import os
    import shutil
    import subprocess
    import sys

    root_repo = Path(__file__).resolve().parents[1]
    shutil.copytree(root_repo / "config", tmp_path / "config")
    env = dict(os.environ, PYTHONPATH=str(root_repo / "src"))
    perintah = [sys.executable, "-m", "rra.cli", "--root", str(tmp_path)]
    subprocess.run([*perintah, "sample-data", "--n", "200"], env=env, check=True,
                   capture_output=True, timeout=600)
    hasil = subprocess.run([*perintah, "evaluate", "--folds", "2", "--iterasi", "1",
                            "--catatan", "prototipe awal"],
                           env=env, capture_output=True, text=True, timeout=900)
    assert hasil.returncode == 0, hasil.stderr
    isi = json.loads((tmp_path / "reports" / "iterasi" / "iterasi-1.json").read_text(encoding="utf-8"))
    assert isi["data_contoh"] is True
    assert isi["catatan"] == "prototipe awal"
    assert set(isi["per_aspek_f1"]) == {"makanan", "pelayanan", "harga", "suasana", "fasilitas"}
