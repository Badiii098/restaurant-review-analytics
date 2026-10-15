"""LAPISAN 1 — Akuisisi & penyimpanan data.

Modul ini bertanggung jawab penuh atas asal-usul data. Lapisan di atasnya
hanya menerima :class:`~rra.contracts.RawReview` dan tidak perlu tahu
apakah data berasal dari hasil <i>scraping</i>, basis data, atau berkas.
"""

from rra.io_layer.loader import ReviewLoader, describe_dataset  # noqa: F401
from rra.io_layer.sample_data import (  # noqa: F401
    ASPECT_PROFILE,
    generate_dataset,
    write_dataset,
)

__all__ = [
    "ReviewLoader",
    "describe_dataset",
    "generate_dataset",
    "write_dataset",
    "ASPECT_PROFILE",
]
