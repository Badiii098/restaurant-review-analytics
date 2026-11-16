"""Antarmuka baris perintah.

Perintah yang tersedia::

    rra sample-data   # buat data contoh berlabel
    rra run           # jalankan alur end-to-end
    rra evaluate      # validasi silang + evaluasi model
    rra benchmark     # ukur kinerja non-fungsional (KNF-01, KNF-02)
    rra models        # tampilkan komponen model yang tersedia
    rra explain       # tunjukkan bahan audit peringkat prioritas
    rra sensitivity   # uji sensitivitas bobot prioritas ±10%
    rra trace         # telusuri praproses satu teks ulasan
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

from rra.config import Config
from rra.pipeline import PipelineError


def _common_options() -> argparse.ArgumentParser:
    """Opsi yang berlaku untuk seluruh perintah.

    Opsi ini dipasang pada parser utama **dan** pada setiap sub-perintah,
    sehingga pengguna dapat menuliskannya sebelum maupun sesudah nama
    perintah::

        rra --set model.aspect_threshold=0.4 run
        rra run --set model.aspect_threshold=0.4

    Keduanya sah, karena pengguna tidak seharusnya perlu menghafal urutan.
    """
    common = argparse.ArgumentParser(add_help=False)
    # Nilai bawaan sengaja dibuat SUPPRESS. Argparse menyalin seluruh nilai
    # dari sub-parser ke ruang nama induk, termasuk nilai bawaannya — bila
    # tidak ditekan, opsi yang dituliskan **sebelum** nama perintah akan
    # tertimpa oleh nilai bawaan sub-perintah dan diam-diam hilang.
    common.add_argument(
        "--config",
        default=argparse.SUPPRESS,
        help="Berkas konfigurasi dasar (bawaan: config/default.yaml).",
    )
    common.add_argument(
        "--override",
        default=argparse.SUPPRESS,
        help="Berkas konfigurasi varian, mis. config/eksperimen.yaml.",
    )
    common.add_argument(
        "--set",
        dest="sets",
        action="append",
        default=argparse.SUPPRESS,
        metavar="KUNCI=NILAI",
        help="Penimpaan langsung, dapat diulang, mis. --set model.aspect_threshold=0.4.",
    )
    common.add_argument(
        "--root",
        default=argparse.SUPPRESS,
        help="Direktori akar proyek tempat jalur relatif diselesaikan "
             "(bawaan: direktori repositori ini).",
    )
    return common


def _build_parser() -> argparse.ArgumentParser:
    common = _common_options()
    parser = argparse.ArgumentParser(
        prog="rra",
        description="Sistem analitik ulasan pelanggan restoran berbasis ABSA.",
        parents=[common],
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p_sample = sub.add_parser("sample-data", parents=[common],
                              help="Buat data contoh yang dapat diulang.")
    p_sample.add_argument("--n", type=int, default=None, help="Jumlah ulasan.")
    p_sample.add_argument("--seed", type=int, default=None, help="Benih pengacakan.")

    p_run = sub.add_parser("run", parents=[common], help="Jalankan alur end-to-end.")
    p_run.add_argument("--no-report", action="store_true", help="Jangan tulis berkas laporan.")
    p_run.add_argument("--save-model", action="store_true", help="Simpan komponen terlatih.")
    p_run.add_argument("--json", action="store_true", help="Cetak hasil ringkas sebagai JSON.")

    p_eval = sub.add_parser("evaluate", parents=[common],
                            help="Evaluasi kinerja komponen model.")
    p_eval.add_argument("--folds", type=int, default=None, help="Jumlah lipatan validasi silang.")
    p_eval.add_argument("--out", default=None, help="Berkas JSON keluaran evaluasi.")

    p_bench = sub.add_parser("benchmark", parents=[common],
                             help="Ukur kinerja non-fungsional.")
    p_bench.add_argument("--repeat", type=int, default=5, help="Jumlah pengulangan.")
    p_bench.add_argument("--out", default=None, help="Berkas JSON keluaran benchmark.")

    sub.add_parser("models", parents=[common], help="Tampilkan komponen model yang terdaftar.")

    p_explain = sub.add_parser("explain", parents=[common],
                               help="Tampilkan bahan audit peringkat prioritas.")
    p_explain.add_argument("--db", default=None, help="Berkas basis data hasil (SQLite).")

    p_sens = sub.add_parser("sensitivity", parents=[common],
                            help="Uji sensitivitas bobot prioritas (±10%%).")
    p_sens.add_argument("--delta", type=float, default=0.10, help="Besar geseran relatif bobot.")
    p_sens.add_argument("--out", default=None, help="Berkas JSON keluaran.")

    p_trace = sub.add_parser("trace", parents=[common],
                             help="Telusuri praproses satu teks ulasan.")
    p_trace.add_argument("text", nargs="+", help="Teks ulasan yang ditelusuri.")

    return parser


def _parse_sets(items: Sequence[str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for item in items:
        if "=" not in item:
            raise SystemExit(f"Format --set salah: '{item}'. Gunakan KUNCI=NILAI.")
        key, _, raw = item.partition("=")
        out[key.strip()] = _coerce(raw.strip())
    return out


def _coerce(text: str) -> Any:
    low = text.lower()
    if low in {"true", "yes"}:
        return True
    if low in {"false", "no"}:
        return False
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        pass
    return text


def _load_config(args: argparse.Namespace) -> Config:
    root_value = getattr(args, "root", None)
    root = Path(root_value).expanduser().resolve() if root_value else None
    return Config.load(
        getattr(args, "config", None) or "config/default.yaml",
        override=getattr(args, "override", None),
        sets=_parse_sets(getattr(args, "sets", None) or []),
        root=root,
    )


# --------------------------------------------------------------------------- #
# Perintah
# --------------------------------------------------------------------------- #

def cmd_sample_data(args: argparse.Namespace, cfg: Config) -> int:
    from rra.io_layer.sample_data import generate_dataset, write_dataset  # noqa: PLC0415

    n = args.n if args.n is not None else int(cfg.get("project.n_reviews", 600))
    seed = args.seed if args.seed is not None else int(cfg.get("project.seed", 42))

    dataset = generate_dataset(n_reviews=n, seed=seed)
    written = write_dataset(dataset, cfg.root)
    print(f"Data contoh dibuat: {dataset.n_reviews} ulasan, {len(dataset.labels)} label aspek")
    for key, path in written.items():
        print(f"  {key}: {path}")
    return 0


def cmd_run(args: argparse.Namespace, cfg: Config) -> int:
    from rra.decision.severity import severity_map  # noqa: PLC0415
    from rra.pipeline import Pipeline  # noqa: PLC0415
    from rra.report.report import ReportWriter, coverage_frame  # noqa: PLC0415
    from rra.storage.repository import ResultRepository  # noqa: PLC0415

    pipeline = Pipeline(cfg)
    output = pipeline.run()
    decision = output.decision
    assert decision is not None

    print(f"Komponen model aktif   : {output.model_name}")
    print(f"Ulasan dianalisis      : {output.n_reviews}")
    print()
    print("Peringkat prioritas perbaikan layanan")
    print("-" * 78)
    for item in decision.priorities:
        print(f"  {item.rank}. {item.label:<12} skor {item.priority:.4f}  "
              f"(volume {item.volume:.3f}, keparahan {item.severity:.3f}, "
              f"keragaman {item.diversity:.3f}, keluhan {item.n_negative})")
    print()
    print("Frasa keluhan dominan")
    print("-" * 78)
    for aspect, items in decision.phrases.items():
        top = ", ".join(f"{p.phrase} ({p.frequency})" for p in items[:3])
        print(f"  {aspect:<12}: {top}")
    print()

    # Simpan ke basis data
    reviews = pipeline.load_reviews()
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
    print(f"Hasil disimpan pada basis data: {cfg.path('paths.db_path')} (run_id={run_id})")

    if not args.no_report:
        writer = ReportWriter(cfg.path("paths.reports"))
        written = writer.write_all(
            output=output,
            extra_frames={"cakupan_aspek": coverage_frame(reviews, decision)},
            summary={"model": output.model_name, "n_reviews": output.n_reviews},
        )
        print(f"Laporan ditulis ke: {cfg.path('paths.reports')}")
        for name, path in written.items():
            print(f"  {name}: {path.name}")

    if args.save_model:
        model = pipeline.build_model_instance()
        texts, aspects, sentiments = pipeline.training_arrays(
            pipeline.load_labels(),
            {item.review_id: item.text_clean for item in output.clean_reviews},
        )
        model.fit(texts, aspects, sentiments)
        target = cfg.path("paths.artifacts") / f"model_{model.name}.joblib"
        target.parent.mkdir(parents=True, exist_ok=True)
        model.save(target)
        print(f"Komponen model disimpan: {target}")

    if args.json:
        print(json.dumps(
            {
                "model": output.model_name,
                "n_reviews": output.n_reviews,
                "timings": output.timings,
                "priorities": [
                    {"rank": i.rank, "aspect": i.aspect, "priority": i.priority}
                    for i in decision.priorities
                ],
            },
            indent=2, ensure_ascii=False,
        ))
    return 0


def cmd_evaluate(args: argparse.Namespace, cfg: Config) -> int:
    import pandas as pd  # noqa: PLC0415

    from rra.evaluate import cross_validate, evaluate_phrase_quality  # noqa: PLC0415
    from rra.models.registry import build_model  # noqa: PLC0415
    from rra.pipeline import Pipeline  # noqa: PLC0415

    folds = args.folds if args.folds is not None else int(cfg.get("evaluation.folds", 10))
    pipeline = Pipeline(cfg)
    reviews = pipeline.load_reviews()
    cleaned = pipeline.clean(reviews)
    examples = pipeline.load_labels()
    lookup = {item.review_id: item.text_clean for item in cleaned}
    texts, aspects, sentiments = pipeline.training_arrays(examples, lookup)
    print(f"Sampel berlabel: {len(texts)} · lipatan: {folds}")
    print()

    names = [str(cfg.get("model.name", "svm"))]
    results: dict[str, Any] = {}

    for name in names:
        def build(name: str = name):  # noqa: ANN202
            root_value = getattr(args, "root", None)
            root = Path(root_value).expanduser().resolve() if root_value else None
            local = Config.load(
                getattr(args, "config", None) or "config/default.yaml",
                override=getattr(args, "override", None),
                sets=_parse_sets(getattr(args, "sets", None) or []),
                root=root,
            )
            local._data["model"]["name"] = name  # noqa: SLF001
            return build_model(local)

        report = cross_validate(build, texts, aspects, sentiments, folds=folds,
                                seed=int(cfg.get("project.seed", 42)))
        results[name] = report
        summary = report["summary"]
        print(f"[{name}] F1-makro aspek     : {summary['aspect_macro_f1_mean']:.4f} "
              f"± {summary['aspect_macro_f1_std']:.4f}")
        print(f"[{name}] F1-makro sentimen  : {summary['sentiment_macro_f1_mean']:.4f} "
              f"± {summary['sentiment_macro_f1_std']:.4f}")

        # Ketepatan peringkat frasa keluhan (Precision@K)
        gold_path = cfg.path("paths.reference") / "gold_phrases.json"
        if gold_path.exists():
            gold = json.loads(gold_path.read_text(encoding="utf-8"))
            output = pipeline.run(model=build())
            assert output.decision is not None
            k = int(cfg.get("evaluation.top_k", 5))
            quality = evaluate_phrase_quality(output.decision.phrases, gold, k=k)
            results[name]["phrase_precision"] = quality
            print(f"[{name}] Precision@{k} frasa : {quality['mean_precision']:.4f}")
        print()

    if args.out:
        target = Path(args.out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Hasil evaluasi ditulis: {target}")
    return 0


def cmd_benchmark(args: argparse.Namespace, cfg: Config) -> int:
    from rra.storage.repository import ResultRepository  # noqa: PLC0415

    pipeline = None
    name = str(cfg.get("model.name", "svm"))
    rows: list[dict[str, Any]] = []
    measured = 0
    import time  # noqa: PLC0415

    from rra.pipeline import Pipeline  # noqa: PLC0415

    print(f"Mengukur kinerja non-fungsional ({args.repeat} pengulangan)…")
    for attempt in range(1, int(args.repeat) + 1):
        pipeline = Pipeline(cfg)
        started = time.perf_counter()
        output = pipeline.run()
        elapsed = time.perf_counter() - started
        measured += 1
        rows.append({"ulangan": attempt, **output.timings, "total_dinding": round(elapsed, 4)})
        print(f"  pengulangan {attempt}: {elapsed:.2f} detik "
              f"({output.timings.get('04_latih_model', 0):.2f} s pelatihan)")

    import statistics as _stat  # noqa: PLC0415

    n_reviews_last = output.n_reviews if pipeline is not None else 1
    elapsed_values = [row["total_dinding"] for row in rows]
    train_values = [row["04_latih_model"] for row in rows]
    inference_values = [row["05_klasifikasi"] for row in rows]
    summary = {
        "n_pengulangan": measured,
        "n_ulasan": n_reviews_last,
        "total_detik_rata_rata": round(_stat.mean(elapsed_values), 4),
        "total_detik_maks": round(max(elapsed_values), 4),
        "latih_detik_rata_rata": round(_stat.mean(train_values), 4),
        "inferensi_detik_rata_rata": round(_stat.mean(inference_values), 4),
        "inferensi_ms_per_ulasan": round(
            1000.0 * _stat.mean(inference_values) / max(n_reviews_last, 1), 4),
    }
    print()
    for key, value in summary.items():
        print(f"  {key}: {value}")

    target = Path(args.out) if args.out else (cfg.path("paths.reports") / "benchmark.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({"summary": summary, "perulangan": rows},
                                 indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nHasil benchmark ditulis: {target}")
    return 0


def cmd_models(_args: argparse.Namespace, _cfg: Config) -> int:
    from rra.models.registry import available_models, get_model_class  # noqa: PLC0415

    print("Komponen model yang terdaftar")
    print("-" * 70)
    for key, display in available_models().items():
        cls = get_model_class(key)
        print(f"  {key:<8} {display}")
        if cls.description:
            print(f"           {cls.description}")
    print()
    print("Penelitian ini memakai satu komponen model: SVM linear berbasis TF-IDF.")
    return 0


def cmd_explain(args: argparse.Namespace, cfg: Config) -> int:
    from rra.storage.repository import ResultRepository  # noqa: PLC0415

    path = Path(args.db) if args.db else cfg.path("paths.db_path")
    repository = ResultRepository(path)
    run_id = repository.latest_run_id()
    if run_id is None:
        print(f"Belum ada hasil pada basis data: {path}", file=sys.stderr)
        print("Jalankan `rra run` lebih dahulu.", file=sys.stderr)
        return 1

    rows = repository.load_priorities(run_id)
    phrases = repository.load_phrases(run_id)
    print(f"Bahan audit peringkat prioritas (run_id={run_id})")
    print("=" * 78)
    for row in rows:
        print(f"\n[{row['rank']}] {row['label']} — skor {row['priority']:.4f}")
        print(f"    Volume    : {row['volume']:.4f}  (dari {row['n_negative']} ulasan negatif)")
        print(f"    Keparahan : {row['severity']:.4f}")
        print(f"    Keragaman : {row['diversity']:.4f}")
        for item in [p for p in phrases if p["aspect"] == row["aspect"]]:
            print(f"      - {item['phrase']} (frekuensi {item['frequency']}, "
                  f"skor {item['score']:.4f})")
    return 0


def cmd_trace(args: argparse.Namespace, cfg: Config) -> int:
    """Telusuri praproses satu teks ulasan, tahap demi tahap.

    Perintah ini ada untuk menjawab pertanyaan yang paling sering muncul saat
    sidang: "mengapa teks ini menjadi seperti itu?". Tanpa penelusuran,
    praproses hanya dapat dipercaya, tidak dapat diperiksa.
    """
    from rra.decision.polarity import clause_polarity, is_complaint_clause  # noqa: PLC0415
    from rra.preprocess.cleaner import TextCleaner  # noqa: PLC0415

    text = " ".join(args.text).strip()
    cleaner = TextCleaner.from_config(cfg)

    print("Teks mentah")
    print(f"  {text}")
    print("\nTahap praproses")
    for stage, value in cleaner.trace(text).items():
        print(f"  {stage:<20} {value or '(kosong)'}")

    print("\nKlausa — satuan analisis polaritas")
    clauses = cleaner.clean_clauses(text)
    if not clauses:
        print("  (tidak ada klausa yang tersisa setelah praproses)")
    for index, clause in enumerate(clauses, start=1):
        polarity = clause_polarity(clause)
        jenis = "keluhan" if is_complaint_clause(clause) else "bukan keluhan"
        print(f"  {index}. [{jenis:>13}] polaritas={polarity:+d}  {clause}")

    print("\nCatatan: polaritas di atas berasal dari leksikon "
          "(src/rra/decision/polarity.py),")
    print("bukan dari komponen model. Leksikon hanya menyaring klausa; "
          "aspek dan sentimen tetap")
    print("ditentukan komponen model pada `rra run`.")
    return 0


def cmd_sensitivity(args: argparse.Namespace, cfg: Config) -> int:
    from rra.decision.sensitivity import weight_sensitivity  # noqa: PLC0415
    from rra.pipeline import Pipeline  # noqa: PLC0415

    output = Pipeline(cfg).run()
    assert output.decision is not None
    rows = weight_sensitivity(output.decision.stats, cfg.get("decision.weights"), args.delta)
    print(f"Uji sensitivitas bobot ±{args.delta:.0%} ({len(rows)} skenario)")
    print("-" * 70)
    for row in rows:
        status = "peringkat 1 sama" if row["peringkat_1_sama"] else "peringkat 1 berubah"
        bobot = " / ".join(f"{row['bobot'][k]:.3f}" for k in ("volume", "severity", "diversity"))
        print(f"  {row['komponen']:<9} {row['arah']}  bobot {bobot}  "
              f"tau {row['tau_kendall']:+.2f}  {status}  {' > '.join(row['peringkat'])}")
    if args.out:
        target = Path(args.out)
        if not target.is_absolute():
            target = cfg.root / target
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nHasil ditulis: {target}")
    return 0


_COMMANDS = {
    "sample-data": cmd_sample_data,
    "run": cmd_run,
    "evaluate": cmd_evaluate,
    "benchmark": cmd_benchmark,
    "models": cmd_models,
    "explain": cmd_explain,
    "sensitivity": cmd_sensitivity,
    "trace": cmd_trace,
}


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        cfg = _load_config(args)
        return _COMMANDS[args.command](args, cfg)
    except FileNotFoundError as error:
        print(f"Berkas tidak ditemukan: {error}", file=sys.stderr)
        print(
            "Periksa opsi --config/--root, atau jalankan perintah dari direktori "
            "akar proyek.",
            file=sys.stderr,
        )
        return 1
    except PipelineError as error:
        # Kekurangan data bukan kesalahan pemrograman, melainkan keadaan yang
        # harus dijelaskan kepada pengguna beserta langkah perbaikannya.
        print(str(error), file=sys.stderr)
        return 1
    except KeyError as error:
        print(f"Komponen tidak ditemukan: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
