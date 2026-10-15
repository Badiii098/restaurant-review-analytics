"""Perhitungan skor prioritas aspek layanan.

Rumus yang dipakai dinyatakan terbuka:

    Prioritas(a) = w1 * Volume(a) + w2 * Keparahan(a) + w3 * Keragaman(a)

dengan ketentuan bobot ``w1 + w2 + w3 = 1``.

**Mengapa Volume dan Keragaman dinormalisasi, sedangkan Keparahan tidak.**
Keparahan sudah berada pada rentang [0, 1] secara alami karena ia
diturunkan dari rating bintang (lihat :mod:`rra.decision.severity`).
Menormalisasikannya kembali akan menghapus makna mutlaknya: aspek yang
seluruh keluhannya berasal dari ulasan berbintang satu tidak boleh
memperoleh nilai keparahan yang sama dengan aspek yang keluhannya
berbintang empat. Sebaliknya, Volume dan Keragaman tidak memiliki skala
alamiah, sehingga perlu disetarakan terlebih dahulu.

**Mengapa rumus ini penting.** Penelitian terdahulu menentukan prioritas
melalui pembacaan manual dan diskusi dengan pemilik usaha, sehingga hasilnya
tidak dapat diulang dan tidak dapat diaudit. Setiap angka pada rumus ini
dapat diperiksa, dan setiap komponennya disimpan bersama hasilnya sehingga
pengguna dapat menelusuri asal sebuah peringkat.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Mapping, Sequence

from rra.contracts import ASPECT_LABELS, AspectPriority


@dataclass(slots=True)
class AspectStat:
    """Bahan mentah penghitungan prioritas untuk satu aspek."""

    aspect: str
    n_total: int = 0
    n_negative: int = 0
    severities: list[float] = field(default_factory=list)
    n_phrases: int = 0

    @property
    def mean_severity(self) -> float:
        return round(sum(self.severities) / len(self.severities), 6) if self.severities else 0.0


def minmax_normalize(values: Mapping[str, float]) -> dict[str, float]:
    """Setarakan nilai ke rentang [0, 1].

    Bila seluruh nilai sama (rentang nol), seluruh aspek dianggap setara.
    Dalam keadaan itu aspek yang bernilai positif diberi 1,0 dan yang
    bernilai nol diberi 0,0, sebagaimana dinyatakan pada dokumentasi kelas
    ini agar tidak menimbulkan ambiguitas saat diaudit.
    """
    if not values:
        return {}
    low = min(values.values())
    high = max(values.values())
    span = high - low
    if span <= 0:
        return {key: (1.0 if value > 0 else 0.0) for key, value in values.items()}
    return {key: round((value - low) / span, 6) for key, value in values.items()}


class PriorityEngine:
    """Mesin peringkat prioritas aspek layanan."""

    DEFAULT_WEIGHTS: dict[str, float] = {"volume": 0.4, "severity": 0.4, "diversity": 0.2}

    def __init__(self, weights: Mapping[str, float] | None = None) -> None:
        merged = dict(self.DEFAULT_WEIGHTS)
        if weights:
            merged.update({key: float(value) for key, value in weights.items()})
        total = sum(merged.values())
        if total <= 0:
            raise ValueError("Jumlah bobot prioritas harus positif.")
        # Setarakan agar jumlahnya tepat 1 — agar skor tetap sebanding
        # walau pengguna memasukkan bobot dengan skala berbeda.
        self.weights = {key: round(value / total, 6) for key, value in merged.items()}

    @classmethod
    def from_config(cls, cfg) -> "PriorityEngine":
        return cls(cfg.get("decision.weights"))

    # ------------------------------------------------------------------ #
    def compute(self, stats: Mapping[str, AspectStat]) -> list[AspectPriority]:
        """Hitung prioritas seluruh aspek dan kembalikan dalam urutan peringkat."""
        if not stats:
            return []

        volume_norm = minmax_normalize({a: float(s.n_negative) for a, s in stats.items()})
        diversity_norm = minmax_normalize({a: float(s.n_phrases) for a, s in stats.items()})

        results: list[AspectPriority] = []
        for aspect, stat in stats.items():
            volume = volume_norm.get(aspect, 0.0)
            severity = stat.mean_severity              # sudah pada rentang [0, 1]
            diversity = diversity_norm.get(aspect, 0.0)
            priority = (
                self.weights["volume"] * volume
                + self.weights["severity"] * severity
                + self.weights["diversity"] * diversity
            )
            results.append(
                AspectPriority(
                    aspect=aspect,
                    label=ASPECT_LABELS.get(aspect, aspect.title()),
                    rank=0,
                    priority=round(priority, 6),
                    volume=volume,
                    severity=severity,
                    diversity=diversity,
                    n_negative=stat.n_negative,
                    n_total=stat.n_total,
                )
            )

        # Urutkan menurun; bila skor seri, aspek dengan volume keluhan lebih
        # besar didahulukan, lalu diurutkan menurut nama agar hasilnya tetap
        # sama pada setiap kali dijalankan.
        results.sort(key=lambda item: (-item.priority, -item.n_negative, item.aspect))
        # AspectPriority bersifat tidak dapat diubah (frozen), sehingga
        # peringkat disisipkan dengan membuat salinan baru.
        return [replace(item, rank=position) for position, item in enumerate(results, start=1)]

    def describe(self) -> dict[str, object]:
        return {"weights": dict(self.weights), "formula": "w1*Volume + w2*Keparahan + w3*Keragaman"}
