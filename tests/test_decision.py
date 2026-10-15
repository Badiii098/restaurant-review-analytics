"""Pengujian Lapisan 4 — modul keputusan yang eksplisit dan dapat diaudit."""

from __future__ import annotations

import pytest

from rra.contracts import SEVERITY_DEFAULT
from rra.decision.phrases import ComplaintPhraseExtractor
from rra.decision.polarity import clause_polarity, is_complaint_clause
from rra.decision.priority import AspectStat, PriorityEngine, minmax_normalize
from rra.decision.rules import FALLBACK, recommend_action, rules_for
from rra.decision.severity import review_severity, severity_map
from rra.contracts import RawReview


# --------------------------------------------------------------------------- #
# Keparahan
# --------------------------------------------------------------------------- #

def test_severity_maps_one_star_to_maximum() -> None:
    assert review_severity(1) == 1.0


def test_severity_maps_five_stars_to_zero() -> None:
    assert review_severity(5) == 0.0


def test_severity_is_monotonic_decreasing() -> None:
    values = [review_severity(rating) for rating in (1, 2, 3, 4, 5)]
    assert values == sorted(values, reverse=True)


def test_severity_without_rating_uses_default() -> None:
    assert review_severity(None) == SEVERITY_DEFAULT


def test_severity_is_clamped_outside_range() -> None:
    assert review_severity(0) == 1.0
    assert review_severity(99) == 0.0


def test_severity_map_keys_by_review_id() -> None:
    reviews = [
        RawReview(review_id="R1", text="a", rating=1),
        RawReview(review_id="R2", text="b", rating=None),
    ]
    mapping = severity_map(reviews)
    assert mapping["R1"] == 1.0
    assert mapping["R2"] == SEVERITY_DEFAULT


# --------------------------------------------------------------------------- #
# Skor prioritas
# --------------------------------------------------------------------------- #

def test_minmax_normalize_spans_zero_to_one() -> None:
    assert minmax_normalize({"a": 10, "b": 20}) == {"a": 0.0, "b": 1.0}


def test_minmax_normalize_handles_zero_span() -> None:
    assert minmax_normalize({"a": 5, "b": 5}) == {"a": 1.0, "b": 1.0}


def test_minmax_normalize_handles_empty_input() -> None:
    assert minmax_normalize({}) == {}


def test_weights_are_normalised_to_one() -> None:
    engine = PriorityEngine({"volume": 2, "severity": 2, "diversity": 1})
    assert round(sum(engine.weights.values()), 6) == 1.0
    assert engine.weights["diversity"] == pytest.approx(0.2)


def test_formula_is_applied_exactly() -> None:
    """Prioritas = w1*Volume + w2*Keparahan + w3*Keragaman, tanpa normalisasi keparahan."""
    engine = PriorityEngine({"volume": 0.5, "severity": 0.3, "diversity": 0.2})
    stats = {
        "makanan": AspectStat("makanan", n_total=10, n_negative=10,
                              severities=[0.5] * 10, n_phrases=2),
        "pelayanan": AspectStat("pelayanan", n_total=10, n_negative=0,
                                severities=[], n_phrases=1),
    }
    ranked = engine.compute(stats)
    assert [item.aspect for item in ranked] == ["makanan", "pelayanan"]
    top = ranked[0]
    expected = 0.5 * 1.0 + 0.3 * 0.5 + 0.2 * 1.0
    assert top.priority == pytest.approx(expected, abs=1e-6)
    # Keparahan tetap apa adanya, tidak disetarakan ke rentang [0, 1]
    assert top.severity == pytest.approx(0.5)


def test_ranks_are_sequential_and_unique() -> None:
    stats = {
        aspect: AspectStat(aspect, n_total=5, n_negative=n, severities=[0.5] * n, n_phrases=1)
        for aspect, n in zip(("makanan", "pelayanan", "harga", "suasana", "fasilitas"),
                             (5, 4, 3, 2, 1), strict=True)
    }
    ranked = PriorityEngine().compute(stats)
    assert [item.rank for item in ranked] == [1, 2, 3, 4, 5]
    assert [item.aspect for item in ranked][0] == "makanan"


def test_ties_broken_deterministically() -> None:
    stats = {
        "makanan": AspectStat("makanan", n_total=3, n_negative=3, severities=[0.5] * 3, n_phrases=1),
        "harga": AspectStat("harga", n_total=3, n_negative=3, severities=[0.5] * 3, n_phrases=1),
    }
    first = [item.aspect for item in PriorityEngine().compute(stats)]
    second = [item.aspect for item in PriorityEngine().compute(stats)]
    assert first == second


def test_explain_line_lists_every_component() -> None:
    stats = {"makanan": AspectStat("makanan", n_total=2, n_negative=2,
                                   severities=[0.5, 0.5], n_phrases=1)}
    engine = PriorityEngine()
    item = engine.compute(stats)[0]
    line = item.explain(engine.weights)
    assert "Volume" in line and "Keparahan" in line and "Keragaman" in line


