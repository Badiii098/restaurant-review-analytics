"""Modul keputusan — merangkai seluruh komponen Lapisan 4.

Kelas :class:`DecisionModule` adalah satu-satunya antarmuka yang dikenal
oleh lapisan di atasnya. Ia menerima ulasan bersih dan hasil klasifikasi,
lalu mengembalikan peringkat prioritas, frasa keluhan dominan, dan
rekomendasi tindakan.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Sequence

from rra.contracts import (
    ASPECTS,
    ComplaintPhrase,
    Prediction,
    RawReview,
    Recommendation,
)
from rra.decision.phrases import ComplaintPhraseExtractor
from rra.decision.priority import AspectStat, PriorityEngine
from rra.decision.rules import recommend_action
from rra.decision.severity import severity_map


@dataclass(slots=True)
class DecisionOutput:
    """Seluruh keluaran modul keputusan beserta bahan auditnya."""

    priorities: list = field(default_factory=list)
    phrases: dict[str, list[ComplaintPhrase]] = field(default_factory=dict)
    recommendations: list[Recommendation] = field(default_factory=list)
    stats: dict[str, AspectStat] = field(default_factory=dict)
    weights: dict[str, float] = field(default_factory=dict)
    model_name: str = ""
    n_reviews: int = 0
    n_negative_reviews: int = 0

    def audit_lines(self) -> list[str]:
        """Keterangan terbaca manusia untuk setiap peringkat prioritas."""
        return [item.explain(self.weights) for item in self.priorities]


class DecisionModule:
    """Mengubah hasil klasifikasi menjadi keputusan yang dapat diaudit."""

    def __init__(
        self,
        *,
        extractor: ComplaintPhraseExtractor | None = None,
        engine: PriorityEngine | None = None,
        severity_default: float = 0.5,
    ) -> None:
        self.extractor = extractor or ComplaintPhraseExtractor()
        self.engine = engine or PriorityEngine()
        self.severity_default = float(severity_default)

    @classmethod
    def from_config(cls, cfg) -> "DecisionModule":
        return cls(
            extractor=ComplaintPhraseExtractor.from_config(cfg),
            engine=PriorityEngine.from_config(cfg),
            severity_default=float(cfg.get("decision.severity_default", 0.5)),
        )

    # ------------------------------------------------------------------ #
    def run(
        self,
        reviews: Sequence[RawReview],
        predictions: Sequence[Prediction],
        *,
        clean_text: Mapping[str, str],
        clauses: Mapping[str, Sequence[str]] | None = None,
        model_name: str = "",
    ) -> DecisionOutput:
        """Jalankan seluruh perhitungan Lapisan 4.

        Parameters
        ----------
        reviews:
            Ulasan asli (menyediakan ``review_id`` dan ``rating``).
        predictions:
            Keluaran komponen model untuk setiap ulasan.
        clean_text:
            Pemetaan ``review_id`` ke teks yang telah dipraproses.
        clauses:
            Pemetaan ``review_id`` ke deret klausa bersih. Bila tidak
            diberikan, teks utuh dipakai sebagai satu klausa tunggal.
        """
        severities = severity_map(reviews, default=self.severity_default)

        n_total: dict[str, int] = {aspect: 0 for aspect in ASPECTS}
        n_negative: dict[str, int] = {aspect: 0 for aspect in ASPECTS}
        negative_severities: dict[str, list[float]] = {aspect: [] for aspect in ASPECTS}
        docs_by_aspect: dict[str, list[tuple[str, Sequence[str]]]] = {
            aspect: [] for aspect in ASPECTS
        }

        for prediction in predictions:
            review_id = prediction.review_id
            severity = severities.get(review_id, self.severity_default)
            for item in prediction.items:
                if item.aspect not in n_total:
                    continue
                n_total[item.aspect] += 1
                if item.sentiment == "negatif":
                    n_negative[item.aspect] += 1
                    negative_severities[item.aspect].append(severity)
                    if clauses and clauses.get(review_id):
                        review_clauses = list(clauses[review_id])
                    else:
                        text = clean_text.get(review_id, "")
                        review_clauses = [text] if text else []
                    if review_clauses:
                        docs_by_aspect[item.aspect].append((review_id, review_clauses))

        phrases = self.extractor.extract_all(docs_by_aspect)

        stats: dict[str, AspectStat] = {}
        for aspect in ASPECTS:
            stats[aspect] = AspectStat(
                aspect=aspect,
                n_total=n_total[aspect],
                n_negative=n_negative[aspect],
                severities=negative_severities[aspect],
                n_phrases=self.extractor.candidate_count(aspect)
                or len(phrases.get(aspect, [])),
            )

        priorities = self.engine.compute(stats)

        recommendations: list[Recommendation] = []
        for item in priorities:
            for phrase in phrases.get(item.aspect, []):
                recommendations.append(
                    Recommendation(
                        aspect=item.aspect,
                        phrase=phrase.phrase,
                        action=recommend_action(item.aspect, phrase.phrase),
                        evidence_review_ids=phrase.example_review_ids,
                    )
                )

        return DecisionOutput(
            priorities=priorities,
            phrases={k: v for k, v in phrases.items() if v},
            recommendations=recommendations,
            stats=stats,
            weights=dict(self.engine.weights),
            model_name=model_name,
            n_reviews=len(reviews),
            n_negative_reviews=sum(1 for prediction in predictions
                                   if any(i.sentiment == "negatif" for i in prediction.items)),
        )
