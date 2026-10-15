"""KONTRAK ANTARMUKA komponen pemodelan.

Kelas abstrak pada modul ini adalah **inti kebaruan penelitian**. Ia
menyatakan secara tegas apa yang dijanjikan sebuah komponen pemodelan,
tanpa menyatakan bagaimana janji itu ditunaikan:

    Masukan  : deretan teks ulasan
    Keluaran : untuk setiap ulasan, daftar pasangan (aspek, sentimen)
               beserta tingkat keyakinan
    Jaminan  : aspek selalu berasal dari taksonomi DINESERV;
               sentimen selalu bernilai positif, negatif, atau netral
    Tidak dijanjikan : algoritma, struktur fitur, maupun bentuk berkas
               model di balik kontrak ini

Konsekuensinya dapat dibuktikan: komponen yang mematuhi kontrak ini
dapat diganti tanpa mengubah modul lain mana pun. Pembuktian itulah
yang dijalankan oleh ``tests/test_modularity.py``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, ClassVar, Mapping, Sequence

from rra.contracts import ASPECTS, SENTIMENTS, Prediction

AspectLabels = Sequence[Sequence[str]]
SentimentLabels = Sequence[Mapping[str, str]]


class ContractViolation(RuntimeError):
    """Dilempar bila sebuah keluaran model menyalahi kontrak yang dijanjikan."""


class AspectSentimentModel(ABC):
    """Kontrak komponen klasifikasi aspek & sentimen."""

    #: Kunci yang dipakai pada ``config/default.yaml`` (``model.name``).
    name: ClassVar[str] = "base"

    #: Nama yang ditampilkan pada antarmuka pengguna.
    display_name: ClassVar[str] = "Model Dasar"

    #: Keterangan singkat mengenai karakter algoritma.
    description: ClassVar[str] = ""

    # ------------------------------------------------------------------ #
    # Yang harus ditunaikan setiap implementasi
    # ------------------------------------------------------------------ #
    @abstractmethod
    def fit(
        self,
        texts: Sequence[str],
        aspect_labels: AspectLabels,
        sentiment_labels: SentimentLabels,
    ) -> "AspectSentimentModel":
        """Latih komponen.

        Parameters
        ----------
        texts:
            Teks ulasan yang telah dipraproses.
        aspect_labels:
            Untuk setiap teks, himpunan aspek yang dibahas.
        sentiment_labels:
            Untuk setiap teks, pemetaan aspek ke polaritas sentimennya.
        """

    @abstractmethod
    def predict(self, texts: Sequence[str]) -> list[Prediction]:
        """Klasifikasikan sejumlah teks menjadi pasangan (aspek, sentimen)."""

    @abstractmethod
    def save(self, path: str | Path) -> Path:
        """Simpan komponen ke berkas agar dapat dipakai ulang."""

    @classmethod
    @abstractmethod
    def load(cls, path: str | Path) -> "AspectSentimentModel":
        """Muat kembali komponen yang telah disimpan."""

    # ------------------------------------------------------------------ #
    # Perilaku bawaan (tidak perlu ditimpa)
    # ------------------------------------------------------------------ #
    def fit_examples(self, examples: Sequence[Any]) -> "AspectSentimentModel":
        """Kemudahan pemakaian: latih langsung dari ``TrainingExample``."""
        texts = [example.text for example in examples]
        aspects = [list(example.aspects) for example in examples]
        sentiments = [dict(example.sentiments) for example in examples]
        return self.fit(texts, aspects, sentiments)

    def describe(self) -> dict[str, Any]:
        """Ringkasan komponen — dipakai pada laporan dan antarmuka."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
        }

    def predict_with_ids(
        self, texts: Sequence[str], review_ids: Sequence[str]
    ) -> list[Prediction]:
        """Klasifikasikan teks sekaligus menetapkan identitas ulasan.

        Kontrak dasar pada :meth:`predict` sengaja tidak menyebutkan
        identitas ulasan karena komponen model tidak perlu mengetahuinya.
        Metode ini menjembatani kepentingan itu tanpa mengubah kontrak.
        """
        if len(texts) != len(review_ids):
            raise ValueError("Jumlah teks dan identitas ulasan tidak sama.")
        predictions = self.predict(texts)
        for prediction, review_id in zip(predictions, review_ids):
            prediction.review_id = str(review_id)
        return predictions

    @staticmethod
    def validate(predictions: Sequence[Prediction]) -> None:
        """Periksa apakah keluaran mematuhi jaminan pada kontrak.

        Dipanggil pada pengujian kontrak dan pada saat sistem berjalan,
        sehingga pelanggaran kontrak terdeteksi lebih awal alih-alih
        menghasilkan rekomendasi yang keliru.
        """
        for prediction in predictions:
            for item in prediction.items:
                if item.aspect not in ASPECTS:
                    raise ContractViolation(
                        f"Aspek '{item.aspect}' di luar taksonomi DINESERV {ASPECTS}"
                    )
                if item.sentiment not in SENTIMENTS:
                    raise ContractViolation(
                        f"Sentimen '{item.sentiment}' tidak dikenal {SENTIMENTS}"
                    )
                if not 0.0 <= item.confidence <= 1.0:
                    raise ContractViolation(
                        f"Tingkat keyakinan {item.confidence} di luar rentang [0, 1]"
                    )
