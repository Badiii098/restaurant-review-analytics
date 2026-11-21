#!/usr/bin/env python3
"""Hitung kesepakatan antar-pemberi label (Cohen's κ).

Nilai κ menyatakan seberapa jauh kesepakatan dua pemberi label melampaui
kesepakatan yang terjadi karena kebetulan. Nilai ini **wajib** dilaporkan
pada Bab IV: tanpa κ, mutu data berlabel tidak dapat dipertanggungjawabkan,
sehingga seluruh angka kinerja model kehilangan pijakan.

Tafsiran yang lazim dipakai (Landis & Koch, 1977):

    0,81 – 1,00  sangat kuat
    0,61 – 0,80  kuat
    0,41 – 0,60  sedang
    0,21 – 0,40  cukup
    0,00 – 0,20  lemah

Contoh::

    python scripts/compute_kappa.py \
        --first data/reference/anotator_1.csv \
        --second data/reference/anotator_2.csv \
        --out reports/kappa.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rra.analysis.agreement import cohen_kappa, compare, interpret  # noqa: E402,F401


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--first", required=True, help="Berkas anotator pertama.")
    parser.add_argument("--second", required=True, help="Berkas anotator kedua.")
    parser.add_argument("--out", default=None, help="Berkas JSON keluaran.")
    args = parser.parse_args()

    first, second = Path(args.first), Path(args.second)
    for path in (first, second):
        if not path.exists():
            print(f"Berkas tidak ditemukan: {path}", file=sys.stderr)
            return 1

    results = {
        "aspek": compare(first, second, "aspek"),
        "sentimen": compare(first, second, "sentimen"),
    }

    print("Kesepakatan antar-pemberi label (Cohen's κ)")
    print("=" * 62)
    for level, result in results.items():
        print(f"{level.capitalize():10s} n={result['n']:5d}  "
              f"kesepakatan={result.get('kesepakatan_teramati', 0):.4f}  "
              f"κ={result['kappa']:.4f}  ({result['tafsiran']})")
    print()
    print("Laporkan kedua nilai κ ini pada Bab IV sebagai bukti mutu data berlabel.")

    if args.out:
        target = Path(args.out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Hasil ditulis: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
