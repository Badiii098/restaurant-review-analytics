#!/usr/bin/env python3
"""Simpan setiap tabel naskah sebagai CSV dan PNG ke folder keluaran.

Contoh::

    python -m scripts.proposal.buat_tabel --out "/path/GAMBAR"
"""

from __future__ import annotations

import argparse
import csv
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from scripts.proposal.tabel import tabel  # noqa: E402

plt.rcParams.update({"font.family": "serif",
                     "font.serif": ["Liberation Serif", "Times New Roman", "DejaVu Serif"]})


def nama_berkas(nomor: str, judul: str, ext: str) -> str:
    return f"Tabel {nomor} - {judul}.{ext}"


def simpan_png(nomor: str, t: dict, target: Path) -> None:
    lebar_total = 7.5  # inci
    skala = [w / sum(t["lebar"]) for w in t["lebar"]]
    char_per_inch = 11
    def bungkus(teks, frac):
        return "\n".join(textwrap.wrap(str(teks), max(4, int(frac * lebar_total * char_per_inch))) or [""])
    sel = [[bungkus(v, skala[j]) for j, v in enumerate(r)] for r in t["baris"]]
    kepala = [bungkus(v, skala[j]) for j, v in enumerate(t["kolom"])]
    tinggi = [max(c.count("\n") + 1 for c in r) for r in [kepala] + sel]
    total = sum(tinggi) * 0.19 + 0.8
    fig, ax = plt.subplots(figsize=(lebar_total, total)); ax.axis("off")
    ax.set_title(f"Tabel {nomor} {t['judul']}", fontsize=10, loc="center")
    tb = ax.table(cellText=sel, colLabels=kepala, colWidths=skala, loc="upper center", cellLoc="left")
    tb.auto_set_font_size(False); tb.set_fontsize(8)
    for (i, j), c in tb.get_celld().items():
        c.set_height(tinggi[i] * 0.19 / total)
        c.set_edgecolor("#333333"); c.set_linewidth(0.5)
        if i == 0:
            c.set_facecolor("#F3F3F3"); c.get_text().set_fontweight("bold")
        c.get_text().set_va("center")
    bawah = 1 - sum(tinggi) * 0.19 / total
    ax.text(0, bawah - 0.02, f"Sumber: {t['sumber']}", fontsize=7, style="italic",
            transform=ax.transAxes, va="top")
    fig.savefig(target, dpi=300, bbox_inches="tight"); plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    for nomor, t in tabel().items():
        with (out / nama_berkas(nomor, t["judul"], "csv")).open("w", encoding="utf-8-sig", newline="") as h:
            w = csv.writer(h); w.writerow(t["kolom"]); w.writerows(t["baris"])
        simpan_png(nomor, t, out / nama_berkas(nomor, t["judul"], "png"))
        print("Ditulis: Tabel", nomor)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
