"""Keputusan hipotesis RM1–RM3 (Tabel 3.3) dari bukti yang benar-benar ada.

Bila bukti belum ada, status ``belum_tersedia`` beserta perintah pembuatnya
dikembalikan; keputusan tidak pernah ditebak.
"""

from __future__ import annotations

from statistics import mean, stdev

from scipy.stats import ttest_1samp

from rra.analysis.expert import uji_median_rho
from rra.requirements import Katalog, persen_terlacak

ALPHA = 0.05
BATAS_DETIK = 60.0
ULANGAN_MIN = 5
AMBANG_RHO = 0.60

_TEKS = {
    1: ("Ada kontrak antar-lapis yang gagal validasi atau kebutuhan yang tidak terlacak ke kasus uji",
        "100% kontrak lolos validasi dan 100% kebutuhan terlacak ke minimal satu kasus uji",
        "Perbaiki kontrak atau tambah kasus uji pada iterasi prototipe berikutnya"),
    2: ("Ada uji kritis yang gagal, atau rata-rata waktu proses > 60 detik per 1.000 ulasan",
        "Seluruh uji kritis lulus dan rata-rata waktu ≤ 60 detik per 1.000 ulasan",
        "Telusuri tahap terlambat dari waktu per tahap, perbaiki, ukur ulang"),
    3: ("Median ρ Spearman antar-restoran ≤ 0,60", "Median ρ Spearman antar-restoran > 0,60",
        "Laporkan sebagai temuan; tinjau bobot melalui uji sensitivitas, definisi komponen, atau cakupan frasa"),
}


def _dasar(rm: int) -> dict:
    h0, h1, rekomendasi = _TEKS[rm]
    return {"rm": rm, "h0": h0, "h1": h1, "rekomendasi": rekomendasi,
            "statistik": None, "p": None, "tolak_h0": None, "status": "selesai"}


def _belum(rm: int, langkah: str) -> dict:
    return {**_dasar(rm), "status": "belum_tersedia", "langkah": langkah}


def uji_h1(katalog: Katalog, junit: dict | None) -> dict:
    if junit is None:
        return _belum(1, "python -m pytest tests --junitxml=reports/pytest.xml")
    kontrak = junit["per_kasus"].get("U-01")
    persen_kontrak = 100.0 if kontrak == "lulus" else 0.0
    # Katalog konsisten DAN uji keterlacakan (penanda kasus pada berkas uji) lulus.
    terlacak = persen_terlacak(katalog) if junit["per_kasus"].get("U-13", "lulus") == "lulus" else 0.0
    return {**_dasar(1),
            "statistik": {"persen_kontrak_lolos": persen_kontrak, "persen_terlacak": terlacak},
            "tolak_h0": persen_kontrak == 100.0 and terlacak == 100.0}


def uji_h2(benchmark: dict | None, junit: dict | None, katalog: Katalog) -> dict:
    if benchmark is None or junit is None:
        return _belum(2, "python -m rra.cli benchmark --repeat 5 ; "
                         "python -m pytest tests --junitxml=reports/pytest.xml")
    n_ulasan = max(int(benchmark["summary"]["n_ulasan"]), 1)
    per_1000 = [float(u["total_dinding"]) * 1000.0 / n_ulasan for u in benchmark["perulangan"]]
    if len(per_1000) < ULANGAN_MIN:
        return _belum(2, f"python -m rra.cli benchmark --repeat {ULANGAN_MIN}")
    gagal = sorted(k for k in katalog.kasus_kritis() if junit["per_kasus"].get(k) != "lulus")
    if stdev(per_1000) > 0:
        uji = ttest_1samp(per_1000, BATAS_DETIK, alternative="less")
        statistik_t, p = float(uji.statistic), float(uji.pvalue)
    else:  # semua ulangan identik: t tak terdefinisi, keputusan dari rata-rata
        statistik_t, p = None, (0.0 if mean(per_1000) < BATAS_DETIK else 1.0)
    return {**_dasar(2), "p": round(p, 6),
            "statistik": {"n": len(per_1000), "t": statistik_t,
                          "rata_rata_detik_per_1000": round(mean(per_1000), 4) if per_1000 else None,
                          "sd_detik_per_1000": round(stdev(per_1000), 4),
                          "maks_detik_per_1000": round(max(per_1000), 4),
                          "kasus_kritis": len(katalog.kasus_kritis()), "kasus_kritis_gagal": gagal},
            "tolak_h0": p < ALPHA and not gagal}


def uji_h3(laporan_pakar: dict | None) -> dict:
    if laporan_pakar is None:
        return _belum(3, "isi data/reference/urutan_pakar.csv, lalu jalankan "
                         "python scripts/uji_pakar.py --pakar data/reference/urutan_pakar.csv")
    uji = uji_median_rho(laporan_pakar["rho_per_restoran"].values(), threshold=AMBANG_RHO, alpha=ALPHA)
    return {**_dasar(3), "p": uji["p"],
            "statistik": {"n": uji["n"], "median_rho": uji["median"], "w": uji["statistik"],
                          "kesesuaian_peringkat_1": laporan_pakar.get("kesesuaian_peringkat_1")},
            "tolak_h0": bool(uji["tolak_h0"])}
