"""Fakta data penelitian yang dikutip naskah, dihitung langsung dari data.

Seluruh angka pada tabel dan teks naskah yang menyangkut data (jumlah ulasan,
sebaran kota, tahun, rating) berasal dari fungsi di sini, sehingga naskah dan
kode tidak dapat berbeda angka.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASPEK = ("makanan", "pelayanan", "harga", "suasana", "fasilitas")
TARGET_TOTAL = 5000


def _restoran() -> list[dict]:
    with (ROOT / "config" / "restaurants.csv").open(encoding="utf-8", newline="") as h:
        return list(csv.DictReader(h))


def sampling() -> dict:
    """Rencana dan realisasi sampel purposive delapan restoran (dari konfigurasi + data)."""
    import sys

    sys.path.insert(0, str(ROOT / "src"))
    from rra.config import Config
    from rra.io_layer.scope import ringkas_sampel

    cfg = Config.load(root=ROOT)
    n = int(cfg.get("sampling.n_restoran", 8))
    rentang = tuple(int(t) for t in cfg.get("sampling.rentang_tahun", [2021, 2026]))
    batas = int(cfg.get("sampling.batas_target", 625))
    maks = int(cfg.get("sampling.maks_per_kategori", 2))
    hasil = ringkas_sampel(ROOT / "config" / "restaurants.csv", ROOT / "data" / "raw" / "maps",
                           n=n, rentang=rentang, maks_per_kategori=maks, batas=batas)
    return {**hasil, "teknik": cfg.get("sampling.teknik", "purposive")}


@lru_cache(maxsize=1)
def fakta() -> dict:
    semua = _restoran()
    aktif = [r for r in semua if r["aktif"] == "1"]
    keluar = [r for r in semua if r["aktif"] != "1"]
    per_restoran, tahun, rating, kota = [], Counter(), Counter(), Counter()
    total = 0
    for r in aktif:
        berkas = ROOT / "data" / "raw" / "maps" / f"{r['kode']}_hasil.jsonl"
        n = 0
        if berkas.exists():
            for baris in berkas.open(encoding="utf-8"):
                if not baris.strip():
                    continue
                d = json.loads(baris)
                n += 1
                tahun[(d.get("tanggal") or "")[:4]] += 1
                rating[int(d.get("rating") or 0)] += 1
        total += n
        kota[r["kota"]] += 1
        per_restoran.append({"kode": r["kode"], "nama": r["nama"], "kota": r["kota"],
                             "kategori": r["kategori"], "target": int(r["target_ulasan"]),
                             "terkumpul": n,
                             "kurang": max(int(r["target_ulasan"]) - n, 0)})
    dalam = sum(v for k, v in tahun.items() if k.isdigit() and 2021 <= int(k) <= 2026)
    rendah = rating[1] + rating[2]
    return {
        "n_restoran": len(aktif), "n_kandidat": len(semua), "keluar": [r["kode"] for r in keluar],
        "total": total, "target_per_restoran": int(aktif[0]["target_ulasan"]) if aktif else 0,
        "target_total": sum(p["target"] for p in per_restoran), "ambang_total": TARGET_TOTAL,
        "per_restoran": per_restoran, "kota": dict(kota), "tahun": dict(sorted(tahun.items())),
        "dalam_rentang": dalam, "rating": dict(sorted(rating.items())), "rating_rendah": rendah,
        "restoran_kurang": [p for p in per_restoran if p["kurang"] > 0],
        "sampling": sampling(),
    }


def angka(n: float, desimal: int = 0) -> str:
    """Format angka gaya Indonesia: 6.874 dan 95,1."""
    teks = f"{n:,.{desimal}f}"
    return teks.replace(",", "_").replace(".", ",").replace("_", ".")


def persen(bagian: float, keseluruhan: float, desimal: int = 1) -> str:
    return angka(100 * bagian / keseluruhan, desimal) if keseluruhan else "0"


if __name__ == "__main__":
    f = fakta()
    print(json.dumps({k: v for k, v in f.items() if k != "per_restoran"}, indent=2, ensure_ascii=False))
