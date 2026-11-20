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
    "3.3": "Arsitektur klien-server lima lapis prototipe",
    "3.4": "Alur data dan kontrak antar-lapis",
    "3.5": "Komponen skor prioritas aspek",
    "3.6": "Ulasan per restoran sampel terhadap batas target",
    "3.7": "Sebaran restoran sampel per kota dan kategori",
    "3.8": "Antarmuka web prototipe pada halaman hasil dan prioritas",
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
    """Tahapan penelitian, tata letak tiga kolom zig-zag sama dengan diagram rujukan.

    Kotak berbingkai ganda di sisi kiri-kanan = proses terdefinisi (langkah SDLC prototipe);
    panah titik-titik = umpan balik iterasi 1–2 dan perbaikan setelah pengujian.
    """
    W, H, DX, DY = 2.7, 0.95, 3.25, 1.3
    simpul = {  # kode: (kolom, baris, teks, jenis)
        "mulai": (0, 0, "Mulai", "ujung"),
        "a": (0, 1, "Identifikasi\nMasalah", "proses"), "b": (1, 1, "Studi Literatur\n(2022–2026)", "proses"),
        "c": (2, 1, "Pengumpulan Data\n(8 restoran)", "proses"),
        "d": (2, 2, "Anotasi Data\n(500 ulasan, kappa)", "proses"), "e": (1, 2, "Metode SDLC\nPrototipe", "proses"),
        "f": (1, 3, "Analisis Kebutuhan\n(FR, KNF)", "sub"), "g": (2, 4, "Desain Cepat\n(arsitektur, kontrak)", "sub"),
        "h": (0, 5, "Pembangunan Prototipe\ndan Pemodelan NLP", "sub"),
        "i": (1, 6, "Evaluasi Prototipe\n(Macro-F1, kebutuhan)", "sub"),
        "j": (2, 7, "Pengujian\nPerangkat Lunak", "sub"),
        "k": (0, 8, "Validasi Pakar\n(ρ Spearman, Wilcoxon)", "proses"),
        "l": (1, 9, "Analisis Hasil dan\nPenarikan Kesimpulan", "proses"), "z": (2, 10, "Selesai", "ujung"),
    }
    pos = {k: (c * DX, -r * DY) for k, (c, r, _, _) in simpul.items()}
    fig, ax = plt.subplots(figsize=(6.3, 7.6)); ax.axis("off")
    ax.set_xlim(-W / 2 - 0.8, 2 * DX + W / 2 + 0.2); ax.set_ylim(-10 * DY - H, H)
    for k, (_, _, teks, jenis) in simpul.items():
        x, y = pos[k]
        lebar = W * (0.75 if jenis == "ujung" else 1)
        gaya = "round,pad=0,rounding_size=0.42" if jenis == "ujung" else "square,pad=0"
        ax.add_patch(FancyBboxPatch((x - lebar / 2, y - H / 2), lebar, H, boxstyle=gaya,
                                    fc="white", ec="#111111", lw=1.2))
        if jenis == "sub":
            for dx in (-W / 2 + 0.16, W / 2 - 0.16):
                ax.plot([x + dx, x + dx], [y - H / 2, y + H / 2], color="#111111", lw=1.1)
        ax.text(x, y, teks, ha="center", va="center", fontsize=9.5, linespacing=1.15)
    panah = dict(arrowstyle="-|>", color="#111111", lw=1.0, mutation_scale=9, shrinkA=0, shrinkB=0)

    def garis(titik: list[tuple[float, float]], titik_titik: bool = False) -> None:
        gaya = ":" if titik_titik else "-"
        for (x1, y1), (x2, y2) in zip(titik[:-2], titik[1:-1]):
            ax.plot([x1, x2], [y1, y2], color="#111111", lw=1.0, ls=gaya)
        ax.annotate("", xy=titik[-1], xytext=titik[-2],
                    arrowprops={**panah, "linestyle": (0, (1, 2)) if titik_titik else "-"})

    def kanan(k): return (pos[k][0] + W / 2, pos[k][1])
    def kiri(k): return (pos[k][0] - W / 2, pos[k][1])
    def atas(k): return (pos[k][0], pos[k][1] + H / 2)
    def bawah(k): return (pos[k][0], pos[k][1] - H / 2)

    garis([bawah("mulai"), atas("a")])
    garis([kanan("a"), kiri("b")]); garis([kanan("b"), kiri("c")])
    garis([bawah("c"), atas("d")]); garis([kiri("d"), kanan("e")]); garis([bawah("e"), atas("f")])
    for asal, tujuan in (("f", "g"), ("i", "j"), ("l", "z"), ("h", "i"), ("k", "l")):
        garis([kanan(asal), (pos[tujuan][0], pos[asal][1]), atas(tujuan)])
    for asal, tujuan in (("g", "h"), ("j", "k")):
        ytengah = (bawah(asal)[1] + atas(tujuan)[1]) / 2
        garis([bawah(asal), (pos[asal][0], ytengah), (pos[tujuan][0], ytengah), atas(tujuan)])
    # umpan balik: evaluasi → pembangunan (iterasi 1–2), pengujian → pembangunan (perbaikan)
    xi = pos["h"][0] + W / 2 - 0.55
    garis([kiri("i"), (xi, pos["i"][1]), (xi, bawah("h")[1])], titik_titik=True)
    ax.text(xi - 0.08, (pos["i"][1] + bawah("h")[1]) / 2, "iterasi 1–2", ha="right", va="center", fontsize=8.5)
    xp = pos["h"][0] - W / 2 + 0.45
    garis([kiri("j"), (xp, pos["j"][1]), (xp, bawah("h")[1])], titik_titik=True)
    ax.text(xp + 0.08, pos["j"][1] + 0.18, "perbaikan", ha="left", va="bottom", fontsize=8.5)
    fig.tight_layout(); fig.savefig(t, dpi=300); plt.close(fig)


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
             ("Lapis 4 — Modul keputusan", "keparahan, skor prioritas, frasa keluhan, aturan, sensitivitas, uji pakar\\ndecision/, analysis/"),
             ("Lapis 5a — Layanan dan API REST", "FastAPI /api/v1, skema OpenAPI dari kontrak, CLI\\napi/, services/, cli.py")]
    nodes = "\n".join(f'L{i} [label="{a}\\n{b}", width=5.2];' for i, (a, b) in enumerate(lapis))
    _dot(f'''digraph G {{ rankdir=TB; ranksep=0.3; nodesep=0.6; {NODE}
    {nodes}
    L5 [label="Lapis 5b — Klien web\\nReact + TypeScript, satu halaman per tahap penelitian\\nfrontend/ (dibundel, tanpa CDN)", width=5.2, fillcolor="#E8EFEB"];
    u [label="Peramban\\npengguna", shape=box, style="rounded,dashed"];
    L0 -> L1 -> L2 -> L3 -> L4 [label=" kontrak"];
    L4 -> L5 [label=" JSON (HTTP)"]; L5 -> u [dir=both, style=dashed];
    cfg [label="config/\\ndefault.yaml, kebutuhan.yaml", shape=note, style=filled, fillcolor="#F4F5F3"];
    db [label="SQLite rra.sqlite\\nruns, priorities,\\npredictions", shape=cylinder, style=filled, fillcolor="#F4F5F3"];
    rep [label="reports/\\npytest.xml, benchmark,\\niterasi, kappa, pakar", shape=folder, style=filled, fillcolor="#F4F5F3"];
    {{rank=same; L2; cfg}} {{rank=same; L3; db}} {{rank=same; L4; rep}}
    cfg -> L2 [style=dashed]; cfg -> L3 [style=dashed];
    L3 -> db [style=dashed, label="simpan"]; db -> L4 [style=dashed, label="baca"]; rep -> L4 [style=dashed, label="bukti"]; }}''', t)


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


