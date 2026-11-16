#!/usr/bin/env python3
"""Bangkitkan gambar naskah proposal (PNG 300 dpi) ke folder keluaran.

Diagram dibuat dengan Graphviz (``dot``), grafik dengan Matplotlib. Angka
pada grafik dibaca dari data lewat scripts/proposal/fakta.py.

Contoh::

    python -m scripts.proposal.buat_gambar --out "/path/GAMBAR"
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

from scripts.proposal.fakta import angka, fakta  # noqa: E402

FONT = "Liberation Serif"
plt.rcParams.update({"font.family": "serif", "font.serif": [FONT, "Times New Roman", "DejaVu Serif"],
                     "font.size": 10})

NODE = (f'node [shape=box, style="rounded,filled", fillcolor="#FFFFFF", color="#333333", '
        f'fontname="{FONT}", fontsize=11, margin="0.15,0.08"]; edge [color="#333333", '
        f'fontname="{FONT}", fontsize=10, arrowsize=0.7];')

GAMBAR: dict[str, str] = {
    "1.1": "Kerangka pemikiran penelitian",
    "3.1": "Tahapan penelitian",
    "3.2": "Siklus SDLC prototipe dengan dua iterasi",
    "3.3": "Arsitektur lima lapis prototipe",
    "3.4": "Alur data dan kontrak antar-lapis",
    "3.5": "Komponen skor prioritas aspek",
    "3.6": "Ulasan terkumpul per restoran terhadap target",
    "3.7": "Sebaran restoran dan ulasan per kota",
    "3.8": "Rancangan halaman laporan prioritas",
}


def nama_berkas(nomor: str) -> str:
    return f"Gambar {nomor} - {GAMBAR[nomor]}.png"


def _dot(src: str, target: Path) -> None:
    subprocess.run(["dot", "-Tpng", "-Gdpi=300", "-o", str(target)], input=src.encode(), check=True)


def g11(t: Path) -> None:
    _dot(f'''digraph G {{ rankdir=TB; nodesep=0.3; ranksep=0.35; {NODE}
    subgraph cluster_m {{ label="Masalah"; labelloc=t; fontname="{FONT}"; color="#999999"; style=dashed;
      m1 [label="Ulasan Google Maps bertambah cepat;\\npemilik hanya membaca rata-rata bintang"];
      m2 [label="Satu ulasan memuat beberapa aspek\\ndengan sentimen berbeda"]; }}
    subgraph cluster_g {{ label="Celah penelitian terdahulu"; fontname="{FONT}"; color="#999999"; style=dashed;
      g1 [label="Berhenti pada akurasi model\\n(Firdaus et al. 2024; Salsabillah et al. 2024)"];
      g2 [label="Prioritas disusun manual,\\ntanpa rumus yang dapat diaudit"];
      g3 [label="Perangkat lunak tidak diuji\\n(unit, integrasi, sistem, non-fungsional)"]; }}
    s [label="Prototipe ABSA lima lapis\\nTF-IDF + SVM linear\\nkontrak data antar-lapis", fillcolor="#E8EFEB"];
    subgraph cluster_l {{ label="Luaran (menjawab RM 1–3)"; labelloc=b; fontname="{FONT}"; color="#999999"; style=dashed;
      l1 [label="RM1: arsitektur,\\nkebutuhan, kontrak"]; l2 [label="RM2: hasil uji perangkat\\nlunak dan waktu proses"];
      l3 [label="RM3: peringkat aspek 0–100\\ndan kesesuaian pakar"]; l1 -> l2 -> l3 [style=invis]; {{rank=same; l1; l2; l3}} }}
    m1 -> g1; m2 -> g2; m2 -> g3; g1 -> s; g2 -> s; g3 -> s; s -> l1; s -> l2; s -> l3; }}''', t)


def g31(t: Path) -> None:
    _dot(f'''digraph G {{ rankdir=TB; nodesep=0.25; ranksep=0.3; {NODE}
    a [label="1. Identifikasi masalah"]; b [label="2. Pengumpulan data\\n(18 restoran, {angka(fakta()['total'])} ulasan)"];
    c [label="3. Studi literatur"];
    subgraph cluster_p {{ label="4. Perancangan sistem — SDLC prototipe"; fontname="{FONT}"; style="rounded,dashed"; color="#12564A";
      d1 [label="Analisis kebutuhan\\n(FR, KNF)"]; d2 [label="Desain cepat\\n(arsitektur, kontrak, antarmuka)"];
      d3 [label="Bangun prototipe"]; d4 [label="Evaluasi prototipe"]; d5 [label="Perbaikan"];
      d1 -> d2 -> d3 -> d4; d4 -> d5 [label=" iterasi 1"]; d5 -> d3 [constraint=false, label=" iterasi 2"]; }}
    e [label="5. Pengujian\\n(unit, integrasi, sistem, non-fungsional, uji pakar)"];
    f [label="6. Analisis hasil dan penarikan kesimpulan"];
    a -> b -> c -> d1; d4 -> e [label=" prototipe final"]; e -> f; }}''', t)


def g32(t: Path) -> None:
    _dot(f'''digraph G {{ rankdir=TB; nodesep=0.45; ranksep=0.45; {NODE}
    k [label="Analisis\\nkebutuhan"]; d [label="Desain\\ncepat"]; b1 [label="Bangun\\niterasi 1"]; e1 [label="Evaluasi\\niterasi 1"];
    p [label="Perbaikan"]; b2 [label="Bangun\\niterasi 2"]; e2 [label="Evaluasi\\niterasi 2"]; f [label="Prototipe\\nfinal", fillcolor="#E8EFEB"];
    {{rank=same; k; d; b1; e1}} {{rank=same; f; e2; b2; p}}
    k -> d -> b1 -> e1; e1 -> p; p -> b2 -> e2 -> f;
    e1 -> k [style=dashed, constraint=false, label="kebutuhan baru"]; }}''', t)


def g33(t: Path) -> None:
    lapis = [("Lapis 1 — Data", "akuisisi Google Maps, muat dan validasi ulasan\\nio_layer, scripts/scraping"),
             ("Lapis 2 — Praproses", "normalisasi, negasi, pemecahan klausa\\npreprocess/cleaner.py"),
             ("Lapis 3 — Komponen model", "TF-IDF + SVM linear (aspek multi-label, sentimen per aspek)\\nmodels/svm_model.py"),
             ("Lapis 4 — Modul keputusan", "keparahan, skor prioritas, frasa keluhan, aturan, sensitivitas\\ndecision/"),
             ("Lapis 5 — Antarmuka", "halaman laporan, CLI, laporan berkas\\napp/, cli.py, report/")]
    nodes = "\n".join(f'L{i} [label="{a}\\n{b}", width=5.2];' for i, (a, b) in enumerate(lapis))
    _dot(f'''digraph G {{ rankdir=TB; ranksep=0.3; nodesep=0.6; {NODE}
    {nodes}
    L0 -> L1 -> L2 -> L3 -> L4 [label=" kontrak"];
    cfg [label="config/default.yaml\\nparameter TF-IDF, bobot", shape=note, style=filled, fillcolor="#F4F5F3"];
    db [label="SQLite rra.sqlite\\nruns, priorities,\\npredictions", shape=cylinder, style=filled, fillcolor="#F4F5F3"];
    {{rank=same; L2; cfg}} {{rank=same; L3; db}}
    cfg -> L2 [style=dashed]; cfg -> L3 [style=dashed];
    L3 -> db [style=dashed, label="simpan"]; db -> L4 [style=dashed, label="baca"]; }}''', t)


def g34(t: Path) -> None:
    _dot(f'''digraph G {{ rankdir=TB; nodesep=0.5; ranksep=0.5; {NODE}
    a [label="Berkas ulasan\\n(CSV)"]; b [label="RawReview"]; c [label="CleanReview\\n(teks, klausa)"];
    d [label="Prediction\\n(aspek, sentimen,\\nkeyakinan)"];
    e [label="AspectStat\\n(keluhan, keparahan,\\nfrasa)"]; f [label="AspectPriority\\nComplaintPhrase\\nRecommendation"];
    g [label="Halaman dan\\nlaporan"];
    {{rank=same; a; b; c; d}} {{rank=same; g; f; e}}
    a -> b [label="L1"]; b -> c [label="L2"]; c -> d [label="L3"]; d -> e [label="L4"];
    f -> e [dir=back, label="L4"]; g -> f [dir=back, label="L5"]; }}''', t)


def g35(t: Path) -> None:
    _dot(f'''digraph G {{ rankdir=TB; nodesep=0.4; ranksep=0.4; {NODE}
    v [label="Volume\\njumlah ulasan negatif per aspek\\n(min–max)"];
    k [label="Keparahan\\nrerata (5 − rating) / 4\\npada ulasan negatif"];
    r [label="Keragaman\\njumlah frasa keluhan unik\\n(min–max)"];
    p [label="Prioritas = 0,4·Volume + 0,4·Keparahan + 0,2·Keragaman\\nditampilkan × 100 (skala 0–100)", fillcolor="#E8EFEB"];
    o [label="Peringkat aspek per restoran\\n+ komponen tersimpan untuk audit"];
    s [label="Uji sensitivitas\\nbobot ±10%"]; x [label="Uji kesesuaian pakar\\n(ρ Spearman, Wilcoxon)"];
    v -> p; k -> p; r -> p; p -> o; o -> s; o -> x; }}''', t)


def g36(t: Path) -> None:
    f = fakta()
    data = sorted(f["per_restoran"], key=lambda p: p["terkumpul"])
    fig, ax = plt.subplots(figsize=(6.3, 5.2))
    warna = ["#8A5A15" if p["kurang"] else "#12564A" for p in data]
    ax.barh([f"{p['kode']} {p['nama']}" for p in data], [p["terkumpul"] for p in data], color=warna)
    ax.axvline(f["target_per_restoran"], color="#333333", ls="--", lw=1)
    ax.text(f["target_per_restoran"] + 5, -0.9, f"target {f['target_per_restoran']}", fontsize=9)
    for i, p in enumerate(data):
        ax.text(p["terkumpul"] + 4, i, angka(p["terkumpul"]), va="center", fontsize=8)
    ax.set_xlabel("Jumlah ulasan")
    ax.set_xlim(0, max(p["terkumpul"] for p in data) * 1.12)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="y", labelsize=8)
    fig.tight_layout(); fig.savefig(t, dpi=300); plt.close(fig)


def g37(t: Path) -> None:
    f = fakta()
    kota = list(f["kota"])
    ulasan = {k: sum(p["terkumpul"] for p in f["per_restoran"] if p["kota"] == k) for k in kota}
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.3, 2.8))
    a1.bar(kota, [f["kota"][k] for k in kota], color="#12564A"); a1.set_title("Restoran", fontsize=10)
    a2.bar(kota, [ulasan[k] for k in kota], color="#12564A"); a2.set_title("Ulasan", fontsize=10)
    for ax, nilai in ((a1, [f["kota"][k] for k in kota]), (a2, [ulasan[k] for k in kota])):
        for i, n in enumerate(nilai):
            ax.text(i, n, angka(n), ha="center", va="bottom", fontsize=8)
        ax.tick_params(axis="x", labelrotation=35, labelsize=8)
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(t, dpi=300); plt.close(fig)


def g38(t: Path) -> None:
    fig, ax = plt.subplots(figsize=(6.3, 4.0)); ax.set_xlim(-2, 103); ax.set_ylim(-5, 65); ax.axis("off")

    def kotak(x, y, w, h, teks, isi="#FFFFFF", tebal=False, ukuran=8):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2,rounding_size=0.6",
                                    fc=isi, ec="#636C6A", lw=0.8))
        ax.text(x + 1.2, y + h - 1.6, teks, va="top", fontsize=ukuran,
                fontweight="bold" if tebal else "normal")

    ax.add_patch(Rectangle((0, 60), 100, 4, fc="#14181A")); ax.text(1, 61.2, "Bilah atas: berkas, basis data, nomor hasil", color="white", fontsize=8)
    kotak(0, 0, 22, 58.5, "Bilah samping\n\nKomponen model:\nSVM linear\n\nSumber masukan\n\n[Hitung ulang\n analisis]\n\nStatus sistem", "#F4F5F3")
    kotak(24, 50, 76, 8.5, "Prioritas perbaikan layanan\nAspek <A> berada di peringkat pertama (skor <S>)", tebal=True)
    for i, label in enumerate(["Ulasan", "Aspek", "Keluhan teratas", "Waktu proses"]):
        kotak(24 + i * 19.2, 42, 17.6, 6.5, label)
    kotak(24, 24, 76, 16.5, "01 Peringkat prioritas\n#  Aspek       Ulasan negatif   Skor\n1  <aspek>     n dari N   ████████ 00,0\n2  <aspek>     n dari N   ████ 00,0")
    kotak(24, 12, 37, 10.5, "02 Frasa keluhan dominan\n<frasa 1> · <frasa 2> · <frasa 3>")
    kotak(63, 12, 37, 10.5, "03 Tindakan disarankan\n<aspek> · <pemicu> → <tindakan>")
    kotak(24, 0, 76, 10.5, "04 Bahan audit: rumus, bobot 0,4/0,4/0,2, waktu per tahap")
    ax.text(50, -3.5, "Rancangan tata letak; isi diganti angka dari basis data hasil.",
            ha="center", fontsize=7, style="italic")
    fig.tight_layout(); fig.savefig(t, dpi=300); plt.close(fig)


PEMBUAT = {"1.1": g11, "3.1": g31, "3.2": g32, "3.3": g33, "3.4": g34, "3.5": g35,
           "3.6": g36, "3.7": g37, "3.8": g38}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    for nomor, fungsi in PEMBUAT.items():
        target = out / nama_berkas(nomor)
        fungsi(target)
        print("Ditulis:", target.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
