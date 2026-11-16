"""LAPISAN 5 — Komponen tampilan sebagai fungsi murni.

Setiap fungsi di sini menerima data biasa (angka, daftar, kamus) dan
mengembalikan potongan HTML. Tidak ada pemanggilan Streamlit, tidak ada
akses berkas, tidak ada perhitungan ulang skor. Pemisahan ini disengaja:
komponen dapat diuji tanpa menyalakan server, dan Lapisan 4 tetap
menjadi satu-satunya tempat angka dihitung.

Susunan dan gaya mengikuti draf desain Google Stitch: bilah atas
institusional, kartu bagian bergaris rambut, tabel peringkat bertanda
satu baris, dua kolom frasa, dan panel audit dua kolom.

Seluruh teks yang berasal dari data (frasa keluhan, label aspek, nama
berkas) melewati ``esc()`` sebelum masuk ke HTML.
"""

from __future__ import annotations

from html import escape
from typing import Any, Iterable, Mapping, Sequence

#: Nama tahap pipeline → kalimat yang dapat dibaca manajer.
STAGE_LABELS = {
    "01_muat_data": "Memuat berkas ulasan",
    "02_praproses": "Pra-pemrosesan teks (tokenisasi, normalisasi slang)",
    "03_muat_label": "Menyiapkan label latih",
    "04_latih_model": "Pelatihan komponen model",
    "05_klasifikasi": "Klasifikasi aspek dan sentimen (TF-IDF)",
    "06_modul_keputusan": "Perhitungan skor prioritas dan frasa",
}


# --------------------------------------------------------------------------- #
# Pemformatan
# --------------------------------------------------------------------------- #
def esc(value: object) -> str:
    """Escape teks untuk disisipkan ke HTML."""
    return escape("" if value is None else str(value), quote=True)


def fmt_int(value: object) -> str:
    """Bilangan bulat dengan pemisah ribuan gaya Indonesia (1.119)."""
    try:
        number = int(round(float(value)))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return "–"
    return f"{number:,}".replace(",", ".")


def fmt_score(value: object, digits: int = 2) -> str:
    """Angka desimal dengan koma sebagai pemisah desimal (0,82)."""
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return "–"
    text = f"{number:.{digits}f}"
    return text.replace(".", ",")


def fmt_seconds(value: object) -> str:
    """Durasi ringkas: milidetik untuk nilai kecil, detik untuk sisanya."""
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return "–"
    if number < 0.01:
        return f"{fmt_score(number * 1000, 1)} ms"
    if number < 1:
        return f"{fmt_int(number * 1000)} ms"
    return f"{fmt_score(number)} s"


def fmt_size(nbytes: object) -> str:
    """Ukuran berkas dalam satuan yang enak dibaca (3,9 MB)."""
    try:
        number = float(nbytes)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return "–"
    if number >= 1024**2:
        return f"{fmt_score(number / 1024**2, 1)} MB"
    if number >= 1024:
        return f"{fmt_int(number / 1024)} KB"
    return f"{fmt_int(number)} B"


def bar_width(value: object, maximum: object) -> str:
    """Lebar batang dalam persen, dijepit pada 0–100."""
    try:
        current = float(value)  # type: ignore[arg-type]
        ceiling = float(maximum)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return "0%"
    if ceiling <= 0:
        return "0%"
    pct = max(0.0, min(1.0, current / ceiling)) * 100
    return f"{pct:.1f}%".replace(".", ",")


def label_tahap(key: object) -> str:
    """Terjemahkan nama kunci tahap menjadi kalimat."""
    kunci = str(key)
    if kunci in STAGE_LABELS:
        return STAGE_LABELS[kunci]
    bersih = kunci.lstrip("0123456789_").replace("_", " ").strip()
    return bersih.capitalize() if bersih else kunci


def code(text: object) -> str:
    """Potongan teks monospasi untuk nama berkas atau kunci basis data."""
    return f"<code>{esc(text)}</code>"


