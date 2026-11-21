"""Pengujian modul evaluasi — sumber angka pada Bab IV."""

from __future__ import annotations

import pytest

from rra.contracts import AspectSentiment, Prediction
from rra.evaluate import (
    cross_validate,
    evaluate_phrase_quality,
    multilabel_metrics,
    precision_at_k,
    sentiment_metrics,
)
from rra.models.registry import get_model_class

pytestmark = pytest.mark.kasus("I-01")


def test_multilabel_metrics_perfect_prediction() -> None:
    truth = [["makanan"], ["harga"], ["makanan", "harga"]]
    scores = multilabel_metrics(truth, truth)
    assert scores["micro_f1"] == 1.0
    assert scores["macro_f1_aktif"] == 1.0
    assert scores["hamming_loss"] == 0.0
    assert scores["subset_accuracy"] == 1.0


def test_macro_f1_counts_absent_aspects_as_zero() -> None:
    """Angka utama sengaja ketat: aspek yang tak pernah dikenali tetap nol."""
    truth = [["makanan"], ["makanan"]]
    scores = multilabel_metrics(truth, truth)
    assert scores["macro_f1"] < 1.0
    assert scores["macro_f1_aktif"] == 1.0
    assert scores["aspek_dinilai"] == ["makanan"]


def test_multilabel_metrics_reports_every_aspect() -> None:
    scores = multilabel_metrics([["makanan"]], [["makanan"]])
    assert set(scores["per_aspect"]) == {"makanan", "pelayanan", "harga", "suasana", "fasilitas"}


def test_multilabel_metrics_detects_missing_label() -> None:
    scores = multilabel_metrics([["makanan", "harga"]], [["makanan"]])
    assert scores["macro_recall"] < 1.0
    assert scores["per_aspect"]["harga"]["recall"] == 0.0


def test_sentiment_metrics_only_compares_shared_aspects() -> None:
    truth = [{"makanan": "negatif"}]
    predictions = [Prediction("R1", [AspectSentiment("makanan", "negatif", 0.9)])]
    scores = sentiment_metrics(truth, predictions)
    assert scores["accuracy"] == 1.0
    assert scores["n_pasangan"] == 1


def test_sentiment_metrics_ignores_unpredicted_aspect() -> None:
    truth = [{"makanan": "negatif", "harga": "positif"}]
    predictions = [Prediction("R1", [AspectSentiment("makanan", "negatif", 0.9)])]
    scores = sentiment_metrics(truth, predictions)
    assert scores["n_pasangan"] == 1


def test_sentiment_metrics_handles_empty_input() -> None:
    scores = sentiment_metrics([], [])
    assert scores["accuracy"] == 0.0 and scores["n_pasangan"] == 0


def test_cross_validate_reports_every_fold(small_labels) -> None:
    texts, aspects, sentiments = small_labels
    report = cross_validate(lambda: get_model_class("svm")(), texts, aspects, sentiments, folds=4)
    assert report["folds"] == 4
    assert len(report["per_fold"]) == 4
    assert len(report["macro_f1_aspect"]) == 4
    assert 0.0 <= report["summary"]["aspect_macro_f1_mean"] <= 1.0


def test_cross_validate_is_reproducible(small_labels) -> None:
    texts, aspects, sentiments = small_labels
    first = cross_validate(lambda: get_model_class("svm")(), texts, aspects, sentiments,
                            folds=4, seed=11)
    second = cross_validate(lambda: get_model_class("svm")(), texts, aspects, sentiments,
                             folds=4, seed=11)
    assert first["macro_f1_aspect"] == second["macro_f1_aspect"]


def test_precision_at_k_counts_exact_match() -> None:
    result = precision_at_k(["pelayanan lambat", "harga mahal"], ["pelayanan lambat"], k=5)
    assert result["hits"] == 1
    assert result["precision"] == 0.5


def test_precision_at_k_allows_subphrase_match() -> None:
    result = precision_at_k(["pelayanan lambat sekali"], ["pelayanan lambat"], k=5)
    assert result["hits"] == 1


def test_precision_at_k_respects_k_limit() -> None:
    result = precision_at_k(["a", "b", "c"], ["c"], k=2)
    assert result["hits"] == 0
    assert result["precision"] == 0.0


def test_precision_at_k_handles_empty_input() -> None:
    assert precision_at_k([], ["apa saja"])["precision"] == 0.0


def test_evaluate_phrase_quality_averages_aspects() -> None:
    class Item:
        def __init__(self, phrase: str) -> None:
            self.phrase = phrase

    phrases = {"makanan": [Item("makanan hambar")], "harga": [Item("harga mahal")]}
    gold = {"makanan": ["hambar"], "harga": ["tidak ada"]}
    result = evaluate_phrase_quality(phrases, gold, k=5)
    assert result["mean_precision"] == 0.5
