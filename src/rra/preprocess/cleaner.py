"""LAPISAN 2 — Pembersih teks berbahasa Indonesia.

Setiap tahap pembersihan dapat ditelusuri satu per satu melalui
:meth:`TextCleaner.trace`. Sifat dapat ditelusuri ini bukan pelengkap:
salah satu kebaruan penelitian adalah keluaran sistem harus dapat
dipertanggungjawabkan, sehingga perubahan tiap tahap pun harus terlihat.
"""

from __future__ import annotations

import re
from typing import Iterable, Sequence

import pandas as pd

from rra.preprocess.resources import (
    CLAUSE_CONNECTORS,
    EMOJI_MAP,
    NEGATION_WORDS,
    SLANG_MAP,
    STOPWORDS,
)

_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_MENTION_RE = re.compile(r"[@#]\w+")
_ELONGATION_RE = re.compile(r"(.)\1{2,}")
_NON_WORD_RE = re.compile(r"[^a-z0-9_\s]")
_MULTISPACE_RE = re.compile(r"\s+")
#: Batas klausa pada teks mentah: tanda baca pemisah dan kata penghubung.
_CLAUSE_SPLIT_RE = re.compile(
    r"[.!?,;:()\[\]\"']+|\b(?:" + "|".join(sorted(CLAUSE_CONNECTORS)) + r")\b",
    flags=re.IGNORECASE,
)
_EMOJI_RE = re.compile(
    "[" "\U0001F300-\U0001FAFF" "\U00002600-\U000027BF" "\U0001F1E6-\U0001F1FF" "\u2b00-\u2bff" "]+"
)


