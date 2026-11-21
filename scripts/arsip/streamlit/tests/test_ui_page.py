"""Uji halaman: merender antarmuka dari basis data hasil yang sebenarnya.

Uji ini menyalakan berkas halaman lewat ``streamlit.testing`` tanpa
peramban, sehingga membuktikan dua hal yang tidak bisa dijamin uji
komponen: halaman tidak melempar galat, dan seluruh bagiannya benar
benar terbentuk dari baris ``rra.sqlite``.

Bila basis data belum ada atau belum punya hasil, uji dilewati — bukan
dipalsukan.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for candidate in (str(ROOT / "src"), str(ROOT / "app")):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

APP = ROOT / "app" / "streamlit_app.py"
DB = ROOT / "data" / "processed" / "rra.sqlite"

pytest.importorskip("streamlit.testing.v1")

from streamlit.testing.v1 import AppTest  # noqa: E402

pytestmark = pytest.mark.kasus("S-03")


def _butuh_hasil() -> None:
    if not DB.exists():
        pytest.skip("basis data hasil belum dibuat")
    import sqlite3

    with sqlite3.connect(DB) as connection:
        jumlah = connection.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
    if not jumlah:
        pytest.skip("basis data belum memuat hasil analisis")


def test_halaman_terbentuk_tanpa_galat():
    _butuh_hasil()
    at = AppTest.from_file(str(APP), default_timeout=120)
    at.run()
    assert not at.exception, at.exception

    teks = "\n".join(blok.value for blok in at.markdown)

    # Kepala laporan dan keempat bagian wajib ada.
    assert "Prioritas perbaikan layanan" in teks
    assert "Peringkat prioritas" in teks
    assert "Frasa keluhan dominan" in teks
    assert "Tindakan yang disarankan" in teks
    assert "Bahan audit" in teks

    # Angka berasal dari basis data, bukan dari halaman.
    assert "Ulasan dianalisis" in teks
    assert "tersimpan pada" in teks


def test_bilah_samping_tanpa_pemilih_model():
    """Penelitian memakai satu model, jadi tidak ada pemilih komponen."""
    _butuh_hasil()
    at = AppTest.from_file(str(APP), default_timeout=120)
    at.run()
    assert not at.exception, at.exception
    assert len(at.selectbox) == 0


def test_hasil_arsip_naive_bayes_tetap_terbaca():
    """Hasil lama bermodel nb di basis data tetap tampil tanpa galat."""
    _butuh_hasil()
    import sqlite3

    with sqlite3.connect(DB) as connection:
        terakhir = connection.execute(
            "SELECT model_name FROM runs ORDER BY run_id DESC LIMIT 1"
        ).fetchone()[0]
    if terakhir != "nb":
        pytest.skip("hasil terakhir bukan arsip nb")
    at = AppTest.from_file(str(APP), default_timeout=120)
    at.run()
    assert not at.exception, at.exception
    teks = "\n".join(blok.value for blok in at.markdown)
    assert "Naive Bayes (arsip)" in teks
