"""Konsolidasi berkas scraping per restoran.

Masalah yang diselesaikan: satu restoran pernah tersimpan di beberapa berkas
(`r05_hasil.jsonl`, `r05_ayam-goreng-fatmawati.jsonl`, ...) sehingga jumlah
ulasan terhitung dobel.

Aturan:
  * gabungkan semua `data/raw/maps/<kode>_*.jsonl`
  * deduplikasi: `review_id`, lalu (teks_normal, penulis, tanggal)
  * urutkan tanggal terbaru -> terlama (sesuai sortir "Terbaru" di Maps)
  * simpan maksimal `--maks` baris (default 400) ke `<kode>_hasil.jsonl`
  * berkas sumber lain dipindahkan ke `data/raw/maps/_arsip_lama/`

Contoh:
    .venv/bin/python scripts/scraping/konsolidasi_data.py --maks 400
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw" / "maps"
ARSIP = RAW_DIR / "_arsip_lama"


def baca(berkas: Path) -> list[dict]:
    baris = []
    with berkas.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    baris.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return baris


def kunci_unik(b: dict) -> tuple:
    rid = b.get("review_id")
    if rid:
        return ("id", rid)
    return (
        "isi",
        (b.get("teks_normal") or "").strip().lower(),
        (b.get("penulis") or "").strip().lower(),
        b.get("tanggal") or b.get("tanggal_teks") or "",
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--maks", type=int, default=400, help="batas baris per restoran")
    ap.add_argument("--kering", action="store_true", help="hanya laporkan, tidak menulis")
    args = ap.parse_args()

    kode_semua = sorted({p.name.split("_")[0] for p in RAW_DIR.glob("r*_*.jsonl")})
    ARSIP.mkdir(parents=True, exist_ok=True)
    total = 0

    for kode in kode_semua:
        berkas = sorted(RAW_DIR.glob(f"{kode}_*.jsonl"))
        gabung: dict[tuple, dict] = {}
        n_baris = 0
        for b in berkas:
            isi = baca(b)
            n_baris += len(isi)
            for rec in isi:
                gabung.setdefault(kunci_unik(rec), rec)

        unik = list(gabung.values())
        unik.sort(key=lambda r: (r.get("tanggal") or "", r.get("diambil_pada") or ""), reverse=True)
        dipakai = unik[: args.maks]
        for i, rec in enumerate(dipakai, 1):
            rec["peringkat_ke"] = i

        kanonik = RAW_DIR / f"{kode}_hasil.jsonl"
        if not args.kering:
            with kanonik.open("w", encoding="utf-8") as fh:
                for rec in dipakai:
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            for b in berkas:
                if b.name != kanonik.name:
                    tujuan = ARSIP / b.name
                    if tujuan.exists():
                        tujuan.unlink()
                    shutil.move(str(b), str(tujuan))

        total += len(dipakai)
        print(f"{kode}: {len(unik):4d} unik dari {n_baris:4d} baris "
              f"-> disimpan {len(dipakai):3d}  ({kanonik.name})")

    print(f"\nTOTAL tersimpan: {total} ulasan pada {len(kode_semua)} restoran")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
