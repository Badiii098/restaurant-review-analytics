"""Keterlacakan kebutuhan → kasus uji → berkas uji (bukti H1 RM1).

Setiap kebutuhan FR/KNF harus punya minimal satu kasus uji; setiap kasus
otomatis harus benar-benar ditandai pada suatu uji dengan
``pytest.mark.kasus("<kode>")``; setiap kasus manual harus menyebut berkas
buktinya.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from rra.requirements import kasus_di_berkas_uji, muat_katalog, persen_terlacak

ROOT = Path(__file__).resolve().parents[1]
KATALOG = muat_katalog(ROOT / "config" / "kebutuhan.yaml")

pytestmark = pytest.mark.kasus("U-13")


def test_katalog_memuat_seluruh_kebutuhan_pakem() -> None:
    kode = [k["kode"] for k in KATALOG.kebutuhan]
    assert kode == [f"FR-0{i}" for i in range(1, 9)] + [f"KNF-0{i}" for i in range(1, 6)]


def test_setiap_kebutuhan_punya_kasus() -> None:
    kasus = {k["kode"] for k in KATALOG.kasus}
    for kebutuhan in KATALOG.kebutuhan:
        assert kebutuhan["kasus"], kebutuhan["kode"]
        assert set(kebutuhan["kasus"]) <= kasus, kebutuhan["kode"]
    assert persen_terlacak(KATALOG) == 100.0


def test_setiap_kasus_otomatis_punya_uji() -> None:
    ditandai = kasus_di_berkas_uji(ROOT / "tests")
    hilang = [k["kode"] for k in KATALOG.kasus if k["jenis"] == "otomatis" and k["kode"] not in ditandai]
    assert hilang == []


def test_kasus_manual_menyebut_bukti() -> None:
    for kasus in KATALOG.kasus:
        if kasus["jenis"] == "manual":
            assert kasus.get("bukti"), kasus["kode"]


def test_persen_terlacak_turun_bila_ada_kebutuhan_tanpa_kasus() -> None:
    from dataclasses import replace

    rusak = replace(KATALOG, kebutuhan=[*KATALOG.kebutuhan, {"kode": "FR-99", "kasus": []}])
    assert persen_terlacak(rusak) < 100.0
