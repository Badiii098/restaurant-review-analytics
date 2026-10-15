"""Sistem Analitik Ulasan Pelanggan Restoran (RRA).

Rancang bangun sistem berbasis *Aspect-Based Sentiment Analysis* dengan
ekstraksi frasa keluhan dominan dan modul keputusan yang dapat diaudit.

Arsitektur sistem terbagi atas lima lapisan dengan tanggung jawab tunggal:

    Lapisan 1  rra.io_layer     akuisisi & penyimpanan data
    Lapisan 2  rra.preprocess   pemrosesan bahasa alami
    Lapisan 3  rra.models       klasifikasi aspek & sentimen  (DAPAT DIGANTI)
    Lapisan 4  rra.decision     ekstraksi frasa & skor prioritas
    Lapisan 5  app/             antarmuka pengguna

Antar-lapisan hanya berkomunikasi melalui objek yang didefinisikan pada
:mod:`rra.contracts`. Konsekuensinya, Lapisan 3 dapat diganti tanpa
mengubah modul lain.
"""

__version__ = "0.1.0"

from rra.contracts import (  # noqa: F401
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

__all__ = [
    "__version__",
    "ASPECTS",
    "SENTIMENTS",
    "RawReview",
    "CleanReview",
    "TrainingExample",
    "AspectSentiment",
    "Prediction",
    "ComplaintPhrase",
    "AspectPriority",
    "Recommendation",
]