# --------------------------------------------------------------------------- #
# Kerangka halaman
# --------------------------------------------------------------------------- #
def top_bar(
    *,
    title: str,
    subtitle: str,
    db_label: str,
    badge: str,
    run_label: str,
) -> str:
    """Bilah atas institusional: identitas berkas, status, nomor hasil."""
    return (
        '<header class="rra-topbar">'
        '<div class="rra-topbar-left">'
        f'<span class="rra-brand">{esc(title)}</span>'
        '<span class="rra-sep"></span>'
        f"<span>{esc(subtitle)}</span>"
        '<span class="rra-sep"></span>'
        f"<span>Arsip basis data: {code(db_label)}</span>"
        "</div>"
        '<div class="rra-topbar-right">'
        f'<span class="rra-chip">{esc(badge)}</span>'
        f"<span>{esc(run_label)}</span>"
        "</div>"
        "</header>"
    )


def alert(title: str, text: str, chip: str = "") -> str:
    """Peringatan berkotak amber: satu-satunya elemen berwarna di halaman."""
    chip_html = f'<span class="rra-alert-chip">{esc(chip)}</span>' if chip else ""
    return (
        '<div class="rra-alert" role="alert">'
        "<div>"
        f'<p class="rra-alert-title">{esc(title)}</p>'
        f'<p class="rra-alert-text">{text}</p>'
        "</div>"
        f"{chip_html}"
        "</div>"
    )


def report_head(title: str, lead: str, meta: Sequence[Mapping[str, str]]) -> str:
    """Judul, kalimat pengantar, dan baris keterangan sumber data."""
    meta_html = "".join(
        f"<div><dt>{esc(item['label'])}</dt><dd>{esc(item['value'])}</dd></div>"
        for item in meta
    )
    return (
        '<section class="rra-card">'
        '<header class="rra-head">'
        f"<h1>{esc(title)}</h1>"
        f'<p class="rra-lead">{lead}</p>'
        f'<dl class="rra-meta">{meta_html}</dl>'
        "</header>"
        "</section>"
    )


def figures(items: Sequence[Mapping[str, str]]) -> str:
    """Empat angka ringkas di dalam satu kartu, dipisahkan garis rambut."""
    cells = "".join(
        "<div>"
        f'<span class="rra-fig-value">{esc(item["value"])}</span>'
        f'<span class="rra-fig-label">{esc(item["label"])}</span>'
        "</div>"
        for item in items
    )
    return f'<section class="rra-card"><div class="rra-figures">{cells}</div></section>'


def section(
    number: int | str,
    title: str,
    note: str,
    body: str,
    *,
    sub: str = "",
    foot: str = "",
) -> str:
    """Kartu bagian bernomor; nomor dipakai karena urutannya bermakna."""
    nomor = str(number).zfill(2) if str(number).isdigit() else str(number)
    sub_html = f'<p class="rra-sec-sub">{esc(sub)}</p>' if sub else ""
    foot_html = f'<p class="rra-card-note">{foot}</p>' if foot else ""
    return (
        '<section class="rra-card">'
        '<div class="rra-sec-head">'
        f'<h2><span class="rra-sec-note">{esc(nomor)}</span>&nbsp;&nbsp;{esc(title)}</h2>'
        f'<p class="rra-sec-note">{esc(note)}</p>'
        "</div>"
        f"{sub_html}{body}{foot_html}"
        "</section>"
    )


def page_footer(text: str) -> str:
    return f'<footer class="rra-page-foot">{esc(text)}</footer>'


# --------------------------------------------------------------------------- #
# Bagian 01 — peringkat prioritas
# --------------------------------------------------------------------------- #
def priority_table(rows: Sequence[Mapping[str, Any]]) -> str:
    """Tabel peringkat dengan batang skor dan rincian komponen.

    ``rows`` memakai kunci dari basis data: ``rank``, ``label``,
    ``priority``, ``volume``, ``severity``, ``diversity``,
    ``n_negative``, ``n_total``.
    """
    if not rows:
        return _empty("Belum ada aspek yang dapat diperingkat.")

    top = max(float(row["priority"]) for row in rows) or 1.0
    body = []
    for row in rows:
        first = int(row["rank"]) == 1
        rincian = (
            f"volume {fmt_score(row['volume'])} · "
            f"keparahan {fmt_score(row['severity'])} · "
            f"keragaman {fmt_score(row['diversity'])}"
        )
        body.append(
            f'<tr class="{"is-first" if first else ""}">'
            f'<td class="rra-idx">{esc(row["rank"])}</td>'
            '<td class="rra-w-aspect">'
            f'<span class="rra-aspect">{esc(row["label"])}</span>'
            f'<span class="rra-sub">{rincian}</span>'
            "</td>"
            f'<td class="n rra-w-count">{fmt_int(row["n_negative"])}'
            f'<span class="rra-sub">dari {fmt_int(row.get("n_total", 0))}</span></td>'
            f'<td class="rra-w-score"><span class="rra-bar">'
            f'<i style="width:{bar_width(row["priority"], top)}"></i></span></td>'
            f'<td class="n rra-w-value rra-score">{fmt_score(row["priority"])}</td>'
            "</tr>"
        )
    return (
        '<table class="rra-table rra-rank">'
        "<thead><tr>"
        '<th class="rra-idx">#</th><th>Aspek layanan</th>'
        '<th class="n">Ulasan negatif</th><th>Skor prioritas</th>'
        '<th class="n">Nilai</th>'
        '</tr></thead><tbody>' + "".join(body) + "</tbody></table>"
    )


