"""Lapis 5a — layanan per tahap penelitian.

Setiap fungsi membaca bukti satu tahap pada diagram SDLC Prototipe dan
mengembalikan ``dict`` siap-JSON. Fungsi tidak pernah memalsukan angka: bila
sumbernya belum ada, ia mengembalikan ``status = "belum_tersedia"`` beserta
perintah yang membuatnya.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from rra.config import Config

SELESAI = "selesai"
BELUM = "belum_tersedia"
TARGET_ANOTASI = 500

TAHAPAN = [
    {"kode": "data", "nama": "Pengumpulan Data", "keterangan": "8 restoran"},
    {"kode": "anotasi", "nama": "Anotasi Data", "keterangan": "500 ulasan, kappa"},
    {"kode": "kebutuhan", "nama": "Analisis Kebutuhan", "keterangan": "FR, KNF"},
    {"kode": "desain", "nama": "Desain Cepat", "keterangan": "arsitektur, kontrak"},
    {"kode": "iterasi", "nama": "Prototipe dan Pemodelan NLP", "keterangan": "iterasi 1–2, Macro-F1"},
    {"kode": "hasil", "nama": "Hasil dan Prioritas", "keterangan": "skor 0–100, frasa, rekomendasi"},
    {"kode": "pengujian", "nama": "Pengujian Perangkat Lunak", "keterangan": "unit, integrasi, sistem, KNF"},
    {"kode": "pakar", "nama": "Validasi Pakar", "keterangan": "ρ Spearman, Wilcoxon"},
    {"kode": "kesimpulan", "nama": "Analisis Hasil dan Kesimpulan", "keterangan": "H1–H3"},
]


def _belum(langkah: str, **lain: Any) -> dict:
    return {"status": BELUM, "langkah": langkah, **lain}


def _json(path: Path) -> Any | None:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _laporan(cfg: Config) -> Path:
    return cfg.path("paths.reports")


def _katalog(cfg: Config):
    from rra.requirements import muat_katalog  # noqa: PLC0415

    return muat_katalog(cfg.root / "config" / "kebutuhan.yaml")


def _junit(cfg: Config) -> dict | None:
    from rra.junit import ringkas_junit  # noqa: PLC0415

    return ringkas_junit(_laporan(cfg) / "pytest.xml")


def _gudang(cfg: Config):
    from rra.storage.repository import ResultRepository  # noqa: PLC0415

    return ResultRepository(cfg.path("paths.db_path"))


# --------------------------------------------------------------------------- #
def status(cfg: Config) -> dict:
    from rra import __version__  # noqa: PLC0415

    gudang = _gudang(cfg)
    run = gudang.load_run()
    return {"status": SELESAI, "versi": __version__, "model": cfg.get("model.name"),
            "basis_data": cfg.path("paths.db_path").name,
            "hasil_terakhir": run["run_id"] if run else None,
            "tahapan": TAHAPAN}


def data(cfg: Config) -> dict:
    import pandas as pd  # noqa: PLC0415

    from rra.io_layer.scope import load_active_restaurants, ringkas_sampel  # noqa: PLC0415

    daftar = cfg.root / "config" / "restaurants.csv"
    kandidat = load_active_restaurants(daftar) if daftar.exists() else []
    sampel = ringkas_sampel(
        daftar, cfg.path("paths.raw") / "maps", n=int(cfg.get("sampling.n_restoran", 8)),
        rentang=tuple(int(t) for t in cfg.get("sampling.rentang_tahun", [2021, 2026])),
        maks_per_kategori=int(cfg.get("sampling.maks_per_kategori", 2)),
        batas=int(cfg.get("sampling.batas_target", 625)))

    ulasan: dict[str, Any] = {"total": 0, "per_restoran": {}, "rating": {}, "tahun": {}}
    berkas = cfg.path("paths.reviews_file")
    if berkas.exists():
        frame = pd.read_csv(berkas, dtype=str).fillna("")
        ulasan["total"] = int(len(frame))
        if "restaurant" in frame:
            ulasan["per_restoran"] = {k: int(v) for k, v in frame["restaurant"].value_counts().items() if k}
        if "rating" in frame:
            ulasan["rating"] = {k: int(v) for k, v in sorted(Counter(
                r.split(".")[0] for r in frame["rating"] if r).items())}
        if "date" in frame:
            ulasan["tahun"] = {k: int(v) for k, v in sorted(Counter(
                d[:4] for d in frame["date"] if d[:4].isdigit()).items())}
    meta = _json(cfg.path("paths.reference") / "dataset_meta.json") or {}
    return {"status": SELESAI if ulasan["total"] else BELUM,
            "langkah": "python -m rra.cli sample-data --n 2000 atau scripts/import_reviews.py",
            "data_contoh": bool(meta.get("data_contoh", False)),
            "kandidat": len(kandidat),
            "sampling": {"n": sampel["n"], "teknik": cfg.get("sampling.teknik", "purposive"),
                         "rentang_tahun": sampel["rentang"], "batas_target": sampel["batas_target"],
                         "maks_per_kategori": sampel["maks_per_kategori"],
                         "ditetapkan": sampel["ditetapkan"], "restoran": sampel["restoran"],
                         "target_total": sampel["target_total"],
                         "langkah": "python scripts/pilih_restoran.py --tulis"},
            "ulasan": ulasan}


def anotasi(cfg: Config) -> dict:
    import pandas as pd  # noqa: PLC0415

    berlabel = 0
    label = cfg.path("paths.reference") / "labels.csv"
    if label.exists():
        berlabel = int(pd.read_csv(label, dtype=str)["review_id"].nunique())
    kappa = _json(_laporan(cfg) / "kappa.json")
    dasar = {"target": TARGET_ANOTASI, "berlabel": berlabel,
             "progres": round(min(berlabel / TARGET_ANOTASI, 1.0) * 100, 1)}
    if kappa is None:
        return _belum("python scripts/compute_kappa.py --first data/reference/anotator_1.csv "
                      "--second data/reference/anotator_2.csv --out reports/kappa.json", **dasar)
    return {"status": SELESAI, **dasar, "kappa": kappa}


def kebutuhan(cfg: Config) -> dict:
    from rra.requirements import persen_terlacak  # noqa: PLC0415

    katalog = _katalog(cfg)
    junit = _junit(cfg)
    per_kasus = (junit or {}).get("per_kasus", {})
    folder = cfg.root
    kasus = []
    for c in katalog.kasus:
        if c["jenis"] == "manual":
            bukti = _json(folder / c["bukti"]) if c.get("bukti") else None
            hasil = (bukti or {}).get("hasil") if isinstance(bukti, dict) and "hasil" in bukti else (
                "ada_bukti" if bukti is not None else "belum_diuji")
        else:
            hasil = per_kasus.get(c["kode"], "belum_dijalankan")
        kasus.append({**c, "hasil": hasil})
    return {"status": SELESAI, "persen_terlacak": persen_terlacak(katalog),
            "junit_tersedia": junit is not None,
            "langkah": "python -m pytest tests --junitxml=reports/pytest.xml",
            "kebutuhan": katalog.kebutuhan, "kasus": kasus}


def desain(cfg: Config) -> dict:
    import dataclasses  # noqa: PLC0415

    from rra import contracts  # noqa: PLC0415

    lapis = [
        {"no": 1, "nama": "Akuisisi & Validasi Data", "modul": "rra.io_layer"},
        {"no": 2, "nama": "Praproses Teks", "modul": "rra.preprocess"},
        {"no": 3, "nama": "Komponen Model (TF-IDF + SVM linear)", "modul": "rra.models"},
        {"no": 4, "nama": "Modul Keputusan", "modul": "rra.decision, rra.analysis"},
        {"no": 5, "nama": "Penyajian: 5a API FastAPI, 5b klien React, CLI",
         "modul": "rra.api, rra.services, frontend/, rra.cli"},
    ]
    kontrak = []
    for nama, obj in vars(contracts).items():
        if dataclasses.is_dataclass(obj) and isinstance(obj, type):
            kontrak.append({"nama": nama, "bidang": [
                {"nama": f.name, "tipe": str(f.type)} for f in dataclasses.fields(obj)]})
    return {"status": SELESAI, "lapis": lapis, "kontrak": kontrak,
            "aspek": list(contracts.ASPECTS), "bobot": cfg.get("decision.weights")}


def iterasi(cfg: Config) -> dict:
    from rra.iterations import bandingkan, muat_iterasi  # noqa: PLC0415

    daftar = muat_iterasi(_laporan(cfg) / "iterasi")
    if not daftar:
        return _belum('python -m rra.cli evaluate --iterasi 1 --catatan "prototipe awal"', iterasi=[])
    selisih = bandingkan(daftar[0], daftar[-1]) if len(daftar) >= 2 else None
    return {"status": SELESAI, "iterasi": daftar, "selisih": selisih}


def hasil(cfg: Config, run_id: int | None = None) -> dict | None:
    """``None`` bila ``run_id`` diminta tetapi tidak ada (API menjawab 404)."""
    gudang = _gudang(cfg)
    run = gudang.load_run(run_id)
    if run is None:
        if run_id is not None and gudang.latest_run_id() is not None:
            return None
        return _belum("python -m rra.cli run", prioritas=[], frasa=[], rekomendasi=[])
    nomor = run["run_id"]
    frasa = gudang.load_phrases(nomor)
    for row in frasa:
        try:
            row["example_review_ids"] = json.loads(row.get("example_review_ids") or "[]")
        except (TypeError, ValueError):
            row["example_review_ids"] = []
    return {"status": SELESAI,
            "run": {k: run[k] for k in ("run_id", "created_at", "model_name", "n_reviews",
                                        "weights", "timings")},
            "prioritas": gudang.load_priorities(nomor), "frasa": frasa,
            "rekomendasi": gudang.load_recommendations(nomor)}


def analisis(cfg: Config) -> int:
    """Latih, analisis, dan simpan satu hasil baru; kembalikan nomornya."""
    from rra.decision.severity import severity_map  # noqa: PLC0415
    from rra.pipeline import Pipeline  # noqa: PLC0415

    pipeline = Pipeline(cfg)
    keluaran = pipeline.run()
    if keluaran.decision is None:
        raise RuntimeError("Pipeline tidak menghasilkan modul keputusan.")
    gudang = _gudang(cfg)
    ulasan = pipeline.load_reviews()
    run_id = gudang.save_run(model_name=keluaran.model_name, decision=keluaran.decision,
                             severities=severity_map(ulasan), reviews=ulasan,
                             timings=keluaran.timings, config=cfg.as_dict())
    gudang.save_predictions(run_id, keluaran.predictions)
    return run_id


def sensitivitas(cfg: Config) -> dict:
    baris = _json(_laporan(cfg) / "sensitivitas.json")
    if baris is None:
        return _belum("python -m rra.cli sensitivity --out reports/sensitivitas.json", skenario=[])
    return {"status": SELESAI, "skenario": baris,
            "peringkat_1_stabil": all(r["peringkat_1_sama"] for r in baris)}


def pengujian(cfg: Config) -> dict:
    junit = _junit(cfg)
    benchmark = _json(_laporan(cfg) / "benchmark.json")
    katalog = _katalog(cfg)
    per_tingkat: dict[str, dict[str, int]] = {}
    for c in katalog.kasus:
        if c["jenis"] != "otomatis":
            continue
        hasil_kasus = (junit or {}).get("per_kasus", {}).get(c["kode"], "belum_dijalankan")
        per_tingkat.setdefault(c["tingkat"], Counter())[hasil_kasus] += 1
    return {"status": SELESAI if junit else BELUM,
            "langkah": "python -m pytest tests --junitxml=reports/pytest.xml ; "
                       "python -m rra.cli benchmark --repeat 5",
            "junit": junit, "per_tingkat": {k: dict(v) for k, v in per_tingkat.items()},
            "benchmark": benchmark}


def pakar(cfg: Config) -> dict:
    laporan = _json(_laporan(cfg) / "uji_pakar.json")
    if laporan is None:
        return _belum("isi data/reference/urutan_pakar.csv lalu python scripts/uji_pakar.py")
    return {"status": SELESAI, **laporan}


def hipotesis(cfg: Config) -> dict:
    from rra.analysis.hypotheses import uji_h1, uji_h2, uji_h3  # noqa: PLC0415

    katalog = _katalog(cfg)
    junit = _junit(cfg)
    benchmark = _json(_laporan(cfg) / "benchmark.json")
    pakar_laporan = _json(_laporan(cfg) / "uji_pakar.json")
    return {"status": SELESAI, "hipotesis": [uji_h1(katalog, junit),
                                              uji_h2(benchmark, junit, katalog),
                                              uji_h3(pakar_laporan)]}
