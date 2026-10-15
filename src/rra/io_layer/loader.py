"""Pembacaan, penyimpanan, dan pemeriksaan mutu data ulasan."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Sequence

import pandas as pd

from rra.contracts import CleanReview, RawReview, TrainingExample

REQUIRED_COLUMNS: tuple[str, ...] = ("review_id", "text")


class ReviewLoader:
    """Pembaca data ulasan dari berbagai bentuk berkas."""

    @staticmethod
    def from_csv(path: str | Path, **kwargs: Any) -> list[RawReview]:
        frame = pd.read_csv(path, **kwargs)
        return ReviewLoader.from_frame(frame)

    @staticmethod
    def from_jsonl(path: str | Path) -> list[RawReview]:
        records: list[dict[str, Any]] = []
        with open(path, "r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return ReviewLoader.from_records(records)

    @staticmethod
    def from_frame(frame: pd.DataFrame) -> list[RawReview]:
        missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
        if missing:
            raise ValueError(
                f"Kolom wajib tidak ditemukan pada data: {missing}. "
                f"Kolom yang tersedia: {list(frame.columns)}"
            )
        return ReviewLoader.from_records(frame.to_dict(orient="records"))

    @staticmethod
    def from_records(records: Iterable[dict[str, Any]]) -> list[RawReview]:
        reviews: list[RawReview] = []
        for record in records:
            text = str(record.get("text", "")).strip()
            if not text:
                continue
            rating = record.get("rating")
            reviews.append(
                RawReview(
                    review_id=str(record.get("review_id")),
                    text=text,
                    rating=float(rating) if rating is not None and str(rating) != "nan" else None,
                    date=_optional_str(record.get("date")),
                    restaurant=_optional_str(record.get("restaurant")),
                )
            )
        return reviews

    # ------------------------------------------------------------------ #
    @staticmethod
    def to_frame(reviews: Sequence[RawReview | CleanReview]) -> pd.DataFrame:
        return pd.DataFrame([review.as_dict() for review in reviews])

    @staticmethod
    def save_csv(reviews: Sequence[RawReview | CleanReview], path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        ReviewLoader.to_frame(reviews).to_csv(path, index=False)
        return path


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text and text.lower() != "nan" else None


# --------------------------------------------------------------------------- #
# Pemeriksaan mutu data (menjadi bagian dari pelaporan Bab IV)
# --------------------------------------------------------------------------- #

def describe_dataset(reviews: Sequence[RawReview], *, label: str = "dataset") -> dict[str, Any]:
    """Hitung ringkasan mutu data yang dapat langsung dilaporkan."""
    total = len(reviews)
    if total == 0:
        return {"label": label, "total": 0}

    lengths = [len(review.text) for review in reviews]
    ratings = [review.rating for review in reviews if review.rating is not None]
    duplicates = total - len({review.text.strip().lower() for review in reviews})

    summary: dict[str, Any] = {
        "label": label,
        "total": total,
        "duplikat": duplicates,
        "duplikat_persen": round(100.0 * duplicates / total, 2),
        "panjang_rata_rata": round(sum(lengths) / total, 1),
        "panjang_min": min(lengths),
        "panjang_maks": max(lengths),
        "jumlah_rating": len(ratings),
    }
    if ratings:
        summary["rating_rata_rata"] = round(sum(ratings) / len(ratings), 3)
        distribution = pd.Series(ratings).round().value_counts().sort_index()
        summary["sebaran_rating"] = {int(k): int(v) for k, v in distribution.items()}
    restaurants = {review.restaurant for review in reviews if review.restaurant}
    if restaurants:
        summary["jumlah_restoran"] = len(restaurants)
    return summary


def load_training_examples(path: str | Path) -> list[TrainingExample]:
    """Muat data berlabel dari berkas CSV panjang (review_id, text, aspect, sentiment)."""
    frame = pd.read_csv(path)
    required = {"review_id", "text", "aspect", "sentiment"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Kolom label tidak lengkap, kurang: {sorted(missing)}")

    examples: list[TrainingExample] = []
    for review_id, group in frame.groupby("review_id", sort=False):
        aspects = tuple(dict.fromkeys(group["aspect"].astype(str)))
        sentiments = {
            str(row.aspect): str(row.sentiment)
            for row in group.itertuples()
        }
        examples.append(
            TrainingExample(
                review_id=str(review_id),
                text=str(group.iloc[0]["text"]),
                aspects=aspects,
                sentiments=sentiments,
            )
        )
    return examples
