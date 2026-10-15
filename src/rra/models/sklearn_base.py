"""Implementasi bersama untuk komponen berbasis pustaka scikit-learn.

Kelas pada modul ini menampung seluruh pekerjaan yang **sama** bagi semua
algoritma: pembobotan TF-IDF, pelatihan multi-label aspek, pelatihan
sentimen per aspek, dan penyimpanan berkas. Yang **berbeda** antar
algoritma hanyalah pembuatan estimator, dan itulah satu-satunya bagian
yang ditimpa oleh subkelas.

Pemisahan semacam ini adalah wujud nyata prinsip *information hiding*
(Parnas, 1972): yang diperkirakan akan berubah disembunyikan pada satu
tempat, sedangkan antarmukanya dibuat stabil.
"""

from __future__ import annotations

from abc import abstractmethod
from pathlib import Path
from typing import Any, ClassVar, Mapping, Sequence

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer

from rra.contracts import ASPECTS, SENTIMENTS, AspectSentiment, Prediction
from rra.models.base import AspectLabels, AspectSentimentModel, SentimentLabels

ARTIFACT_VERSION = 1


def _sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(values, -30.0, 30.0)))


def _scores(estimator: Any, matrix: np.ndarray) -> np.ndarray:
    """Ubah keluaran estimator menjadi nilai keyakinan pada rentang (0, 1).

    Sebagian estimator (mis. SVM linear) tidak menyediakan ``predict_proba``
    melainkan ``decision_function``. Keduanya dijadikan seragam di sini,
    sehingga lapisan di atasnya tidak perlu tahu perbedaannya.
    """
    if hasattr(estimator, "predict_proba"):
        raw = np.asarray(estimator.predict_proba(matrix), dtype=float)
        if raw.ndim == 2 and raw.shape[1] == 2:
            return raw[:, 1]
        return raw
    if hasattr(estimator, "decision_function"):
        decision = np.asarray(estimator.decision_function(matrix), dtype=float)
        if decision.ndim == 1:
            return _sigmoid(decision)
        if decision.shape[1] == 1:
            return _sigmoid(decision[:, 0])
        return _sigmoid(decision)
    raise TypeError(f"Estimator {type(estimator).__name__} tidak menyediakan skor.")


def _class_scores(estimator: Any, matrix: np.ndarray) -> np.ndarray:
    """Nilai keyakinan **per kelas**, berbentuk matriks (jumlah data, jumlah kelas).

    Fungsi ini berbeda dari :func:`_scores` dan perbedaannya penting untuk
    klasifikasi multikelas. Pada klasifier biner, :func:`_scores`
    mengembalikan **satu** nilai per data — yaitu keyakinan terhadap kelas
    kedua. Bila nilai tunggal itu diperlakukan sebagai deret skor kelas,
    ``argmax`` selalu menunjuk indeks nol, sehingga sistem akan terus
    menerka kelas pertama tanpa pernah mempertimbangkan kelas kedua.

    Kesalahan itu pernah terjadi dan menurunkan ketepatan penentuan
    sentimen dari sekitar 0,85 menjadi 0,35. Fungsi ini menutup celah
    tersebut dengan menyusun vektor skor lengkap untuk seluruh kelas.
    """
    if hasattr(estimator, "predict_proba"):
        raw = np.asarray(estimator.predict_proba(matrix), dtype=float)
        if raw.ndim == 2:
            return raw
        return raw.reshape(-1, 1)

    if hasattr(estimator, "decision_function"):
        decision = np.asarray(estimator.decision_function(matrix), dtype=float)
        if decision.ndim == 1:
            positive = _sigmoid(decision)
            return np.column_stack([1.0 - positive, positive])
        if decision.shape[1] == 1:
            positive = _sigmoid(decision[:, 0])
            return np.column_stack([1.0 - positive, positive])
        return _sigmoid(decision)

    raise TypeError(f"Estimator {type(estimator).__name__} tidak menyediakan skor.")


