"""LAPISAN 2 — Praproses teks.

Modul ini mengubah :class:`~rra.contracts.RawReview` menjadi
:class:`~rra.contracts.CleanReview`. Kontraknya sederhana: masuk teks
mentah, keluar teks bersih. Tidak ada modul lain yang perlu tahu
bagaimana pembersihan dilakukan.
"""

from rra.preprocess.cleaner import TextCleaner, clean_dataframe  # noqa: F401
from rra.preprocess.resources import (  # noqa: F401
    ASPECT_KEYWORDS,
    EMOJI_MAP,
    NEGATION_WORDS,
    SLANG_MAP,
    STOPWORDS,
)

__all__ = [
    "TextCleaner",
    "clean_dataframe",
    "SLANG_MAP",
    "EMOJI_MAP",
    "STOPWORDS",
    "NEGATION_WORDS",
    "ASPECT_KEYWORDS",
]
