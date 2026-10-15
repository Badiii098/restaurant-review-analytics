"""LAPISAN 3 — Komponen klasifikasi aspek & sentimen.

Lapisan ini adalah satu-satunya bagian sistem yang bergantung pada
pustaka pembelajaran mesin. Seluruh lapisan lain hanya mengenal
:class:`rra.models.base.AspectSentimentModel`, bukan implementasinya.

Karena itu, mengganti algoritma cukup dengan mengubah ``model.name``
pada berkas konfigurasi.
"""

from rra.models.base import AspectSentimentModel  # noqa: F401
from rra.models.registry import (  # noqa: F401
    available_models,
    build_model,
    register_model,
)

__all__ = [
    "AspectSentimentModel",
    "build_model",
    "available_models",
    "register_model",
]
