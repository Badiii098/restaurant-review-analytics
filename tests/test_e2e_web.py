"""Uji sistem di peramban: klien React + API FastAPI dijalankan seperti oleh pengguna.

Dilewati bila klien belum di-build (``npm --prefix frontend run build``) atau
Playwright tidak tersedia; tidak pernah dipalsukan.
"""

from __future__ import annotations

import socket
import statistics
import threading
import time
from pathlib import Path

import pytest

from conftest import make_project
from rra.config import Config

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "frontend" / "dist"

pytestmark = [
    pytest.mark.skipif(not (DIST / "index.html").exists(), reason="frontend belum di-build"),
]
sync_api = pytest.importorskip("playwright.sync_api")

RUTE = {"/": "Sistem analitik", "/data": "Pengumpulan data", "/anotasi": "Anotasi data",
        "/kebutuhan": "Analisis kebutuhan", "/desain": "Desain cepat", "/iterasi": "Pembangunan prototipe",
        "/hasil": "Hasil & prioritas", "/pengujian": "Pengujian perangkat lunak",
        "/pakar": "Validasi pakar", "/kesimpulan": "Analisis hasil"}


def _port_bebas() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def alamat(tmp_path_factory: pytest.TempPathFactory):
    import uvicorn

    from rra.api.app import create_app
    from rra.services import tahap

    root = make_project(tmp_path_factory.mktemp("e2e"), n_reviews=200)
    cfg = Config.load(root=root)
    tahap.analisis(cfg)
    port = _port_bebas()
    server = uvicorn.Server(uvicorn.Config(create_app(cfg, dist_dir=DIST), host="127.0.0.1",
                                           port=port, log_level="warning"))
    benang = threading.Thread(target=server.run, daemon=True)
    benang.start()
    batas = time.time() + 20
    while not server.started and time.time() < batas:
        time.sleep(0.05)
    yield f"http://127.0.0.1:{port}"
    server.should_exit = True
    benang.join(timeout=10)


@pytest.fixture(scope="module")
def peramban():
    with sync_api.sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


@pytest.mark.kasus("S-03")
def test_setiap_halaman_tampil(alamat: str, peramban) -> None:
    halaman = peramban.new_page()
    galat: list[str] = []
    halaman.on("console", lambda m: galat.append(m.text) if m.type == "error" else None)
    halaman.on("pageerror", lambda e: galat.append(str(e)))
    for rute, judul in RUTE.items():
        halaman.goto(alamat + rute)
        h1 = halaman.locator("h1")
        sync_api.expect(h1).to_contain_text(judul, timeout=10_000)
        halaman.wait_for_load_state("networkidle")
        assert halaman.locator("[role=alert]").count() == 0, rute
    assert galat == []
    halaman.close()


@pytest.mark.kasus("S-03")
def test_hasil_halaman_sama_dengan_api(alamat: str, peramban) -> None:
    import httpx

    api = httpx.get(f"{alamat}/api/v1/hasil/terakhir").json()
    halaman = peramban.new_page()
    halaman.goto(alamat + "/hasil")
    baris = halaman.locator("table").first.locator("tbody tr")
    sync_api.expect(baris).to_have_count(5, timeout=10_000)
    pertama = api["prioritas"][0]
    teks = baris.first.inner_text()
    assert pertama["label"] in teks
    assert f"{pertama['priority'] * 100:.1f}".replace(".", ",") in teks
    halaman.close()


@pytest.mark.kasus("N-03")
def test_knf03_peringkat_tampil_3_detik(alamat: str, peramban) -> None:
    waktu: list[float] = []
    for _ in range(5):
        konteks = peramban.new_context()
        halaman = konteks.new_page()
        mulai = time.perf_counter()
        halaman.goto(alamat + "/hasil")
        halaman.locator("table").first.locator("tbody tr").first.wait_for(state="visible", timeout=10_000)
        waktu.append(time.perf_counter() - mulai)
        konteks.close()
    assert statistics.mean(waktu) <= 3.0, waktu
