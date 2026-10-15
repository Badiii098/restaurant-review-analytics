"""Orkestrasi alur end-to-end.

Kelas :class:`Pipeline` merangkai kelima lapisan secara berurutan dan
mencatat waktu setiap tahap. Pencatatan waktu bukan sekadar alat
penyidikan: ia menjadi bahan bagi pengujian kebutuhan non-fungsional
KNF-01 dan KNF-02 (lihat Sub-bab 3.2).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

import pandas as pd

from rra.config import Config
from rra.contracts import CleanReview, Prediction, RawReview, TrainingExample
from rra.decision.module import DecisionModule, DecisionOutput
from rra.io_layer.loader import ReviewLoader, describe_dataset, load_training_examples
from rra.models.base import AspectSentimentModel
from rra.models.registry import build_model
from rra.preprocess.cleaner import TextCleaner


class PipelineError(RuntimeError):
    """Kesalahan pada alur penelitian yang perlu ditangani pengguna."""


@dataclass(slots=True)
class PipelineOutput:
    """Hasil satu kali penjalanan alur end-to-end."""

    model_name: str = ""
    n_reviews: int = 0
    decision: DecisionOutput | None = None
    predictions: list[Prediction] = field(default_factory=list)
    clean_reviews: list[CleanReview] = field(default_factory=list)
    data_quality: dict[str, Any] = field(default_factory=dict)
    timings: dict[str, float] = field(default_factory=dict)
    model_info: dict[str, Any] = field(default_factory=dict)


class Pipeline:
    """Alur lengkap: muat data → praproses → latih → klasifikasi → keputusan."""

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.cleaner = TextCleaner.from_config(cfg)
        self.decision_module = DecisionModule.from_config(cfg)

    # ------------------------------------------------------------------ #
    # LAPISAN 1 — data
    # ------------------------------------------------------------------ #
    def load_reviews(self) -> list[RawReview]:
        path = self.cfg.path("paths.reviews_file")
        if not path.exists():
            raise PipelineError(
                f"Berkas ulasan tidak ditemukan: {path}\n"
                "Jalankan `python -m rra.cli sample-data` (atau "
                "`python scripts/make_sample_data.py`) untuk membuat data contoh, "
                "atau letakkan berkas hasil pengumpulan data Anda di sana."
            )
        return ReviewLoader.from_csv(path)

    def load_labels(self) -> list[TrainingExample]:
        path = self.cfg.path("paths.reference") / "labels.csv"
        if not path.exists():
            raise PipelineError(
                f"Berkas label tidak ditemukan: {path}\n"
                "Data berlabel wajib tersedia untuk melatih komponen model. "
                "Lihat docs/ANOTASI.md untuk alur anotasi."
            )
        return load_training_examples(path)

    # ------------------------------------------------------------------ #
    # LAPISAN 2 — praproses
    # ------------------------------------------------------------------ #
    def clean(self, reviews: Sequence[RawReview]) -> list[CleanReview]:
        cleaned: list[CleanReview] = []
        for review in reviews:
            cleaned.append(
                CleanReview(
                    review_id=review.review_id,
                    text_raw=review.text,
                    text_clean=self.cleaner.clean(review.text),
                    rating=review.rating,
                    date=review.date,
                    restaurant=review.restaurant,
                    clauses=tuple(self.cleaner.clean_clauses(review.text)),
                )
            )
        return cleaned

    # ------------------------------------------------------------------ #
    # LAPISAN 3 — pemodelan
    # ------------------------------------------------------------------ #
    def build_model_instance(self) -> AspectSentimentModel:
        return build_model(self.cfg)

    @staticmethod
    def training_arrays(
        examples: Sequence[TrainingExample], clean_lookup: dict[str, str]
    ) -> tuple[list[str], list[list[str]], list[dict[str, str]]]:
        """Susun deret teks dan label yang sejajar untuk pelatihan."""
        texts: list[str] = []
        aspects: list[list[str]] = []
        sentiments: list[dict[str, str]] = []
        for example in examples:
            text = clean_lookup.get(example.review_id)
            if not text:
                continue
            texts.append(text)
            aspects.append(list(example.aspects))
            sentiments.append(dict(example.sentiments))
        return texts, aspects, sentiments

    # ------------------------------------------------------------------ #
    # Alur penuh
    # ------------------------------------------------------------------ #
    def run(self, *, model: AspectSentimentModel | None = None) -> PipelineOutput:
        timings: dict[str, float] = {}

        t0 = time.perf_counter()
        reviews = self.load_reviews()
        timings["01_muat_data"] = round(time.perf_counter() - t0, 4)

        t0 = time.perf_counter()
        cleaned = self.clean(reviews)
        timings["02_praproses"] = round(time.perf_counter() - t0, 4)

        t0 = time.perf_counter()
        examples = self.load_labels()
        timings["03_muat_label"] = round(time.perf_counter() - t0, 4)

        clean_lookup = {item.review_id: item.text_clean for item in cleaned}
        texts, aspects, sentiments = self.training_arrays(examples, clean_lookup)
        if not texts:
            raise PipelineError(
                "Tidak ada contoh latih yang dapat dipasangkan dengan teks bersih. "
                "Pastikan berkas label memuat review_id yang ada pada berkas ulasan."
            )

        t0 = time.perf_counter()
        component = model if model is not None else self.build_model_instance()
        component.fit(texts, aspects, sentiments)
        timings["04_latih_model"] = round(time.perf_counter() - t0, 4)

        t0 = time.perf_counter()
        predictions = component.predict_with_ids(
            [item.text_clean for item in cleaned], [item.review_id for item in cleaned]
        )
        timings["05_klasifikasi"] = round(time.perf_counter() - t0, 4)

        t0 = time.perf_counter()
        decision = self.decision_module.run(
            reviews,
            predictions,
            clean_text=clean_lookup,
            clauses={item.review_id: item.clauses for item in cleaned},
            model_name=component.name,
        )
        timings["06_modul_keputusan"] = round(time.perf_counter() - t0, 4)

        timings["total"] = round(sum(timings.values()), 4)

        return PipelineOutput(
            model_name=component.name,
            n_reviews=len(cleaned),
            decision=decision,
            predictions=predictions,
            clean_reviews=cleaned,
            data_quality=describe_dataset(reviews, label="data_ulasan"),
            timings=timings,
            model_info=component.describe(),
        )

    # ------------------------------------------------------------------ #
    # Keluaran
    # ------------------------------------------------------------------ #
    def priorities_frame(self, output: PipelineOutput) -> pd.DataFrame:
        """Tabel peringkat prioritas beserta komponen pembentuk skornya."""
        if not output.decision:
            return pd.DataFrame()
        rows = []
        for item in output.decision.priorities:
            rows.append(
                {
                    "peringkat": item.rank,
                    "aspek": item.label,
                    "kode_aspek": item.aspect,
                    "skor_prioritas": item.priority,
                    "volume": item.volume,
                    "keparahan": item.severity,
                    "keragaman": item.diversity,
                    "jumlah_keluhan": item.n_negative,
                    "jumlah_dibahas": item.n_total,
                }
            )
        return pd.DataFrame(rows)

    def phrases_frame(self, output: PipelineOutput) -> pd.DataFrame:
        if not output.decision:
            return pd.DataFrame()
        rows = []
        for aspect, items in output.decision.phrases.items():
            for position, item in enumerate(items, start=1):
                rows.append(
                    {
                        "aspek": aspect,
                        "peringkat_frasa": position,
                        "frasa": item.phrase,
                        "frekuensi": item.frequency,
                        "bobot_tfidf": item.tfidf_weight,
                        "skor": item.score,
                        "contoh_ulasan": ", ".join(item.example_review_ids),
                    }
                )
        return pd.DataFrame(rows)

    def predictions_frame(self, output: PipelineOutput) -> pd.DataFrame:
        rows = []
        lookup = {item.review_id: item for item in output.clean_reviews}
        for prediction in output.predictions:
            review = lookup.get(prediction.review_id)
            for item in prediction.items:
                rows.append(
                    {
                        "review_id": prediction.review_id,
                        "aspek": item.aspect,
                        "sentimen": item.sentiment,
                        "keyakinan": item.confidence,
                        "rating": review.rating if review else None,
                        "teks_asli": review.text_raw if review else "",
                    }
                )
        return pd.DataFrame(rows)
