#!/usr/bin/env python3
"""Jalankan alur end-to-end dan tulis seluruh laporan.

Contoh::

    python scripts/run_pipeline.py
    python scripts/run_pipeline.py --model nb
    python scripts/run_pipeline.py --override config/model_nb.yaml
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rra.config import Config  # noqa: E402
from rra.decision.severity import severity_map  # noqa: E402
from rra.pipeline import Pipeline, PipelineError  # noqa: E402
from rra.report.report import ReportWriter, coverage_frame  # noqa: E402
from rra.storage.repository import ResultRepository  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default=None, choices=["svm", "nb"],
                        help="Komponen model yang dipakai.")
    parser.add_argument("--override", default=None, help="Berkas konfigurasi varian.")
    parser.add_argument("--root", default=str(ROOT), help="Direktori akar proyek.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    cfg = Config.load(root=root, override=args.override)
    if args.model:
        cfg._data["model"]["name"] = args.model

    try:
        output = Pipeline(cfg).run()
    except PipelineError as error:
        print(error, file=sys.stderr)
        return 1

    decision = output.decision
    assert decision is not None
    reviews = Pipeline(cfg).load_reviews()

    print(f"Komponen model : {output.model_name}")
    print(f"Ulasan         : {output.n_reviews}")
    print("\nPeringkat prioritas perbaikan layanan")
    print("-" * 78)
    for item in decision.priorities:
        print(f"  {item.rank}. {item.label:<12} {item.priority:.4f}  "
              f"(volume {item.volume:.3f} · keparahan {item.severity:.3f} · "
              f"keragaman {item.diversity:.3f})")

    print("\nFrasa keluhan dominan")
    print("-" * 78)
    for aspect, items in decision.phrases.items():
        daftar = ", ".join(f"{p.phrase} ({p.frequency})" for p in items[:5])
        print(f"  {aspect:<12} {daftar}")

    repository = ResultRepository(cfg.path("paths.db_path"))
    run_id = repository.save_run(
        model_name=output.model_name,
        decision=decision,
        severities=severity_map(reviews),
        reviews=reviews,
        timings=output.timings,
        config=cfg.as_dict(),
    )
    repository.save_predictions(run_id, output.predictions)
    print(f"\nBasis data : {cfg.path('paths.db_path')} (run_id={run_id})")

    writer = ReportWriter(cfg.path("paths.reports"))
    written = writer.write_all(
        output=output,
        extra_frames={"cakupan_aspek": coverage_frame(reviews, decision)},
        summary={"model": output.model_name, "n_reviews": output.n_reviews},
    )
    print(f"Laporan    : {cfg.path('paths.reports')}")
    for label, path in written.items():
        print(f"  {label:18s} {path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
