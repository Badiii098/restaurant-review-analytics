"""Uji kesesuaian peringkat sistem dengan urutan pakar (RM3)."""

from __future__ import annotations

import pytest

from rra.analysis.expert import spearman_per_restaurant, top1_agreement
from rra.analysis.expert import uji_median_rho as uji_median

pytestmark = pytest.mark.kasus("U-08")

URUT = ["pelayanan", "makanan", "harga", "suasana", "fasilitas"]


def test_urutan_identik_dan_terbalik() -> None:
    rho = spearman_per_restaurant({"r01": URUT, "r02": URUT}, {"r01": URUT, "r02": URUT[::-1]})
    assert rho["r01"] == pytest.approx(1.0)
    assert rho["r02"] == pytest.approx(-1.0)


def test_restoran_tanpa_urutan_pakar_atau_tidak_terdefinisi_bernilai_none() -> None:
    rho = spearman_per_restaurant({"r01": URUT, "r02": URUT}, {"r01": ["pelayanan"]})
    assert rho == {"r01": None, "r02": None}


def test_median_tinggi_menolak_h0() -> None:
    hasil = uji_median([0.9] * 9 + [0.8])
    assert hasil["n"] == 10
    assert hasil["tolak_h0"] is True
    assert hasil["p"] < 0.05


def test_median_rendah_tidak_menolak_h0() -> None:
    hasil = uji_median([0.3] * 9 + [0.2])
    assert hasil["tolak_h0"] is False


def test_nilai_none_dikeluarkan_dari_uji() -> None:
    hasil = uji_median([0.9] * 9 + [0.8, None])
    assert hasil["n"] == 10


def test_kesesuaian_peringkat_pertama() -> None:
    sistem = {k: URUT for k in ("a", "b", "c", "d")}
    pakar = {"a": URUT, "b": URUT, "c": URUT, "d": URUT[::-1]}
    assert top1_agreement(sistem, pakar) == pytest.approx(0.75)
