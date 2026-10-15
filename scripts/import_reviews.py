#!/usr/bin/env python3
"""Ubah data ulasan hasil pengumpulan menjadi format yang dipakai sistem.

Sistem menerima berkas CSV atau JSONL dengan kolom::

    review_id, text, rating, date, restaurant

Berkas keluaran hasil pengumpulan sering kali belum memuat ``review_id``
atau memakai nama kolom yang berbeda. Skrip ini menyeragamkannya,
membuang baris kosong, dan mencatat ringkasan mutunya.

Contoh::

    python scripts/import_reviews.py \
        --input ~/unduhan/maps_export.csv \
        --id-column reviewId --text-column reviewText --rating-column stars

**Catatan penting mengenai pengumpulan data.** Pengambilan data secara
otomatis dari Google Maps perlu memperhatikan Syarat Layanan penyedia.
Cara yang paling aman adalah mengekspor data melalui fitur ekspor resmi
(mis. Google Takeout untuk lokasi Anda sendiri) atau menyalin ulasan satu
per satu secara manual dengan tetap mencantumkan sumbernya. Skrip ini
tidak melakukan pengambilan data; ia hanya menyeragamkan berkas yang
sudah Anda peroleh.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd  # noqa: E402

from rra.config import Config  # noqa: E402
from rra.io_layer.loader import ReviewLoader, describe_dataset  # noqa: E402


def make_id(text: str, index: int) -> str:
    """Bentuk identitas ulasan dari isi teksnya, agar tetap sama antar-jalan.

    Memakai indeks biasa akan menghasilkan identitas yang berbeda setiap
    kali data diimpor ulang dengan urutan yang berbeda, sehingga rujukan
    pada laporan menjadi tidak sahih. Sidik jari isi mengatasi hal itu.
    """
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]
    return f"GM{digest}"


def load_any(path: Path) -> pd.DataFrame:
    if path.suffix.lower() in {".jsonl", ".ndjson"}:
        return pd.read_json(path, lines=True)
    return pd.read_csv(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Berkas masukan (CSV/JSONL).")
    parser.add_argument("--output", default=None,
                        help="Berkas keluaran (bawaan: data/raw/reviews.csv).")
    parser.add_argument("--text-column", default="text")
    parser.add_argument("--id-column", default=None)
    parser.add_argument("--rating-column", default=None)
    parser.add_argument("--date-column", default=None)
    parser.add_argument("--restaurant-column", default=None)
    parser.add_argument("--root", default=str(ROOT))
    args = parser.parse_args()

    root = Path(args.root).resolve()
    cfg = Config.load(root=root)
    source = Path(args.input).expanduser()
    if not source.exists():
        print(f"Berkas masukan tidak ditemukan: {source}", file=sys.stderr)
        return 1

    frame = load_any(source)
    if args.text_column not in frame.columns:
        print(f"Kolom teks '{args.text_column}' tidak ada. "
              f"Kolom tersedia: {list(frame.columns)}", file=sys.stderr)
        return 1

    text = frame[args.text_column].astype(str).str.strip()
    keep = text.ne("") & text.str.lower().ne("nan")
    frame, text = frame[keep], text[keep]

    if args.id_column and args.id_column in frame.columns:
        review_id = frame[args.id_column].astype(str)
    else:
        review_id = pd.Series(
            [make_id(value, index) for index, value in enumerate(text)], dtype=str
        )

    # Buang duplikat berdasarkan isi ulasan — ulasan kembar akan membuat
    # frekuensi frasa keluhan terhitung berlebihan.
    result = pd.DataFrame({
        "review_id": review_id,
        "text": text,
        "rating": frame[args.rating_column] if args.rating_column in frame.columns else None,
        "date": frame[args.date_column] if args.date_column in frame.columns else None,
        "restaurant": (frame[args.restaurant_column]
                       if args.restaurant_column in frame.columns else None),
    })
    before = len(result)
    result = result.drop_duplicates(subset=["text"]).reset_index(drop=True)

    reviews = ReviewLoader.from_frame(result)
    target = Path(args.output) if args.output else cfg.path("paths.reviews_file")
    target.parent.mkdir(parents=True, exist_ok=True)
    ReviewLoader.save_csv(reviews, target)

    summary = describe_dataset(reviews, label="data_import")
    print(f"Masukan   : {source}")
    print(f"Keluaran  : {target}")
    print(f"Baris     : {before} → {len(result)} (duplikat dibuang)")
    for key in ("total", "jumlah_rating", "rating_rata_rata", "panjang_rata_rata"):
        if key in summary:
            print(f"  {key}: {summary[key]}")
    print()
    print("Langkah berikutnya: beri label aspek & sentimen pada "
          f"{cfg.path('paths.reference') / 'labels.csv'} — lihat docs/ANOTASI.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