# --------------------------------------------------------------------------- #
# Bagian 02 — frasa keluhan
# --------------------------------------------------------------------------- #
def phrase_grid(groups: Iterable[Mapping[str, Any]]) -> str:
    """Frasa keluhan dominan per aspek, dua kolom; blok terakhir melebar."""
    daftar = list(groups)
    if not daftar:
        return _empty("Belum ada frasa keluhan yang dapat ditampilkan.")

    blocks = []
    for posisi, group in enumerate(daftar):
        pertama = bool(group.get("is_first"))
        terakhir_tunggal = len(daftar) % 2 == 1 and posisi == len(daftar) - 1
        items = list(group.get("phrases") or [])
        if items:
            puncak = max(int(item["frequency"]) for item in items) or 1
            isi = "".join(
                '<div class="rra-ph-item">'
                '<div class="rra-ph-line">'
                f'<span class="t">{esc(item["phrase"])}</span>'
                f'<span class="n">{fmt_int(item["frequency"])}</span>'
                "</div>"
                '<span class="rra-ph-track">'
                f'<i style="width:{bar_width(item["frequency"], puncak)}"></i></span>'
                "</div>"
                for item in items
            )
        else:
            isi = '<p class="rra-ph-empty">Tidak ada frasa yang lolos ambang.</p>'

        kelas = "rra-ph"
        if terakhir_tunggal:
            kelas += " wide"
        if pertama:
            kelas += " is-first"
        blocks.append(
            f'<div class="{kelas}">'
            '<div class="rra-ph-head">'
            f"<h3>{esc(group['label'])}</h3>"
            f'<span class="{"is-first" if pertama else ""}">'
            f"{fmt_int(group.get('n_negative', 0))} ulasan negatif</span>"
            "</div>"
            f'<div class="rra-ph-items">{isi}</div>'
            "</div>"
        )
    return f'<div class="rra-phrases">{"".join(blocks)}</div>'


# --------------------------------------------------------------------------- #
# Bagian 03 — tindakan
# --------------------------------------------------------------------------- #
def action_table(rows: Sequence[Mapping[str, Any]]) -> str:
    """Tabel pemicu → tindakan; isinya berasal dari aturan kualitas layanan."""
    if not rows:
        return _empty("Belum ada rekomendasi tindakan.")
    body = "".join(
        f'<tr class="{"is-first" if posisi == 0 else ""}">'
        f"<td>{esc(row.get('aspect_label', row.get('aspect', '')))}</td>"
        f"<td>{esc(row.get('phrase', ''))}</td>"
        f"<td>{esc(row.get('action', ''))}</td>"
        "</tr>"
        for posisi, row in enumerate(rows)
    )
    return (
        '<table class="rra-table rra-actions">'
        "<thead><tr><th>Aspek</th><th>Frasa pemicu</th>"
        "<th>Tindakan yang disarankan</th></tr></thead>"
        f"<tbody>{body}</tbody></table>"
    )