class TextCleaner:
    """Rangkaian tahap praproses yang dapat dikonfigurasi.

    Parameter diambil dari ``config/default.yaml`` bagian ``preprocess``
    melalui :meth:`from_config`, namun kelas ini juga dapat dipakai
    langsung dengan argumen kata kunci.
    """

    def __init__(
        self,
        *,
        lowercase: bool = True,
        remove_urls: bool = True,
        remove_mentions_hashtags: bool = True,
        remove_numbers: bool = True,
        convert_emoji: bool = True,
        normalize_slang: bool = True,
        handle_negation: bool = True,
        negation_window: int = 3,
        remove_stopwords: bool = True,
        collapse_elongation: bool = True,
        min_token_length: int = 2,
    ) -> None:
        self.lowercase = lowercase
        self.remove_urls = remove_urls
        self.remove_mentions_hashtags = remove_mentions_hashtags
        self.remove_numbers = remove_numbers
        self.convert_emoji = convert_emoji
        self.normalize_slang = normalize_slang
        self.handle_negation = handle_negation
        self.negation_window = int(negation_window)
        self.remove_stopwords = remove_stopwords
        self.collapse_elongation = collapse_elongation
        self.min_token_length = int(min_token_length)

    # ------------------------------------------------------------------ #
    @classmethod
    def from_config(cls, cfg) -> "TextCleaner":
        """Bangun pembersih dari objek :class:`rra.config.Config`."""
        keys = {
            "lowercase", "remove_urls", "remove_mentions_hashtags", "remove_numbers",
            "convert_emoji", "normalize_slang", "handle_negation", "negation_window",
            "remove_stopwords", "collapse_elongation", "min_token_length",
        }
        kwargs = {key: cfg.get(f"preprocess.{key}") for key in keys}
        return cls(**{k: v for k, v in kwargs.items() if v is not None})

    # ------------------------------------------------------------------ #
    # Tahap-tahap pembersihan
    # ------------------------------------------------------------------ #
    def _step_lowercase(self, text: str) -> str:
        return text.lower()

    def _step_urls(self, text: str) -> str:
        return _URL_RE.sub(" ", text)

    def _step_mentions(self, text: str) -> str:
        return _MENTION_RE.sub(" ", text)

    def _step_emoji(self, text: str) -> str:
        def replace(match: re.Match[str]) -> str:
            return " " + " ".join(EMOJI_MAP.get(ch, "") for ch in match.group()) + " "

        return _EMOJI_RE.sub(replace, text)

    def _step_elongation(self, text: str) -> str:
        # "enakkkk" -> "enak" ; huruf yang diulang lebih dari dua kali dipangkas
        return _ELONGATION_RE.sub(r"\1\1", text)

    def _step_slang(self, text: str) -> str:
        return " ".join(SLANG_MAP.get(token, token) for token in text.split())

    def _step_punctuation(self, text: str) -> str:
        text = _NON_WORD_RE.sub(" ", text)
        if self.remove_numbers:
            text = re.sub(r"\b\d+\b", " ", text)
        return text

    def _step_negation(self, text: str) -> str:
        """Tempelkan penanda negasi pada kata yang benar-benar dinegasikan.

        "tidak enak" menjadi "tidak_enak" sehingga model melihat satu
        penanda bermakna, bukan kata positif yang menyesatkan.

        Dua pembatasan diberlakukan:

        1. **Cakupan berhenti pada kata penghubung antarklausa** (dan, tapi,
           namun, cuma, serta). Tanpa aturan ini, jendela tetap akan
           melintasi batas klausa dan menandai kata dari klausa berikutnya
           sebagai ternyata — misalnya "rasanya kurang dan bumbunya gak
           meresap" sempat menandai "bumbunya" sebagai bagian dari negasi
           "kurang", padahal keduanya membahas hal berbeda.
        2. **Hanya kata bermakna terdekat yang ditandai.** Sebelumnya
           seluruh kata dalam jendela ditandai, sehingga "tidak datang
           parkirnya juga susah" menghasilkan "tidak_datang",
           "tidak_parkirnya", dan "tidak_juga" sekaligus. Penandaan
           berantai itu keliru: negasi menyangkut satu kata yang
           dinegasikan, dan penanda seperti "tidak_juga" tidak pernah ada
           dalam bahasa Indonesia. Kata yang dilewati (kata tugas) tetap
           ditulis apa adanya.
        """
        tokens = text.split()
        out: list[str] = []
        index = 0
        while index < len(tokens):
            token = tokens[index]
            if token in NEGATION_WORDS:
                follow = index + 1
                target: int | None = None
                # ``negation_window`` membatasi seberapa jauh ke depan kata
                # yang dinegasikan dicari, sehingga "tidak" yang berdiri
                # sendiri tidak menyerap kata dari kalimat berikutnya.
                while follow < len(tokens) and follow <= index + self.negation_window:
                    if tokens[follow] in CLAUSE_CONNECTORS:
                        break
                    if tokens[follow] not in STOPWORDS:
                        target = follow
                        break
                    follow += 1
                if target is None:
                    # Tidak ada kata bermakna yang tercakup (mis. negasi di
                    # akhir klausa: "rasanya kurang"). Penanda negasi tetap
                    # dipertahankan agar makna kalimat tidak hilang.
                    out.append("tidak")
                    index += 1
                    continue
                out.append(f"tidak_{tokens[target]}")
                index = target + 1
                continue
            out.append(token)
            index += 1
        return " ".join(out)

    def _step_stopwords(self, text: str) -> str:
        kept: list[str] = []
        for token in text.split():
            # token berpenanda negasi selalu dipertahankan
            if "_" in token:
                kept.append(token)
                continue
            if token in STOPWORDS:
                continue
            if len(token) < self.min_token_length:
                continue
            kept.append(token)
        return " ".join(kept)

    # ------------------------------------------------------------------ #
    # Antarmuka publik
    # ------------------------------------------------------------------ #
    def trace(self, text: str) -> dict[str, str]:
        """Kembalikan hasil setiap tahap — dipakai untuk audit & pengujian."""
        stages: list[tuple[str, str]] = [("00_mentah", text)]
        current = text
        pipeline: tuple[tuple[str, bool, str], ...] = (
            ("01_lowercase", self.lowercase, "_step_lowercase"),
            ("02_url", self.remove_urls, "_step_urls"),
            ("03_mention_hashtag", self.remove_mentions_hashtags, "_step_mentions"),
            ("04_emoji", self.convert_emoji, "_step_emoji"),
            ("05_elongasi", self.collapse_elongation, "_step_elongation"),
            ("06_slang", self.normalize_slang, "_step_slang"),
            ("07_tanda_baca", True, "_step_punctuation"),
            ("08_negasi", self.handle_negation, "_step_negation"),
            ("09_stopword", self.remove_stopwords, "_step_stopwords"),
        )
        for label, enabled, method in pipeline:
            if enabled:
                current = getattr(self, method)(current)
            stages.append((label, current))
        stages.append(("10_final", self._finalize(current)))
        return dict(stages)

    def _finalize(self, text: str) -> str:
        return _MULTISPACE_RE.sub(" ", text).strip()

    def clean(self, text: str) -> str:
        """Bersihkan satu teks."""
        if not isinstance(text, str):
            return ""
        if self.lowercase:
            text = self._step_lowercase(text)
        if self.remove_urls:
            text = self._step_urls(text)
        if self.remove_mentions_hashtags:
            text = self._step_mentions(text)
        if self.convert_emoji:
            text = self._step_emoji(text)
        if self.collapse_elongation:
            text = self._step_elongation(text)
        if self.normalize_slang:
            text = self._step_slang(text)
        text = self._step_punctuation(text)
        if self.handle_negation:
            text = self._step_negation(text)
        if self.remove_stopwords:
            text = self._step_stopwords(text)
        return self._finalize(text)

    def clean_many(self, texts: Iterable[str]) -> list[str]:
        return [self.clean(text) for text in texts]

    # ------------------------------------------------------------------ #
    # Pemecahan klausa
    # ------------------------------------------------------------------ #
    def clauses(self, text: str) -> list[str]:
        """Pecah teks mentah menjadi klausa berdasarkan tanda baca dan penghubung.

        Klausa dipakai modul keputusan untuk memastikan frasa keluhan yang
        dilaporkan benar-benar berasal dari bagian ulasan yang membahas
        aspek bersangkutan, bukan dari kalimat lain di ulasan yang sama.
        """
        if not isinstance(text, str) or not text.strip():
            return []
        parts = _CLAUSE_SPLIT_RE.split(text)
        return [part.strip() for part in parts if part and part.strip()]

    def clean_clauses(self, text: str) -> list[str]:
        """Bersihkan setiap klausa; klausa kosong setelah pembersihan dibuang."""
        cleaned = [self.clean(part) for part in self.clauses(text)]
        return [part for part in cleaned if part]


def clean_dataframe(
    frame: pd.DataFrame,
    cleaner: TextCleaner,
    *,
    text_column: str = "text",
    out_column: str = "text_clean",
) -> pd.DataFrame:
    """Tambahkan kolom teks bersih pada sebuah DataFrame."""
    result = frame.copy()
    result[out_column] = result[text_column].astype(str).map(cleaner.clean)
    return result


def tokenize(text: str) -> list[str]:
    """Pemecahan sederhana berbasis spasi (dipakai modul keputusan)."""
    return text.split()


def ngrams(tokens: Sequence[str], n: int) -> list[tuple[str, ...]]:
    """Bentuk n-gram dari daftar token."""
    if n <= 0 or len(tokens) < n:
        return []
    return [tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]
