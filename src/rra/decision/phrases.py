"""Ekstraksi frasa keluhan dominan.

Metode yang dipakai adalah gabungan **frekuensi kemunculan** dan
**bobot TF-IDF**, dihitung terpisah untuk setiap aspek layanan.

Pilihan ini disengaja. Pendekatan berbasis frekuensi bersifat transparan:
setiap frasa yang muncul di peringkat teratas dapat ditelusuri langsung
ke ulasan asalnya dengan membaca teks aslinya. Pada sistem pendukung
keputusan yang arketipenya *advisory*, sifat dapat ditelusuri ini lebih
bernilai daripada kecanggihan metode.

**Batas klaim.** Frasa yang paling sering muncul bukanlah bukti penyebab
suatu persoalan. Modul ini mengukur seberapa *menonjol* sebuah frasa,
bukan seberapa besar *pengaruhnya*. Karena itu istilah yang dipakai
adalah "frasa keluhan dominan", bukan "akar masalah".
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Iterable, Mapping, Sequence

from rra.contracts import ComplaintPhrase
from rra.decision.polarity import is_complaint_clause
from rra.preprocess.cleaner import ngrams
from rra.preprocess.resources import ASPECT_KEYWORDS, ASPECT_NOUNS

#: Kata penghubung yang tidak boleh menjadi bagian frasa.
FORBIDDEN_TOKENS: frozenset[str] = frozenset(
    {"namun", "tetapi", "tapi", "cuma", "sayangnya", "sedangkan", "dan", "atau", "juga", "sih"}
)

#: Kata benda penanda aspek; frasa satu kata berupa kata ini dibuang karena
#: hanya mengulang nama aspeknya sendiri (mis. "harga" pada aspek harga).
ASPECT_MARKER_TOKENS: frozenset[str] = frozenset(ASPECT_NOUNS)

#: Akhiran yang boleh mengikuti kata penanda aspek pada pencocokan klausa.
_ALLOWED_SUFFIXES: frozenset[str] = frozenset({"nya", "ku", "mu", "lah", "kah"})


def display_phrase(phrase: str) -> str:
    """Ubah frasa menjadi bentuk yang dibaca manusia.

    Tahap negasi pada praproses menyatukan kata ``tidak`` dengan kata yang
    dinegasikannya memakai garis bawah (``tidak_meresap``) agar keduanya
    terhitung sebagai satu satuan. Garis bawah itu penting bagi penghitungan,
    tetapi tidak layak ditampilkan pada laporan, sehingga diganti spasi.
    """
    return phrase.replace("_", " ")


class ComplaintPhraseExtractor:
    """Peringkat frasa keluhan untuk setiap aspek.

    Parameters
    ----------
    top_k:
        Jumlah frasa teratas yang dikembalikan untuk setiap aspek (=*K*
        pada pengukuran Precision@K).
    ngram_max:
        Panjang frasa maksimum dalam satuan kata.
    min_freq:
        Frekuensi dokumen minimum agar sebuah frasa dipertimbangkan.
        Menyaring frasa yang muncul sekali karena kebetulan.
    length_bonus:
        Bobot tambahan untuk frasa yang lebih panjang. Frasa dua kata
        ("pelayanan lambat") jauh lebih informatif daripada satu kata
        ("lambat"), sehingga diberi sedikit keunggulan.
    """

    def __init__(
        self,
        *,
        top_k: int = 5,
        ngram_max: int = 3,
        min_freq: int = 3,
        length_bonus: float = 0.15,
    ) -> None:
        self.top_k = int(top_k)
        self.ngram_max = int(ngram_max)
        self.min_freq = int(min_freq)
        self.length_bonus = float(length_bonus)
        #: Banyaknya frasa berbeda yang lolos ambang frekuensi untuk setiap
        #: aspek, **sebelum** dipotong menjadi ``top_k``. Angka ini dipakai
        #: sebagai komponen "keragaman" pada skor prioritas; memakai jumlah
        #: frasa teratas tidak berguna karena pemotongan membuat seluruh
        #: aspek bernilai sama.
        self._candidate_counts: dict[str, int] = {}

    def candidate_count(self, aspect: str) -> int:
        """Banyaknya frasa keluhan berbeda yang ditemukan untuk satu aspek."""
        return self._candidate_counts.get(aspect, 0)

    @classmethod
    def from_config(cls, cfg) -> "ComplaintPhraseExtractor":
        decision = cfg.get("decision", {}) or {}
        return cls(
            top_k=int(decision.get("top_k_phrases", 5)),
            ngram_max=int(decision.get("phrase_ngram_max", 3)),
            min_freq=int(decision.get("min_phrase_freq", 3)),
        )

    # ------------------------------------------------------------------ #
    def extract_all(
        self,
        docs_by_aspect: Mapping[str, Sequence[tuple[str, Sequence[str]]]],
    ) -> dict[str, list[ComplaintPhrase]]:
        """Peringkat frasa untuk seluruh aspek sekaligus.

        Parameters
        ----------
        docs_by_aspect:
            Pemetaan aspek ke daftar pasangan ``(review_id, klausa)``, dengan
            ``klausa`` berupa deret klausa bersih dari ulasan yang bersentimen
            negatif pada aspek tersebut.

        Catatan rancangan
        -----------------
        Penghitungan **tidak** dilakukan atas seluruh teks ulasan, melainkan
        hanya atas klausa yang memuat kata penanda aspek bersangkutan.
        Tanpa pembatasan ini, frasa yang muncul dominan hanyalah kata yang
        paling sering muncul di seluruh ulasan — bukan keluhan tentang aspek
        tersebut. Bila tidak ada klausa yang cocok, seluruh klausa ulasan
        dipakai agar tidak ada ulasan yang hilang dari penghitungan; keadaan
        ini disengaja dan bukan kegagalan.
        """
        counts: dict[str, Counter[str]] = {}
        examples: dict[str, dict[str, list[str]]] = {}

        for aspect, docs in docs_by_aspect.items():
            counter: Counter[str] = Counter()
            example_map: dict[str, list[str]] = {}

            for review_id, clauses in self._select_clauses(aspect, docs):
                for phrase in self._candidates(clauses):
                    counter[phrase] += 1
                    bucket = example_map.setdefault(phrase, [])
                    if len(bucket) < 3:
                        bucket.append(review_id)
            counts[aspect] = counter
            examples[aspect] = example_map

        total_docs = sum(len(docs) for docs in docs_by_aspect.values())
        document_frequency: Counter[str] = Counter()
        for counter in counts.values():
            document_frequency.update(counter)

        results: dict[str, list[ComplaintPhrase]] = {}
        for aspect, counter in counts.items():
            scored: list[tuple[float, str, int, float]] = []
            for phrase, frequency in counter.items():
                if frequency < self.min_freq:
                    continue
                weight = self._tfidf(frequency, document_frequency[phrase], total_docs)
                n_tokens = phrase.count(" ") + 1
                score = weight * (1.0 + self.length_bonus * (n_tokens - 1))
                scored.append((score, phrase, frequency, weight))

            self._candidate_counts[aspect] = len(scored)
            scored.sort(key=lambda item: (-item[0], item[1]))
            top = scored[: self.top_k]
            peak = top[0][0] if top else 0.0

            results[aspect] = [
                ComplaintPhrase(
                    aspect=aspect,
                    phrase=display_phrase(phrase),
                    frequency=frequency,
                    tfidf_weight=round(weight, 6),
                    score=round(score / peak, 6) if peak > 0 else 0.0,
                    example_review_ids=tuple(examples[aspect].get(phrase, [])),
                )
                for score, phrase, frequency, weight in top
            ]
        return results

    # ------------------------------------------------------------------ #
    def _select_clauses(
        self,
        aspect: str,
        docs: Sequence[tuple[str, Sequence[str]]],
    ) -> list[tuple[str, list[str]]]:
        """Pilih klausa yang menyumbang frasa keluhan untuk satu aspek.

        Penyaringan dilakukan bertingkat dan **berlaku untuk keseluruhan
        aspek**, bukan per ulasan:

        1. klausa yang memuat kata penanda aspek **dan** bernada keluhan;
        2. bila aspek itu tidak menghasilkan satu pun klausa keluhan,
           seluruh klausa yang memuat kata penanda aspek;
        3. bila masih kosong, seluruh klausa ulasan.

        Tingkat 2 dan 3 adalah jaring pengaman agar sebuah aspek tidak
        menghasilkan daftar kosong hanya karena leksikon tidak mengenali
        satu pun katanya. Berbeda dari penyaringan per ulasan, jaring
        pengaman ini tidak dapat dipakai untuk menyelundupkan kembali
        klausa pujian ke dalam daftar keluhan.
        """
        complaint = [(rid, self._filter(aspect, clauses, complaint_only=True))
                     for rid, clauses in docs]
        if any(selected for _, selected in complaint):
            return complaint

        matched = [(rid, self._filter(aspect, clauses, complaint_only=False))
                   for rid, clauses in docs]
        if any(selected for _, selected in matched):
            return matched

        return [(rid, list(clauses)) for rid, clauses in docs]

    @staticmethod
    def _clause_matches(clause: str, keywords: Sequence[str]) -> bool:
        """Benar bila klausa memuat salah satu kata penanda aspek.

        Pencocokan dilakukan **per kata**, bukan per substring pada seluruh
        klausa. Pencocokan substring pernah dipakai dan terbukti salah:
        kata penanda ``menu`` ikut cocok dengan kata ``menunggu``, sehingga
        klausa tentang pelayanan masuk ke daftar aspek makanan.

        Akhiran pemilik/keterangan (``-nya``, ``-ku``, ``-mu``, ``-lah``)
        tetap diizinkan, sehingga ``tempatnya`` dikenali sebagai ``tempat``.
        """
        if not keywords:
            return True
        tokens = clause.split()
        padded = f" {clause} "
        for keyword in keywords:
            if " " in keyword:
                if f" {keyword} " in padded:
                    return True
                continue
            for token in tokens:
                if token == keyword:
                    return True
                if token.startswith(keyword) and token[len(keyword) :] in _ALLOWED_SUFFIXES:
                    return True
        return False

    @staticmethod
    def _filter(
        aspect: str, clauses: Sequence[str], *, complaint_only: bool
    ) -> list[str]:
        keywords = ASPECT_KEYWORDS.get(aspect, ())
        selected = [
            clause for clause in clauses
            if ComplaintPhraseExtractor._clause_matches(clause, keywords)
        ]
        if complaint_only:
            return [clause for clause in selected if is_complaint_clause(clause)]
        return selected

    def _candidates(self, clauses: Sequence[str]) -> Iterable[str]:
        """Bentuk seluruh kandidat frasa dari deret klausa.

        N-gram tidak dibentuk melintasi batas klausa, sehingga frasa yang
        dihasilkan selalu merupakan rangkaian kata yang berdekatan pada
        teks aslinya.
        """
        seen: set[str] = set()
        for clause in clauses:
            tokens = clause.split()
            for size in range(1, self.ngram_max + 1):
                for gram in ngrams(tokens, size):
                    if not self._valid(gram):
                        continue
                    phrase = " ".join(gram)
                    if phrase not in seen:
                        seen.add(phrase)
                        yield phrase

    def _valid(self, gram: Sequence[str]) -> bool:
        if any(token in FORBIDDEN_TOKENS for token in gram):
            return False
        # Frasa satu kata yang hanya mengulang kata penanda aspeknya sendiri
        # ("harga", "rasanya", "tempatnya") tidak informatif bagi pengelola.
        if len(gram) == 1 and self._is_aspect_marker(gram[0]):
            return False
        # Harus memuat sekurang-kurangnya satu token bermakna
        return any(len(token) > 2 and token not in FORBIDDEN_TOKENS for token in gram)

    @staticmethod
    def _is_aspect_marker(token: str) -> bool:
        """Benar bila token hanyalah kata penanda aspek beserta akhirannya."""
        for keyword in ASPECT_MARKER_TOKENS:
            if token == keyword:
                return True
            if token.startswith(keyword) and token[len(keyword) :] in _ALLOWED_SUFFIXES:
                return True
        return False

    @staticmethod
    def _tfidf(term_frequency: int, document_frequency: int, total_docs: int) -> float:
        """Bobot gabungan frekuensi dan kekhasan frasa.

        Rumusnya:  tf * log(1 + N / df)

        Bagian ``N / df`` membuat frasa yang muncul pada banyak aspek
        (sehingga kurang khas) memperoleh bobot lebih rendah daripada
        frasa yang khas pada satu aspek.
        """
        if term_frequency <= 0 or total_docs <= 0:
            return 0.0
        idf = math.log(1.0 + total_docs / max(document_frequency, 1))
        return float(term_frequency) * idf
