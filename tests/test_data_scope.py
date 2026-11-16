"""Cakupan data penelitian: 18 restoran Jabodetabek, target total 5.000 ulasan."""

from __future__ import annotations

from pathlib import Path

from rra.io_layer.scope import load_active_restaurants, shortfall

ROOT = Path(__file__).resolve().parents[1]
RESTAURANTS = ROOT / "config" / "restaurants.csv"
DIKELUARKAN = {"r06", "r11", "r14", "r16", "r18", "r20", "r24"}


def test_delapan_belas_restoran_aktif() -> None:
    aktif = load_active_restaurants(RESTAURANTS)
    assert len(aktif) == 18
    assert not DIKELUARKAN & {row["kode"] for row in aktif}


def test_target_total_minimal_lima_ribu() -> None:
    aktif = load_active_restaurants(RESTAURANTS)
    assert all(int(row["target_ulasan"]) == 280 for row in aktif)
    assert sum(int(row["target_ulasan"]) for row in aktif) == 5040


def test_shortfall_melaporkan_kekurangan_tanpa_galat() -> None:
    aktif = [{"kode": "r10", "target_ulasan": "280"}, {"kode": "r01", "target_ulasan": "280"},
             {"kode": "r99", "target_ulasan": "280"}]
    hasil = {row["kode"]: row for row in shortfall(aktif, {"r10": 228, "r01": 400})}
    assert hasil["r10"]["kurang"] == 52
    assert hasil["r01"]["kurang"] == 0
    assert hasil["r99"] == {"kode": "r99", "target": 280, "terkumpul": 0, "kurang": 280}
