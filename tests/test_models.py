"""Pengujian Lapisan 3 — kontrak dan kepatuhan komponen model.

Berkas ini adalah bukti utama klaim kebaruan penelitian: setiap komponen
model yang terdaftar wajib mematuhi kontrak yang sama. Pengujian dijalankan
untuk **seluruh** model yang terdaftar, sehingga algoritma baru yang
ditambahkan kelak otomatis ikut teruji.
"""

from __future__ import annotations

import pytest

from rra.contracts import ASPECTS, SENTIMENTS
from rra.models.base import AspectSentimentModel
from rra.models.registry import available_models, build_model, get_model_class

MODEL_NAMES = sorted(available_models())


def test_registry_is_not_empty() -> None:
    assert MODEL_NAMES, "Registri komponen model tidak boleh kosong."


def test_registry_contains_documented_models() -> None:
    assert {"svm", "nb"} <= set(MODEL_NAMES)


@pytest.mark.parametrize("name", MODEL_NAMES)
def test_model_is_subclass_of_contract(name: str) -> None:
    assert issubclass(get_model_class(name), AspectSentimentModel)


@pytest.mark.parametrize("name", MODEL_NAMES)
def test_model_fits_and_predicts(name: str, small_labels) -> None:
    texts, aspects, sentiments = small_labels
    model = get_model_class(name)()
    model.fit(texts, aspects, sentiments)
    predictions = model.predict(texts)

    assert len(predictions) == len(texts)
    for prediction in predictions:
        for item in prediction.items:
            assert item.aspect in ASPECTS
            assert item.sentiment in SENTIMENTS
            assert 0.0 <= item.confidence <= 1.0


@pytest.mark.parametrize("name", MODEL_NAMES)
def test_predict_before_fit_is_refused(name: str) -> None:
    model = get_model_class(name)()
    with pytest.raises(RuntimeError):
        model.predict(["makanan hambar"])


@pytest.mark.parametrize("name", MODEL_NAMES)
def test_fit_rejects_mismatched_lengths(name: str) -> None:
    model = get_model_class(name)()
    with pytest.raises(ValueError):
        model.fit(["a", "b"], [["makanan"]], [{"makanan": "positif"}])


@pytest.mark.parametrize("name", MODEL_NAMES)
def test_predict_with_ids_assigns_identity(name: str, small_labels) -> None:
    texts, aspects, sentiments = small_labels
    model = get_model_class(name)()
    model.fit(texts, aspects, sentiments)
    predictions = model.predict_with_ids(texts, [f"R{i}" for i in range(len(texts))])
    assert [p.review_id for p in predictions] == [f"R{i}" for i in range(len(texts))]


@pytest.mark.parametrize("name", MODEL_NAMES)
def test_predict_with_ids_rejects_mismatch(name: str, small_labels) -> None:
    texts, aspects, sentiments = small_labels
    model = get_model_class(name)()
    model.fit(texts, aspects, sentiments)
    with pytest.raises(ValueError):
        model.predict_with_ids(texts, ["R1"])


@pytest.mark.parametrize("name", MODEL_NAMES)
def test_save_and_load_roundtrip(name: str, small_labels, tmp_path) -> None:
    texts, aspects, sentiments = small_labels
    model = get_model_class(name)()
    model.fit(texts, aspects, sentiments)

    target = tmp_path / f"{name}.joblib"
    model.save(target)
    assert target.exists()

    restored = get_model_class(name).load(target)
    original = [item.aspect for item in model.predict(texts)[0].items]
    reloaded = [item.aspect for item in restored.predict(texts)[0].items]
    assert original == reloaded


def test_build_model_follows_configuration(config) -> None:
    config._data["model"]["name"] = "svm"
    assert build_model(config).name == "svm"
    config._data["model"]["name"] = "nb"
    assert build_model(config).name == "nb"


