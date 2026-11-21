"""Catatan iterasi prototipe (SDLC Prototipe, iterasi 1–2).

Setiap evaluasi prototipe disimpan sebagai ``reports/iterasi/iterasi-N.json``
berisi Macro-F1 aspek dan sentimen dari validasi silang, catatan perbaikan,
dan penanda apakah memakai data contoh. Selisih iterasi 2 − iterasi 1 tidak
pernah dikarang: ia hanya dihitung dari dua catatan yang benar-benar ada.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def simpan_iterasi(laporan: dict, nomor: int, catatan: str, folder: Path, *,
                   data_contoh: bool, commit: str | None) -> Path:
    if nomor < 1:
        raise ValueError("Nomor iterasi dimulai dari 1.")
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    per_aspek: dict[str, list[float]] = {}
    for lipatan in laporan.get("per_fold", []):
        for aspek, nilai in (lipatan.get("aspect", {}).get("per_aspect") or {}).items():
            if isinstance(nilai, dict) and "f1" in nilai:
                per_aspek.setdefault(aspek, []).append(float(nilai["f1"]))
    isi = {
        "nomor": nomor,
        "waktu": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "commit": commit,
        "data_contoh": bool(data_contoh),
        "catatan": catatan,
        "ringkasan": laporan.get("summary", {}),
        "per_lipatan": {
            "aspek": [lip.get("aspect", {}).get("macro_f1") for lip in laporan.get("per_fold", [])],
            "sentimen": [lip.get("sentiment", {}).get("macro_f1") for lip in laporan.get("per_fold", [])],
        },
        "per_aspek_f1": {a: round(sum(v) / len(v), 6) for a, v in per_aspek.items()},
    }
    target = folder / f"iterasi-{nomor}.json"
    target.write_text(json.dumps(isi, indent=2, ensure_ascii=False), encoding="utf-8")
    return target


def muat_iterasi(folder: Path) -> list[dict]:
    folder = Path(folder)
    if not folder.is_dir():
        return []
    isi = [json.loads(p.read_text(encoding="utf-8")) for p in folder.glob("iterasi-*.json")]
    return sorted(isi, key=lambda item: int(item["nomor"]))


def bandingkan(a: dict, b: dict) -> dict:
    """Selisih Macro-F1 iterasi ``b`` terhadap ``a`` (positif = membaik)."""
    ra, rb = a["ringkasan"], b["ringkasan"]
    return {
        "aspek_macro_f1": round(rb["aspect_macro_f1_mean"] - ra["aspect_macro_f1_mean"], 4),
        "sentimen_macro_f1": round(rb["sentiment_macro_f1_mean"] - ra["sentiment_macro_f1_mean"], 4),
    }
