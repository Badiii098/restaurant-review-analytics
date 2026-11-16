#!/usr/bin/env python3
"""Uji kesesuaian peringkat prioritas sistem dengan urutan pakar (RM3).

Langkah:
1. Jalankan alur sekali (latih + klasifikasi).
2. Hitung peringkat lima aspek untuk setiap restoran dengan modul keputusan.
3. Bandingkan dengan urutan pakar pada ``data/reference/urutan_pakar.csv``
   (kolom: restoran, aspek, peringkat_pakar; 1 = paling mendesak).
   Nilai ``restoran`` harus sama dengan kolom ``restaurant`` pada data/raw/reviews.csv.
4. Tulis ρ per restoran, median, uji Wilcoxon, dan kesesuaian peringkat 1.

Contoh::

    python scripts/uji_pakar.py --pakar data/reference/urutan_pakar.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rra.analysis.expert import (  # noqa: E402
    spearman_per_restaurant,
    top1_agreement,
    uji_median_rho,
)
from rra.config import Config  # noqa: E402
from rra.pipeline import Pipeline  # noqa: E402


def baca_pakar(path: Path) -> dict[str, list[str]]:
    rows: dict[str, list[tuple[int, str]]] = defaultdict(list)
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            rows[row["restoran"].strip()].append(
                (int(row["peringkat_pakar"]), row["aspek"].strip().lower())
            )
    return {kode: [aspek for _, aspek in sorted(items)] for kode, items in rows.items()}


def peringkat_sistem(pipeline: Pipeline) -> dict[str, list[str]]:
    output = pipeline.run()
    reviews = pipeline.load_reviews()
    bersih = {item.review_id: item for item in output.clean_reviews}
    prediksi = {item.review_id: item for item in output.predictions}
    per_restoran: dict[str, list] = defaultdict(list)
    for review in reviews:
        if review.review_id in bersih and review.restaurant:
            per_restoran[review.restaurant].append(review)
    hasil = {}
    for nama, kelompok in per_restoran.items():
        ids = [r.review_id for r in kelompok]
        keputusan = pipeline.decision_module.run(
            kelompok, [prediksi[i] for i in ids if i in prediksi],
            clean_text={i: bersih[i].text_clean for i in ids},
            clauses={i: bersih[i].clauses for i in ids},
            model_name=output.model_name,
        )
        hasil[nama] = [p.aspect for p in keputusan.priorities]
    return hasil


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pakar", default="data/reference/urutan_pakar.csv")
    parser.add_argument("--out", default="reports/uji_pakar.json")
    parser.add_argument("--root", default=str(ROOT))
    args = parser.parse_args()

    root = Path(args.root).resolve()
    cfg = Config.load(root=root)
    pakar_path = Path(args.pakar) if Path(args.pakar).is_absolute() else root / args.pakar
    if not pakar_path.exists():
        print(f"Berkas urutan pakar belum ada: {pakar_path}\n"
              "Salin data/reference/urutan_pakar_template.csv lalu isi peringkat pakar.",
              file=sys.stderr)
        return 1

    sistem = peringkat_sistem(Pipeline(cfg))
    pakar = baca_pakar(pakar_path)
    rhos = spearman_per_restaurant(sistem, pakar)
    uji = uji_median_rho(rhos.values())
    laporan = {"rho_per_restoran": rhos, "uji_median": uji,
               "kesesuaian_peringkat_1": top1_agreement(sistem, pakar),
               "peringkat_sistem": sistem}

    target = Path(args.out) if Path(args.out).is_absolute() else root / args.out
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(laporan, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Restoran dinilai: {uji['n']} · median ρ = {uji['median']} · p = {uji['p']}")
    print("Keputusan:", "H0 ditolak" if uji["tolak_h0"] else "H0 tidak ditolak")
    print(f"Hasil ditulis: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
