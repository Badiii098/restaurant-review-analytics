"""Cakupan sampel penelitian: restoran aktif dan kekurangan ulasan.

Kandidat penelitian adalah 18 restoran aktif di Jabodetabek. Sampel analisis
dipilih dari kandidat itu secara *purposive* dengan kriteria tertulis pada
``config/default.yaml`` (blok ``sampling``): urut menurut jumlah ulasan dalam
rentang tahun, paling banyak ``maks_per_kategori`` per kategori, sampai
``n_restoran`` (8). Restoran dengan kolom ``aktif`` bernilai 0 tetap tercatat
di ``config/restaurants.csv`` agar alasan pengeluarannya dapat ditelusuri.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable, Mapping

_TIDAK_AKTIF = {"0", "false", "False", "tidak"}


def load_active_restaurants(path: Path) -> list[dict]:
    """Baca daftar restoran dan kembalikan yang aktif saja, urut sesuai berkas."""
    with Path(path).open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return [row for row in rows if (row.get("aktif") or "1").strip() not in _TIDAK_AKTIF]


def shortfall(active: Iterable[Mapping[str, str]], counts: Mapping[str, int]) -> list[dict]:
    """Kekurangan ulasan per restoran terhadap targetnya.

    Kekurangan dilaporkan, bukan dianggap galat: restoran yang ulasannya
    di bawah target tetap dianalisis dan kekurangannya dicatat sebagai batasan.
    """
    hasil = []
    for row in active:
        target = int(row["target_ulasan"])
        terkumpul = int(counts.get(row["kode"], 0))
        hasil.append({"kode": row["kode"], "target": target, "terkumpul": terkumpul,
                      "kurang": max(target - terkumpul, 0)})
    return hasil


def load_sample(path: Path) -> list[dict]:
    """Restoran yang sudah ditetapkan sebagai sampel (kolom ``sampel`` = 1).

    Kosong bila kolom ``sampel`` belum ada, artinya pemilihan belum dijalankan.
    """
    with Path(path).open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return [row for row in rows if (row.get("sampel") or "").strip() == "1"]


def hitung_ulasan_dalam_rentang(maps_dir: Path, rentang: tuple[int, int]) -> dict[str, int]:
    """Jumlah ulasan per kode restoran yang tahunnya berada dalam ``rentang`` (inklusif)."""
    folder = Path(maps_dir)
    if not folder.is_dir():
        return {}
    awal, akhir = rentang
    hasil: dict[str, int] = {}
    for berkas in sorted(folder.glob("*_hasil.jsonl")):
        kode = berkas.name.removesuffix("_hasil.jsonl")
        n = 0
        for baris in berkas.open(encoding="utf-8"):
            if not baris.strip():
                continue
            tahun = (json.loads(baris).get("tanggal") or "")[:4]
            if tahun.isdigit() and awal <= int(tahun) <= akhir:
                n += 1
        hasil[kode] = n
    return hasil


def pilih_sampel(kandidat: Iterable[Mapping[str, str]], jumlah_dalam_rentang: Mapping[str, int],
                 n: int, maks_per_kategori: int) -> list[dict]:
    """Purposive sampling deterministik.

    Kandidat diurut menurun menurut jumlah ulasan dalam rentang (seri: kode
    menaik), lalu diambil berurutan dengan paling banyak ``maks_per_kategori``
    per kategori. Bila batas kategori menyisakan kurang dari ``n``, sisa
    urutan dipakai untuk mencukupi, karena jumlah sampel adalah pakem.
    """
    urut = sorted((dict(r) for r in kandidat),
                  key=lambda r: (-int(jumlah_dalam_rentang.get(r["kode"], 0)), r["kode"]))
    terpilih: list[dict] = []
    per_kategori: dict[str, int] = {}
    for row in urut:
        kategori = row.get("kategori", "")
        if len(terpilih) < n and per_kategori.get(kategori, 0) < maks_per_kategori:
            terpilih.append(row)
            per_kategori[kategori] = per_kategori.get(kategori, 0) + 1
    for row in urut:
        if len(terpilih) >= n:
            break
        if row not in terpilih:
            terpilih.append(row)
    return terpilih


def target_per_restoran(tersedia: int, batas: int) -> int:
    """Target ulasan per restoran: data yang tersedia, dibatasi ``batas``."""
    return min(int(tersedia), int(batas))


def ringkas_sampel(daftar: Path, maps_dir: Path, *, n: int, rentang: tuple[int, int],
                   maks_per_kategori: int, batas: int) -> dict:
    """Sampel yang dipakai sistem dan naskah: tetapan di ``restaurants.csv`` bila ada,
    selain itu usulan otomatis dari data mentah, selain itu kosong.

    Bila sampel sudah ditetapkan tetapi data mentah tidak ada (klon baru, CI),
    target dibaca dari kolom ``target_sampel`` dan ``tersedia`` bernilai ``None``
    — tidak pernah dihitung ulang menjadi nol.
    """
    jumlah = hitung_ulasan_dalam_rentang(maps_dir, rentang)
    daftar = Path(daftar)
    ditetapkan = load_sample(daftar) if daftar.exists() else []
    if ditetapkan:
        terpilih = ditetapkan
    elif jumlah and daftar.exists():
        terpilih = pilih_sampel(load_active_restaurants(daftar), jumlah, n, maks_per_kategori)
    else:
        terpilih = []
    restoran = []
    for r in terpilih:
        tersedia = jumlah.get(r["kode"]) if jumlah else None
        tersimpan = (r.get("target_sampel") or "").strip()
        if tersimpan.isdigit():
            target: int | None = int(tersimpan)
        elif tersedia is not None:
            target = target_per_restoran(tersedia, batas)
        else:
            target = None
        restoran.append({"kode": r["kode"], "nama": r.get("nama", ""), "kota": r.get("kota", ""),
                         "kategori": r.get("kategori", ""), "tersedia": tersedia, "target": target})
    return {"n": n, "rentang": list(rentang), "maks_per_kategori": maks_per_kategori,
            "batas_target": batas, "ditetapkan": bool(ditetapkan), "restoran": restoran,
            "target_total": sum(r["target"] or 0 for r in restoran)}


def ambil_berstrata(frame, n: int, kolom: str, seed: int):  # noqa: ANN001, ANN201
    """Sampel acak berstrata proporsional (pembulatan sisa terbesar) menurut ``kolom``."""
    import pandas as pd

    n = min(int(n), len(frame))
    ukuran = frame[kolom].fillna("").value_counts().sort_index()
    kuota = ukuran * n / ukuran.sum()
    jatah = kuota.astype(int)
    sisa = n - int(jatah.sum())
    for kunci in (kuota - jatah).sort_values(ascending=False, kind="stable").index[:sisa]:
        jatah[kunci] += 1
    bagian = [frame[frame[kolom].fillna("") == kunci].sample(n=int(k), random_state=seed)
              for kunci, k in jatah.items() if k > 0]
    return pd.concat(bagian).sample(frac=1, random_state=seed).reset_index(drop=True)
