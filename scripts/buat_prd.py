#!/usr/bin/env python3
"""Bangun PRD dan dokumen arsitektur lengkap (PDF) dari repositori ini.

Kebutuhan, kasus uji, dan endpoint dibaca dari kode/konfigurasi agar dokumen
tidak menyimpang dari sistem. Perlu: reportlab, pyyaml, dan Graphviz (`dot`).

    python scripts/buat_prd.py --out docs/PRD-dan-Arsitektur-RRA.pdf
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from reportlab.lib import colors  # noqa: E402
from reportlab.lib.enums import TA_JUSTIFY  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.styles import ParagraphStyle  # noqa: E402
from reportlab.lib.units import cm  # noqa: E402
from reportlab.pdfbase import pdfmetrics  # noqa: E402
from reportlab.pdfbase.ttfonts import TTFont  # noqa: E402
from reportlab.platypus import (  # noqa: E402
    Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents  # noqa: E402

from rra.requirements import muat_katalog  # noqa: E402

FD = "/usr/share/fonts/truetype/dejavu/"
for nama, berkas in (("DV", "DejaVuSans.ttf"), ("DV-B", "DejaVuSans-Bold.ttf"),
                     ("DV-I", "DejaVuSans.ttf"), ("DV-BI", "DejaVuSans-Bold.ttf"),  # miring tidak tersedia: pakai tegak
                     ("DVM", "DejaVuSansMono.ttf")):
    pdfmetrics.registerFont(TTFont(nama, FD + berkas))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV-I", boldItalic="DV-BI")

HIJAU, HIJAU_MUDA, ABU = colors.HexColor("#12564A"), colors.HexColor("#E8EFEB"), colors.HexColor("#5C6563")
S = {
    "body": ParagraphStyle("body", fontName="DV", fontSize=9.2, leading=13.4, alignment=TA_JUSTIFY, spaceAfter=5),
    "h1": ParagraphStyle("h1", fontName="DV-B", fontSize=15, leading=19, textColor=HIJAU, spaceBefore=6, spaceAfter=8, keepWithNext=1),
    "h2": ParagraphStyle("h2", fontName="DV-B", fontSize=11.5, leading=15, textColor=colors.HexColor("#14181A"), spaceBefore=9, spaceAfter=4, keepWithNext=1),
    "h3": ParagraphStyle("h3", fontName="DV-B", fontSize=9.6, leading=13, textColor=HIJAU, spaceBefore=6, spaceAfter=3, keepWithNext=1),
    "cell": ParagraphStyle("cell", fontName="DV", fontSize=7.8, leading=10.2),
    "cellb": ParagraphStyle("cellb", fontName="DV-B", fontSize=7.8, leading=10.2, textColor=colors.white),
    "bul": ParagraphStyle("bul", fontName="DV", fontSize=9.2, leading=13, leftIndent=14, bulletIndent=3, spaceAfter=2),
    "note": ParagraphStyle("note", fontName="DV-I", fontSize=8.2, leading=11.5, textColor=ABU, spaceAfter=6),
    "cap": ParagraphStyle("cap", fontName="DV-I", fontSize=8, leading=10.5, textColor=ABU, alignment=1, spaceAfter=8),
    "mono": ParagraphStyle("mono", fontName="DVM", fontSize=7.6, leading=10, backColor=colors.HexColor("#F4F5F3"),
                           borderPadding=4, spaceAfter=6),
    "toc1": ParagraphStyle("toc1", fontName="DV-B", fontSize=9.4, leading=14, leftIndent=0, spaceBefore=2),
    "toc2": ParagraphStyle("toc2", fontName="DV", fontSize=7.8, leading=10, leftIndent=14, textColor=ABU),
}


def P(t: str, s: str = "body") -> Paragraph:
    return Paragraph(t, S[s])


def bullets(items: list[str]) -> list[Paragraph]:
    return [Paragraph(i, S["bul"], bulletText="•") for i in items]


def tabel(kolom: list[str], baris: list[list[str]], lebar: list[float]) -> Table:
    total = sum(lebar)
    ukuran = [w / total * (A4[0] - 4 * cm) for w in lebar]
    data = [[Paragraph(k, S["cellb"]) for k in kolom]] + [[Paragraph(str(c), S["cell"]) for c in r] for r in baris]
    t = Table(data, colWidths=ukuran, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HIJAU), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DCE1DD")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F9F7")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    return t


class Dokumen(SimpleDocTemplate):
    def afterFlowable(self, f) -> None:  # noqa: ANN001
        if isinstance(f, Paragraph) and f.style.name == "h1":
            self.notify("TOCEntry", (0, f.getPlainText(), self.page))


def halaman(canvas, doc) -> None:  # noqa: ANN001
    canvas.saveState()
    canvas.setFont("DV", 7.5); canvas.setFillColor(ABU)
    canvas.drawString(2 * cm, 1.2 * cm, "RRA — PRD dan Arsitektur · v1.0 · 2026-11-21")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Halaman {doc.page}")
    canvas.setStrokeColor(colors.HexColor("#DCE1DD")); canvas.line(2 * cm, 1.6 * cm, A4[0] - 2 * cm, 1.6 * cm)
    canvas.restoreState()


# --------------------------------------------------------------------------- #
FONT = "DejaVu Sans"
NODE = (f'node [shape=box, style="rounded,filled", fillcolor="#FFFFFF", color="#333333", fontname="{FONT}", '
        f'fontsize=10, margin="0.14,0.07"]; edge [color="#555555", fontname="{FONT}", fontsize=9, arrowsize=0.7];')


def dot(src: str, target: Path) -> Path:
    subprocess.run(["dot", "-Tpng", "-Gdpi=170", "-o", str(target)], input=src.encode(), check=True)
    return target


def _kotak(ax, x, y, w, h, teks, fc="#FFFFFF", fs=7.6, tebal=False, ls="-"):  # noqa: ANN001, ANN202
    from matplotlib.patches import FancyBboxPatch
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.12", fc=fc, ec="#333333", lw=1, ls=ls))
    ax.text(x + w / 2, y + h / 2, teks, ha="center", va="center", fontsize=fs, fontweight="bold" if tebal else "normal", linespacing=1.25)


def _panah(ax, x1, y1, x2, y2, teks="", gaya="-", tw=0.1):  # noqa: ANN001, ANN202
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color="#555555", lw=1, ls=gaya, shrinkA=0, shrinkB=0))
    if teks:
        ax.text((x1 + x2) / 2 + tw, (y1 + y2) / 2, teks, fontsize=6.8, color="#555555", va="center")


def _gambar_arsitektur(target: Path) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6.6, 6.2)); ax.set_xlim(0, 10); ax.set_ylim(0, 9.4); ax.axis("off")
    hij = "#E8EFEB"
    ax.add_patch(plt.Rectangle((0.1, 8.0), 6.6, 1.3, fc="none", ec="#999999", ls="--", lw=0.9))
    ax.text(0.25, 9.12, "Klien — peramban pengguna", fontsize=6.8, color="#666666", va="top")
    _kotak(ax, 0.4, 8.12, 6.0, 0.85, "Lapis 5b — Aplikasi web (React + TypeScript + Vite)\n10 halaman = 10 tahap penelitian · aset dibundel, tanpa CDN", hij, tebal=False)
    ax.add_patch(plt.Rectangle((0.1, 0.1), 6.6, 7.55, fc="none", ec="#999999", ls="--", lw=0.9))
    ax.text(0.25, 7.5, "Server — satu proses Python (uvicorn)", fontsize=6.8, color="#666666", va="top")
    _kotak(ax, 0.4, 6.15, 6.0, 0.9, "Lapis 5a — API REST FastAPI  /api/v1\nrouter · model respons dari kontrak · kunci analisis (409)", hij)
    _kotak(ax, 0.4, 5.05, 6.0, 0.75, "Layanan per tahap (rra.services.tahap)\nmembaca basis data, reports/, config/; memicu analisis ulang")
    _kotak(ax, 0.4, 3.75, 6.0, 0.95, "Lapis 4 — Modul keputusan\nkeparahan · skor prioritas · frasa keluhan\naturan DINESERV · sensitivitas · hipotesis")
    _kotak(ax, 0.4, 2.65, 6.0, 0.75, "Lapis 3 — Komponen model: TF-IDF + SVM linear (satu model)")
    _kotak(ax, 0.4, 1.6, 6.0, 0.75, "Lapis 2 — Praproses teks Indonesia: normalisasi · negasi · klausa")
    _kotak(ax, 0.4, 0.4, 6.0, 0.95, "Lapis 1 — Data\nmuat dan validasi ulasan · pemilihan sampel purposive")
    _panah(ax, 3.4, 8.12, 3.4, 7.05, "JSON / HTTP")
    _panah(ax, 3.4, 6.15, 3.4, 5.8); _panah(ax, 3.4, 5.05, 3.4, 4.7, "analisis ulang")
    for y1, y2 in ((1.35, 1.6), (2.35, 2.65), (3.4, 3.75)):
        _panah(ax, 5.6, y1, 5.6, y2, "kontrak" if y1 == 2.35 else "", tw=0.08)
    _kotak(ax, 7.4, 4.95, 2.4, 1.0, "Berkas bukti\nreports/*.json · pytest.xml\nconfig/*.yaml · data/", "#F4F5F3", fs=7)
    _kotak(ax, 7.4, 3.65, 2.4, 1.0, "SQLite rra.sqlite\nhasil + komponen skor", "#F4F5F3", fs=7)
    _panah(ax, 6.4, 5.45, 7.4, 5.45, "", "--")
    _panah(ax, 6.4, 4.15, 7.4, 4.15, "", "--")
    ax.text(6.9, 5.58, "baca bukti", fontsize=6, color="#555555", ha="center")
    ax.text(6.9, 4.28, "simpan/baca", fontsize=6, color="#555555", ha="center")
    fig.tight_layout(pad=0.2); fig.savefig(target, dpi=220); plt.close(fig)
    return target


def _gambar_alur(target: Path) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6.6, 3.5)); ax.set_xlim(0, 10); ax.set_ylim(0, 5.3); ax.axis("off")
    w, h = 2.1, 0.95
    xs = [0.1, 2.65, 5.2, 7.75]
    baris1 = ["Ulasan\nGoogle Maps", "Sampel purposive\n8 restoran", "Anotasi 500 ulasan\ndua anotator", "κ Cohen\n(aspek, sentimen)"]
    baris2 = ["Data berlabel", "Praproses\n+ TF-IDF", "SVM linear\naspek + sentimen", "Skor prioritas 0–100\n+ frasa + rekomendasi"]
    for x, t in zip(xs, baris1): _kotak(ax, x, 4.0, w, h, t)
    for x, t in zip(xs, baris2): _kotak(ax, x, 2.3, w, h, t, "#E8EFEB" if t.startswith("Skor") else "#FFFFFF", fs=7.2 if t.startswith("Skor") else 7.6)
    for i in range(3): _panah(ax, xs[i] + w, 4.47, xs[i + 1], 4.47)
    _panah(ax, xs[2] + w / 2, 4.0, xs[0] + w / 2 + 0.6, 3.25)
    for i in range(3): _panah(ax, xs[i] + w, 2.77, xs[i + 1], 2.77)
    _kotak(ax, xs[0], 0.5, w, h, "Pakar:\nurutan aspek per restoran")
    _kotak(ax, xs[1], 0.5, w, h, "ρ Spearman\n+ Wilcoxon")
    _kotak(ax, xs[2], 0.5, w, h, "Keputusan\nH1–H3", "#E8EFEB")
    _kotak(ax, xs[3], 0.5, w, h, "SQLite → API\n→ aplikasi web")
    _panah(ax, xs[0] + w, 0.97, xs[1], 0.97); _panah(ax, xs[1] + w, 0.97, xs[2], 0.97)
    _panah(ax, xs[3] + 0.3, 2.3, xs[1] + w - 0.3, 1.45)
    _panah(ax, xs[3] + w - 0.3, 2.3, xs[3] + w - 0.3, 1.45)
    fig.tight_layout(pad=0.2); fig.savefig(target, dpi=220); plt.close(fig)
    return target


def diagram(tmp: Path) -> dict[str, Path]:
    arsitektur = _gambar_arsitektur(tmp / "arsitektur.png")
    alur = _gambar_alur(tmp / "alur.png")
    erd = dot(f'''digraph G {{ rankdir=LR; nodesep=0.3; ranksep=0.5; {NODE.replace('"rounded,filled"', '"filled"')}
    runs [shape=record, label="{{runs|run_id PK\\lcreated_at\\lmodel_name\\ln_reviews\\lweights_json\\ltimings_json\\lconfig_json\\l}}"];
    pr [shape=record, label="{{priorities|run_id PK,FK\\laspect PK\\lrank · label · priority\\lvolume · severity · diversity\\ln_negative · n_total\\l}}"];
    ph [shape=record, label="{{phrases|run_id PK,FK\\laspect PK · rank PK\\lphrase · frequency\\ltfidf_weight · score\\lexample_review_ids\\l}}"];
    rc [shape=record, label="{{recommendations|run_id FK\\laspect · phrase\\laction · evidence\\l}}"];
    pd [shape=record, label="{{predictions|run_id PK,FK\\lreview_id PK · aspect PK\\lsentiment · confidence\\l}}"];
    rs [shape=record, label="{{review_severity|run_id PK,FK\\lreview_id PK\\lrating · severity\\l}}"];
    runs -> pr; runs -> ph; runs -> rc; runs -> pd; runs -> rs; }}''', tmp / "erd.png")
    return {"arsitektur": arsitektur, "alur": alur, "erd": erd}


def gambar(path: Path, lebar_cm: float, teks: str) -> KeepTogether:
    from PIL import Image as PI
    w, h = PI.open(path).size
    lebar = lebar_cm * cm
    return KeepTogether([Image(str(path), width=lebar, height=lebar * h / w), P(teks, "cap")])


# --------------------------------------------------------------------------- #
def isi(img: dict[str, Path]) -> list:
    kat = muat_katalog(ROOT / "config" / "kebutuhan.yaml")
    fr = [k for k in kat.kebutuhan if k["kode"].startswith("FR")]
    knf = [k for k in kat.kebutuhan if k["kode"].startswith("KNF")]
    cerita: list = []
    add = cerita.append
    ext = cerita.extend

    # ---- sampul
    add(Spacer(1, 3.2 * cm))
    add(Paragraph("PRODUCT REQUIREMENTS DOCUMENT<br/>DAN ARSITEKTUR SISTEM", ParagraphStyle(
        "cv", fontName="DV-B", fontSize=22, leading=28, textColor=HIJAU)))
    add(Spacer(1, 0.5 * cm))
    add(Paragraph("Restaurant Review Analytics (RRA)", ParagraphStyle("cv2", fontName="DV-B", fontSize=14, leading=18)))
    add(Paragraph("Sistem analitik ulasan restoran berbasis Aspect-Based Sentiment Analysis dengan ekstraksi frasa "
                  "keluhan dominan untuk rekomendasi prioritas perbaikan layanan",
                  ParagraphStyle("cv3", fontName="DV", fontSize=10.5, leading=15, textColor=ABU, spaceBefore=6)))
    add(Spacer(1, 1.2 * cm))
    add(tabel(["Atribut", "Isi"], [
        ["Versi / tanggal", "1.0 — 21 November 2026"],
        ["Jenis produk", "Prototipe riset (artefak skripsi S1 Teknik Informatika), bukan produk produksi"],
        ["Pemilik produk", "Abdi (peneliti)"],
        ["Repositori", "github.com/Badiii098/restaurant-review-analytics — PR #1, branch claude/practical-rubin-ft5ib8"],
        ["Status implementasi", "Prototipe berjalan end-to-end pada data contoh sintetis; data penelitian asli menunggu pengumpulan/anotasi"],
        ["Tujuan dokumen", "Bahan analisis lanjutan: menyatukan kebutuhan produk, keputusan desain, arsitektur, risiko, dan celah yang belum tertutup"],
    ], [1.3, 4.2]))
    add(Spacer(1, 0.6 * cm))
    add(P("Dokumen ini dibangkitkan dari kode dan konfigurasi repositori (katalog kebutuhan, endpoint, skema basis data), "
          "sehingga angka dan nama komponen mengikuti implementasi. Bagian yang bersifat keputusan peneliti atau asumsi "
          "ditandai eksplisit. Angka hasil model pada dokumen ini <b>tidak ada</b>, karena data penelitian asli belum "
          "tersedia di lingkungan pembangun.", "note"))
    add(PageBreak())
    toc = TableOfContents()
    toc.levelStyles = [S["toc1"], S["toc2"]]
    add(Paragraph("Daftar Isi", ParagraphStyle("dt", fontName="DV-B", fontSize=15, leading=19, textColor=HIJAU, spaceAfter=8))); add(toc); add(PageBreak())

    # ---- 1
    add(P("1. Ringkasan Eksekutif", "h1"))
    add(P("RRA mengubah tumpukan ulasan Google Maps berbahasa Indonesia menjadi <b>urutan prioritas perbaikan layanan</b> "
          "untuk pemilik restoran: aspek apa yang harus dibenahi lebih dulu, seberapa parah, dengan frasa keluhan apa, dan "
          "tindakan apa yang disarankan. Rantai penalarannya eksplisit dan dapat diaudit: ulasan → aspek → sentimen per "
          "aspek → keparahan (dari rating bintang) → frasa keluhan dominan → skor prioritas 0–100 → rekomendasi aturan "
          "DINESERV."))
    add(P("Kontribusi penelitian <b>bukan pada algoritma</b> (TF-IDF + SVM linear sudah terbukti pada ulasan restoran "
          "Indonesia), melainkan pada <b>rekayasa sistem</b>: arsitektur lima lapis dengan kontrak data tetap, skor "
          "prioritas yang transparan, pengujian perangkat lunak berjenjang, keterlacakan kebutuhan ke kasus uji, dan "
          "validasi terhadap urutan pakar."))
    add(P("Produk dikembangkan dengan <b>SDLC model prototipe</b> (dua iterasi) dan disajikan sebagai API REST (FastAPI) "
          "plus aplikasi web (React) yang setiap halamannya adalah satu tahap diagram penelitian lengkap dengan buktinya."))
    ext([P("Status singkat", "h3")] + bullets([
        f"<b>Selesai:</b> inti analitik lima lapis, API 13 titik akhir, aplikasi web 10 halaman, katalog {len(kat.kebutuhan)} kebutuhan dan {len(kat.kasus)} kasus uji, "
        "keputusan hipotesis otomatis, CI, naskah Bab I–III selaras.",
        "<b>Menunggu data asli:</b> pemilihan 8 restoran, anotasi 500 ulasan dan kappa, urutan pakar, iterasi 2, bukti manual KNF.",
        "<b>Terbuka:</b> Bab IV (hasil), sitasi untuk subbab teknis, dan beberapa perbaikan minor (bagian 14).",
    ]))

    # ---- 2
    add(P("2. Latar Belakang dan Masalah", "h1"))
    add(P("Ulasan daring tumbuh lebih cepat daripada kemampuan pemilik usaha membacanya, dan rata-rata bintang tidak "
          "menunjukkan aspek mana yang bermasalah karena satu ulasan dapat memuji makanan sekaligus mengeluhkan "
          "pelayanan. ABSA memecah ulasan per aspek, tetapi penelitian terdahulu berhenti di ketepatan model."))
    add(tabel(["Celah pada penelitian terdahulu", "Dampak bagi pengguna", "Jawaban RRA"], [
        ["Berhenti pada akurasi model", "Pemilik tidak tahu apa yang diperbaiki lebih dulu", "Skor prioritas komposit 0–100 per restoran"],
        ["Prioritas disusun manual / frekuensi saja", "Tidak dapat diulang dan diaudit", "Rumus terbuka, komponen skor tersimpan per hasil"],
        ["Akar masalah lewat diskusi", "Mahal, subjektif", "Frasa keluhan dominan yang dapat ditelusuri ke ulasan asal"],
        ["Perangkat lunak tidak diuji", "Hasil tidak dapat dipercaya di luar eksperimen", "Uji unit, integrasi, sistem, non-fungsional; keterlacakan FR/KNF"],
        ["Dataset berpusat pada tolok ukur berbahasa Inggris", "Kurang mewakili ulasan lokal", "Data ulasan restoran Jabodetabek berbahasa Indonesia"],
    ], [2.2, 2.2, 2.6]))

    # ---- 3
    add(P("3. Tujuan, Non-Tujuan, dan Metrik Keberhasilan", "h1"))
    add(P("3.1 Tujuan produk", "h2"))
    ext(bullets([
        "Menghasilkan peringkat prioritas perbaikan per restoran yang konsisten dengan penilaian pakar.",
        "Menyediakan bukti setiap tahap penelitian dalam satu tampilan yang dapat diperiksa penguji.",
        "Menjamin angka di layar, CLI, dan basis data berasal dari satu perhitungan yang sama.",
        "Berjalan sepenuhnya lokal tanpa jaringan (privasi data ulasan, kemudahan demo sidang).",
    ]))
    add(P("3.2 Non-tujuan dan anti-tujuan", "h2"))
    ext(bullets([
        "<b>Non-tujuan:</b> membandingkan algoritma, meningkatkan akurasi model, multi-pengguna/akun, integrasi kasir atau "
        "API resmi Google, penemuan aspek otomatis, analisis tren bulanan, uji penerimaan pengguna, skalabilitas cloud.",
        "<b>Anti-tujuan (gagal walau berjalan):</b> angka dashboard berbeda dari CLI/basis data; halaman memuat aset dari "
        "internet; uji dilemahkan atau dilewati; angka dikarang saat bukti belum ada; pakem penelitian berubah diam-diam.",
    ]))
    add(P("3.3 Rumusan masalah, hipotesis, dan kriteria keberhasilan", "h2"))
    add(tabel(["RM", "Pertanyaan", "Hipotesis (H1)", "Prosedur keputusan"], [
        ["1", "Rancangan arsitektur lima lapis beserta katalog kebutuhan dan kontrak antar-lapis", "100% kontrak lolos validasi dan 100% kebutuhan terlacak ke kasus uji", "Uji kontrak (U-01) + uji keterlacakan (U-13) dari laporan pytest"],
        ["2", "Persentase kasus uji lulus dan waktu proses per 1.000 ulasan", "Seluruh uji kritis lulus dan rata-rata ≤ 60 detik per 1.000 ulasan", "Uji-t satu sampel satu sisi, α = 0,05, minimal 5 ulangan, uji kritis = kasus terpetakan ke FR"],
        ["3", "Aspek prioritas pertama per restoran dan korelasinya dengan urutan pakar", "Median ρ Spearman antar-restoran > 0,60", "Wilcoxon satu sampel satu sisi, α = 0,05 (n = 8 restoran, p minimum 1/256)"],
    ], [0.5, 2.6, 2.4, 2.8]))
    add(P("Bila H0 tidak ditolak, hasil tetap dilaporkan sebagai temuan dengan rekomendasi perbaikan. Macro-F1 klasifikasi "
          "adalah bukti pendukung, bukan hipotesis.", "note"))

    # ---- 4
    add(P("4. Pengguna dan Skenario", "h1"))
    add(tabel(["Persona", "Kebutuhan", "Cara memakai RRA"], [
        ["Pemilik / pengelola restoran", "Tahu apa yang diperbaiki lebih dulu, beserta alasan dan tindakan", "Halaman Hasil & Prioritas: peringkat 0–100, frasa keluhan, tindakan, sensitivitas bobot"],
        ["Peneliti (Abdi)", "Menjalankan seluruh tahap, menghimpun bukti, menulis Bab IV", "CLI + halaman tahap; ekspor naskah; catatan iterasi"],
        ["Dosen penguji / pembimbing", "Memeriksa kebenaran klaim dan keterulangan", "Ringkasan, Kebutuhan, Pengujian, Kesimpulan; API /docs; kode dan CI"],
        ["Peneliti berikutnya", "Memakai ulang kontrak, kasus uji, prosedur", "Repositori, docs/KONTRAK.md, docs/openapi.json"],
    ], [1.6, 2.6, 3.2]))
    add(P("User story utama", "h3"))
    ext(bullets([
        "Sebagai pemilik restoran, saya ingin melihat aspek yang paling mendesak beserta angka penyusunnya agar saya dapat memutuskan investasi perbaikan.",
        "Sebagai peneliti, saya ingin menjalankan analisis ulang dengan satu tombol/perintah agar hasil selalu sesuai data terbaru.",
        "Sebagai penguji, saya ingin melihat status lulus/gagal setiap kebutuhan dan keputusan hipotesis yang dihitung dari bukti, bukan tulisan tangan.",
        "Sebagai peneliti, saya ingin sistem menolak menampilkan angka bila bukti belum ada, dan memberi tahu perintah untuk membuatnya.",
    ]))

    # ---- 5
    add(P("5. Lingkup Produk", "h1"))
    add(tabel(["Dalam lingkup", "Di luar lingkup"], [
        ["Ulasan publik Google Maps berbahasa Indonesia, 8 restoran sampel Jabodetabek, periode 2021–2026", "Ulasan bahasa lain, sarkasme dan emoji yang ditangani khusus, ulasan di luar periode"],
        ["5 aspek tetap (makanan, pelayanan, harga, suasana, fasilitas); 3 kelas sentimen", "Penemuan aspek otomatis, aspek kebersihan terpisah"],
        ["Satu model: TF-IDF + SVM linear", "Perbandingan algoritma, transformer, deep learning, LLM"],
        ["Skor prioritas 0,4/0,4/0,2 + uji sensitivitas ±10%", "Pakar menilai bobot (pakar hanya mengurutkan aspek)"],
        ["Aplikasi web lokal, tanpa akun", "Multi-pengguna, autentikasi, cloud, SLA produksi"],
        ["Uji unit, integrasi, sistem, non-fungsional", "Uji keamanan/penetrasi, beban ekstrem, usability/SUS"],
    ], [1, 1]))

    # ---- 6
    add(P("6. Kebutuhan Fungsional dan Non-Fungsional", "h1"))
    add(P("Sumber tunggal: <font name='DVM'>config/kebutuhan.yaml</font>. Dibaca oleh kode, uji keterlacakan, API, dan naskah.", "note"))
    add(P("6.1 Kebutuhan fungsional (FR)", "h2"))
    add(tabel(["Kode", "Kebutuhan", "Kriteria lulus", "Kasus uji"],
              [[k["kode"], k["uraian"], k["kriteria"], ", ".join(k["kasus"])] for k in fr], [0.8, 3.2, 3, 1.4]))
    add(P("6.2 Kebutuhan non-fungsional (KNF)", "h2"))
    add(tabel(["Kode", "Kebutuhan", "Kriteria lulus", "Kasus uji"],
              [[k["kode"], k["uraian"], k["kriteria"], ", ".join(k["kasus"])] for k in knf], [0.8, 3.2, 3, 1.4]))
    add(P("6.3 Kasus uji dan keterlacakan", "h2"))
    tk = {"unit": "Unit", "integrasi": "Integrasi", "sistem": "Sistem", "nonfungsional": "Non-fungsional"}
    add(tabel(["Kode", "Tingkat", "Yang diuji", "Berkas / bukti", "Jenis", "Kritis"],
              [[c["kode"], tk[c["tingkat"]], c["nama"], c.get("berkas") or c.get("bukti", ""), c["jenis"], "ya" if c.get("kritis") else "tidak"]
               for c in kat.kasus], [0.7, 1.5, 3.0, 2.0, 0.9, 0.6]))
    add(P("Kasus <i>otomatis</i> wajib memiliki uji bertanda <font name='DVM'>pytest.mark.kasus(\"KODE\")</font>; kasus "
          "<i>manual</i> wajib menyebut berkas bukti di <font name='DVM'>reports/manual/</font>. Status kasus dibaca dari "
          "<font name='DVM'>reports/pytest.xml</font>. Uji kritis (dipakai pada H2) = seluruh kasus yang terpetakan ke FR.", "note"))

    # ---- 7
    add(P("7. Spesifikasi Fitur Aplikasi Web", "h1"))
    add(P("Navigasi samping berupa garis tahapan; urutan halaman mengikuti diagram penelitian. Setiap halaman memuat "
          "keadaan <i>belum tersedia</i> yang menampilkan perintah pembuat bukti, bukan angka perkiraan."))
    add(tabel(["Halaman", "Tahap diagram", "Isi dan perilaku", "Endpoint"], [
        ["Ringkasan <font name='DVM'>/</font>", "—", "Alur penelitian dapat diklik, 4 statistik utama, tabel keputusan H1–H3, peringatan data contoh", "hasil, data, hipotesis"],
        ["Pengumpulan Data <font name='DVM'>/data</font>", "Pengumpulan data (8 restoran)", "Kandidat, sampel purposive dan target, grafik ulasan per restoran dan rating", "data"],
        ["Anotasi <font name='DVM'>/anotasi</font>", "Anotasi (500 ulasan, kappa)", "Progres terhadap 500, κ aspek dan sentimen beserta tafsiran", "anotasi"],
        ["Kebutuhan <font name='DVM'>/kebutuhan</font>", "Analisis kebutuhan", "Matriks FR/KNF → kasus → status; % keterlacakan", "kebutuhan"],
        ["Desain <font name='DVM'>/desain</font>", "Desain cepat", "Lima lapis, tabel kontrak, bobot, tautan OpenAPI", "desain"],
        ["Prototipe & Iterasi <font name='DVM'>/iterasi</font>", "Pembangunan + evaluasi prototipe", "Macro-F1 iterasi 1 vs 2, F1 per aspek, selisih, catatan perbaikan", "iterasi"],
        ["Hasil & Prioritas <font name='DVM'>/hasil</font>", "Hasil analisis", "Peringkat 0–100, frasa, rekomendasi (2 per aspek + semua), sensitivitas, tombol hitung ulang", "hasil/terakhir, sensitivitas, POST analisis"],
        ["Pengujian <font name='DVM'>/pengujian</font>", "Pengujian perangkat lunak", "Jumlah uji, kasus per tingkat, KNF-01 per ulangan vs batas 60 s", "pengujian"],
        ["Validasi Pakar <font name='DVM'>/pakar</font>", "Validasi pakar", "ρ per restoran vs 0,60, median, p Wilcoxon, kesesuaian peringkat 1", "pakar"],
        ["Kesimpulan <font name='DVM'>/kesimpulan</font>", "Analisis hasil dan kesimpulan", "H0/H1, statistik uji, p, rekomendasi bila H0 tidak ditolak", "hipotesis"],
    ], [1.7, 1.4, 3.6, 1.5]))
    add(P("Persyaratan tampilan: mode terang/gelap mengikuti OS; lebar ponsel tanpa scroll horizontal; grafik memakai palet "
          "tervalidasi buta warna (biru #2A78D6, oranye #EB6834), label langsung dan tooltip; skor ditampilkan 0–100 "
          "dengan format angka Indonesia (koma desimal, titik ribuan).", "note"))

    # ---- 8
    add(P("8. Data", "h1"))
    add(P("8.1 Sumber, sampel, dan anotasi", "h2"))
    add(tabel(["Topik", "Keputusan"], [
        ["Sumber", "Ulasan publik Google Maps, diambil dengan Playwright (jeda acak, tanpa paralel); nama penulis tidak dimuat"],
        ["Kandidat", "25 restoran awal → 18 aktif (lolos syarat awal) di config/restaurants.csv"],
        ["Sampel", "8 restoran purposive: urut jumlah ulasan 2021–2026, maks. 2 per kategori, isi ulang bila kurang dari 8; deterministik (scripts/pilih_restoran.py)"],
        ["Target ulasan", "Per restoran = min(tersedia, 625); restoran di bawah batas tetap dianalisis, kekurangan dilaporkan"],
        ["Anotasi", "500 ulasan acak berstrata proporsional per restoran; dua anotator melabeli seluruhnya secara terpisah; κ Cohen tingkat aspek dan sentimen; label berbeda diselesaikan lewat diskusi"],
        ["Skema masukan", "review_id, text, rating (opsional), date, restaurant"],
        ["Penanda data contoh", "dataset_meta.json berisi data_contoh = true; dashboard menampilkan peringatan"],
    ], [1.3, 4.7]))
    add(P("8.2 Skema basis data (SQLite)", "h2"))
    add(gambar(img["erd"], 11, "Gambar 1. Skema basis data hasil analisis (rra.sqlite): satu baris runs per analisis, semua tabel lain terhubung lewat run_id."))
    add(P("Seluruh komponen skor (volume, keparahan, keragaman, bobot) disimpan per hasil sebagai bahan audit; hasil lama "
          "tidak ditimpa sehingga riwayat analisis dapat dibandingkan.", "note"))

    # ---- 9
    add(P("9. Spesifikasi Algoritma dan Perhitungan", "h1"))
    add(gambar(img["alur"], 16, "Gambar 2. Alur data dan bukti dari ulasan sampai keputusan hipotesis."))
    add(tabel(["Komponen", "Spesifikasi"], [
        ["Praproses", "Huruf kecil; hapus URL/mention/angka; konversi emoji; normalisasi kata tidak baku; penyeragaman huruf berulang; stopword; negasi dengan jendela 3 kata yang tidak melintasi batas klausa; tanpa stemming; pemecahan klausa pada tanda baca dan kata pertentangan"],
        ["Fitur", "TF-IDF sublinear, maks. 20.000 fitur, n-gram 1–2, min_df 2, max_df 0,95"],
        ["Model", "SVM linear satu-lawan-semua; aspek multi-label dengan ambang keyakinan 0,50; sentimen 3 kelas per aspek; bobot kelas seimbang; benih acak 42; keyakinan = sigmoid dari fungsi keputusan"],
        ["Keparahan", "Rerata (5 − rating) / 4 pada ulasan negatif; berasal dari rating, bukan dari model; bawaan 0,5 bila tanpa rating"],
        ["Skor prioritas", "0,4·Volume + 0,4·Keparahan + 0,2·Keragaman; Volume dan Keragaman min–max; skala tampil ×100"],
        ["Frasa keluhan", "n-gram 1–3 kata pada klausa bernada keluhan (leksikon domain), frekuensi minimum 3, 5 teratas per aspek, bobot TF-IDF, ditelusuri ke ulasan contoh"],
        ["Rekomendasi", "Tabel aturan DINESERV per aspek (kata kunci → tindakan) dengan aturan cadangan; sengaja bukan keluaran model"],
        ["Sensitivitas", "Setiap bobot digeser ±10% (6 skenario), dinormalisasi ulang; dilaporkan peringkat, τ Kendall, kesamaan peringkat 1"],
        ["Evaluasi", "Validasi silang 10 lipatan per ulasan; Macro-F1 aspek dan sentimen (aspek tanpa dukungan dihitung nol); Precision@5 frasa terhadap gold set"],
        ["Kesesuaian pakar", "ρ Spearman per restoran (≥3 aspek, tanpa seri); median ρ diuji Wilcoxon satu sisi terhadap 0,60; kesesuaian peringkat 1"],
    ], [1.2, 4.8]))

    # ---- 10
    add(P("10. Arsitektur Sistem", "h1"))
    add(P("10.1 Gambaran umum", "h2"))
    add(P("Arsitektur klien-server lokal dengan lima lapis. Lapis 1–4 adalah inti analitik Python dengan kontrak data tetap "
          "(<font name='DVM'>src/rra/contracts.py</font>); lapis 5 dipecah menjadi 5a (API dan layanan) dan 5b (klien web). "
          "Lapis 5 sengaja tipis: tidak ada logika keputusan di dalamnya, sehingga angka di layar tidak dapat menyimpang "
          "dari arsip."))
    add(gambar(img["arsitektur"], 15, "Gambar 3. Arsitektur klien-server lima lapis RRA."))
    add(P("10.2 Tanggung jawab lapis dan kontrak", "h2"))
    add(tabel(["Lapis", "Modul", "Masukan → keluaran", "Alasan desain"], [
        ["1 Data", "io_layer/loader, scope, sample_data", "CSV/JSONL → RawReview; pemilihan sampel", "Memisahkan bentuk berkas dari isi; sumber baru = pemuat baru"],
        ["2 Praproses", "preprocess/cleaner, resources", "RawReview → CleanReview (teks bersih, klausa)", "Aturan bahasa Indonesia terpusat dan dapat diuji"],
        ["3 Model", "models/svm_model, registry", "CleanReview → Prediction (aspek, sentimen, keyakinan)", "Satu komponen berkontrak; model dapat dilatih ulang cepat tanpa GPU"],
        ["4 Keputusan", "decision/*, analysis/*", "Prediction + rating → AspectPriority, ComplaintPhrase, Recommendation; kappa, hipotesis", "Satu-satunya tempat skor dihitung; eksplisit dan dapat diaudit"],
        ["5a Layanan/API", "services/tahap, api/app, api/schemas", "Basis data + berkas bukti → JSON /api/v1", "Menyajikan bukti tanpa logika bisnis; skema dari kontrak"],
        ["5b Klien web", "frontend/src", "JSON → 10 halaman", "Hanya memformat tampilan; offline; mudah diuji terpisah"],
        ["Penyimpanan", "storage/repository", "Hasil analisis ⇄ SQLite", "Satu pintu baca/tulis; hasil lama tidak ditimpa"],
    ], [1.15, 1.6, 2.3, 2.3]))
    add(P("10.3 Kontrak data antar-lapis", "h2"))
    add(P("Dataclass di <font name='DVM'>contracts.py</font>: RawReview, CleanReview, TrainingExample, AspectSentiment, "
          "Prediction, ComplaintPhrase, AspectPriority, Recommendation, AnalysisResult. Dokumen "
          "<font name='DVM'>docs/KONTRAK.md</font> dan skema <font name='DVM'>docs/openapi.json</font> dibangkitkan dari "
          "kode oleh <font name='DVM'>scripts/export_contracts.py</font>; respons /hasil memakai AspectPriority langsung "
          "sebagai model respons sehingga dokumentasi API tidak dapat menyimpang dari kontrak."))
    add(P("10.4 API REST /api/v1", "h2"))
    add(tabel(["Metode", "Jalur", "Fungsi", "Sumber data"], [
        ["GET", "/status", "Versi, model, basis data, hasil terakhir, daftar tahapan", "config, SQLite"],
        ["GET", "/data", "Kandidat, sampel purposive, target, sebaran ulasan/rating/tahun", "restaurants.csv, data/raw"],
        ["GET", "/anotasi", "Progres vs 500, κ aspek dan sentimen", "labels.csv, reports/kappa.json"],
        ["GET", "/kebutuhan", "Katalog, status kasus, % keterlacakan", "kebutuhan.yaml, pytest.xml, reports/manual"],
        ["GET", "/desain", "Lima lapis, kontrak, bobot", "kode (contracts), config"],
        ["GET", "/iterasi", "Catatan iterasi dan selisih Macro-F1", "reports/iterasi/*.json"],
        ["GET", "/hasil/terakhir · /hasil/{run_id}", "Prioritas, frasa, rekomendasi (404 bila run tidak ada)", "SQLite"],
        ["POST", "/analisis", "Latih dan simpan hasil baru; 409 bila sedang berjalan", "pipeline → SQLite"],
        ["GET", "/sensitivitas", "Enam skenario geser bobot", "reports/sensitivitas.json"],
        ["GET", "/pengujian", "Ringkasan pytest per tingkat, benchmark", "pytest.xml, benchmark.json"],
        ["GET", "/pakar", "ρ per restoran, uji median, kesesuaian peringkat 1", "reports/uji_pakar.json"],
        ["GET", "/hipotesis", "Keputusan H1–H3 dari bukti", "gabungan semua bukti"],
        ["GET", "/docs · /openapi.json", "Dokumentasi interaktif dan skema OpenAPI", "FastAPI"],
    ], [0.7, 1.9, 2.8, 1.9]))
    add(P("Konvensi: bila sumber bukti belum ada, respons 200 dengan <font name='DVM'>status = belum_tersedia</font> dan "
          "<font name='DVM'>langkah</font> berisi perintah pembuatnya; endpoint tidak pernah memalsukan angka. "
          "Rute selain /api/v1 menyajikan klien web (rute SPA) atau pesan cara membangunnya.", "note"))
    add(P("10.5 Struktur repositori", "h2"))
    add(P("restaurant-review-analytics/<br/>"
          "├─ src/rra/ — contracts, config, pipeline, evaluate, iterations, requirements, junit, cli<br/>"
          "│  ├─ io_layer · preprocess · models · decision · analysis (agreement, expert, hypotheses)<br/>"
          "│  ├─ storage · report · services (tahap) · api (app, schemas)<br/>"
          "├─ frontend/ — React + TS + Vite (src/pages, components, layout, styles)<br/>"
          "├─ config/ — default.yaml, model_svm.yaml, kebutuhan.yaml, restaurants.csv<br/>"
          "├─ tests/ — unit, integrasi, sistem (API, peramban), keterlacakan<br/>"
          "├─ scripts/ — pilih_restoran, compute_kappa, uji_pakar, scraping, proposal (naskah), arsip/streamlit<br/>"
          "├─ docs/ — ARSITEKTUR, ALUR, KONTRAK, openapi.json, PENGUJIAN, proposal/ (BAB I–III siap tempel)<br/>"
          "└─ .github/workflows/ci.yml", "mono"))
    add(P("10.6 Perintah operasional (CLI)", "h2"))
    add(tabel(["Perintah", "Fungsi"], [
        ["python -m rra.cli sample-data --n 2000", "Bangkitkan data contoh (ditandai data_contoh)"],
        ["python -m rra.cli run", "Alur end-to-end → SQLite, CSV, Markdown"],
        ["python -m rra.cli evaluate --folds 10 --iterasi N --catatan \"…\"", "Validasi silang; catat iterasi prototipe"],
        ["python -m rra.cli benchmark --repeat 5", "KNF-01 (waktu proses, simpangan baku)"],
        ["python -m rra.cli sensitivity --out reports/sensitivitas.json", "Uji sensitivitas bobot ±10%"],
        ["python scripts/pilih_restoran.py --tulis", "Tetapkan 8 restoran sampel"],
        ["python scripts/compute_kappa.py --first … --second … --out reports/kappa.json", "κ Cohen aspek dan sentimen"],
        ["python scripts/uji_pakar.py --pakar data/reference/urutan_pakar.csv", "ρ Spearman, Wilcoxon, kesesuaian peringkat 1"],
        ["python -m rra.cli serve [--port 8000]", "API + aplikasi web"],
    ], [3.4, 2.6]))

    # ---- 11
    add(P("11. Atribut Kualitas (Non-Fungsional) dan Keputusan Teknis", "h1"))
    add(tabel(["Atribut", "Target dan cara dipenuhi", "Bukti"], [
        ["Kinerja", "≤ 60 detik per 1.000 ulasan (rata-rata 5 ulangan, uji-t); halaman ≤ 3 detik sampai peringkat tampil", "benchmark.json; test_e2e_web (N-03)"],
        ["Offline", "Aset klien dibundel, tanpa CDN/font daring; data lokal SQLite", "Uji manual N-02; arsitektur"],
        ["Keterulangan", "Benih acak 42, konfigurasi disimpan per hasil, sampel deterministik, CI tiap perubahan", "runs.config_json; ci.yml"],
        ["Keterlacakan", "Katalog tunggal FR/KNF ↔ kasus ↔ uji bertanda", "test_traceability; H1"],
        ["Kejujuran bukti", "Status belum_tersedia, bukan angka perkiraan; peringatan data contoh; H2 butuh ≥ 5 ulangan", "test_api, test_hypotheses"],
        ["Kompatibilitas", "Chrome, Firefox, Edge; Python 3.11 dan 3.12", "N-04, N-05 (manual); CI matrix"],
        ["Keamanan dasar", "Penyajian berkas statis dengan pemeriksaan jalur (anti path traversal); tanpa autentikasi karena lokal; ikat 127.0.0.1", "Tinjauan kode"],
        ["Privasi", "Hanya ulasan publik; nama penulis tidak dimuat; data tidak keluar dari mesin", "Kebijakan scraping"],
        ["Dapat dipelihara", "Satu tanggung jawab per modul; komponen model dapat diganti lewat konfigurasi; format commit tipe(scope): pesan", "Struktur repo"],
    ], [1.1, 3.5, 1.9]))
    add(P("11.1 Catatan keputusan arsitektur (ADR ringkas)", "h2"))
    add(tabel(["Keputusan", "Alternatif", "Alasan"], [
        ["FastAPI + React (SPA), dibundel dan disajikan FastAPI", "Streamlit (iterasi 1); FastAPI + HTMX; Next.js", "Antarmuka modern, API terdokumentasi sebagai bukti kontrak, uji terpisah; Next.js ditolak karena memecah inti Python"],
        ["Satu proses, SQLite", "Server basis data, antrean tugas", "Skala prototipe lokal; boring-by-default; mudah didemokan"],
        ["Bukti berupa berkas + SQLite", "Semua ke basis data", "Hasil CLI/pytest/benchmark tetap tersedia tanpa server; dashboard hanya membaca"],
        ["Grafik SVG buatan sendiri", "Recharts/D3", "Ringan, offline, cukup untuk grafik batang; bila butuh grafik garis interaktif perlu pustaka"],
        ["Keputusan hipotesis dihitung kode", "Ditulis manual di naskah", "Angka naskah = angka sistem; dapat diulang"],
        ["Playwright Python untuk e2e", "Playwright Node", "Hasil masuk pytest.xml sehingga dashboard dan H1/H2 dapat membacanya"],
        ["Satu model SVM", "Banding algoritma", "Fokus penelitian di rekayasa sistem; perbandingan sudah ada pada literatur"],
    ], [2.0, 1.6, 2.9]))

    # ---- 12
    add(P("12. Strategi Pengujian dan CI/CD", "h1"))
    add(tabel(["Tingkat", "Alat", "Cakupan"], [
        ["Unit", "pytest", "Kontrak, praproses, model, keparahan/skor/frasa/aturan, sensitivitas, ρ/Wilcoxon, κ, iterasi, hipotesis, sampling, keterlacakan"],
        ["Integrasi", "pytest", "Validasi silang dan metrik; pipeline end-to-end termasuk masukan tidak sempurna"],
        ["Sistem", "pytest (CLI subprocess), TestClient (API), Playwright (peramban)", "CLI kotak hitam; setiap endpoint; sepuluh halaman tanpa galat konsol; kesamaan angka UI–API; KNF-03"],
        ["Komponen UI", "Vitest + Testing Library", "Skor 0–100, tabel prioritas, navigasi tahapan, keadaan belum tersedia"],
        ["Non-fungsional", "benchmark CLI, manual", "KNF-01 otomatis; KNF-02/04/05 dicatat sebagai bukti manual JSON"],
    ], [1.0, 2.1, 3.4]))
    add(P("CI (GitHub Actions): job <i>web</i> (npm ci, Vitest, build, unggah dist) lalu job <i>uji</i> (matriks Python 3.11 "
          "dan 3.12; pytest dengan pytest.xml; sample-data; run; evaluate). Hasil CI terakhir pada PR #1 hijau di tiga job. "
          "Aturan repositori: commit kecil dan atomik berformat tipe(scope): pesan, kerja di branch fitur, uji dijalankan "
          "sebelum commit."))

    # ---- 13
    add(P("13. Risiko dan Mitigasi", "h1"))
    add(tabel(["Risiko", "Dampak", "Mitigasi / status"], [
        ["Data asli belum ada / kurang dari target", "Hasil bergantung data contoh; target tidak terpenuhi", "Target = min(tersedia, 625); kekurangan dilaporkan; peringatan data contoh di UI"],
        ["Wilcoxon n = 8 rapuh (p min. 1/256) dan ρ berlangkah 0,1", "H0 RM3 mudah tidak ditolak", "Dicatat sebagai keterbatasan; hasil tetap temuan; rekomendasi perbaikan otomatis"],
        ["500 ulasan berlabel kecil untuk kelas jarang", "Macro-F1 rendah/berfluktuasi", "Macro-F1 sebagai bukti pendukung; iterasi 1→2 mendokumentasikan perbaikan"],
        ["Kappa rendah", "Mutu label dipertanyakan", "Panduan anotasi, latihan 20 ulasan, diskusi label berbeda"],
        ["Scraping Google Maps berubah/diblokir", "Pengumpulan data terhambat", "Skrip akuisisi terpisah, login manual, jeda acak; data dapat diimpor CSV"],
        ["Perubahan keputusan sampel (18 → 8)", "Naskah dan data tidak selaras", "Sampel dari konfigurasi; naskah dibangkitkan dari fakta; konfirmasi dosen"],
        ["Sitasi subbab teknis belum ada", "Tinjauan kurang berjangkar", "Tambah dari folder REFERENSI; kunci baru di pustaka.py"],
        ["Perbedaan lingkungan (Windows/Python 3.14)", "Instalasi gagal", "pythonpath di pyproject; perintah portabel; CI 3.11/3.12; Python 3.12 disarankan"],
        ["Jadwal 7 bulan (Nov 2026–Mei 2027) padat", "Keterlambatan iterasi/pengujian", "Bukti otomatis mengurangi kerja manual; urut tugas lihat bagian 15"],
    ], [2.0, 1.7, 2.8]))

    # ---- 14
    add(P("14. Status Implementasi dan Celah yang Diketahui", "h1"))
    add(P("14.1 Matriks status", "h2"))
    add(tabel(["Area", "Status", "Catatan"], [
        ["Inti analitik lima lapis", "Selesai", "Berjalan pada data contoh; kontrak diuji"],
        ["API 13 titik akhir + OpenAPI", "Selesai", "Diuji; docs/openapi.json"],
        ["Aplikasi web 10 halaman", "Selesai", "Terang/gelap, ponsel, tanpa galat konsol"],
        [f"Katalog {len(kat.kebutuhan)} kebutuhan, {len(kat.kasus)} kasus, keterlacakan", "Selesai", "100% terlacak"],
        ["Keputusan H1–H3 otomatis", "Selesai", "H1, H2 terhitung pada data contoh; H3 menunggu data pakar"],
        ["CI web + Python", "Selesai", "Hijau pada PR #1"],
        ["Naskah Bab I–III dan ekspor Markdown", "Selesai", "docs/proposal/*.md; .docx perlu templat FIK"],
        ["Pemilihan 8 restoran, target ulasan", "Menunggu data", "scripts/pilih_restoran.py --tulis"],
        ["Anotasi 500 ulasan + κ", "Menunggu data", "make_annotation_template, compute_kappa"],
        ["Urutan pakar → ρ, Wilcoxon", "Menunggu data", "urutan_pakar.csv, uji_pakar.py"],
        ["Iterasi 2 prototipe", "Menunggu data", "Setelah perbaikan nyata pada data asli"],
        ["Bukti manual KNF-02, -04, -05", "Menunggu pelaksana", "reports/manual/*.json"],
        ["Bab IV–V", "Belum", "Menunggu semua bukti di atas"],
    ], [2.6, 1.2, 2.7]))
    add(P("14.2 Utang teknis dan temuan minor (dari tinjauan kode)", "h2"))
    ext(bullets([
        "Kasus kritis yang <i>dilewati</i> pada H2 dilabeli gagal; sebaiknya dilaporkan terpisah.",
        "Kappa tingkat aspek mengabaikan ulasan yang oleh satu anotator dinilai tanpa aspek (dapat menaikkan κ); n_ulasan belum masuk kappa.json.",
        "Berkas bukti manual JSON yang rusak atau labels.csv tanpa kolom review_id menyebabkan HTTP 500; perlu validasi masukan.",
        "Klien yang di-build setelah server berjalan baru tampil setelah restart; /api/v2 yang tidak ada mendapat halaman SPA, bukan galat.",
        "Rumus bobot di halaman Hasil ditulis tetap, belum dibaca dari run.weights; kunci React dari label terpotong dapat ganda.",
        "KNF-01 menormalisasi seluruh waktu (termasuk pelatihan) per ulasan; perlu satu kalimat batasan di Bab IV.",
        "Sebagian gambar naskah masih memerlukan Graphviz (dot); Gambar 3.1 sudah bebas Graphviz.",
        "Seed data berlabel dari generator sintetis membuat F1 = 1,000 pada data contoh; tidak boleh dikutip.",
    ]))

    # ---- 15
    add(P("15. Rencana Lanjutan dan Pertanyaan Terbuka", "h1"))
    add(P("15.1 Urutan pekerjaan yang disarankan", "h2"))
    add(tabel(["#", "Pekerjaan", "Keluaran", "Prasyarat"], [
        ["1", "Letakkan data scraping di data/raw/maps lalu jalankan pilih_restoran --tulis", "8 restoran, target, Tabel 3.1, Gambar 3.6–3.7", "Data mentah"],
        ["2", "Anotasi 500 ulasan oleh dua anotator; hitung κ", "reports/kappa.json; halaman Anotasi terisi", "#1; panduan ANOTASI.md"],
        ["3", "Latih ulang dengan data berlabel; evaluate --iterasi 1", "Macro-F1 iterasi 1", "#2"],
        ["4", "Perbaikan nyata (praproses/leksikon/ambang) lalu evaluate --iterasi 2", "Selisih Macro-F1 yang jujur", "#3"],
        ["5", "Pengujian: pytest.xml, benchmark 5 ulangan, bukti manual N-02/04/05", "H1, H2 pada data asli", "#4"],
        ["6", "Pakar mengurutkan aspek per restoran; uji_pakar", "ρ per restoran, Wilcoxon, H3", "#1"],
        ["7", "Tulis Bab IV–V dari halaman Kesimpulan; tambah sitasi", "Naskah lengkap", "#5, #6"],
    ], [0.4, 3.0, 2.0, 1.1]))
    add(P("15.2 Pertanyaan terbuka untuk analisis", "h2"))
    ext(bullets([
        "Apakah dosen/pembimbing menyetujui pergeseran 18 → 8 restoran dan 5.040 → min(tersedia, 625) ulasan? Perlu konfirmasi tertulis.",
        "Siapa pakar (jumlah, kriteria) dan bagaimana prosedur penyusunan urutan agar bebas pengaruh dari hasil sistem?",
        "Apa perbaikan iterasi 2 yang bermakna dan dapat dipertanggungjawabkan, tanpa menyetel pada data uji?",
        "Apakah sitasi untuk REST/OpenAPI, purposive sampling, uji-t/Wilcoxon, dan Macro-F1 akan diambil dari folder REFERENSI?",
        "Perlukah KNF-04 (Firefox/Edge) diotomatiskan, atau cukup bukti manual?",
        "Apakah demo sidang berjalan lokal (laptop) atau perlu paket terpasang (Docker/executable)?",
    ]))

    # ---- lampiran
    add(P("Lampiran A. Glosarium", "h1"))
    add(tabel(["Istilah", "Arti"], [
        ["ABSA", "Aspect-Based Sentiment Analysis — sentimen per aspek yang dibicarakan"],
        ["DINESERV", "Kerangka mutu layanan restoran (Stevens dkk., 1995) sebagai dasar aspek dan aturan rekomendasi"],
        ["TF-IDF", "Pembobotan kata berdasarkan frekuensi dalam dokumen dan kelangkaan di korpus"],
        ["SVM linear", "Pengklasifikasi margin maksimum; bobot fitur dapat diperiksa"],
        ["Macro-F1", "Rerata tanpa bobot F1 antar-kelas; bukti pendukung kinerja klasifikasi"],
        ["κ Cohen", "Kesepakatan antar-anotator terkoreksi kebetulan"],
        ["ρ Spearman", "Korelasi peringkat antara urutan sistem dan urutan pakar"],
        ["Wilcoxon", "Uji peringkat bertanda satu sampel; di sini terhadap ambang median ρ 0,60"],
        ["τ Kendall", "Ukuran kesamaan peringkat; dipakai pada uji sensitivitas"],
        ["SDLC prototipe", "Siklus kebutuhan → desain cepat → bangun → evaluasi → perbaikan, dua iterasi"],
        ["Kontrak", "Bentuk data tetap yang dipertukarkan antar-lapis, diuji dan dibangkitkan dari kode"],
        ["Purposive sampling", "Penarikan sampel nonprobabilitas berdasar kriteria tertulis"],
        ["SPA", "Single-page application — aplikasi web yang memuat data lewat API"],
    ], [1.3, 4.7]))
    add(P("Lampiran B. Cara menjalankan", "h1"))
    add(P("python3.12 -m venv .venv &amp;&amp; source .venv/bin/activate<br/>"
          "pip install -r requirements.txt &amp;&amp; pip install -e .<br/>"
          "npm --prefix frontend install &amp;&amp; npm --prefix frontend run build<br/>"
          "python -m rra.cli sample-data --n 2000 --seed 42<br/>"
          "python -m rra.cli run<br/>"
          "python -m rra.cli serve   # http://127.0.0.1:8000", "mono"))
    add(P("Pada Python 3.14 tanpa paket venv sistem: <font name='DVM'>sudo apt install python3.14-venv</font> atau "
          "pakai uv/Python 3.12. Di Windows PowerShell atur <font name='DVM'>$env:PYTHONPATH = \"src\"</font> atau pakai "
          "<font name='DVM'>pip install -e .</font>.", "note"))
    return cerita


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(ROOT / "docs" / "PRD-dan-Arsitektur-RRA.pdf"))
    args = parser.parse_args()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        img = diagram(Path(tmp))
        doc = Dokumen(str(out), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2.2 * cm,
                      title="PRD dan Arsitektur Restaurant Review Analytics", author="Abdi")
        doc.multiBuild(isi(img), onFirstPage=halaman, onLaterPages=halaman)
    print(f"Ditulis: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
