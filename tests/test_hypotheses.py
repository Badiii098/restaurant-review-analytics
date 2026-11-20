"""Keputusan hipotesis RM1–RM3 dari bukti yang benar-benar ada."""

from __future__ import annotations

from pathlib import Path

import pytest

from rra.analysis.hypotheses import uji_h1, uji_h2, uji_h3
from rra.junit import ringkas_junit
from rra.requirements import Katalog

pytestmark = pytest.mark.kasus("U-12")

KATALOG = Katalog(
    kebutuhan=[{"kode": "FR-01", "kasus": ["U-01"]}, {"kode": "KNF-01", "kasus": ["N-01"]}],
    kasus=[{"kode": "U-01", "jenis": "otomatis", "kritis": True},
           {"kode": "N-01", "jenis": "manual", "kritis": False, "bukti": "reports/benchmark.json"}],
)

JUNIT = """<?xml version="1.0"?><testsuites><testsuite name="pytest" tests="4">
<testcase classname="t" name="a"><properties><property name="kasus" value="U-01"/></properties></testcase>
<testcase classname="t" name="b"><properties><property name="kasus" value="U-01,U-02"/></properties></testcase>
<testcase classname="t" name="c"><properties><property name="kasus" value="U-02"/></properties><failure message="x"/></testcase>
<testcase classname="t" name="d"><properties><property name="kasus" value="U-03"/></properties><skipped/></testcase>
</testsuite></testsuites>"""


def _benchmark(detik: list[float], n_ulasan: int = 1000) -> dict:
    return {"summary": {"n_ulasan": n_ulasan},
            "perulangan": [{"ulangan": i + 1, "total_dinding": d} for i, d in enumerate(detik)]}


def test_ringkas_junit_per_kasus(tmp_path: Path) -> None:
    berkas = tmp_path / "pytest.xml"
    berkas.write_text(JUNIT, encoding="utf-8")
    hasil = ringkas_junit(berkas)
    assert (hasil["total"], hasil["lulus"], hasil["gagal"], hasil["dilewati"]) == (4, 2, 1, 1)
    assert hasil["per_kasus"] == {"U-01": "lulus", "U-02": "gagal", "U-03": "dilewati"}


def test_ringkas_junit_tanpa_berkas(tmp_path: Path) -> None:
    assert ringkas_junit(tmp_path / "tidak-ada.xml") is None


def test_h1_tolak_h0_bila_kontrak_lolos_dan_terlacak() -> None:
    hasil = uji_h1(KATALOG, {"per_kasus": {"U-01": "lulus"}})
    assert hasil["status"] == "selesai" and hasil["tolak_h0"] is True
    assert hasil["statistik"] == {"persen_kontrak_lolos": 100.0, "persen_terlacak": 100.0}


def test_h1_tidak_tolak_bila_kontrak_gagal() -> None:
    assert uji_h1(KATALOG, {"per_kasus": {"U-01": "gagal"}})["tolak_h0"] is False


def test_h2_tolak_h0_bila_cepat_dan_uji_kritis_lulus() -> None:
    hasil = uji_h2(_benchmark([10.0, 11.0, 9.5, 10.2, 10.4]), {"per_kasus": {"U-01": "lulus"}}, KATALOG)
    assert hasil["tolak_h0"] is True
    assert hasil["statistik"]["rata_rata_detik_per_1000"] == pytest.approx(10.22)
    assert hasil["p"] < 0.05


def test_h2_dinormalisasi_per_seribu_ulasan() -> None:
    hasil = uji_h2(_benchmark([5.0, 5.0, 5.1, 4.9, 5.0], n_ulasan=2000), {"per_kasus": {"U-01": "lulus"}}, KATALOG)
    assert hasil["statistik"]["rata_rata_detik_per_1000"] == pytest.approx(2.5)


def test_h2_tidak_tolak_bila_satu_uji_kritis_gagal() -> None:
    hasil = uji_h2(_benchmark([10.0, 11.0, 9.5, 10.2, 10.4]), {"per_kasus": {"U-01": "gagal"}}, KATALOG)
    assert hasil["tolak_h0"] is False
    assert hasil["statistik"]["kasus_kritis_gagal"] == ["U-01"]


def test_h3_tolak_h0_dengan_delapan_restoran() -> None:
    rho = [1, 0.9, 0.9, 0.8, 1, 0.9, 0.7, 0.9]
    laporan = {"rho_per_restoran": {f"r{i}": r for i, r in enumerate(rho)},
               "kesesuaian_peringkat_1": 0.75}
    hasil = uji_h3(laporan)
    assert hasil["tolak_h0"] is True and hasil["statistik"]["n"] == 8


@pytest.mark.parametrize("fungsi", ["h1", "h2", "h3"])
def test_tanpa_bukti_belum_tersedia(fungsi: str) -> None:
    hasil = {"h1": lambda: uji_h1(KATALOG, None), "h2": lambda: uji_h2(None, None, KATALOG),
             "h3": lambda: uji_h3(None)}[fungsi]()
    assert hasil["status"] == "belum_tersedia" and hasil["tolak_h0"] is None
    assert hasil["langkah"]
