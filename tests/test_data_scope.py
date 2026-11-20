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


# --- Pemilihan sampel delapan restoran (purposive, kriteria tertulis) -------
import csv  # noqa: E402
import json  # noqa: E402

from rra.config import Config  # noqa: E402
from rra.io_layer.scope import (  # noqa: E402
    hitung_ulasan_dalam_rentang,
    load_sample,
    pilih_sampel,
    target_per_restoran,
)


def _kandidat(spek: list[tuple[str, str]]) -> list[dict]:
    return [{"kode": kode, "kategori": kategori, "target_ulasan": "280"} for kode, kategori in spek]


def test_pilih_delapan_urut_jumlah() -> None:
    kandidat = _kandidat([(f"r{i:02d}", f"k{i}") for i in range(1, 11)])
    jumlah = {f"r{i:02d}": 100 * i for i in range(1, 11)}
    hasil = pilih_sampel(kandidat, jumlah, n=8, maks_per_kategori=2)
    assert [r["kode"] for r in hasil] == [f"r{i:02d}" for i in range(10, 2, -1)]


def test_batas_dua_per_kategori() -> None:
    kandidat = _kandidat([("r01", "A"), ("r02", "A"), ("r03", "A"), ("r04", "B"), ("r05", "C")])
    jumlah = {"r01": 900, "r02": 800, "r03": 700, "r04": 100, "r05": 50}
    hasil = pilih_sampel(kandidat, jumlah, n=3, maks_per_kategori=2)
    assert [r["kode"] for r in hasil] == ["r01", "r02", "r04"]


def test_isi_ulang_bila_batas_menyisakan_kurang() -> None:
    kandidat = _kandidat([("r01", "A"), ("r02", "A"), ("r03", "A"), ("r04", "B")])
    jumlah = {"r01": 900, "r02": 800, "r03": 700, "r04": 100}
    hasil = pilih_sampel(kandidat, jumlah, n=4, maks_per_kategori=2)
    assert sorted(r["kode"] for r in hasil) == ["r01", "r02", "r03", "r04"]


def test_seri_diurut_kode() -> None:
    kandidat = _kandidat([("r03", "A"), ("r01", "B"), ("r02", "C")])
    hasil = pilih_sampel(kandidat, {"r01": 5, "r02": 5, "r03": 5}, n=2, maks_per_kategori=2)
    assert [r["kode"] for r in hasil] == ["r01", "r02"]


def test_target_dibatasi_625() -> None:
    assert target_per_restoran(900, 625) == 625
    assert target_per_restoran(380, 625) == 380


def test_load_sample_tanpa_kolom_kosong(tmp_path: Path) -> None:
    berkas = tmp_path / "r.csv"
    berkas.write_text("kode,nama,aktif\nr01,A,1\n", encoding="utf-8")
    assert load_sample(berkas) == []
    berkas.write_text("kode,nama,aktif,sampel\nr01,A,1,1\nr02,B,1,0\n", encoding="utf-8")
    assert [r["kode"] for r in load_sample(berkas)] == ["r01"]


def test_hitung_ulasan_dalam_rentang(tmp_path: Path) -> None:
    baris = [{"tanggal": "2020-05-01"}, {"tanggal": "2021-01-02"}, {"tanggal": "2026-12-31"}, {}]
    (tmp_path / "r01_hasil.jsonl").write_text(
        "\n".join(json.dumps(b) for b in baris) + "\n", encoding="utf-8")
    assert hitung_ulasan_dalam_rentang(tmp_path, (2021, 2026)) == {"r01": 2}
    assert hitung_ulasan_dalam_rentang(tmp_path / "tidak-ada", (2021, 2026)) == {}


def test_sampel_sesuai_konfigurasi() -> None:
    cfg = Config.load(root=ROOT)
    assert int(cfg.get("sampling.n_restoran")) == 8
    with RESTAURANTS.open(encoding="utf-8", newline="") as handle:
        kolom = csv.DictReader(handle).fieldnames or []
    if "sampel" in kolom:
        assert len(load_sample(RESTAURANTS)) == 8


def test_skrip_pilih_restoran_menulis_kolom_sampel(tmp_path: Path) -> None:
    import subprocess
    import sys

    (tmp_path / "config").mkdir()
    import shutil
    shutil.copy(ROOT / "config" / "default.yaml", tmp_path / "config" / "default.yaml")
    shutil.copy(ROOT / "config" / "model_svm.yaml", tmp_path / "config" / "model_svm.yaml")
    baris = ["kode,nama,query,kota,kategori,target_ulasan,aktif"]
    baris += [f"r{i:02d},R{i},q,Jakarta,K{i % 5},280,1" for i in range(1, 13)]
    (tmp_path / "config" / "restaurants.csv").write_text("\n".join(baris) + "\n", encoding="utf-8")
    maps = tmp_path / "data" / "raw" / "maps"
    maps.mkdir(parents=True)
    for i in range(1, 13):
        (maps / f"r{i:02d}_hasil.jsonl").write_text(
            "".join(json.dumps({"tanggal": "2024-01-01"}) + "\n" for _ in range(50 * i)),
            encoding="utf-8")
    proses = subprocess.run([sys.executable, str(ROOT / "scripts" / "pilih_restoran.py"),
                             "--root", str(tmp_path), "--tulis"], capture_output=True, text=True)
    assert proses.returncode == 0, proses.stderr
    sampel = load_sample(tmp_path / "config" / "restaurants.csv")
    assert len(sampel) == 8
    assert all(int(r["target_sampel"]) <= 625 for r in sampel)
    assert {r["kode"] for r in sampel} >= {"r12", "r11"}
