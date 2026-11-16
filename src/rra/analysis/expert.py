"""Kesesuaian peringkat prioritas sistem dengan urutan pakar (RM3).

Per restoran, urutan lima aspek dari sistem dibandingkan dengan urutan dari
pakar memakai korelasi peringkat Spearman. Dengan hanya lima aspek, uji per
restoran hampir tidak bermakna: pada uji dua sisi α = 0,05 hanya ρ = 1,0 yang
signifikan (p = 0,017), sedangkan ρ = 0,9 belum (p = 0,083). Karena itu keputusan
diambil pada tingkat seluruh restoran: median ρ diuji
terhadap ambang 0,60 dengan uji peringkat bertanda Wilcoxon satu sisi.

H0: median ρ ≤ 0,60. H1: median ρ > 0,60.
"""

from __future__ import annotations

import math
from statistics import median
from typing import Iterable, Mapping, Sequence

from scipy.stats import spearmanr, wilcoxon


def _rho(sistem: Sequence[str], pakar: Sequence[str]) -> float | None:
    aspek = [a for a in sistem if a in pakar]
    if len(aspek) < 3 or len(set(pakar)) != len(pakar):
        return None
    nilai = spearmanr([sistem.index(a) for a in aspek], [pakar.index(a) for a in aspek])[0]
    return None if nilai is None or math.isnan(nilai) else float(nilai)


def spearman_per_restaurant(
    system: Mapping[str, Sequence[str]], expert: Mapping[str, Sequence[str]]
) -> dict[str, float | None]:
    """ρ per restoran; ``None`` bila urutan pakar tidak ada, kurang dari tiga aspek, atau seri."""
    return {kode: (_rho(urut, expert[kode]) if kode in expert else None)
            for kode, urut in system.items()}


def uji_median_rho(rhos: Iterable[float | None], threshold: float = 0.60,
                   alpha: float = 0.05) -> dict:
    """Wilcoxon satu sampel satu sisi: apakah median ρ melebihi ``threshold``."""
    nilai = [float(r) for r in rhos if r is not None]
    selisih = [r - threshold for r in nilai]
    if not nilai or all(d == 0 for d in selisih):
        return {"n": len(nilai), "median": median(nilai) if nilai else None,
                "statistik": None, "p": None, "tolak_h0": False}
    hasil = wilcoxon(selisih, alternative="greater")
    p = float(hasil.pvalue)
    return {"n": len(nilai), "median": round(median(nilai), 4),
            "statistik": float(hasil.statistic), "p": round(p, 6), "tolak_h0": p < alpha}


def top1_agreement(system: Mapping[str, Sequence[str]],
                   expert: Mapping[str, Sequence[str]]) -> float:
    """Proporsi restoran yang aspek peringkat pertamanya sama antara sistem dan pakar."""
    kode = [k for k in system if k in expert and system[k] and expert[k]]
    if not kode:
        return 0.0
    return sum(system[k][0] == expert[k][0] for k in kode) / len(kode)
