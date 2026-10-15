"""Pengujian modularitas — bukti utama klaim kebaruan penelitian.

Pengujian di berkas ini menjawab pertanyaan yang menjadi kebaruan skripsi:
**apakah komponen model benar-benar dapat diganti tanpa menyentuh satu baris
kode pun?**

Cara pengujiannya sederhana namun tegas: seluruh berkas Python pada ``src/``
dicatat sidik jarinya (SHA-256) sebelum dan sesudah penggantian komponen
model. Bila ada satu saja berkas kode yang berubah, pengujian gagal.

Pengujian ini juga memastikan bahwa penggantian tersebut benar-benar terjadi
— keluaran kedua komponen dibandingkan dan harus berbeda pada sebagian
ulasan — sehingga bukan sekadar nama yang berubah.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from rra.config import Config
from rra.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]


def hash_project_sources(root: Path) -> dict[str, str]:
    """Sidik jari seluruh berkas kode Python pada direktori ``src``."""
    result: dict[str, str] = {}
    for path in sorted((root / "src").rglob("*.py")):
        result[str(path.relative_to(root))] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
    return result


def config_for(root: Path, model_name: str) -> Config:
    cfg = Config.load(root=root)
    cfg._data["model"]["name"] = model_name
    return cfg


@pytest.fixture(scope="module")
def swap_results(dataset_root: Path, project_root: Path):
    """Jalankan alur penuh dengan kedua komponen model, catat sidik jari kode."""
    before = hash_project_sources(project_root)

    output_svm = Pipeline(config_for(dataset_root, "svm")).run()
    sources_after_swap = hash_project_sources(project_root)
    output_nb = Pipeline(config_for(dataset_root, "nb")).run()
    after = hash_project_sources(project_root)

    return {
        "before": before,
        "after_first_swap": sources_after_swap,
        "after": after,
        "svm": output_svm,
        "nb": output_nb,
    }


def test_swapping_model_requires_no_code_change(swap_results) -> None:
    """Tidak satu pun berkas kode berubah karena penggantian komponen."""
    assert swap_results["before"] == swap_results["after_first_swap"]
    assert swap_results["before"] == swap_results["after"]


def test_both_components_were_actually_used(swap_results) -> None:
    assert swap_results["svm"].model_name == "svm"
    assert swap_results["nb"].model_name == "nb"


def test_swapped_component_produces_its_own_results(swap_results) -> None:
    """Penggantian bukan sekadar label: hasil klasifikasinya berbeda."""
    svm_predictions = {
        (p.review_id, item.aspect, item.sentiment)
        for p in swap_results["svm"].predictions
        for item in p.items
    }
    nb_predictions = {
        (p.review_id, item.aspect, item.sentiment)
        for p in swap_results["nb"].predictions
        for item in p.items
    }
    assert svm_predictions != nb_predictions


def test_downstream_layers_are_agnostic_to_component(swap_results) -> None:
    """Lapisan keputusan tetap menghasilkan bentuk keluaran yang sama."""
    for output in (swap_results["svm"], swap_results["nb"]):
        decision = output.decision
        assert decision is not None
        assert [item.rank for item in decision.priorities] == [1, 2, 3, 4, 5]
        assert set(decision.stats) == {"makanan", "pelayanan", "harga", "suasana", "fasilitas"}
        assert decision.phrases
        assert decision.recommendations


def test_analysis_output_shape_is_identical(swap_results) -> None:
    """Struktur keluaran sama, meski nilainya berbeda."""
    svm_keys = set(swap_results["svm"].timings)
    nb_keys = set(swap_results["nb"].timings)
    assert svm_keys == nb_keys
    assert swap_results["svm"].n_reviews == swap_results["nb"].n_reviews


def test_config_files_differ_by_one_key_only() -> None:
    """Berkas konfigurasi varian hanya mengubah kunci ``model.name``."""
    base = Config.load(root=ROOT)
    svm = Config.load(root=ROOT, override="config/model_svm.yaml")
    nb = Config.load(root=ROOT, override="config/model_nb.yaml")

    assert svm.get("model.name") == "svm"
    assert nb.get("model.name") == "nb"

    # Konfigurasi dasar sudah memakai SVM, sehingga yang dibandingkan adalah
    # dasar melawan varian Naive Bayes — di situlah perbedaannya terlihat.
    base_flat, nb_flat = _flatten(base.as_dict()), _flatten(nb.as_dict())
    differing = [key for key in base_flat if base_flat[key] != nb_flat.get(key)]
    assert differing == ["model.name"]

    svm_flat = _flatten(svm.as_dict())
    assert [key for key in base_flat if base_flat[key] != svm_flat.get(key)] == []


def _flatten(data: dict, prefix: str = "") -> dict[str, object]:
    flat: dict[str, object] = {}
    for key, value in data.items():
        dotted = f"{prefix}{key}"
        if isinstance(value, dict):
            flat.update(_flatten(value, f"{dotted}."))
        else:
            flat[dotted] = value
    return flat
