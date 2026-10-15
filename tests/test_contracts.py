"""Pengujian kontrak data antar-lapisan."""

from __future__ import annotations

import pytest

from rra.contracts import (
    ASPECTS,
    SENTIMENTS,
    AspectPriority,
    AspectSentiment,
    CleanReview,
    ComplaintPhrase,
    Prediction,
    RawReview,
    Recommendation,
    TrainingExample,
)


def test_taxonomy_is_fixed_and_ordered() -> None:
    assert ASPECTS == ("makanan", "pelayanan", "harga", "suasana", "fasilitas")
    assert SENTIMENTS == ("positif", "negatif", "netral")


def test_raw_review_is_immutable() -> None:
    review = RawReview(review_id="R1", text="makanan hambar")
    with pytest.raises(Exception):
        review.text = "berubah"


def test_clean_review_keeps_original_text() -> None:
    review = CleanReview(review_id="R1", text_raw="Makanannya tidak enak!!",
                         text_clean="makanan tidak_enak")
    assert review.text_raw != review.text_clean


def test_clean_review_serialises_clauses() -> None:
    review = CleanReview(review_id="R1", text_raw="a", text_clean="b",
                         clauses=("makanan hambar", "harga mahal"))
    assert review.as_dict()["clauses"] == "makanan hambar | harga mahal"


def test_training_example_supports_many_aspects() -> None:
    example = TrainingExample(
        review_id="R1", text="makanan hambar harga mahal",
        aspects=("makanan", "harga"),
        sentiments={"makanan": "negatif", "harga": "negatif"},
    )
    assert len(example.aspects) == 2


def test_prediction_exposes_aspects_and_lookup() -> None:
    prediction = Prediction(
        review_id="R1",
        items=[AspectSentiment("makanan", "negatif", 0.9),
               AspectSentiment("harga", "positif", 0.6)],
    )
    assert set(prediction.aspects) == {"makanan", "harga"}
    assert prediction.sentiment_of("harga") == "positif"
    assert prediction.sentiment_of("suasana") is None


def test_aspect_priority_is_immutable_and_explainable() -> None:
    item = AspectPriority(aspect="makanan", label="Makanan", rank=1, priority=0.8,
                          volume=1.0, severity=0.5, diversity=1.0,
                          n_negative=10, n_total=12)
    line = item.explain({"volume": 0.4, "severity": 0.4, "diversity": 0.2})
    assert "Makanan" in line and "0.8" in line
    with pytest.raises(Exception):
        item.rank = 2


def test_complaint_phrase_and_recommendation_shapes() -> None:
    phrase = ComplaintPhrase(aspect="makanan", phrase="hambar", frequency=5,
                             tfidf_weight=1.2, score=0.9,
                             example_review_ids=("R1", "R2"))
    assert phrase.example_review_ids == ("R1", "R2")
    rec = Recommendation(aspect="makanan", phrase="hambar", action="Tinjau resep")
    assert rec.evidence_review_ids == ()
