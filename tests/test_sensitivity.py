"""Uji sensitivitas bobot skor prioritas terhadap perubahan ±10%."""

from __future__ import annotations

import pytest

from rra.decision.priority import AspectStat
from rra.decision.sensitivity import weight_sensitivity

pytestmark = pytest.mark.kasus("U-07")


@pytest.fixture()
def stats() -> dict[str, AspectStat]:
    return {
        "pelayanan": AspectStat("pelayanan", n_total=1700, n_negative=750,
                                severities=[0.6] * 10, n_phrases=40),
        "makanan": AspectStat("makanan", n_total=2000, n_negative=370,
                              severities=[0.55] * 10, n_phrases=20),
        "harga": AspectStat("harga", n_total=1200, n_negative=370,
                            severities=[0.5] * 10, n_phrases=10),
        "suasana": AspectStat("suasana", n_total=1100, n_negative=360,
                              severities=[0.5] * 10, n_phrases=22),
        "fasilitas": AspectStat("fasilitas", n_total=800, n_negative=230,
                                severities=[0.45] * 10, n_phrases=8),
    }


def test_enam_skenario_untuk_tiga_komponen_dua_arah(stats) -> None:
    rows = weight_sensitivity(stats)
    assert len(rows) == 6
    assert {(r["komponen"], r["arah"]) for r in rows} == {
        (k, a) for k in ("volume", "severity", "diversity") for a in ("+", "-")
    }


def test_bobot_hasil_perturbasi_dinormalisasi_ulang(stats) -> None:
    for row in weight_sensitivity(stats):
        assert sum(row["bobot"].values()) == pytest.approx(1.0, abs=1e-6)


def test_aspek_dominan_tetap_peringkat_pertama(stats) -> None:
    rows = weight_sensitivity(stats)
    assert all(row["peringkat_1_sama"] for row in rows)
    assert all(row["peringkat"][0] == "pelayanan" for row in rows)
    assert all(-1.0 <= row["tau_kendall"] <= 1.0 for row in rows)
