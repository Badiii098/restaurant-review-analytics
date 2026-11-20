"""Uji sistem lapis 5a: API FastAPI menyajikan bukti tiap tahap penelitian."""

from __future__ import annotations

import threading
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from rra.api.app import create_app
from rra.config import Config
from rra.services import tahap
from rra.storage.repository import ResultRepository

from conftest import make_project

pytestmark = pytest.mark.kasus("S-02")

ENDPOINT = ["status", "data", "anotasi", "kebutuhan", "desain", "iterasi", "hasil/terakhir",
            "sensitivitas", "pengujian", "pakar", "hipotesis"]


@pytest.fixture(scope="module")
def proyek(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = make_project(tmp_path_factory.mktemp("api"), n_reviews=200)
    tahap.analisis(Config.load(root=root))
    return root


@pytest.fixture()
def klien(proyek: Path) -> TestClient:
    return TestClient(create_app(Config.load(root=proyek), dist_dir=proyek / "tidak-ada"))


@pytest.mark.parametrize("nama", ENDPOINT)
def test_setiap_endpoint_menjawab(klien: TestClient, nama: str) -> None:
    respons = klien.get(f"/api/v1/{nama}")
    assert respons.status_code == 200, respons.text
    assert isinstance(respons.json(), dict)


def test_api_tanpa_hasil(tmp_path: Path) -> None:
    root = make_project(tmp_path, n_reviews=60)
    klien = TestClient(create_app(Config.load(root=root), dist_dir=tmp_path / "x"))
    for nama in ENDPOINT:
        assert klien.get(f"/api/v1/{nama}").status_code == 200, nama
    hasil = klien.get("/api/v1/hasil/terakhir").json()
    assert hasil["status"] == "belum_tersedia"
    assert "rra.cli run" in hasil["langkah"]


def test_hasil_sama_dengan_repository(klien: TestClient, proyek: Path) -> None:
    gudang = ResultRepository(Config.load(root=proyek).path("paths.db_path"))
    hasil = klien.get("/api/v1/hasil/terakhir").json()
    assert hasil["status"] == "selesai"
    harapan = [(r["aspect"], round(r["priority"], 6)) for r in gudang.load_priorities()]
    assert [(r["aspect"], round(r["priority"], 6)) for r in hasil["prioritas"]] == harapan
    assert len(hasil["prioritas"]) == 5
    assert hasil["run"]["n_reviews"] == 200


def test_hasil_nomor_tidak_ada_404(klien: TestClient) -> None:
    assert klien.get("/api/v1/hasil/9999").status_code == 404


def test_analisis_bersamaan_409(proyek: Path) -> None:
    app = create_app(Config.load(root=proyek), dist_dir=proyek / "x")
    kunci: threading.Lock = app.state.kunci_analisis
    kunci.acquire()
    try:
        respons = TestClient(app).post("/api/v1/analisis")
    finally:
        kunci.release()
    assert respons.status_code == 409
    assert respons.json()["detail"] == "Analisis sedang berjalan"


def test_root_tanpa_build(klien: TestClient) -> None:
    respons = klien.get("/")
    assert respons.status_code == 200
    assert "npm --prefix frontend run build" in respons.text


def test_root_menyajikan_spa(proyek: Path, tmp_path: Path) -> None:
    (tmp_path / "assets").mkdir()
    (tmp_path / "index.html").write_text("<html>RRA</html>", encoding="utf-8")
    (tmp_path / "assets" / "app.js").write_text("console.log(1)", encoding="utf-8")
    klien = TestClient(create_app(Config.load(root=proyek), dist_dir=tmp_path))
    assert klien.get("/").text == "<html>RRA</html>"
    assert klien.get("/hasil").text == "<html>RRA</html>"
    assert klien.get("/assets/app.js").text == "console.log(1)"
    assert klien.get("/api/v1/tidak-ada").status_code == 404


def test_openapi_memuat_skema_kontrak(klien: TestClient) -> None:
    skema = klien.get("/api/v1/openapi.json").json()["components"]["schemas"]
    assert "AspectPriority" in skema


def test_hipotesis_tiga_rm(klien: TestClient) -> None:
    isi = klien.get("/api/v1/hipotesis").json()
    assert [h["rm"] for h in isi["hipotesis"]] == [1, 2, 3]


def test_data_menandai_sampel_belum_ditetapkan(klien: TestClient) -> None:
    isi = klien.get("/api/v1/data").json()
    assert isi["sampling"]["n"] == 8
    assert isi["sampling"]["ditetapkan"] is False
    assert isi["ulasan"]["total"] == 200


def test_kebutuhan_terlacak_penuh(klien: TestClient) -> None:
    isi = klien.get("/api/v1/kebutuhan").json()
    assert isi["persen_terlacak"] == 100.0
    assert len(isi["kebutuhan"]) == 13


def test_perintah_serve_terdaftar() -> None:
    import subprocess
    import sys

    root = Path(__file__).resolve().parents[1]
    hasil = subprocess.run([sys.executable, "-m", "rra.cli", "serve", "--help"],
                           capture_output=True, text=True, env={"PYTHONPATH": str(root / "src"),
                                                                "PATH": ""}, timeout=120)
    assert hasil.returncode == 0, hasil.stderr
    assert "--port" in hasil.stdout


def test_ekspor_openapi(tmp_path: Path) -> None:
    import importlib.util
    import json

    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location("export_contracts", root / "scripts" / "export_contracts.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    target = modul.tulis_openapi(tmp_path / "openapi.json")
    assert "AspectPriority" in json.loads(target.read_text(encoding="utf-8"))["components"]["schemas"]


def test_endpoint_tahap_tanpa_parameter(klien: TestClient) -> None:
    jalur = klien.get("/api/v1/openapi.json").json()["paths"]
    for nama in ("status", "data", "hipotesis"):
        assert not jalur[f"/api/v1/{nama}"]["get"].get("parameters"), nama


def test_langkah_api_portabel(klien: TestClient) -> None:
    import json as _json

    teks = _json.dumps([klien.get(f"/api/v1/{n}").json() for n in ENDPOINT])
    assert "PYTHONPATH=" not in teks
