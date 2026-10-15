#!/usr/bin/env python3
"""Siapkan berkas kerja anotasi untuk dua pemberi label.

Menghasilkan dua berkas terpisah yang memuat **sebagian** ulasan yang sama
(bagian tumpang tindih) dan sisanya berbeda. Bagian tumpang tindih inilah
yang dipakai menghitung kesepakatan antar-pemberi label (Cohen's κ).

Contoh::

    python scripts/make_annotation_template.py --overlap 150
"""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd  # noqa: E402

from rra.config import Config  # noqa: E402

COLUMNS = ["review_id", "text", "aspect", "sentiment"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--overlap", type=int, default=150,
                        help="Jumlah ulasan yang dilabeli oleh KEDUA pemberi label.")
    parser.add_argument("--each", type=int, default=400,
                        help="Jumlah ulasan per pemberi label (termasuk overlap).")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--root", default=str(ROOT))
    args = parser.parse_args()

    root = Path(args.root).resolve()
    cfg = Config.load(root=root)
    reviews_path = cfg.path("paths.reviews_file")
    if not reviews_path.exists():
        print(f"Data ulasan belum ada: {reviews_path}", file=sys.stderr)
        return 1

    frame = pd.read_csv(reviews_path)
    total = len(frame)
    needed = min(total, min(args.each * 2 - args.overlap, total))
    rng = random.Random(args.seed)
    sampled = frame.sample(n=needed, random_state=args.seed).reset_index(drop=True)

    overlap_count = min(args.overlap, needed)
    overlap = sampled.iloc[:overlap_count]
    remaining = sampled.iloc[overlap_count:]

    target_each = max(0, args.each - overlap_count)
    first_extra = remaining.iloc[:target_each]
    second_extra = remaining.iloc[target_each:target_each * 2]

    out_dir = cfg.path("paths.reference")
    out_dir.mkdir(parents=True, exist_ok=True)

    written = {}
    for name, part in (("anotator_1", pd.concat([overlap, first_extra])),
                       ("anotator_2", pd.concat([overlap, second_extra]))):
        blank = pd.DataFrame({
            "review_id": part["review_id"].astype(str).values,
            "text": part["text"].astype(str).values,
            "aspect": "",
            "sentiment": "",
        })
        path = out_dir / f"{name}.csv"
        blank.to_csv(path, index=False)
        written[name] = (path, len(blank))

    print(f"Ulasan tersedia     : {total}")
    print(f"Ulasan tumpang tindih: {overlap_count} (dipakai menghitung Cohen's κ)")
    for name, (path, count) in written.items():
        print(f"{name:12s}: {count} baris → {path}")
    print()
    print("Petunjuk pengisian:")
    print("  aspect    : makanan | pelayanan | harga | suasana | fasilitas")
    print("  sentiment : positif | negatif | netral")
    print("  Satu ulasan boleh memakai beberapa baris (satu baris per aspek).")
    print("  Baris dengan aspect kosong akan diabaikan saat penggabungan.")
    print()
    print("Setelah selesai:")
    print("  python scripts/compute_kappa.py "
          f"--first {out_dir / 'anotator_1.csv'} --second {out_dir / 'anotator_2.csv'}")
    print("  python scripts/merge_labels.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
