"""Katalog kebutuhan FR/KNF dan kasus uji (satu sumber untuk kode dan naskah)."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Katalog:
    kebutuhan: list[dict]
    kasus: list[dict]

    def kasus_kritis(self) -> set[str]:
        return {k["kode"] for k in self.kasus if k.get("kritis")}


def muat_katalog(path: Path) -> Katalog:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return Katalog(kebutuhan=list(data.get("kebutuhan", [])), kasus=list(data.get("kasus", [])))


def persen_terlacak(katalog: Katalog) -> float:
    """Persentase kebutuhan yang terpetakan ke minimal satu kasus uji yang terdaftar."""
    if not katalog.kebutuhan:
        return 0.0
    terdaftar = {k["kode"] for k in katalog.kasus}
    terlacak = sum(1 for k in katalog.kebutuhan
                   if k.get("kasus") and set(k["kasus"]) <= terdaftar)
    return round(100.0 * terlacak / len(katalog.kebutuhan), 2)


def _kode_dari_marker(node: ast.AST) -> list[str]:
    """Ambil argumen string dari ``pytest.mark.kasus("U-01", ...)``."""
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr == "kasus"):
        return [a.value for a in node.args if isinstance(a, ast.Constant) and isinstance(a.value, str)]
    return []


def kasus_di_berkas_uji(folder: Path) -> dict[str, list[str]]:
    """Peta kode kasus → berkas uji yang menandainya (dibaca statis dari sumber)."""
    hasil: dict[str, list[str]] = {}
    for berkas in sorted(Path(folder).glob("test_*.py")):
        pohon = ast.parse(berkas.read_text(encoding="utf-8"))
        for node in ast.walk(pohon):
            for kode in _kode_dari_marker(node):
                hasil.setdefault(kode, [])
                if berkas.name not in hasil[kode]:
                    hasil[kode].append(berkas.name)
    return hasil
