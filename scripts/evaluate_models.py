#!/usr/bin/env python3
"""Evaluasi kinerja komponen model: validasi silang dan Precision@K.

Menghasilkan berkas JSON yang menjadi sumber angka pada Bab IV, termasuk
rincian per lipatan yang menjadi bahan pengujian Hipotesis 1.

Contoh::

    python scripts/evaluate_models.py --folds 10
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rra.config import Config  # noqa: E402
from rra.evaluate import cross_validate, evaluate_phrase_quality  # noqa: E402
from rra.models.registry import build_model  # noqa: E402
from rra.pipeline import Pipeline  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folds", type=int, default=10)
    parser.add_argument("--out", default="reports/evaluasi.json")
    parser.add_argument("--root", default=str(ROOT))
    args = parser.parse_args()

    root = Path(args.root).resolve()
    cfg = Config.load(root=root)
    pipeline = Pipeline(cfg)
    cleaned = pipeline.clean(pipeline.load_reviews())
    lookup = {item.review_id: item.text_clean for item in cleaned}
    texts, aspects, sentiments = pipeline.training_arrays(pipeline.load_labels(), lookup)

    names = [str(cfg.get("model.name", "svm"))]
    results: dict[str, object] = {}
    k = int(cfg.get("evaluation.top_k", 5))

    print(f"Sampel berlabel: {len(texts)} · lipatan: {args.folds}\n")
    for name in names:
        def build():
            local = Config.load(root=root)
            local._data["model"]["name"] = name
            return build_model(local)

        report = cross_validate(build, texts, aspects, sentiments,
                                folds=args.folds, seed=int(cfg.get("project.seed", 42)))

        gold_path = cfg.path("paths.reference") / "gold_phrases.json"
        if gold_path.exists():
            gold = json.loads(gold_path.read_text(encoding="utf-8"))
            output = pipeline.run(model=build())
            report["phrase_precision"] = evaluate_phrase_quality(
                output.decision.phrases, gold, k=k
            )

        results[name] = report
        summary = report["summary"]
        print(f"[{name}] F1-makro aspek    : {summary['aspect_macro_f1_mean']:.4f} "
              f"± {summary['aspect_macro_f1_std']:.4f}")
        print(f"[{name}] F1-makro sentimen : {summary['sentiment_macro_f1_mean']:.4f} "
              f"± {summary['sentiment_macro_f1_std']:.4f}")
        if "phrase_precision" in report:
            print(f"[{name}] Precision@{k} frasa: "
                  f"{report['phrase_precision']['mean_precision']:.4f}")
        print()

    target = Path(args.out)
    if not target.is_absolute():
        target = root / target
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Hasil ditulis: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
