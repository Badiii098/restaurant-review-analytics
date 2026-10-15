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

import pandas as pd  # noqa: E402

from rra.contracts import ASPECTS  # noqa: E402


def interpret(value: float) -> str:
    if value >= 0.81:
        return "sangat kuat"
    if value >= 0.61:
        return "kuat"
    if value >= 0.41:
        return "sedang"
    if value >= 0.21:
        return "cukup"
    return "lemah"


def cohen_kappa(first: pd.Series, second: pd.Series) -> float:
    """Hitung κ tanpa pustaka luar agar rumusnya dapat diperiksa langsung.

    κ = (Po - Pe) / (1 - Pe)

    dengan Po adalah kesepakatan yang teramati dan Pe adalah kesepakatan
    yang diharapkan terjadi karena kebetulan semata.
    """
    n = len(first)
    if n == 0:
        return 0.0
    labels = sorted(set(first) | set(second))
    observed = float((first.values == second.values).sum()) / n

    expected = 0.0
    for label in labels:
        p_first = float((first.values == label).sum()) / n
        p_second = float((second.values == label).sum()) / n
        expected += p_first * p_second

    if expected >= 1.0:
        # Seluruh pengamatan sepakat pada satu nilai yang sama.
        return 1.0 if observed == 1.0 else 0.0
    return (observed - expected) / (1.0 - expected)


def compare(first_path: Path, second_path: Path, level: str) -> dict:
    """Bandingkan penilaian dua pemberi label pada satu tingkat.

    Dua tingkat dibandingkan dengan cara yang **berbeda**, karena keduanya
    mengukur hal yang berbeda:

    * **Aspek** — diukur sebagai penandaan (ada/tidak ada) untuk setiap
      pasangan ``(review_id, aspect)``. Setiap aspek dari seluruh taksonomi
      menjadi satu pengamatan, termasuk aspek yang tidak disebut. Bila
      perbandingan dilakukan hanya atas baris yang tertulis, penggabungan
      pada ``review_id`` akan memasangkan aspek yang berbeda-beda (ulasan
      dengan tiga aspek menghasilkan perkalian baris), dan nilai κ menjadi
      keliru rendah tanpa alasan yang nyata.
    * **Sentimen** — diukur hanya atas pasangan ``(review_id, aspect)`` yang
      **keduanya** beri label, sebab sentimen hanya bermakna bila aspeknya
      sama.
    """
    first = pd.read_csv(first_path, dtype=str).fillna("")
    second = pd.read_csv(second_path, dtype=str).fillna("")

    for frame, path in ((first, first_path), (second, second_path)):
        missing = {"review_id", "aspect", "sentiment"} - set(frame.columns)
        if missing:
            raise ValueError(f"Kolom {sorted(missing)} tidak ada pada {path}")

    left = first[["review_id", "aspect", "sentiment"]].copy()
    right = second[["review_id", "aspect", "sentiment"]].copy()
    for frame in (left, right):
        frame["aspect"] = frame["aspect"].str.strip().str.lower()
        frame["sentiment"] = frame["sentiment"].str.strip().str.lower()
        frame.drop(frame[frame["aspect"].eq("")].index, inplace=True)

    if level == "aspek":
        left_keys = set(zip(left["review_id"], left["aspect"]))
        right_keys = set(zip(right["review_id"], right["aspect"]))
        # Hanya ulasan yang **keduanya** nilai yang dibandingkan. Bila
        # seluruh ulasan digabung, ulasan yang hanya dilihat satu pemberi
        # label akan selalu tampak tidak sepakat, dan κ jatuh bukan karena
        # penilaiannya berbeda melainkan karena kumpulan ulasannya berbeda.
        shared = sorted({key[0] for key in left_keys} & {key[0] for key in right_keys})
        aspects = sorted(ASPECTS)
        universe = [(rid, aspect) for rid in shared for aspect in aspects]

        first_series = pd.Series(
            ["ada" if key in left_keys else "tidak ada" for key in universe], dtype=str
        )
        second_series = pd.Series(
            ["ada" if key in right_keys else "tidak ada" for key in universe], dtype=str
        )
        kappa = cohen_kappa(first_series, second_series)
        agreement = float((first_series.values == second_series.values).mean())
        return {
            "tingkat": level,
            "n": int(len(universe)),
            "satuan": "pasangan (ulasan, aspek) dengan seluruh taksonomi",
            "kesepakatan_teramati": round(agreement, 4),
            "kappa": round(kappa, 4),
            "tafsiran": interpret(kappa),
            "jumlah_ditandai_1": int(len(left_keys)),
            "jumlah_ditandai_2": int(len(right_keys)),
        }

    merged = left.merge(right, on=["review_id", "aspect"], suffixes=("_1", "_2"))
    merged = merged[merged["sentiment_1"].ne("") & merged["sentiment_2"].ne("")]
    if merged.empty:
        return {"tingkat": level, "n": 0, "satuan": "pasangan (ulasan, aspek)",
                "kappa": 0.0, "tafsiran": "tidak dapat dihitung"}

    kappa = cohen_kappa(merged["sentiment_1"], merged["sentiment_2"])
    agreement = float(
        (merged["sentiment_1"].values == merged["sentiment_2"].values).mean()
    )
    return {
        "tingkat": level,
        "n": int(len(merged)),
        "satuan": "pasangan (ulasan, aspek) yang dilabeli keduanya",
        "kesepakatan_teramati": round(agreement, 4),
        "kappa": round(kappa, 4),
        "tafsiran": interpret(kappa),
        "sebaran_label_1": merged["sentiment_1"].value_counts().to_dict(),
        "sebaran_label_2": merged["sentiment_2"].value_counts().to_dict(),
    }


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
