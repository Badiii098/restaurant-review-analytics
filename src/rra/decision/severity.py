"""Penghitungan tingkat keparahan ulasan.

Tingkat keparahan diturunkan dari rating bintang, karena bintang adalah
satu-satunya isyarat tingkat kepuasan yang tersedia secara luas dan
tidak bergantung pada model. Pendekatan ini dipilih secara sengaja:
komponen keputusan tidak boleh sepenuhnya bergantung pada keluaran
model, agar kesalahan model tidak merambat tanpa kendali.
"""

from __future__ import annotations

from typing import Mapping, Sequence

from rra.contracts import SEVERITY_DEFAULT, RawReview

RATING_MIN = 1.0
RATING_MAX = 5.0


def review_severity(rating: float | None, *, default: float = SEVERITY_DEFAULT) -> float:
    """Ubah rating bintang menjadi tingkat keparahan pada rentang [0, 1].

    Bintang 1 menghasilkan keparahan 1,0 (paling parah) dan bintang 5
    menghasilkan 0,0. Rumusnya:

        Keparahan(u) = (RATING_MAX - rating(u)) / (RATING_MAX - RATING_MIN)
    """
    if rating is None:
        return float(default)
    clamped = min(RATING_MAX, max(RATING_MIN, float(rating)))
    return round((RATING_MAX - clamped) / (RATING_MAX - RATING_MIN), 6)


def severity_map(
    reviews: Sequence[RawReview],
    *,
    default: float = SEVERITY_DEFAULT,
) -> dict[str, float]:
    """Pemetaan ``review_id`` ke tingkat keparahan."""
    return {review.review_id: review_severity(review.rating, default=default) for review in reviews}


def mean_severity(severities: Sequence[float]) -> float:
    """Rata-rata keparahan; mengembalikan 0 bila tidak ada data."""
    values = [float(value) for value in severities]
    return round(sum(values) / len(values), 6) if values else 0.0


class SeverityScale:
    """Skala keparahan yang dapat dikonfigurasi (mis. bila bintang 0-10)."""

    def __init__(self, minimum: float = RATING_MIN, maximum: float = RATING_MAX,
                 default: float = SEVERITY_DEFAULT) -> None:
        if maximum <= minimum:
            raise ValueError("Nilai maksimum harus lebih besar daripada minimum.")
        self.minimum = float(minimum)
        self.maximum = float(maximum)
        self.default = float(default)

    def of(self, rating: float | None) -> float:
        if rating is None:
            return self.default
        clamped = min(self.maximum, max(self.minimum, float(rating)))
        return round((self.maximum - clamped) / (self.maximum - self.minimum), 6)

    def for_reviews(self, reviews: Sequence[RawReview]) -> Mapping[str, float]:
        return {review.review_id: self.of(review.rating) for review in reviews}
