#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pembersihan dan rekap data ulasan hasil scraping.

Membaca seluruh data/raw/*.jsonl lalu menghasilkan:
  data/processed/reviews_all.csv        -> semua ulasan + kolom flag & normalisasi
  data/processed/reviews_clean.csv      -> hanya dalam rentang tahun & bukan noise
  data/processed/ringkasan_per_restoran.csv -> rekap per restoran (untuk BAB III/IV)
  data/processed/laporan_kualitas.json  -> metrik QA akuisisi data

Aturan penting: ulasan noise TIDAK dihapus pada reviews_all.csv, hanya diberi
flag, sehingga jumlah sebelum/sesudah penyaringan dapat dilaporkan di naskah.

  python scripts/scraping/preprocess_reviews.py --tahun-mulai 2021 --tahun-akhir 2026
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils_teks import is_noise, normalize_text  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "maps"
OUT = ROOT / "data" / "processed" / "scraping"

FIELDS = [
    "kode_restoran", "nama_tempat_maps", "kota", "review_id", "penulis", "rating",
    "tanggal", "tanggal_presisi", "tanggal_teks", "teks", "teks_normal",
    "respons_pemilik", "panjang_karakter", "jumlah_kata", "flag_noise", "alasan_noise",
    "duplikat", "dalam_rentang", "local_guide", "sumber_url", "diambil_pada",
]


def load_raw() -> tuple[list[dict], list[dict]]:
    rows, metas = [], []
    for path in sorted(RAW.glob("*.jsonl")):
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    for path in sorted(RAW.glob("*.meta.json")):
        metas.append(json.loads(path.read_text(encoding="utf-8")))
    return rows, metas


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tahun-mulai", type=int, default=2021)
    ap.add_argument("--tahun-akhir", type=int, default=2026)
    ap.add_argument("--min-karakter", type=int, default=15)
    ap.add_argument("--min-kata", type=int, default=3)
    args = ap.parse_args()

    rows, metas = load_raw()
    if not rows:
        raise SystemExit("Tidak ada data pada data/raw/maps/. Jalankan scripts/scraping/scrape_maps.py lebih dulu.")
    OUT.mkdir(parents=True, exist_ok=True)

    # 1) tandai duplikat (kombinasi restoran + penulis + teks normal + tanggal teks)
    seen: set[tuple] = set()
    dup = 0
    for r in rows:
        r["teks_normal"] = normalize_text(r.get("teks", ""))
        key = (r.get("kode_restoran"), r.get("penulis"), r["teks_normal"], r.get("tanggal_teks"))
        if r["teks_normal"] and key in seen:
            r["duplikat"] = True
            dup += 1
        else:
            r["duplikat"] = False
            if r["teks_normal"]:
                seen.add(key)

    # 2) flag noise & rentang tahun
    for r in rows:
        noise, reason = is_noise(r.get("teks", ""), args.min_karakter, args.min_kata)
        r["flag_noise"] = noise
        r["alasan_noise"] = reason
        tgl = r.get("tanggal") or ""
        r["dalam_rentang"] = bool(tgl) and f"{args.tahun_mulai}-01-01" <= tgl <= f"{args.tahun_akhir}-12-31"
        r["panjang_karakter"] = len(r.get("teks") or "")
        r["jumlah_kata"] = len((r.get("teks") or "").split())

    # 3) tulis CSV
    all_path = OUT / "reviews_all.csv"
    with all_path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in sorted(rows, key=lambda x: (x.get("kode_restoran") or "", x.get("tanggal") or "")):
            w.writerow(r)

    clean = [r for r in rows if r["dalam_rentang"] and not r["flag_noise"] and not r["duplikat"]]
    clean_path = OUT / "reviews_clean.csv"
    with clean_path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in sorted(clean, key=lambda x: (x.get("kode_restoran") or "", x.get("tanggal") or "")):
            w.writerow(r)

    # 4) rekap per restoran
    per = defaultdict(lambda: {"total": 0, "dalam_rentang": 0, "bersih": 0, "negatif": 0,
                               "positif": 0, "netral": 0, "tahun": Counter(), "rating_sum": 0.0,
                               "rating_n": 0, "presisi_exact": 0})
    for r in rows:
        k = r.get("kode_restoran") or "?"
        d = per[k]
        d["total"] += 1
        d["dalam_rentang"] += int(r["dalam_rentang"])
        if r["dalam_rentang"] and not r["flag_noise"] and not r["duplikat"]:
            d["bersih"] += 1
        rt = r.get("rating")
        if rt:
            d["rating_sum"] += float(rt)
            d["rating_n"] += 1
            if float(rt) <= 2:
                d["negatif"] += 1
            elif float(rt) == 3:
                d["netral"] += 1
            else:
                d["positif"] += 1
        if r.get("tanggal"):
            d["tahun"][r["tanggal"][:4]] += 1
        if r.get("tanggal_presisi") == "exact":
            d["presisi_exact"] += 1

    rekap_path = OUT / "ringkasan_per_restoran.csv"
    years = [str(y) for y in range(args.tahun_mulai, args.tahun_akhir + 1)]
    with rekap_path.open("w", encoding="utf-8", newline="") as fh:
        cols = ["kode_restoran", "nama_tempat_maps", "kota", "total_ulasan", "dalam_rentang",
                "bersih", "negatif", "netral", "positif", "pct_negatif", "rating_rata2",
                "presisi_tanggal_exact"] + [f"n_{y}" for y in years]
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for k in sorted(per):
            d = per[k]
            nama = next((r.get("nama_tempat_maps") for r in rows if r.get("kode_restoran") == k), "")
            kota = next((r.get("kota") for r in rows if r.get("kode_restoran") == k), "")
            w.writerow({
                "kode_restoran": k,
                "nama_tempat_maps": nama,
                "kota": kota,
                "total_ulasan": d["total"],
                "dalam_rentang": d["dalam_rentang"],
                "bersih": d["bersih"],
                "negatif": d["negatif"],
                "netral": d["netral"],
                "positif": d["positif"],
                "pct_negatif": round(100 * d["negatif"] / d["total"], 2) if d["total"] else 0,
                "rating_rata2": round(d["rating_sum"] / d["rating_n"], 2) if d["rating_n"] else "",
                "presisi_tanggal_exact": d["presisi_exact"],
                **{f"n_{y}": d["tahun"].get(y, 0) for y in years},
            })

    # 5) laporan kualitas
    total = len(rows)
    noise = sum(1 for r in rows if r["flag_noise"])
    laporan = {
        "jumlah_restoran_terbaca": len({r.get("kode_restoran") for r in rows}),
        "total_ulasan_mentah": total,
        "duplikat": dup,
        "noise": noise,
        "pct_noise": round(100 * noise / total, 2) if total else 0,
        "dalam_rentang": sum(1 for r in rows if r["dalam_rentang"]),
        "bersih_final": len(clean),
        "tanggal_exact": sum(1 for r in rows if r.get("tanggal_presisi") == "exact"),
        "tanggal_relative": sum(1 for r in rows if r.get("tanggal_presisi") == "relative"),
        "tanggal_tidak_terbaca": sum(1 for r in rows if r.get("tanggal_presisi") == "none"),
        "sebaran_tahun": dict(Counter(r["tanggal"][:4] for r in rows if r.get("tanggal"))),
        "meta_pengambilan": metas,
        "rentang": [args.tahun_mulai, args.tahun_akhir],
    }
    (OUT / "laporan_kualitas.json").write_text(json.dumps(laporan, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"ulasan mentah : {total}")
    print(f"duplikat      : {dup}")
    print(f"noise         : {noise} ({laporan['pct_noise']}%)")
    print(f"dalam rentang : {laporan['dalam_rentang']}")
    print(f"bersih final  : {len(clean)}")
    print(f"presisi tanggal: exact={laporan['tanggal_exact']} relative={laporan['tanggal_relative']} "
          f"none={laporan['tanggal_tidak_terbaca']}")
    print("sebaran tahun :", laporan["sebaran_tahun"])
    print(f"output        : {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
