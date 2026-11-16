#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rekap hasil scraping per restoran (tabel siap lampirkan BAB III/IV).

Membaca  : config/restaurants.csv  +  data/raw/maps/*.jsonl
Menulis  : data/processed/scraping/rekap_restoran.csv
           data/processed/scraping/reviews_mentah.csv  (gabungan semua ulasan)

Pemakaian
    .venv/bin/python scripts/scraping/rekap_restoran.py
    .venv/bin/python scripts/scraping/rekap_restoran.py --dir logs/scraping/contoh_anonim \
        --out-suffix _contoh
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config" / "restaurants.csv"
RAW_DIR = ROOT / "data" / "raw" / "maps"
OUT_DIR = ROOT / "data" / "processed" / "scraping"

KOLOM_ULASAN = ["review_id", "nama_restoran", "kota", "rating", "tanggal",
                "tanggal_presisi", "teks", "respons_pemilik", "penulis",
                "local_guide", "sumber_url", "diambil_pada"]


def baca_config() -> list[dict]:
    with CONFIG.open(encoding="utf-8-sig") as fh:
        return [r for r in csv.DictReader(fh)
                if (r.get("aktif", "1").strip() not in ("0", "false", "False"))]


def baca_jsonl(folder: Path) -> list[dict]:
    baris: list[dict] = []
    for f in sorted(folder.glob("*.jsonl")):
        with f.open(encoding="utf-8") as fh:
            for ln in fh:
                ln = ln.strip()
                if ln:
                    baris.append(json.loads(ln))
    return baris


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=str(RAW_DIR))
    ap.add_argument("--out-suffix", default="")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    config = baca_config()
    ulasan = baca_jsonl(Path(args.dir))

    per_kode: dict[str, list[dict]] = defaultdict(list)
    for u in ulasan:
        per_kode[u.get("kode_restoran") or "?"].append(u)

    rekap = []
    for row in config:
        kode = row["kode"]
        data = per_kode.get(kode, [])
        target = int(row.get("target_ulasan") or 400)
        tanggal = sorted(u["tanggal"] for u in data if u.get("tanggal"))
        rating = [u["rating"] for u in data if isinstance(u.get("rating"), (int, float))]
        rekap.append({
            "kode": kode,
            "nama_restoran": row["nama"],
            "kota": row.get("kota", ""),
            "kategori": row.get("kategori", ""),
            "target_ulasan": target,
            "terkumpul": len(data),
            "persen_target": f"{(len(data) / target * 100):.1f}" if target else "0.0",
            "status": ("lengkap" if len(data) >= target else
                       ("sebagian" if data else "belum_diambil")),
            "tanggal_terawal": tanggal[0] if tanggal else "",
            "tanggal_terbaru": tanggal[-1] if tanggal else "",
            "rating_rata2": f"{sum(rating) / len(rating):.2f}" if rating else "",
            "teks_kosong": sum(1 for u in data if not (u.get("teks") or "").strip()),
        })

    out_rekap = OUT_DIR / f"rekap_restoran{args.out_suffix}.csv"
    with out_rekap.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rekap[0].keys()))
        w.writeheader()
        w.writerows(rekap)
        w.writerow({
            "kode": "TOTAL", "nama_restoran": f"{len(rekap)} restoran",
            "kota": "", "kategori": "",
            "target_ulasan": sum(r["target_ulasan"] for r in rekap),
            "terkumpul": sum(r["terkumpul"] for r in rekap),
            "persen_target": "",
            "status": "", "tanggal_terawal": "", "tanggal_terbaru": "",
            "rating_rata2": "", "teks_kosong": sum(r["teks_kosong"] for r in rekap),
        })

    # selaraskan nama kolom JSONL -> kolom CSV metodologi
    ulasan_csv = []
    for u in ulasan:
        baris = dict(u)
        baris["nama_restoran"] = u.get("nama_restoran_config") or u.get("nama_tempat_maps")
        ulasan_csv.append(baris)

    out_ulasan = OUT_DIR / f"reviews_mentah{args.out_suffix}.csv"
    with out_ulasan.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=KOLOM_ULASAN, extrasaction="ignore")
        w.writeheader()
        w.writerows(ulasan_csv)

    print(f"{'kode':5} {'restoran':32} {'kota':12} {'target':>6} {'dapat':>6}  status")
    for r in rekap:
        print(f"{r['kode']:5} {r['nama_restoran'][:32]:32} {r['kota'][:12]:12} "
              f"{r['target_ulasan']:6} {r['terkumpul']:6}  {r['status']}")
    total = sum(r["terkumpul"] for r in rekap)
    target = sum(r["target_ulasan"] for r in rekap)
    print(f"\nTOTAL: {total} ulasan terkumpul dari target {target} "
          f"({len(rekap)} restoran)")
    print(f"sumber data : {Path(args.dir)}")
    print(f"rekap       : {out_rekap}")
    print(f"ulasan      : {out_ulasan}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
