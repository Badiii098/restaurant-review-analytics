#!/usr/bin/env python3
"""Hitung skor SUS (System Usability Scale) dari rekap jawaban.

Masukan: CSV dengan kolom ``responden`` dan ``q1`` … ``q10`` (skala 1–5).
Pernyataan bernomor **ganjil** bersifat positif, **genap** bersifat negatif.

Contoh::

    python scripts/hitung_sus.py --input data/sus_jawaban.csv --out reports/sus.json
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd  # noqa: E402

POSITIVE = (1, 3, 5, 7, 9)
NEGATIVE = (2, 4, 6, 8, 10)


def score_row(row: pd.Series) -> float:
    """Skor SUS satu responden (0–100)."""
    total = 0.0
    for index in POSITIVE:
        total += float(row[f"q{index}"]) - 1.0
    for index in NEGATIVE:
        total += 5.0 - float(row[f"q{index}"])
    return 2.5 * total


def interpret(value: float) -> tuple[str, str]:
    if value >= 80.3:
        return "sangat baik", "A"
    if value >= 68.0:
        return "baik", "B–C"
    if value >= 51.0:
        return "cukup", "D"
    return "kurang", "E–F"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="CSV rekap jawaban.")
    parser.add_argument("--out", default="reports/sus.json")
    parser.add_argument("--threshold", type=float, default=68.0,
                        help="Nilai pembanding untuk KNF-03.")
    args = parser.parse_args()

    source = Path(args.input).expanduser()
    if not source.exists():
        print(f"Berkas tidak ditemukan: {source}", file=sys.stderr)
        return 1

    frame = pd.read_csv(source)
    expected = {"responden", *(f"q{i}" for i in range(1, 11))}
    missing = expected - set(frame.columns)
    if missing:
        print(f"Kolom belum lengkap, kurang: {sorted(missing)}", file=sys.stderr)
        return 1

    answers = frame[[f"q{i}" for i in range(1, 11)]]
    out_of_range = ((answers < 1) | (answers > 5)).any(axis=None)
    if out_of_range:
        print("Ada jawaban di luar skala 1–5. Periksa kembali berkas masukan.",
              file=sys.stderr)
        return 1

    frame["sus"] = frame.apply(score_row, axis=1)
    values = frame["sus"].tolist()
    mean = statistics.mean(values)

    summary = {
        "n_responden": len(values),
        "sus_rata_rata": round(mean, 2),
        "sus_simpangan_baku": round(statistics.stdev(values) if len(values) > 1 else 0.0, 2),
        "sus_terendah": round(min(values), 2),
        "sus_tertinggi": round(max(values), 2),
        "tafsiran": interpret(mean)[0],
        "peringkat": interpret(mean)[1],
        "ambang_knf03": args.threshold,
        "knf03_terpenuhi": bool(mean >= args.threshold),
    }

    print(f"Responden        : {summary['n_responden']}")
    print(f"SUS rata-rata    : {summary['sus_rata_rata']} "
          f"± {summary['sus_simpangan_baku']}")
    print(f"Rentang          : {summary['sus_terendah']} – {summary['sus_tertinggi']}")
    print(f"Tafsiran         : {summary['tafsiran']} (peringkat {summary['peringkat']})")
    print(f"KNF-03 (≥ {args.threshold:g}) : "
          f"{'TERPENUHI' if summary['knf03_terpenuhi'] else 'BELUM TERPENUHI'}")
    print()
    print("Catatan pelaporan: SUS mengukur persepsi penerimaan pengguna, bukan")
    print("kebenaran keluaran sistem. Nyatakan hal ini pada Bab IV.")

    target = Path(args.out)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nHasil ditulis: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
