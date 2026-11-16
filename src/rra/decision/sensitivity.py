"""Uji sensitivitas bobot skor prioritas.

Bobot 0,40/0,40/0,20 ditetapkan peneliti, sehingga harus ditunjukkan bahwa
peringkat tidak berubah drastis bila bobot itu sedikit digeser. Setiap
komponen dinaikkan dan diturunkan 10% (relatif), bobot dinormalisasi ulang
agar berjumlah 1, lalu peringkat baru dibandingkan dengan peringkat dasar
memakai tau Kendall dan kesamaan aspek peringkat pertama.
"""

from __future__ import annotations

from typing import Mapping

from scipy.stats import kendalltau

from rra.decision.priority import AspectStat, PriorityEngine

KOMPONEN: tuple[str, ...] = ("volume", "severity", "diversity")


def _ranking(stats: Mapping[str, AspectStat], weights: Mapping[str, float]) -> list[str]:
    return [item.aspect for item in PriorityEngine(weights).compute(stats)]


def weight_sensitivity(
    stats: Mapping[str, AspectStat],
    base: Mapping[str, float] | None = None,
    delta: float = 0.10,
) -> list[dict]:
    """Peringkat aspek untuk setiap komponen bobot yang digeser ±``delta``."""
    dasar = PriorityEngine(base).weights
    peringkat_dasar = _ranking(stats, dasar)
    posisi_dasar = {aspek: i for i, aspek in enumerate(peringkat_dasar)}

    rows: list[dict] = []
    for komponen in KOMPONEN:
        for arah, faktor in (("+", 1 + delta), ("-", 1 - delta)):
            mentah = dict(dasar)
            mentah[komponen] = dasar[komponen] * faktor
            total = sum(mentah.values())
            bobot = {k: v / total for k, v in mentah.items()}
            peringkat = _ranking(stats, bobot)
            tau = kendalltau([posisi_dasar[a] for a in peringkat], range(len(peringkat)))[0]
            rows.append({
                "komponen": komponen,
                "arah": arah,
                "bobot": bobot,
                "peringkat": peringkat,
                "peringkat_1_sama": peringkat[:1] == peringkat_dasar[:1],
                "tau_kendall": round(float(tau), 4) if tau == tau else 1.0,
            })
    return rows
