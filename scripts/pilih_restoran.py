#!/usr/bin/env python3
"""Pilih delapan restoran sampel secara purposive dari kandidat aktif.

Kriteria dibaca dari ``config/default.yaml`` (blok ``sampling``):

1. kandidat = restoran ``aktif = 1`` di ``config/restaurants.csv``;
2. urut menurun menurut jumlah ulasan dalam ``rentang_tahun``
   (dihitung dari ``data/raw/maps/<kode>_hasil.jsonl``);
3. ambil berurutan, paling banyak ``maks_per_kategori`` per kategori,
   sampai ``n_restoran``;
4. target per restoran = min(ulasan tersedia dalam rentang, ``batas_target``).

Tanpa ``--tulis`` hanya mencetak hasil. Dengan ``--tulis`` kolom ``sampel``
dan ``target_sampel`` diisi pada ``config/restaurants.csv``.

Contoh::

    python scripts/pilih_restoran.py
    python scripts/pilih_restoran.py --tulis
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rra.config import Config  # noqa: E402
from rra.io_layer.scope import (  # noqa: E402
    hitung_ulasan_dalam_rentang,
    load_active_restaurants,
    pilih_sampel,
    target_per_restoran,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--tulis", action="store_true", help="Tulis hasil ke restaurants.csv.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    cfg = Config.load(root=root)
    daftar = root / "config" / "restaurants.csv"
    rentang = tuple(int(t) for t in cfg.get("sampling.rentang_tahun", [2021, 2026]))
    n = int(cfg.get("sampling.n_restoran", 8))
    batas = int(cfg.get("sampling.batas_target", 625))
    jumlah = hitung_ulasan_dalam_rentang(root / "data" / "raw" / "maps", rentang)
    if not jumlah:
        print("Data mentah belum ada di data/raw/maps; pemilihan sampel menunggu data.",
              file=sys.stderr)
        return 1

    kandidat = load_active_restaurants(daftar)
    terpilih = pilih_sampel(kandidat, jumlah, n=n,
                            maks_per_kategori=int(cfg.get("sampling.maks_per_kategori", 2)))
    kode_terpilih = {r["kode"] for r in terpilih}

    print(f"Sampel purposive: {len(terpilih)} dari {len(kandidat)} kandidat "
          f"(rentang {rentang[0]}–{rentang[1]})")
    total = 0
    for urut, row in enumerate(terpilih, start=1):
        target = target_per_restoran(jumlah.get(row["kode"], 0), batas)
        total += target
        print(f"  {urut}. {row['kode']}  {row.get('nama', ''):40s} {row.get('kategori', ''):22s} "
              f"tersedia {jumlah.get(row['kode'], 0):5d}  target {target}")
    print(f"Target total: {total}")

    if args.tulis:
        with daftar.open(encoding="utf-8", newline="") as handle:
            pembaca = csv.DictReader(handle)
            kolom = list(pembaca.fieldnames or [])
            rows = list(pembaca)
        for nama in ("sampel", "target_sampel"):
            if nama not in kolom:
                kolom.append(nama)
        for row in rows:
            dipilih = row["kode"] in kode_terpilih
            row["sampel"] = "1" if dipilih else "0"
            row["target_sampel"] = (str(target_per_restoran(jumlah.get(row["kode"], 0), batas))
                                    if dipilih else "")
        with daftar.open("w", encoding="utf-8", newline="") as handle:
            penulis = csv.DictWriter(handle, fieldnames=kolom)
            penulis.writeheader()
            penulis.writerows(rows)
        print(f"Ditulis: {daftar}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