# --------------------------------------------------------------------------- #
# Bagian 04 — bahan audit
# --------------------------------------------------------------------------- #
def audit_panel(
    *,
    weights: Mapping[str, float],
    timings: Mapping[str, float],
    lines: Sequence[str],
    footer_left: str = "",
    footer_right: str = "",
    total_label: str = "Total durasi komputasi",
) -> str:
    """Rumus skor, bobot, waktu per tahap, dan baris penelusuran."""
    bobot = (
        '<div class="rra-weights">'
        f"<div><span>volume (w₁)</span><b>{fmt_score(weights.get('volume', 0))}</b></div>"
        f"<div><span>keparahan (w₂)</span><b>{fmt_score(weights.get('severity', 0))}</b></div>"
        f"<div><span>keragaman (w₃)</span><b>{fmt_score(weights.get('diversity', 0))}</b></div>"
        "</div>"
    )
    rumus = (
        '<div class="rra-formula">'
        '<p class="rra-label">Formula skor</p>'
        '<span class="rra-eq">skor = w₁·volume + w₂·keparahan + w₃·keragaman</span>'
        f"{bobot}"
        "</div>"
    )

    baris_waktu = []
    total = None
    for kunci, nilai in timings.items():
        if str(kunci) == "total":
            total = nilai
            continue
        baris_waktu.append(
            f"<tr><td>{esc(label_tahap(kunci))}</td>"
            f"<td>{fmt_seconds(nilai)}</td></tr>"
        )
    if total is not None:
        baris_waktu.append(
            '<tr class="total"><td>' + esc(total_label) + "</td>"
            f"<td>{fmt_seconds(total)}</td></tr>"
        )
    waktu = (
        '<p class="rra-block-title">Waktu proses per tahap</p>'
        f'<table class="rra-timings">{"".join(baris_waktu)}</table>'
        if baris_waktu
        else ""
    )

    penelusuran = "".join(
        f'<li><span class="dot">•</span><span>{line}</span></li>' for line in lines
    )
    kaki = ""
    if footer_left or footer_right:
        kaki = (
            '<div class="rra-trace-foot">'
            f"<span>{footer_left}</span><span>{footer_right}</span></div>"
        )

    return (
        '<div class="rra-audit">'
        f'<div class="rra-audit-left">{rumus}{waktu}</div>'
        '<div class="rra-trace">'
        "<div>"
        "<h3>Penelusuran peringkat</h3>"
        f"<ul>{penelusuran}</ul>"
        "</div>"
        f"{kaki}"
        "</div>"
        "</div>"
    )


# --------------------------------------------------------------------------- #
# Bilah samping
# --------------------------------------------------------------------------- #
def sidebar_head(title: str, caption: str) -> str:
    return (
        f'<p class="rra-side-title">{esc(title)}</p>'
        f'<p class="rra-side-caption">{esc(caption)}</p>'
    )


def sidebar_status(items: Sequence[Mapping[str, Any]]) -> str:
    """Blok status sistem: label tenang, nilai rata kanan."""
    baris = []
    for item in items:
        kelas = []
        if item.get("mono"):
            kelas.append("mono")
        if item.get("accent"):
            kelas.append("accent")
        attr = f' class="{" ".join(kelas)}"' if kelas else ""
        baris.append(
            f"<tr{attr}><td>{esc(item['label'])}</td>"
            f"<td>{esc(item['value'])}</td></tr>"
        )
    return (
        '<div class="rra-side-block">'
        '<p class="rra-label">Status sistem saat ini</p>'
        f'<table class="rra-kv">{"".join(baris)}</table>'
        "</div>"
    )


def sidebar_inset(title: str, text: str, quote: str = "") -> str:
    kutipan = f"<q>{esc(quote)}</q>" if quote else ""
    return (
        '<div class="rra-side-block">'
        '<div class="rra-side-inset">'
        f"<b>{esc(title)}</b>{esc(text)}{kutipan}"
        "</div></div>"
    )


def sidebar_foot(line1: str, line2: str) -> str:
    return f'<div class="rra-side-foot"><b>{esc(line1)}</b>{esc(line2)}</div>'


# --------------------------------------------------------------------------- #
# Keadaan kosong
# --------------------------------------------------------------------------- #
def _empty(message: str) -> str:
    return f'<p class="rra-note">{esc(message)}</p>'


def empty_card(title: str, text: str) -> str:
    """Kartu arahan saat belum ada hasil analisis sama sekali."""
    return (
        '<section class="rra-card">'
        '<div class="rra-sec-head"><h2>'
        f'<span class="rra-sec-note">00</span>&nbsp;&nbsp;{esc(title)}</h2></div>'
        f'<p class="rra-ph-empty">{esc(text)}</p>'
        "</section>"
    )


def note(message: str) -> str:
    """Catatan kaki bergaya kutipan di dalam kartu."""
    return f'<p class="rra-card-note">{message}</p>'
