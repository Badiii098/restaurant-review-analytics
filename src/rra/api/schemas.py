"""Skema respons API yang dibangkitkan dari kontrak ``rra.contracts``.

``AspectPriority`` dipakai langsung sebagai model respons sehingga skema
OpenAPI dan kontrak antar-lapis tidak dapat berbeda (bukti H1 RM1).
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

from rra.contracts import AspectPriority


class Frasa(BaseModel):
    model_config = ConfigDict(extra="ignore")
    aspect: str
    rank: int
    phrase: str
    frequency: int
    tfidf_weight: float
    score: float
    example_review_ids: list[str] = []


class Rekomendasi(BaseModel):
    model_config = ConfigDict(extra="ignore")
    aspect: str
    phrase: str
    action: str
    evidence: str = ""


class Hasil(BaseModel):
    status: str
    langkah: str | None = None
    run: dict[str, Any] | None = None
    prioritas: list[AspectPriority] = []
    frasa: list[Frasa] = []
    rekomendasi: list[Rekomendasi] = []


class AnalisisBaru(BaseModel):
    run_id: int
