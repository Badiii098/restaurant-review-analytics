"""Pengujian Lapisan 2 — praproses teks."""

from __future__ import annotations

import pytest

from rra.preprocess.cleaner import TextCleaner, ngrams
from rra.preprocess.resources import CLAUSE_CONNECTORS

pytestmark = pytest.mark.kasus("U-02")


@pytest.fixture()
def cleaner() -> TextCleaner:
    return TextCleaner()


def test_lowercase_and_punctuation_removed(cleaner: TextCleaner) -> None:
    result = cleaner.clean("Makanannya ENAK banget!!!")
    assert result == result.lower()
    assert "!" not in result


def test_elongation_collapsed(cleaner: TextCleaner) -> None:
    assert "enak" in cleaner.clean("enakkkkk banget")


def test_slang_normalised(cleaner: TextCleaner) -> None:
    assert "tidak" in cleaner.clean("gak enak")


def test_negation_marks_following_word(cleaner: TextCleaner) -> None:
    result = cleaner.clean("makanannya tidak enak")
    assert "tidak_enak" in result


def test_negation_window_stops_at_clause_connector(cleaner: TextCleaner) -> None:
    """Negasi tidak boleh menyeberang ke klausa berikutnya.

    Tanpa aturan ini, kata "bumbunya" ikut ditandai ternyata oleh "kurang",
    padahal keduanya membahas hal yang berbeda.
    """
    result = cleaner.clean("rasanya kurang tapi bumbunya meresap")
    assert "bumbunya" in result
    assert "tidak_bumbunya" not in result


def test_negation_does_not_chain_across_words(cleaner: TextCleaner) -> None:
    """Negasi hanya menandai satu kata, bukan seluruh kata sesudahnya.

    Sebelum perbaikan, "tidak datang parkirnya juga susah" menghasilkan
    "tidak_datang", "tidak_parkirnya", dan "tidak_juga" sekaligus. Penanda
    semacam "tidak_juga" tidak ada dalam bahasa Indonesia dan mengotori
    fitur yang dipelajari model.
    """
    result = cleaner.clean("tidak datang parkirnya juga susah")
    assert "tidak_datang" in result
    assert "tidak_juga" not in result
    assert "tidak_parkirnya" not in result


def test_clause_split_on_punctuation_and_connectors(cleaner: TextCleaner) -> None:
    clauses = cleaner.clauses("Makanannya hambar. Pelayanannya ramah, tapi toiletnya kotor")
    assert len(clauses) >= 3
    assert any("hambar" in clause for clause in clauses)
    assert any("toiletnya kotor" in clause for clause in clauses)


def test_clean_clauses_are_individually_cleaned(cleaner: TextCleaner) -> None:
    clauses = cleaner.clean_clauses("Makanannya tidak enak, tempatnya nyaman")
    assert any("tidak_enak" in clause for clause in clauses)
    assert all(clause == clause.lower() for clause in clauses)


def test_clause_connectors_are_removed_from_clean_text(cleaner: TextCleaner) -> None:
    result = cleaner.clean("makanan enak dan harga murah")
    for connector in CLAUSE_CONNECTORS:
        assert connector not in result.split()


def test_trace_covers_all_stages(cleaner: TextCleaner) -> None:
    stages = cleaner.trace("Makannya gak enak bgt 🙏")
    assert set(stages) >= {"00_mentah", "01_lowercase", "07_tanda_baca", "08_negasi", "10_final"}
    assert stages["00_mentah"] != stages["10_final"]


def test_ngrams_respects_length() -> None:
    assert ngrams(["a", "b", "c"], 2) == [("a", "b"), ("b", "c")]
    assert ngrams(["a"], 2) == []
    assert ngrams(["a", "b"], 0) == []


def test_empty_input_is_safe(cleaner: TextCleaner) -> None:
    assert cleaner.clean("") == ""
    assert cleaner.clauses("") == []
    assert cleaner.clean_clauses("") == []