def _kosong(t: Path, pesan: str) -> None:
    fig, ax = plt.subplots(figsize=(6.3, 1.6)); ax.axis("off")
    ax.text(0.5, 0.5, pesan, ha="center", va="center", fontsize=10, wrap=True)
    fig.savefig(t, dpi=300); plt.close(fig)


def g36(t: Path) -> None:
    s = fakta()["sampling"]
    if not s["restoran"]:
        _kosong(t, "Ulasan per restoran sampel ditampilkan setelah pemilihan sampel\n(python scripts/pilih_restoran.py --tulis)")
        return
    data = sorted(s["restoran"], key=lambda r: r["tersedia"])
    fig, ax = plt.subplots(figsize=(6.3, 3.6))
    warna = ["#8A5A15" if r["tersedia"] < s["batas_target"] else "#12564A" for r in data]
    ax.barh([f"{r['kode']} {r['nama']}" for r in data], [r["tersedia"] for r in data], color=warna)
    ax.axvline(s["batas_target"], color="#333333", ls="--", lw=1)
    ax.text(s["batas_target"] + 5, -0.9, f"batas target {angka(s['batas_target'])}", fontsize=9)
    for i, r in enumerate(data):
        ax.text(r["tersedia"] + 4, i, angka(r["tersedia"]), va="center", fontsize=8)
    ax.set_xlabel(f"Jumlah ulasan {s['rentang'][0]}–{s['rentang'][1]}")
    ax.set_xlim(0, max(max(r["tersedia"] for r in data), s["batas_target"]) * 1.15)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="y", labelsize=8)
    fig.tight_layout(); fig.savefig(t, dpi=300); plt.close(fig)


