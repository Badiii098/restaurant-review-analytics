#!/usr/bin/env python3
"""Gabungkan berkas anotasi menjadi data berlabel yang dipakai pelatihan.

Aturan penggabungan:

* Baris dengan ``aspect`` kosong diabaikan.
* Bila kedua pemberi label menilai ulasan yang sama, yang dipakai adalah
  penilaian pemberi label pertama; perbedaan tetap tercatat pada berkas
  ``pertentangan.csv`` agar dapat dibahas pada Bab IV.
* Bila hanya satu pemberi label menilai, penilaian itu yang dipakai.

Contoh::

    python scripts/merge_labels.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd  # noqa: E402

from rra.config import Config  # noqa: E402
from rra.contracts import ASPECTS, SENTIMENTS  # noqa: E402


def read_annotations(path: Path, annotator: str) -> pd.DataFrame:
    frame = pd.read_csv(path, dtype=str).fillna("")
    for column in ("review_id", "text", "aspect", "sentiment"):
        if column not in frame.columns:
            raise ValueError(f"Kolom '{column}' tidak ada pada {path}")
    frame = frame[frame["aspect"].str.strip().ne("")]
    frame["aspect"] = frame["aspect"].str.strip().str.lower()
    frame["sentiment"] = frame["sentiment"].str.strip().str.lower()
    unknown = frame[~frame["aspect"].isin(ASPECTS)]
    if not unknown.empty:
        raise ValueError(
            f"Aspek tidak dikenal pada {path}: {sorted(set(unknown['aspect']))}. "
            f"Pilihan: {list(ASPECTS)}"
        )
    bad = frame[~frame["sentiment"].isin(SENTIMENTS)]
    if not bad.empty:
        raise ValueError(
            f"Sentimen tidak dikenal pada {path}: {sorted(set(bad['sentiment']))}. "
            f"Pilihan: {list(SENTIMENTS)}"
        )
    frame["annotator"] = annotator
    return frame


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(ROOT))
    args = parser.parse_args()

    root = Path(args.root).resolve()
    cfg = Config.load(root=root)
    reference = cfg.path("paths.reference")

    sources = [p for p in (reference / "anotator_1.csv", reference / "anotator_2.csv")
               if p.exists()]
    if not sources:
        print(f"Tidak ada berkas anotasi pada {reference}. "
              "Jalankan scripts/make_annotation_template.py lebih dahulu.",
              file=sys.stderr)
        return 1

    frames = [read_annotations(path, path.stem) for path in sources]
    combined = pd.concat(frames, ignore_index=True)

    # Perbedaan antar-pemberi label dicatat, tidak dibuang diam-diam.
    pivot = combined.pivot_table(
        index=["review_id", "aspect"], columns="annotator",
        values="sentiment", aggfunc="first",
    ).reset_index()
    if {"anotator_1", "anotator_2"} <= set(pivot.columns):
        disagreement = pivot[
            pivot["anotator_1"].notna() & pivot["anotator_2"].notna()
            & (pivot["anotator_1"] != pivot["anotator_2"])
        ]
        if not disagreement.empty:
            path = reference / "pertentangan.csv"
            disagreement.to_csv(path, index=False)
            print(f"Pertentangan dicatat: {len(disagreement)} baris → {path}")

    # Penilaian yang dipakai: anotator_1 bila ada, selain itu anotator_2.
    if "annotator" in combined.columns:
        combined["prioritas"] = combined["annotator"].map(
            {"anotator_1": 0, "anotator_2": 1}
        ).fillna(2)
        combined = combined.sort_values("prioritas")

    merged = (
        combined.drop_duplicates(subset=["review_id", "aspect"], keep="first")
        [["review_id", "text", "aspect", "sentiment"]]
        .reset_index(drop=True)
    )

    target = reference / "labels.csv"
    merged.to_csv(target, index=False)
    print(f"Data berlabel  : {target}")
    print(f"Baris label    : {len(merged)} (dari {combined['review_id'].nunique()} ulasan)")
    print(f"Aspek          : {sorted(set(merged['aspect']))}")
    print(f"Sentimen       : {sorted(set(merged['sentiment']))}")
    print()
    print("Langkah berikutnya: python -m rra.cli run")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