class SklearnAspectSentimentModel(AspectSentimentModel):
    """Kerangka umum komponen berbasis scikit-learn."""

    #: Apakah estimator memerlukan fitur bernilai tidak negatif (mis. Naive Bayes).
    requires_nonnegative: ClassVar[bool] = False

    def __init__(
        self,
        *,
        tfidf: Mapping[str, Any] | None = None,
        aspect_threshold: float = 0.5,
        seed: int = 42,
    ) -> None:
        self.tfidf_params: dict[str, Any] = {
            "max_features": 20000,
            "ngram_range": (1, 2),
            "min_df": 2,
            "max_df": 0.95,
            "sublinear_tf": True,
            "lowercase": False,          # teks sudah dinormalkan pada Lapisan 2
        }
        if tfidf:
            self.tfidf_params.update(dict(tfidf))
        if isinstance(self.tfidf_params.get("ngram_range"), list):
            self.tfidf_params["ngram_range"] = tuple(self.tfidf_params["ngram_range"])

        self.aspect_threshold = float(aspect_threshold)
        self.seed = int(seed)

        self.vectorizer: TfidfVectorizer | None = None
        self.aspect_classifier: OneVsRestClassifier | None = None
        self.aspect_binarizer: MultiLabelBinarizer | None = None
        self.sentiment_models: dict[str, Any] = {}
        self.constant_sentiment: dict[str, str] = {}
        self.is_fitted: bool = False

    # ------------------------------------------------------------------ #
    # Bagian yang berbeda antar-algoritma
    # ------------------------------------------------------------------ #
    @abstractmethod
    def _make_aspect_estimator(self) -> Any:
        """Buat estimator biner untuk tugas multi-label aspek."""

    @abstractmethod
    def _make_sentiment_estimator(self) -> Any:
        """Buat estimator multikelas untuk tugas sentimen per aspek."""

    # ------------------------------------------------------------------ #
    # Pelatihan
    # ------------------------------------------------------------------ #
    def fit(
        self,
        texts: Sequence[str],
        aspect_labels: AspectLabels,
        sentiment_labels: SentimentLabels,
    ) -> "SklearnAspectSentimentModel":
        texts = list(texts)
        if not texts:
            raise ValueError("Tidak ada teks untuk dilatih.")
        if not (len(texts) == len(aspect_labels) == len(sentiment_labels)):
            raise ValueError("Panjang teks dan label tidak sama.")

        self.vectorizer = TfidfVectorizer(**self.tfidf_params)
        matrix = self.vectorizer.fit_transform(texts)

        # --- tugas 1: multi-label aspek -------------------------------
        self.aspect_binarizer = MultiLabelBinarizer(classes=list(ASPECTS))
        targets = self.aspect_binarizer.fit_transform([list(items) for items in aspect_labels])
        self.aspect_classifier = OneVsRestClassifier(
            self._make_aspect_estimator(), n_jobs=1
        )
        self.aspect_classifier.fit(matrix, targets)

        # --- tugas 2: sentimen per aspek ------------------------------
        self.sentiment_models = {}
        self.constant_sentiment = {}
        for column, aspect in enumerate(self.aspect_binarizer.classes_):
            rows = [
                row
                for row in np.where(targets[:, column] == 1)[0]
                if sentiment_labels[row].get(aspect) in SENTIMENTS
            ]
            labels = [str(sentiment_labels[row][aspect]) for row in rows]
            if not rows:
                self.constant_sentiment[aspect] = "netral"
                continue
            unique = sorted(set(labels))
            if len(unique) < 2:
                # Hanya satu kelas tersedia: model konstan, dicatat apa adanya
                # agar tidak menimbulkan klaim kinerja yang berlebihan.
                self.constant_sentiment[aspect] = unique[0]
                continue
            estimator = self._make_sentiment_estimator()
            estimator.fit(matrix[rows], labels)
            self.sentiment_models[aspect] = estimator

        self.is_fitted = True
        return self

    # ------------------------------------------------------------------ #
    # Prediksi
    # ------------------------------------------------------------------ #
    def predict(self, texts: Sequence[str]) -> list[Prediction]:
        if not self.is_fitted or self.vectorizer is None or self.aspect_classifier is None:
            raise RuntimeError("Komponen belum dilatih. Panggil fit() lebih dahulu.")
        texts = list(texts)
        if not texts:
            return []

        matrix = self.vectorizer.transform(texts)
        aspect_scores = np.atleast_2d(_scores(self.aspect_classifier, matrix))
        classes = list(self.aspect_binarizer.classes_)

        results: list[Prediction] = []
        for index, text in enumerate(texts):
            items: list[AspectSentiment] = []
            for column, aspect in enumerate(classes):
                confidence = float(aspect_scores[index, column])
                if confidence < self.aspect_threshold:
                    continue
                sentiment, sentiment_confidence = self._predict_sentiment(aspect, matrix[index:index + 1])
                items.append(
                    AspectSentiment(
                        aspect=aspect,
                        sentiment=sentiment,
                        confidence=round(min(confidence, sentiment_confidence), 6),
                    )
                )
            if not items:
                # Jaminan kontrak: setiap ulasan minimal menghasilkan satu pasangan.
                best = int(np.argmax(aspect_scores[index]))
                aspect = classes[best]
                sentiment, sentiment_confidence = self._predict_sentiment(aspect, matrix[index:index + 1])
                items.append(
                    AspectSentiment(
                        aspect=aspect,
                        sentiment=sentiment,
                        confidence=round(min(float(aspect_scores[index, best]), sentiment_confidence), 6),
                    )
                )
            results.append(Prediction(review_id=str(index), items=items))

        self.validate(results)
        return results

    def _predict_sentiment(self, aspect: str, row: np.ndarray) -> tuple[str, float]:
        if aspect in self.constant_sentiment:
            return self.constant_sentiment[aspect], 1.0
        estimator = self.sentiment_models[aspect]
        scores = np.atleast_2d(_class_scores(estimator, row))[0]
        classes = list(estimator.classes_)
        if len(scores) != len(classes):
            raise RuntimeError(
                f"Jumlah skor ({len(scores)}) tidak sesuai jumlah kelas "
                f"({len(classes)}) pada aspek '{aspect}'."
            )
        best = int(np.argmax(scores))
        return str(classes[best]), float(scores[best])

    # ------------------------------------------------------------------ #
    # Penyimpanan
    # ------------------------------------------------------------------ #
    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "artifact_version": ARTIFACT_VERSION,
                "model_name": self.name,
                "vectorizer": self.vectorizer,
                "aspect_classifier": self.aspect_classifier,
                "aspect_binarizer": self.aspect_binarizer,
                "sentiment_models": self.sentiment_models,
                "constant_sentiment": self.constant_sentiment,
                "aspect_threshold": self.aspect_threshold,
                "tfidf_params": self.tfidf_params,
                "seed": self.seed,
            },
            path,
        )
        return path

    @classmethod
    def load(cls, path: str | Path) -> "SklearnAspectSentimentModel":
        payload = joblib.load(Path(path))
        if payload.get("artifact_version") != ARTIFACT_VERSION:
            raise ValueError(
                f"Versi artefak tidak cocok: {payload.get('artifact_version')} "
                f"(diharapkan {ARTIFACT_VERSION})"
            )
        instance = cls(
            tfidf=payload.get("tfidf_params"),
            aspect_threshold=payload.get("aspect_threshold", 0.5),
            seed=payload.get("seed", 42),
        )
        instance.vectorizer = payload["vectorizer"]
        instance.aspect_classifier = payload["aspect_classifier"]
        instance.aspect_binarizer = payload["aspect_binarizer"]
        instance.sentiment_models = payload["sentiment_models"]
        instance.constant_sentiment = payload["constant_sentiment"]
        instance.is_fitted = True
        return instance

    def describe(self) -> dict[str, Any]:
        info = super().describe()
        info.update(
            {
                "tfidf": dict(self.tfidf_params),
                "aspect_threshold": self.aspect_threshold,
                "seed": self.seed,
                "jumlah_fitur": (
                    int(len(self.vectorizer.vocabulary_)) if self.vectorizer else 0
                ),
                "aspek_model_konstan": sorted(self.constant_sentiment),
            }
        )
        return info
