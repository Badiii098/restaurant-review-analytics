#!/usr/bin/env python3
"""Tulis dokumen kontrak antar-lapis (docs/KONTRAK.md) dan skema API (docs/openapi.json).

Dokumen dibangkitkan dari kode, bukan ditulis tangan, sehingga kontrak pada
naskah (luaran L3) tidak dapat menyimpang dari kontrak yang benar-benar dipakai.

Contoh::

    python scripts/export_contracts.py
"""

from __future__ import annotations

import dataclasses
import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rra import contracts  # noqa: E402


def _default(field: dataclasses.Field) -> str:
    if field.default is not dataclasses.MISSING:
        return repr(field.default)
    if field.default_factory is not dataclasses.MISSING:  # type: ignore[misc]
        return f"{field.default_factory.__name__}()"  # type: ignore[misc]
    return "wajib"


def render() -> str:
    lines = [
        "# Kontrak Data Antar-Lapis",
        "",
        "Dibangkitkan dari `src/rra/contracts.py` oleh `scripts/export_contracts.py`. "
        "Jangan diedit tangan.",
        "",
        f"- Aspek: {', '.join(contracts.ASPECTS)}",
        f"- Sentimen: {', '.join(contracts.SENTIMENTS)}",
        "",
    ]
    kelas = [obj for _, obj in inspect.getmembers(contracts, inspect.isclass)
             if dataclasses.is_dataclass(obj) and obj.__module__ == contracts.__name__]
    kelas.sort(key=lambda c: inspect.getsourcelines(c)[1])
    for cls in kelas:
        doc = (inspect.getdoc(cls) or "").splitlines()[0] if inspect.getdoc(cls) else ""
        lines += [f"## {cls.__name__}", "", doc, "",
                  "| Bidang | Tipe | Bawaan |", "|---|---|---|"]
        for field in dataclasses.fields(cls):
            tipe = field.type if isinstance(field.type, str) else getattr(field.type, "__name__", str(field.type))
            tipe = str(tipe).replace("|", "\\|")
            lines.append(f"| `{field.name}` | `{tipe}` | {_default(field)} |")
        lines.append("")
    return "\n".join(lines)


def tulis_openapi(target: Path = ROOT / "docs" / "openapi.json") -> Path:
    """Skema OpenAPI API lapis 5a; respons hasil memakai kontrak ``AspectPriority``."""
    import json

    from rra.api.app import create_app
    from rra.config import Config

    skema = create_app(Config.load(root=ROOT)).openapi()
    target.write_text(json.dumps(skema, indent=2, ensure_ascii=False), encoding="utf-8")
    return target


def main() -> int:
    target = ROOT / "docs" / "KONTRAK.md"
    target.write_text(render(), encoding="utf-8")
    print(f"Ditulis: {target}")
    print(f"Ditulis: {tulis_openapi()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
