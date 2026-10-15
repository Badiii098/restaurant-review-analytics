"""Registri komponen model.

Registri memetakan nilai ``model.name`` pada berkas konfigurasi ke kelas
implementasinya. Inilah satu-satunya tempat yang perlu disentuh ketika
sebuah algoritma baru ditambahkan — dan untuk mengganti algoritma yang
sudah ada, cukup ubah konfigurasinya.

Modul implementasi dimuat secara *malas* (``importlib``) agar tidak
menimbulkan ketergantungan melingkar: modul implementasi mengimpor
``register_model`` dari sini, sehingga modul ini tidak boleh mengimpor
mereka pada saat pemuatan.
"""

from __future__ import annotations

import importlib
from typing import Any, Type

from rra.models.base import AspectSentimentModel

#: Modul bawaan yang didaftarkan ketika registri pertama kali dipakai.
BUILTIN_MODULES: tuple[str, ...] = (
    "rra.models.svm_model",
    "rra.models.nb_model",
)

_REGISTRY: dict[str, Type[AspectSentimentModel]] = {}
_LOADED = False


def register_model(cls: Type[AspectSentimentModel]) -> Type[AspectSentimentModel]:
    """Daftarkan sebuah implementasi komponen model (dipakai sebagai dekorator)."""
    key = getattr(cls, "name", None)
    if not key or key == "base":
        raise ValueError(f"Kelas {cls.__name__} belum menetapkan atribut 'name'.")
    existing = _REGISTRY.get(key)
    if existing is not None and existing is not cls:
        raise ValueError(f"Nama model '{key}' sudah dipakai oleh {existing.__name__}.")
    _REGISTRY[key] = cls
    return cls


def _ensure_loaded() -> None:
    """Muat seluruh modul implementasi bawaan sekali saja."""
    global _LOADED
    if _LOADED:
        return
    for module_name in BUILTIN_MODULES:
        importlib.import_module(module_name)
    _LOADED = True


def available_models() -> dict[str, str]:
    """Kembalikan daftar model yang tersedia beserta nama tampilannya."""
    _ensure_loaded()
    return {key: cls.display_name for key, cls in sorted(_REGISTRY.items())}


def get_model_class(name: str) -> Type[AspectSentimentModel]:
    _ensure_loaded()
    try:
        return _REGISTRY[name]
    except KeyError:
        raise KeyError(
            f"Model '{name}' tidak terdaftar. Pilihan yang tersedia: {sorted(_REGISTRY)}"
        ) from None


def build_model(cfg: Any) -> AspectSentimentModel:
    """Bangun komponen model sesuai isi konfigurasi.

    Hanya nilai ``model.name`` yang menentukan implementasi mana yang
    dipakai. Seluruh parameter lain diteruskan tanpa perubahan — inilah
    yang membuat penggantian komponen cukup dilakukan lewat konfigurasi.
    """
    name = str(cfg.get("model.name", "svm"))
    cls = get_model_class(name)
    kwargs: dict[str, Any] = {
        "tfidf": cfg.get("model.tfidf"),
        "aspect_threshold": cfg.get("model.aspect_threshold", 0.5),
        "seed": cfg.get("project.seed", 42),
    }
    return cls(**kwargs)


def load_artifact(path: str | Any, name: str | None = None) -> AspectSentimentModel:
    """Muat komponen tersimpan; kelas ditentukan oleh nama model pada artefak."""
    import joblib

    payload = joblib.load(path)
    key = name or str(payload.get("model_name", "svm"))
    return get_model_class(key).load(path)