def g37(t: Path) -> None:
    s = fakta()["sampling"]
    if not s["restoran"]:
        _kosong(t, "Sebaran restoran sampel per kota dan kategori ditampilkan setelah pemilihan sampel")
        return
    from collections import Counter
    kota, kategori = Counter(r["kota"] for r in s["restoran"]), Counter(r["kategori"] for r in s["restoran"])
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.3, 2.9))
    for ax, hitung, judul in ((a1, kota, "Restoran per kota"), (a2, kategori, "Restoran per kategori")):
        kunci = list(hitung)
        ax.bar(kunci, [hitung[k] for k in kunci], color="#12564A"); ax.set_title(judul, fontsize=10)
        for i, k in enumerate(kunci):
            ax.text(i, hitung[k], angka(hitung[k]), ha="center", va="bottom", fontsize=8)
        ax.tick_params(axis="x", labelrotation=35, labelsize=8)
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(t, dpi=300); plt.close(fig)


def g38(t: Path) -> None:
    """Tangkapan layar dashboard (halaman Hasil & Prioritas) dari prototipe yang berjalan."""
    import socket
    import sys
    import threading
    import time

    root = Path(__file__).resolve().parents[2]
    if not (root / "frontend" / "dist" / "index.html").exists():
        _kosong(t, "Bangun klien web dahulu: npm --prefix frontend install && npm --prefix frontend run build")
        return
    sys.path.insert(0, str(root / "src"))
    import uvicorn
    from playwright.sync_api import sync_playwright

    from rra.api.app import create_app
    from rra.config import Config

    with socket.socket() as sk:
        sk.bind(("127.0.0.1", 0)); port = sk.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(create_app(Config.load(root=root)), host="127.0.0.1",
                                           port=port, log_level="warning"))
    threading.Thread(target=server.run, daemon=True).start()
    while not server.started:
        time.sleep(0.05)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            hal = b.new_page(viewport={"width": 1280, "height": 900}, device_scale_factor=2, color_scheme="light")
            hal.goto(f"http://127.0.0.1:{port}/hasil"); hal.wait_for_load_state("networkidle")
            hal.screenshot(path=str(t)); b.close()
    finally:
        server.should_exit = True


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