# --------------------------------------------------------------------------- #
# Aturan rekomendasi
# --------------------------------------------------------------------------- #

def test_recommendation_matches_keyword() -> None:
    action = recommend_action("pelayanan", "pelayanan lambat")
    assert "tenaga kerja" in action or "alur" in action


def test_recommendation_falls_back_when_no_keyword_matches() -> None:
    assert recommend_action("suasana", "kata yang tidak dikenal") == FALLBACK["suasana"]


def test_every_aspect_has_rules_and_fallback() -> None:
    for aspect in ("makanan", "pelayanan", "harga", "suasana", "fasilitas"):
        assert rules_for(aspect)
        assert FALLBACK[aspect]
        assert recommend_action(aspect, "zzz")


def test_unknown_aspect_still_returns_action() -> None:
    assert recommend_action("aspek_baru", "apa saja")


# --------------------------------------------------------------------------- #
# Polaritas klausa
# --------------------------------------------------------------------------- #

def test_positive_clause_detected() -> None:
    assert clause_polarity("pelayanan ramah cepat") > 0
    assert not is_complaint_clause("pelayanan ramah cepat")


def test_negative_clause_detected() -> None:
    assert clause_polarity("pelayanan lambat cuek") < 0
    assert is_complaint_clause("pelayanan lambat cuek")


def test_negated_positive_becomes_complaint() -> None:
    assert is_complaint_clause("makanan tidak_enak")


def test_neutral_clause_is_not_complaint() -> None:
    assert clause_polarity("pesanan datang") == 0
    assert not is_complaint_clause("pesanan datang")


# --------------------------------------------------------------------------- #
# Ekstraksi frasa keluhan
# --------------------------------------------------------------------------- #

@pytest.fixture()
def extractor() -> ComplaintPhraseExtractor:
    return ComplaintPhraseExtractor(top_k=3, ngram_max=3, min_freq=2)


def test_extracts_complaint_phrase(extractor: ComplaintPhraseExtractor) -> None:
    docs = {
        "pelayanan": [
            ("R1", ["pelayanan lambat", "tempatnya nyaman"]),
            ("R2", ["pelayanan lambat sekali"]),
            ("R3", ["pelayanan lambat banget"]),
        ]
    }
    result = extractor.extract_all(docs)
    phrases = [item.phrase for item in result["pelayanan"]]
    assert "pelayanan lambat" in phrases
    # Klausa pujian tidak boleh masuk daftar keluhan
    assert not any("nyaman" in phrase for phrase in phrases)


def test_aspect_marker_alone_is_not_a_phrase(extractor: ComplaintPhraseExtractor) -> None:
    docs = {"harga": [("R1", ["harga mahal"]), ("R2", ["harga mahal"]),
                      ("R3", ["harga mahal"])]}
    phrases = [item.phrase for item in extractor.extract_all(docs)["harga"]]
    assert "harga" not in phrases
    assert "mahal" in phrases


def test_keyword_matching_respects_word_boundaries(extractor: ComplaintPhraseExtractor) -> None:
    """``menu`` tidak boleh cocok dengan ``menunggu``."""
    docs = {
        "makanan": [
            ("R1", ["menunggu lama", "makanan hambar"]),
            ("R2", ["menunggu lama", "makanan hambar"]),
            ("R3", ["menunggu lama", "makanan hambar"]),
        ]
    }
    phrases = [item.phrase for item in extractor.extract_all(docs)["makanan"]]
    assert any("hambar" in phrase for phrase in phrases)
    assert not any("menunggu" in phrase for phrase in phrases)


def test_scores_are_normalised_within_aspect(extractor: ComplaintPhraseExtractor) -> None:
    docs = {"makanan": [(f"R{i}", ["makanan hambar", "kuah asin"]) for i in range(5)]}
    items = extractor.extract_all(docs)["makanan"]
    assert items
    assert max(item.score for item in items) == pytest.approx(1.0)


def test_phrases_are_sorted_by_score(extractor: ComplaintPhraseExtractor) -> None:
    docs = {"makanan": [(f"R{i}", ["makanan hambar", "kuah asin", "porsi sedikit"])
                        for i in range(6)]}
    items = extractor.extract_all(docs)["makanan"]
    scores = [item.score for item in items]
    assert scores == sorted(scores, reverse=True)


def test_example_review_ids_are_attached(extractor: ComplaintPhraseExtractor) -> None:
    docs = {"makanan": [(f"R{i}", ["makanan hambar"]) for i in range(4)]}
    items = extractor.extract_all(docs)["makanan"]
    assert items[0].example_review_ids
    assert all(rid.startswith("R") for rid in items[0].example_review_ids)


def test_low_frequency_phrases_are_filtered(extractor: ComplaintPhraseExtractor) -> None:
    docs = {"makanan": [("R1", ["makanan hambar"])]}
    assert extractor.extract_all(docs)["makanan"] == []


def test_empty_input_yields_empty_result(extractor: ComplaintPhraseExtractor) -> None:
    assert extractor.extract_all({"makanan": []})["makanan"] == []
