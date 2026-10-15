"""LAPISAN 4 — Modul keputusan.

Lapisan ini mengubah hasil klasifikasi menjadi peringkat prioritas dan
rekomendasi tindakan. Berbeda dari penelitian terdahulu yang menemukan
"akar masalah" melalui pembacaan manual dan diskusi dengan pemilik
usaha, seluruh perhitungan di sini **dinyatakan secara eksplisit**
sehingga dapat diperiksa, diulang, dan dipertanggungjawabkan.

Modul-modul pada lapisan ini tidak mengetahui algoritma apa yang dipakai
pada Lapisan 3. Ia hanya menerima :class:`~rra.contracts.Prediction`.
"""

from rra.decision.module import DecisionModule, DecisionOutput  # noqa: F401
from rra.decision.phrases import ComplaintPhraseExtractor  # noqa: F401
from rra.decision.priority import PriorityEngine, minmax_normalize  # noqa: F401
from rra.decision.rules import recommend_action  # noqa: F401
from rra.decision.severity import review_severity, severity_map  # noqa: F401

__all__ = [
    "DecisionModule",
    "DecisionOutput",
    "ComplaintPhraseExtractor",
    "PriorityEngine",
    "minmax_normalize",
    "recommend_action",
    "review_severity",
    "severity_map",
]