def test_build_model_rejects_unknown_name(config) -> None:
    config._data["model"]["name"] = "tidak_ada"
    with pytest.raises(KeyError):
        build_model(config)


def test_every_model_declares_display_metadata() -> None:
    for name in MODEL_NAMES:
        cls = get_model_class(name)
        assert cls.display_name and cls.display_name != "Model Dasar"
        assert cls.description


@pytest.mark.parametrize("name", MODEL_NAMES)
def test_sentiment_scores_cover_every_class(name: str, small_labels) -> None:
    """Regresi: skor sentimen harus tersedia untuk **setiap** kelas.

    Pernah terjadi kesalahan ketika kelas biner hanya menghasilkan satu
    nilai skor, sehingga ``argmax`` selalu menunjuk kelas pertama dan
    ketepatan sentimen anjlok. Pengujian ini memastikan jumlah skor
    sejalan dengan jumlah kelas pada setiap aspek.
    """
    import numpy as np

    from rra.models.sklearn_base import _class_scores

    texts, aspects, sentiments = small_labels
    model = get_model_class(name)()
    model.fit(texts, aspects, sentiments)
    matrix = model.vectorizer.transform(texts)

    for aspect, estimator in model.sentiment_models.items():
        scores = np.atleast_2d(_class_scores(estimator, matrix))
        assert scores.shape[1] == len(estimator.classes_), (
            f"Jumlah skor pada aspek '{aspect}' tidak sama dengan jumlah kelas."
        )
        assert np.allclose(scores.sum(axis=1), 1.0, atol=1e-6)


@pytest.mark.parametrize("name", MODEL_NAMES)
def test_both_sentiment_classes_can_be_predicted(name: str) -> None:
    """Model harus mampu menghasilkan sentimen positif dan negatif."""
    texts = [
        "makanan hambar kuah tidak_enak bumbu tidak_meresap",
        "makanan enak lezat gurih porsi banyak bumbu meresap",
        "makanan hambar porsi sedikit",
        "makanan enak mantap porsi banyak",
    ]
    aspects = [["makanan"]] * 4
    sentiments = [
        {"makanan": "negatif"}, {"makanan": "positif"},
        {"makanan": "negatif"}, {"makanan": "positif"},
    ]
    model = get_model_class(name)()
    model.fit(texts, aspects, sentiments)
    predicted = {item.sentiment for p in model.predict(texts) for item in p.items}
    assert predicted == {"positif", "negatif"}


def test_svm_handles_aspect_present_in_every_example() -> None:
    """Aspek yang muncul di semua contoh tidak boleh membuat prediksi gagal.

    OneVsRestClassifier mengganti estimator aspek konstan dengan prediktor
    konstan yang punya ``predict_proba``, sehingga ``hasattr`` salah menyimpulkan
    bahwa seluruh estimator SVM menyediakannya.
    """
    texts = [
        "makanan enak pelayanan cepat", "makanan hambar pelayanan lambat",
        "makanan enak harga murah", "makanan dingin harga mahal",
        "makanan gurih pelayanan ramah", "makanan asin harga mahal",
    ]
    aspects = [["makanan", "pelayanan"], ["makanan", "pelayanan"], ["makanan", "harga"],
               ["makanan", "harga"], ["makanan", "pelayanan"], ["makanan", "harga"]]
    sentiments = [{"makanan": "positif", "pelayanan": "positif"},
                  {"makanan": "negatif", "pelayanan": "negatif"},
                  {"makanan": "positif", "harga": "positif"},
                  {"makanan": "negatif", "harga": "negatif"},
                  {"makanan": "positif", "pelayanan": "positif"},
                  {"makanan": "negatif", "harga": "negatif"}]
    model = get_model_class("svm")(tfidf={"min_df": 1})
    model.fit(texts, aspects, sentiments)
    predictions = model.predict(texts)
    assert len(predictions) == len(texts)
    assert all(any(i.aspect == "makanan" for i in p.items) for p in predictions)
