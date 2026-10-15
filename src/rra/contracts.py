"""Kontrak data antar-lapisan.

Seluruh objek yang berpindah dari satu lapisan ke lapisan lain
didefinisikan di sini. Dengan menetapkan bentuk data pada satu tempat,
setiap lapisan dapat diuji dan diganti secara terpisah — persis seperti
yang dituntut oleh prinsip *information hiding* (Parnas, 1972).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# --------------------------------------------------------------------------- #
# Taksonomi tetap (lihat Sub-bab 2.1.6 — kerangka DINESERV)
# --------------------------------------------------------------------------- #

ASPECTS: tuple[str, ...] = ("makanan", "pelayanan", "harga", "suasana", "fasilitas")

ASPECT_LABELS: dict[str, str] = {
    "makanan": "Makanan",
    "pelayanan": "Pelayanan",
    "harga": "Harga",
    "suasana": "Suasana",
    "fasilitas": "Fasilitas",
}

SENTIMENTS: tuple[str, ...] = ("positif", "negatif", "netral")

#: Nilai keparahan awal bila rating bintang tidak tersedia.
SEVERITY_DEFAULT: float = 0.5


# --------------------------------------------------------------------------- #
# LAPISAN 1 — Data
# --------------------------------------------------------------------------- #

@dataclass(slots=True, frozen=True)
class RawReview:
    """Satu ulasan sebagaimana diambil dari sumbernya, belum diolah."""

    review_id: str
    text: str
    rating: float | None = None
    date: str | None = None
    restaurant: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "review_id": self.review_id,
            "text": self.text,
            "rating": self.rating,
            "date": self.date,
            "restaurant": self.restaurant,
        }


# --------------------------------------------------------------------------- #
# LAPISAN 2 — Praproses
# --------------------------------------------------------------------------- #

@dataclass(slots=True, frozen=True)
class CleanReview:
    """Ulasan setelah praproses. Menyimpan teks asli agar dapat ditelusuri."""

    review_id: str
    text_raw: str
    text_clean: str
    rating: float | None = None
    date: str | None = None
    restaurant: str | None = None
    clauses: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "review_id": self.review_id,
            "text_raw": self.text_raw,
            "text_clean": self.text_clean,
            "rating": self.rating,
            "date": self.date,
            "restaurant": self.restaurant,
            "clauses": " | ".join(self.clauses),
        }


@dataclass(slots=True, frozen=True)
class TrainingExample:
    """Contoh berlabel untuk melatih komponen model.

    Sejalan dengan unit analisis "satu ulasan = banyak aspek", satu contoh
    dapat memuat lebih dari satu aspek beserta sentimennya masing-masing.
    """

    review_id: str
    text: str
    aspects: tuple[str, ...]
    sentiments: dict[str, str] = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# LAPISAN 3 — Keluaran komponen model
# --------------------------------------------------------------------------- #

@dataclass(slots=True, frozen=True)
class AspectSentiment:
    """Satu pasangan (aspek, sentimen) beserta tingkat keyakinan model."""

    aspect: str
    sentiment: str
    confidence: float = 0.0


@dataclass(slots=True)
class Prediction:
    """Hasil klasifikasi satu ulasan."""

    review_id: str
    items: list[AspectSentiment] = field(default_factory=list)

    @property
    def aspects(self) -> list[str]:
        return [item.aspect for item in self.items]

    def sentiment_of(self, aspect: str) -> str | None:
        for item in self.items:
            if item.aspect == aspect:
                return item.sentiment
        return None


# --------------------------------------------------------------------------- #
# LAPISAN 4 — Keluaran modul keputusan
# --------------------------------------------------------------------------- #

@dataclass(slots=True, frozen=True)
class ComplaintPhrase:
    """Frasa keluhan dominan pada satu aspek.

    Istilah "dominan" dipilih secara sengaja: skor di sini mengukur
    seberapa menonjol sebuah frasa, **bukan** membuktikan hubungan
    sebab-akibat. Lihat Sub-bab 1.3 butir 3.
    """

    aspect: str
    phrase: str
    frequency: int
    tfidf_weight: float
    score: float
    example_review_ids: tuple[str, ...] = ()


@dataclass(slots=True, frozen=True)
class AspectPriority:
    """Skor prioritas satu aspek beserta komponen pembentuknya.

    Seluruh komponen disimpan agar setiap angka dapat ditelusuri asalnya —
    inilah sifat *dapat diaudit* yang menjadi salah satu kebaruan penelitian.
    """

    aspect: str
    label: str
    rank: int
    priority: float
    volume: float
    severity: float
    diversity: float
    n_negative: int
    n_total: int

    def explain(self, weights: dict[str, float]) -> str:
        return (
            f"{self.label}: prioritas {self.priority:.4f} = "
            f"{weights.get('volume', 0):.1f}xVolume({self.volume:.4f}) + "
            f"{weights.get('severity', 0):.1f}xKeparahan({self.severity:.4f}) + "
            f"{weights.get('diversity', 0):.1f}xKeragaman({self.diversity:.4f})"
        )


@dataclass(slots=True, frozen=True)
class Recommendation:
    """Rekomendasi tindakan yang bersesuaian dengan aspek dan frasa keluhan."""

    aspect: str
    phrase: str
    action: str
    evidence_review_ids: tuple[str, ...] = ()


@dataclass(slots=True)
class AnalysisResult:
    """Bungkusan lengkap keluaran satu kali analisis."""

    model_name: str = ""
    n_reviews: int = 0
    priorities: list[AspectPriority] = field(default_factory=list)
    phrases: dict[str, list[ComplaintPhrase]] = field(default_factory=dict)
    recommendations: list[Recommendation] = field(default_factory=list)
