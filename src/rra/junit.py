"""Ringkasan laporan pytest (JUnit XML) per kasus uji katalog."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path


def _status(testcase: ET.Element) -> str:
    if testcase.find("failure") is not None or testcase.find("error") is not None:
        return "gagal"
    if testcase.find("skipped") is not None:
        return "dilewati"
    return "lulus"


def ringkas_junit(path: Path) -> dict | None:
    """``None`` bila berkas belum ada. Status kasus: gagal bila ada satu uji gagal,
    lulus bila ada yang lulus dan tidak ada yang gagal, dilewati bila semuanya dilewati."""
    path = Path(path)
    if not path.exists():
        return None
    akar = ET.parse(path).getroot()
    hitung = {"lulus": 0, "gagal": 0, "dilewati": 0}
    per_kasus: dict[str, set[str]] = {}
    for testcase in akar.iter("testcase"):
        status = _status(testcase)
        hitung[status] += 1
        for prop in testcase.iter("property"):
            if prop.get("name") == "kasus":
                for kode in filter(None, (prop.get("value") or "").split(",")):
                    per_kasus.setdefault(kode.strip(), set()).add(status)
    ringkas = {}
    for kode, status in sorted(per_kasus.items()):
        ringkas[kode] = "gagal" if "gagal" in status else ("lulus" if "lulus" in status else "dilewati")
    return {"total": sum(hitung.values()), **hitung, "per_kasus": ringkas}
