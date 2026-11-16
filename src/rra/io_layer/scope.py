"""Cakupan sampel penelitian: restoran aktif dan kekurangan ulasan.

Sampel penelitian adalah 18 restoran di Jabodetabek dengan target 280 ulasan
per restoran (total 5.040, di atas ambang 5.000). Restoran dengan kolom
``aktif`` bernilai 0 tetap tercatat di ``config/restaurants.csv`` agar alasan
pengeluarannya dapat ditelusuri, tetapi tidak ikut dianalisis.
"""

from __future__ import annotations

import csv
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
