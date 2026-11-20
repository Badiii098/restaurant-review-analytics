"""Aplikasi FastAPI: API ``/api/v1`` dan klien web hasil build ``frontend/dist``."""

from __future__ import annotations

import threading
from pathlib import Path
from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from rra.api.schemas import AnalisisBaru, Hasil
from rra.config import Config
from rra.services import tahap

DIST_BAWAAN = Path(__file__).resolve().parents[3] / "frontend" / "dist"
PESAN_BUILD = ("Klien web belum dibangun.\n\nJalankan sekali:\n"
               "    npm --prefix frontend install\n    npm --prefix frontend run build\n\n"
               "API tetap tersedia di /api/v1 (dokumentasi: /api/v1/docs).\n")


def create_app(cfg: Config, dist_dir: Path | None = None) -> FastAPI:
    app = FastAPI(title="Restaurant Review Analytics", version="2.0.0",
                  openapi_url="/api/v1/openapi.json", docs_url="/api/v1/docs", redoc_url=None)
    app.state.cfg = cfg
    app.state.kunci_analisis = threading.Lock()
    api = APIRouter(prefix="/api/v1")

    sederhana = {"status": tahap.status, "data": tahap.data, "anotasi": tahap.anotasi,
                 "kebutuhan": tahap.kebutuhan, "desain": tahap.desain, "iterasi": tahap.iterasi,
                 "sensitivitas": tahap.sensitivitas, "pengujian": tahap.pengujian,
                 "pakar": tahap.pakar, "hipotesis": tahap.hipotesis}
    def _titik(fungsi: Callable[[Config], dict]) -> Callable[[], dict[str, Any]]:
        def titik() -> dict[str, Any]:
            return fungsi(app.state.cfg)
        return titik

    for nama, fungsi in sederhana.items():
        api.add_api_route(f"/{nama}", _titik(fungsi), methods=["GET"], name=nama, tags=["tahap"])

    @api.get("/hasil/terakhir", response_model=Hasil, tags=["hasil"])
    def hasil_terakhir() -> dict:
        return tahap.hasil(app.state.cfg)

    @api.get("/hasil/{run_id}", response_model=Hasil, tags=["hasil"])
    def hasil_nomor(run_id: int) -> dict:
        isi = tahap.hasil(app.state.cfg, run_id)
        if isi is None:
            raise HTTPException(404, f"Hasil nomor {run_id} tidak ada")
        return isi

    @api.post("/analisis", response_model=AnalisisBaru, tags=["hasil"])
    def analisis() -> dict:
        kunci: threading.Lock = app.state.kunci_analisis
        if not kunci.acquire(blocking=False):
            raise HTTPException(409, "Analisis sedang berjalan")
        try:
            return {"run_id": tahap.analisis(app.state.cfg)}
        finally:
            kunci.release()

    @api.get("/{sisa:path}", include_in_schema=False)
    def tidak_ada(sisa: str) -> None:
        raise HTTPException(404, f"Endpoint /api/v1/{sisa} tidak ada")

    app.include_router(api)
    _pasang_klien(app, Path(dist_dir) if dist_dir is not None else DIST_BAWAAN)
    return app


def _pasang_klien(app: FastAPI, dist: Path) -> None:
    indeks = dist / "index.html"
    if (dist / "assets").is_dir():
        app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

    @app.get("/{rute:path}", include_in_schema=False)
    def klien(rute: str):  # noqa: ANN202
        if not indeks.exists():
            return PlainTextResponse(PESAN_BUILD)
        berkas = (dist / rute).resolve()
        if rute and berkas.is_file() and dist.resolve() in berkas.parents:
            return FileResponse(berkas)
        return FileResponse(indeks)
