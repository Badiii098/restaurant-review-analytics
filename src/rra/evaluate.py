"""Evaluasi kinerja komponen model dan modul keputusan.

Seluruh ukuran yang dilaporkan pada Bab IV dihitung di modul ini, sehingga
angka yang muncul pada naskah dan angka yang muncul pada sistem berasal
dari satu sumber yang sama.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping, Sequence

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    hamming_loss,
    precision_recall_fscore_support,
)
from sklearn.model_selection import KFold
from sklearn.preprocessing import MultiLabelBinarizer

from rra.contracts import ASPECTS, SENTIMENTS


# --------------------------------------------------------------------------- #
# Ukuran multi-label untuk tugas aspek
# --------------------------------------------------------------------------- #

def multilabel_metrics(
    y_true: Sequence[Sequence[str]],
    y_pred: Sequence[Sequence[str]],
) -> dict[str, Any]:
    """Hitung ukuran kinerja untuk tugas multi-label aspek."""
    encoder = MultiLabelBinarizer(classes=list(ASPECTS))
    matrix_true = encoder.fit_transform([list(items) for items in y_true])
    matrix_pred = encoder.transform([list(items) for items in y_pred])

    precision, recall, f1, support = precision_recall_fscore_support(
        matrix_true, matrix_pred, average=None, zero_division=0, labels=range(len(ASPECTS))
    )
    micro = precision_recall_fscore_support(
        matrix_true, matrix_pred, average="micro", zero_division=0
    )
    macro = precision_recall_fscore_support(
        matrix_true, matrix_pred, average="macro", zero_division=0
    )

    per_aspect = {
        aspect: {
            "precision": round(float(precision[i]), 6),
            "recall": round(float(recall[i]), 6),
            "f1": round(float(f1[i]), 6),
            "support": int(support[i]),
        }
        for i, aspect in enumerate(ASPECTS)
    }

    # Rata-rata kedua: hanya atas aspek yang benar-benar muncul pada data
    # acuan. Angka utama tetap memakai seluruh aspek (bersifat lebih ketat,
    # karena aspek yang selalu terlewat tetap dihitung nol), sedangkan angka
    # ini memisahkan mutu pengenalan aspek dari kelangkaan kelas.
    active = [index for index, value in enumerate(support) if value > 0]
    if active:
        active_scores = precision_recall_fscore_support(
            matrix_true[:, active], matrix_pred[:, active],
            average="macro", zero_division=0,
        )
        macro_f1_active = round(float(active_scores[2]), 6)
    else:
        macro_f1_active = 0.0

    return {
        "macro_precision": round(float(macro[0]), 6),
        "macro_recall": round(float(macro[1]), 6),
        "macro_f1": round(float(macro[2]), 6),
        "macro_f1_aktif": macro_f1_active,
        "aspek_dinilai": [ASPECTS[index] for index in active],
        "micro_precision": round(float(micro[0]), 6),
        "micro_recall": round(float(micro[1]), 6),
        "micro_f1": round(float(micro[2]), 6),
        "hamming_loss": round(float(hamming_loss(matrix_true, matrix_pred)), 6),
        "subset_accuracy": round(float(accuracy_score(matrix_true, matrix_pred)), 6),
        "per_aspect": per_aspect,
    }


# --------------------------------------------------------------------------- #
# Ukuran untuk tugas sentimen per aspek
# --------------------------------------------------------------------------- #

def sentiment_metrics(
    y_true: Sequence[Mapping[str, str]],
    predictions: Sequence[Any],
) -> dict[str, Any]:
    """Hitung kinerja sentimen pada pasangan (ulasan, aspek) yang terklasifikasi.

    Perbandingan hanya dilakukan pada pasangan yang **kedua-duanya** ada:
    aspek benar-benar dibahas dan aspek itu berhasil dikenali model. Dengan
    begitu angka yang dihasilkan mengukur mutu penentuan sentimen, terpisah
    dari mutu pengenalan aspek.
    """
    y_true_flat: list[str] = []
    y_pred_flat: list[str] = []
    per_aspect_true: dict[str, list[str]] = {aspect: [] for aspect in ASPECTS}
    per_aspect_pred: dict[str, list[str]] = {aspect: [] for aspect in ASPECTS}

    for truth, prediction in zip(y_true, predictions):
        predicted_map = {item.aspect: item.sentiment for item in prediction.items}
        for aspect, sentiment in truth.items():
            if sentiment not in SENTIMENTS:
                continue
            guessed = predicted_map.get(aspect)
            if guessed is None:
                continue
            y_true_flat.append(sentiment)
            y_pred_flat.append(guessed)
            per_aspect_true[aspect].append(sentiment)
            per_aspect_pred[aspect].append(guessed)

    if not y_true_flat:
        return {"accuracy": 0.0, "macro_f1": 0.0, "n_pasangan": 0, "per_aspect": {}}

    # Rata-rata dihitung hanya atas kelas yang benar-benar muncul pada data
    # acuan. Bila kelas "netral" tidak pernah muncul, memasukkannya akan
    # memberi F1 nol untuk kelas itu dan menekan angka rata-rata tanpa
    # alasan yang sebenarnya. Kelas yang dinilai dicantumkan pada keluaran
    # agar pilihan ini terbuka untuk diperiksa.
    labels_present = sorted(set(y_true_flat))
    macro = f1_score(y_true_flat, y_pred_flat, average="macro", zero_division=0,
                     labels=labels_present)
    per_aspect: dict[str, dict[str, Any]] = {}
    for aspect in ASPECTS:
        if not per_aspect_true[aspect]:
            continue
        aspect_labels = sorted(set(per_aspect_true[aspect]))
        per_aspect[aspect] = {
            "accuracy": round(float(accuracy_score(
                per_aspect_true[aspect], per_aspect_pred[aspect])), 6),
            "macro_f1": round(float(f1_score(
                per_aspect_true[aspect], per_aspect_pred[aspect],
                average="macro", zero_division=0, labels=aspect_labels)), 6),
            "n": len(per_aspect_true[aspect]),
        }

    return {
        "accuracy": round(float(accuracy_score(y_true_flat, y_pred_flat)), 6),
        "macro_f1": round(float(macro), 6),
        "kelas_dinilai": labels_present,
        "n_pasangan": len(y_true_flat),
        "per_aspect": per_aspect,
    }


# --------------------------------------------------------------------------- #
# Validasi silang
# --------------------------------------------------------------------------- #

def cross_validate(
    build_fn: Callable[[], Any],
    texts: Sequence[str],
    aspect_labels: Sequence[Sequence[str]],
    sentiment_labels: Sequence[Mapping[str, str]],
    *,
    folds: int = 10,
    seed: int = 42,
) -> dict[str, Any]:
    """Jalankan validasi silang dan kembalikan rincian per lipatan.

    Pembagian lipatan menggunakan pengacakan dengan ``seed`` yang tetap
    sehingga hasilnya dapat diulang persis. Karena tugas aspek bersifat
    multi-label, penstratifikasian per kelas tidak dapat diterapkan
    langsung; keterbatasan ini dicatat pada Bab IV.

    Rincian per lipatan dikembalikan utuh karena menjadi bahan bagi
    pengujian Hipotesis 1 (uji berpasangan antara dua algoritma).
    """
    texts = list(texts)
    n_samples = len(texts)
    folds = max(2, min(int(folds), n_samples))

    splitter = KFold(n_splits=folds, shuffle=True, random_state=int(seed))
    per_fold: list[dict[str, Any]] = []

    for fold_index, (train_index, test_index) in enumerate(splitter.split(texts), start=1):
        model = build_fn()
        model.fit(
            [texts[i] for i in train_index],
            [aspect_labels[i] for i in train_index],
            [sentiment_labels[i] for i in train_index],
        )
        predictions = model.predict([texts[i] for i in test_index])

        aspect_scores = multilabel_metrics(
            [aspect_labels[i] for i in test_index],
            [list(prediction.aspects) for prediction in predictions],
        )
        sentiment_scores = sentiment_metrics(
            [sentiment_labels[i] for i in test_index], predictions
        )
        per_fold.append(
            {
                "fold": fold_index,
                "n_train": len(train_index),
                "n_test": len(test_index),
                "aspect": aspect_scores,
                "sentiment": sentiment_scores,
            }
        )

    return {
        "folds": folds,
        "seed": seed,
        "n_samples": n_samples,
        "per_fold": per_fold,
        "macro_f1_aspect": [round(float(f["aspect"]["macro_f1"]), 6) for f in per_fold],
        "macro_f1_sentiment": [round(float(f["sentiment"]["macro_f1"]), 6) for f in per_fold],
        "summary": {
            "aspect_macro_f1_mean": round(float(np.mean([f["aspect"]["macro_f1"] for f in per_fold])), 6),
            "aspect_macro_f1_std": round(float(np.std([f["aspect"]["macro_f1"] for f in per_fold], ddof=1)), 6),
            "sentiment_macro_f1_mean": round(float(np.mean([f["sentiment"]["macro_f1"] for f in per_fold])), 6),
            "sentiment_macro_f1_std": round(float(np.std([f["sentiment"]["macro_f1"] for f in per_fold], ddof=1)), 6),
        },
    }


# --------------------------------------------------------------------------- #
# Ketepatan peringkat frasa keluhan
# --------------------------------------------------------------------------- #

def precision_at_k(
    extracted: Sequence[str],
    gold: Sequence[str],
    k: int = 5,
) -> dict[str, Any]:
    """Hitung Precision@K untuk daftar frasa.

    Sebuah frasa dinilai relevan bila salah satu frasa acuan pakar
    termuat di dalamnya (atau sebaliknya). Pencocokan longgar ini dipakai
    karena sistem dapat menghasilkan frasa yang lebih panjang, misalnya
    "pelayanan lambat sekali" sebagai perluasan dari "pelayanan lambat".
    Aturan pencocokan dinyatakan terbuka agar dapat diperiksa.
    """
    top = list(extracted)[:k]
    if not top:
        return {"k": k, "hits": 0, "precision": 0.0, "matched": []}

    gold_clean = [phrase.lower().strip() for phrase in gold]
    matched: list[str] = []
    hits = 0
    for phrase in top:
        candidate = phrase.lower().strip()
        if any(g in candidate or candidate in g for g in gold_clean):
            hits += 1
            matched.append(phrase)

    return {
        "k": k,
        "hits": hits,
        "precision": round(hits / len(top), 6),
        "matched": matched,
        "considered": top,
    }


def evaluate_phrase_quality(
    phrases_by_aspect: Mapping[str, Sequence[Any]],
    gold_by_aspect: Mapping[str, Sequence[str]],
    *,
    k: int = 5,
) -> dict[str, Any]:
    """Hitung Precision@K untuk seluruh aspek sekaligus."""
    per_aspect: dict[str, Any] = {}
    for aspect, items in phrases_by_aspect.items():
        extracted = [item.phrase for item in items]
        result = precision_at_k(extracted, gold_by_aspect.get(aspect, []), k=k)
        per_aspect[aspect] = result

    values = [result["precision"] for result in per_aspect.values()]
    return {
        "k": k,
        "mean_precision": round(float(np.mean(values)), 6) if values else 0.0,
        "per_aspect": per_aspect,
    }
