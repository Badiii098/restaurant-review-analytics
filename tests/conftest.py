"""Peralatan bersama untuk seluruh pengujian."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rra.config import Config  # noqa: E402
from rra.io_layer.sample_data import generate_dataset, write_dataset  # noqa: E402


def make_project(tmp: Path, *, n_reviews: int = 160, seed: int = 7) -> Path:
    """Siapkan direktori proyek mandiri: konfigurasi + dataset kecil.

    Direktori ini memuat seluruh jalur relatif yang dipakai sistem, sehingga
    pengujian tidak pernah menulis ke dalam repositori.
    """
    tmp = Path(tmp)
    shutil.copytree(ROOT / "config", tmp / "config", dirs_exist_ok=True)
    write_dataset(generate_dataset(n_reviews=n_reviews, seed=seed), tmp)
    return tmp


@pytest.fixture(scope="session")
def project_root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def dataset_root(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Direktori proyek berisi dataset kecil yang dapat diulang."""
    return make_project(tmp_path_factory.mktemp("rra-data"))


@pytest.fixture()
def config(dataset_root: Path) -> Config:
    """Konfigurasi yang menunjuk ke direktori proyek sementara."""
    return Config.load(root=dataset_root)


@pytest.fixture()
def small_labels() -> tuple[list[str], list[list[str]], list[dict[str, str]]]:
    """Deret latih kecil dengan beberapa aspek dan kedua polaritas."""
    texts = [
        "makanan hambar kuah tidak_enak",
        "makanan enak porsi banyak bumbu meresap",
        "pelayanan lambat pesanan keliru",
        "pelayanan ramah cepat tanggap",
        "harga mahal tidak_sepadan",
        "harga murah sepadan porsi banyak",
        "toilet kotor tempatnya sempit",
        "tempatnya nyaman bersih wangi",
    ]
    aspects = [
        ["makanan"], ["makanan"], ["pelayanan"], ["pelayanan"],
        ["harga"], ["harga"], ["fasilitas", "suasana"], ["suasana"],
    ]
    sentiments = [
        {"makanan": "negatif"}, {"makanan": "positif"},
        {"pelayanan": "negatif"}, {"pelayanan": "positif"},
        {"harga": "negatif"}, {"harga": "positif"},
        {"fasilitas": "negatif", "suasana": "negatif"}, {"suasana": "positif"},
    ]
    return texts, aspects, sentiments
