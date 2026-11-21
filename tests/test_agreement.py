"""Kesepakatan antar-anotator (κ Cohen) sebagai modul inti."""

from __future__ import annotations

import pytest

import importlib.util
from pathlib import Path

import pandas as pd

from rra.analysis import agreement

pytestmark = pytest.mark.kasus("U-10")

ROOT = Path(__file__).resolve().parents[1]


def test_kappa_sempurna() -> None:
    seri = pd.Series(["positif", "negatif", "netral", "negatif"])
    assert agreement.cohen_kappa(seri, seri.copy()) == 1.0


def test_kappa_kebetulan() -> None:
    a = pd.Series(["a", "a", "b", "b"])
    b = pd.Series(["a", "b", "a", "b"])
    assert agreement.cohen_kappa(a, b) == 0.0


def _tulis(path: Path, baris: list[tuple[str, str, str]]) -> Path:
    pd.DataFrame(baris, columns=["review_id", "aspect", "sentiment"]).to_csv(path, index=False)
    return path


def test_ringkas_kappa_dari_berkas(tmp_path: Path) -> None:
    satu = _tulis(tmp_path / "a1.csv", [("r1", "makanan", "positif"), ("r2", "harga", "negatif"),
                                         ("r3", "pelayanan", "negatif")])
    dua = _tulis(tmp_path / "a2.csv", [("r1", "makanan", "positif"), ("r2", "harga", "negatif"),
                                        ("r4", "suasana", "netral")])
    hasil = agreement.ringkas_kappa(satu, dua)
    assert hasil["n_ulasan"] == 2
    assert hasil["aspek"]["kappa"] == 1.0
    assert hasil["sentimen"]["n"] == 2


def test_skrip_dan_modul_sama() -> None:
    spec = importlib.util.spec_from_file_location("compute_kappa", ROOT / "scripts" / "compute_kappa.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    assert modul.compare is agreement.compare
