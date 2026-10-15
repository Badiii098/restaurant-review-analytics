"""Pemuatan konfigurasi sistem.

Konfigurasi disusun berlapis: berkas dasar (``config/default.yaml``) dapat
ditimpa oleh berkas varian (mis. ``config/model_nb.yaml``) dan oleh
penimpaan langsung dari baris perintah (``--set model.name=nb``).

Pemisahan inilah yang membuat penggantian komponen model hanya menuntut
perubahan konfigurasi, bukan perubahan kode.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Mapping

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def deep_merge(base: Mapping[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    """Gabungkan dua kamus secara rekursif; nilai pada *override* menang."""
    result: dict[str, Any] = copy.deepcopy(dict(base))
    for key, value in override.items():
        if key in result and isinstance(result[key], Mapping) and isinstance(value, Mapping):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def _coerce(raw: str) -> Any:
    """Ubah nilai teks menjadi tipe Python yang sesuai."""
    text = raw.strip()
    low = text.lower()
    if low in {"true", "yes"}:
        return True
    if low in {"false", "no"}:
        return False
    if low in {"null", "none", "~"}:
        return None
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        pass
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        return [_coerce(part) for part in inner.split(",")] if inner else []
    return text


class Config:
    """Konfigurasi sistem dengan akses bertitik (``cfg.get("model.name")``)."""

    def __init__(self, data: Mapping[str, Any], root: Path = PROJECT_ROOT) -> None:
        self._data: dict[str, Any] = copy.deepcopy(dict(data))
        self.root = Path(root)

    # ------------------------------------------------------------------ #
    # Akses nilai
    # ------------------------------------------------------------------ #
    def get(self, dotted: str, default: Any = None) -> Any:
        node: Any = self._data
        for part in dotted.split("."):
            if not isinstance(node, Mapping) or part not in node:
                return default
            node = node[part]
        return node

    def __getitem__(self, dotted: str) -> Any:
        value = self.get(dotted, _MISSING)
        if value is _MISSING:
            raise KeyError(f"Kunci konfigurasi tidak ditemukan: {dotted}")
        return value

    def __contains__(self, dotted: str) -> bool:
        return self.get(dotted, _MISSING) is not _MISSING

    def path(self, dotted: str) -> Path:
        """Kembalikan jalur absolut untuk kunci yang memuat jalur relatif."""
        value = self[dotted]
        path = Path(str(value)).expanduser()
        return path if path.is_absolute() else (self.root / path)

    def as_dict(self) -> dict[str, Any]:
        return copy.deepcopy(self._data)

    # ------------------------------------------------------------------ #
    # Pemuatan
    # ------------------------------------------------------------------ #
    @classmethod
    def load(
        cls,
        base: str | Path = "config/default.yaml",
        *,
        override: str | Path | None = None,
        sets: Mapping[str, Any] | None = None,
        root: Path | None = None,
    ) -> "Config":
        """Muat konfigurasi dasar, lalu timpa dengan berkas varian dan/atau nilai langsung."""
        root = Path(root) if root else PROJECT_ROOT
        base_path = Path(base)
        if not base_path.is_absolute():
            base_path = root / base_path
        if not base_path.exists():
            raise FileNotFoundError(f"Berkas konfigurasi dasar tidak ditemukan: {base_path}")

        data = yaml.safe_load(base_path.read_text(encoding="utf-8")) or {}

        if override:
            override_path = Path(override)
            if not override_path.is_absolute():
                override_path = root / override_path
            if not override_path.exists():
                raise FileNotFoundError(f"Berkas konfigurasi varian tidak ditemukan: {override_path}")
            data = deep_merge(data, yaml.safe_load(override_path.read_text(encoding="utf-8")) or {})

        for dotted, value in (sets or {}).items():
            data = deep_merge(data, _nest(dotted, value))

        return cls(data, root=root)


class _Missing:
    """Penanda nilai kosong; dibedakan dari ``None``."""


_MISSING = _Missing()


def _nest(dotted: str, value: Any) -> dict[str, Any]:
    """Ubah ``"model.name"`` menjadi ``{"model": {"name": value}}``."""
    keys = dotted.split(".")
    node: Any = value
    for key in reversed(keys):
        node = {key: node}
    return node
