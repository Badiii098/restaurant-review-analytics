#!/usr/bin/env python3
"""Ukur kinerja non-fungsional (KNF-01 dan KNF-02).

Mengukur waktu pelatihan, waktu analisis, dan waktu per ulasan selama
beberapa pengulangan, lalu menuliskannya sebagai JSON.

Contoh::

    python scripts/benchmark.py --repeat 5
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rra.config import Config  # noqa: E402
from rra.pipeline import Pipeline  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--model", default=None, choices=["svm", "nb"])
    parser.add_argument("--out", default="reports/benchmark.json")
    parser.add_argument("--root", default=str(ROOT))
    args = parser.parse_args()

    root = Path(args.root).resolve()
    cfg = Config.load(root=root)
    if args.model:
        cfg._data["model"]["name"] = args.model

    rows: list[dict[str, float]] = []
    n_reviews = 0
    print(f"Mengukur {args.repeat} pengulangan dengan komponen "
          f"'{cfg.get('model.name')}'…")
    for attempt in range(1, args.repeat + 1):
        started = time.perf_counter()
        output = Pipeline(cfg).run()
        wall = time.perf_counter() - started
        n_reviews = output.n_reviews
        rows.append({"ulangan": attempt, **output.timings, "total_dinding": round(wall, 4)})
        print(f"  {attempt}: {wall:.2f} s "
              f"(latih {output.timings['04_latih_model']:.2f} s · "
              f"klasifikasi {output.timings['05_klasifikasi']:.2f} s)")

    wall_values = [row["total_dinding"] for row in rows]
    train_values = [row["04_latih_model"] for row in rows]
    inference_values = [row["05_klasifikasi"] for row in rows]

    summary = {
        "komponen_model": str(cfg.get("model.name")),
        "n_ulasan": n_reviews,
        "n_pengulangan": args.repeat,
        "total_detik_rata_rata": round(statistics.mean(wall_values), 4),
        "total_detik_simpangan": round(
            statistics.stdev(wall_values) if len(wall_values) > 1 else 0.0, 4),
        "total_detik_maks": round(max(wall_values), 4),
        "latih_detik_rata_rata": round(statistics.mean(train_values), 4),
        "klasifikasi_detik_rata_rata": round(statistics.mean(inference_values), 4),
        "klasifikasi_ms_per_ulasan": round(
            1000.0 * statistics.mean(inference_values) / max(n_reviews, 1), 4),
    }

    print()
    for key, value in summary.items():
        print(f"  {key}: {value}")

    target = Path(args.out)
    if not target.is_absolute():
        target = root / target
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps({"ringkasan": summary, "perulangan": rows},
                   indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\nHasil ditulis: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
