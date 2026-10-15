#!/usr/bin/env python3
"""Buat dataset contoh yang dapat diulang.

Contoh::

    python scripts/make_sample_data.py --n 2000 --seed 42
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rra.io_layer.sample_data import generate_dataset, write_dataset  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=2000, help="Jumlah ulasan.")
    parser.add_argument("--seed", type=int, default=42, help="Benih pengacakan.")
    parser.add_argument("--root", default=str(ROOT), help="Direktori akar proyek.")
    args = parser.parse_args()

    dataset = generate_dataset(n_reviews=args.n, seed=args.seed)
    written = write_dataset(dataset, Path(args.root))

    print(f"{dataset.n_reviews} ulasan · {len(dataset.labels)} label aspek · benih {dataset.seed}")
    for label, path in written.items():
        print(f"  {label:14s} {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
