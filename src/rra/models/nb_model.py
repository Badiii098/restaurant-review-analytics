"""Komponen model: Multinomial Naive Bayes.

Berkas ini adalah **komponen pengganti** yang dipakai untuk membuktikan
modularitas sistem. Perhatikan bahwa ia mematuhi kontrak yang sama
dengan :mod:`rra.models.svm_model`, sehingga dapat ditukar tanpa
mengubah satu pun modul di lapisan lain.
"""

from __future__ import annotations

from typing import Any

from sklearn.naive_bayes import MultinomialNB

from rra.models.registry import register_model
from rra.models.sklearn_base import SklearnAspectSentimentModel


@register_model
class NaiveBayesAspectSentimentModel(SklearnAspectSentimentModel):
    """ABSA berbasis TF-IDF dan Multinomial Naive Bayes.

    Naive Bayes mewakili keluarga pendekatan yang berbeda dari SVM:
    probabilistik, bukan geometris. Perbedaan ini menjadikan keduanya
    pasangan yang bermakna untuk pengujian Hipotesis 1, sekaligus
    bukti nyata bahwa sistem dapat menampung algoritma dari keluarga
    yang berlainan.
    """

    name = "nb"
    display_name = "Multinomial Naive Bayes"
    description = (
        "Mengasumsikan setiap fitur saling bebas dan menghitung peluang "
        "kelas melalui teorema Bayes. Sangat efisien secara komputasi dan "
        "menyediakan probabilitas secara langsung."
    )

    def __init__(self, *, alpha: float = 0.3, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.alpha = float(alpha)

    def _make_aspect_estimator(self) -> Any:
        return MultinomialNB(alpha=self.alpha)

    def _make_sentiment_estimator(self) -> Any:
        return MultinomialNB(alpha=self.alpha)

    def describe(self) -> dict[str, Any]:
        info = super().describe()
        info["alpha"] = self.alpha
        return info
