"""Komponen model: Support Vector Machine linear.

Implementasi ini adalah pilihan bawaan sistem. Perhatikan betapa
pendeknya berkas ini: seluruh pekerjaan berat berada pada
:class:`~rra.models.sklearn_base.SklearnAspectSentimentModel`, sedangkan
di sini hanya ditentukan estimator yang dipakai. Itulah wujud nyata
pemisahan tanggung jawab.
"""

from __future__ import annotations

from typing import Any

from sklearn.svm import LinearSVC

from rra.models.registry import register_model
from rra.models.sklearn_base import SklearnAspectSentimentModel


@register_model
class SvmAspectSentimentModel(SklearnAspectSentimentModel):
    """ABSA berbasis TF-IDF dan SVM linear.

    SVM linear dipilih karena tahan terhadap data teks berdimensi tinggi
    dan pembobotan kelasnya dapat diseimbangkan tanpa menambah beban
    komputasi — penting agar sistem tetap berjalan tanpa kartu grafis.
    """

    name = "svm"
    display_name = "Support Vector Machine (linear)"
    description = (
        "Mencari bidang pemisah dengan margin maksimum. Tahan terhadap "
        "overfitting pada data berdimensi tinggi. Tidak menyediakan "
        "probabilitas langsung, sehingga tingkat keyakinan diturunkan dari "
        "nilai keputusan melalui fungsi sigmoid."
    )

    def __init__(self, *, C: float = 1.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.C = float(C)

    def _make_aspect_estimator(self) -> Any:
        return LinearSVC(
            C=self.C,
            class_weight="balanced",
            random_state=self.seed,
            max_iter=5000,
        )

    def _make_sentiment_estimator(self) -> Any:
        return LinearSVC(
            C=self.C,
            class_weight="balanced",
            random_state=self.seed,
            max_iter=5000,
        )

    def describe(self) -> dict[str, Any]:
        info = super().describe()
        info["C"] = self.C
        return info
