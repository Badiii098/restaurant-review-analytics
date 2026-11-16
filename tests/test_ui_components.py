"""Uji komponen tampilan (Lapisan 5) — tanpa menyalakan server.

Yang diuji bukan "tampilannya bagus", melainkan janji-janji yang bisa
salah tanpa terlihat: angka diformat konsisten, teks data di-escape,
baris peringkat pertama ditandai tepat satu, dan blok frasa terakhir
melebar hanya ketika jumlahnya ganjil.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for candidate in (str(ROOT / "src"), str(ROOT / "app")):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

import components as ui  # noqa: E402
import theme  # noqa: E402


# --------------------------------------------------------------------------- #
# Pemformatan
# --------------------------------------------------------------------------- #
def test_fmt_int_memakai_pemisah_ribuan_indonesia():
    assert ui.fmt_int(2000) == "2.000"
    assert ui.fmt_int(714) == "714"
    assert ui.fmt_int("bukan angka") == "–"


def test_fmt_score_memakai_koma_desimal():
    assert ui.fmt_score(0.8216) == "0,82"
    assert ui.fmt_score(0.4, 1) == "0,4"


def test_fmt_priority_memakai_skala_0_100():
    assert ui.fmt_priority(0.8151) == "81,5"
    assert ui.fmt_priority(0) == "0,0"
    assert ui.fmt_priority(1) == "100,0"
    assert ui.fmt_priority(None) == "–"


def test_fmt_seconds_memilih_satuan_yang_terbaca():
    assert ui.fmt_seconds(1.9022) == "1,90 s"
    assert ui.fmt_seconds(0.0189) == "19 ms"
    assert ui.fmt_seconds(0.0031) == "3,1 ms"
    assert ui.fmt_seconds(None) == "–"


def test_fmt_size():
    assert ui.fmt_size(4_042_752) == "3,9 MB"


def test_bar_width_dijepit_dan_nol_aman():
    assert ui.bar_width(1.0, 1.0) == "100,0%"
    assert ui.bar_width(0.4639, 0.8216) == "56,5%"
    assert ui.bar_width(5, 0) == "0%"


def test_label_tahap_dikenal_dan_tidak_dikenal():
    assert ui.label_tahap("05_klasifikasi") == "Klasifikasi aspek dan sentimen (TF-IDF)"
    assert ui.label_tahap("07_evaluasi_model") == "Evaluasi model"


# --------------------------------------------------------------------------- #
# Kerangka
# --------------------------------------------------------------------------- #
def test_top_bar_memuat_identitas_status_dan_nomor_hasil():
    html = ui.top_bar(
        title="RRA · Restaurant Review Analytics",
        subtitle="Tugas akhir sarjana informatika",
        db_label="rra.sqlite",
        badge="Hasil tersimpan",
        run_label="Hasil nomor 22",
    )
    assert "Restaurant Review Analytics" in html
    assert "Arsip basis data: <code>rra.sqlite</code>" in html
    assert "Hasil tersimpan" in html
    assert "Hasil nomor 22" in html


def test_alert_menjaga_markup_penekanan_tetapi_meng_escape_judul():
    html = ui.alert("Keselarasan <model>", "Teks <strong>tebal</strong>.", "Konsistensi #22")
    assert "Keselarasan &lt;model&gt;" in html
    assert "<strong>tebal</strong>" in html
    assert "Konsistensi #22" in html


def test_report_head_menyusun_empat_keterangan():
    html = ui.report_head(
        "Prioritas perbaikan layanan",
        "Kalimat <strong>utama</strong>.",
        [
            {"label": "Sumber data", "value": "Ulasan pelanggan (data contoh)"},
            {"label": "Komponen model", "value": "SVM"},
            {"label": "Hasil nomor", "value": "22"},
            {"label": "Waktu analisis", "value": "19 Okt 2026, 21.24"},
        ],
    )
    assert html.count("<dt>") == 4
    assert "<strong>utama</strong>" in html
    assert "19 Okt 2026, 21.24" in html


def test_figures_dan_section_memberi_nomor_dua_digit():
    html = ui.section(1, "Peringkat prioritas", "catatan", "<p>x</p>", foot="kaki")
    assert "01" in html
    assert "Peringkat prioritas" in html
    assert "kaki" in html
    angka = ui.figures([{"value": "2.000", "label": "Ulasan dianalisis"}])
    assert "rra-fig-value" in angka and "2.000" in angka


# --------------------------------------------------------------------------- #
# Bagian 01
# --------------------------------------------------------------------------- #
BARIS = [
    {
        "rank": 1,
        "aspect": "pelayanan",
        "label": "Pelayanan",
        "priority": 0.8216,
        "volume": 1.0,
        "severity": 0.5541,
        "diversity": 1.0,
        "n_negative": 714,
        "n_total": 1000,
    },
    {
        "rank": 2,
        "aspect": "makanan",
        "label": "Makanan <pedas>",
        "priority": 0.4639,
        "volume": 0.5,
        "severity": 0.4,
        "diversity": 0.4,
        "n_negative": 320,
        "n_total": 1000,
    },
]


def test_priority_table_menandai_tepat_satu_baris_dan_meng_escape_label():
    html = ui.priority_table(BARIS)
    assert html.count('class="is-first"') == 1
    assert "Makanan &lt;pedas&gt;" in html
    assert "dari 1.000" in html
    assert "volume 1,00 · keparahan 0,55 · keragaman 1,00" in html
    assert 'style="width:100,0%"' in html
    assert ">82,2<" in html  # skor ditampilkan pada skala 0–100


def test_priority_table_kosong_memberi_pesan():
    assert "Belum ada aspek" in ui.priority_table([])


# --------------------------------------------------------------------------- #
# Bagian 02
# --------------------------------------------------------------------------- #
def _grup(label, frasa, negatif, pertama=False):
    return {
        "label": label,
        "n_negative": negatif,
        "is_first": pertama,
        "phrases": [
            {"phrase": teks, "frequency": jumlah, "rank": posisi + 1}
            for posisi, (teks, jumlah) in enumerate(frasa)
        ],
    }


def test_phrase_grid_melebarkan_blok_terakhir_bila_ganjil():
    html = ui.phrase_grid(
        [
            _grup("Pelayanan", [("lambat", 295)], 714, True),
            _grup("Makanan", [("dingin", 120)], 320),
            _grup("Fasilitas", [("sempit", 54)], 66),
        ]
    )
    assert html.count('class="rra-ph wide"') == 1
    assert html.count('class="rra-ph is-first"') == 1 or "rra-ph is-first" in html
    assert "295" in html


def test_phrase_grid_genap_tidak_melebarkan_blok():
    html = ui.phrase_grid(
        [_grup("Pelayanan", [("lambat", 295)], 714), _grup("Makanan", [("dingin", 120)], 320)]
    )
    assert "wide" not in html


def test_phrase_grid_menangani_aspek_tanpa_frasa():
    html = ui.phrase_grid([_grup("Harga", [], 12)])
    assert "Tidak ada frasa yang lolos ambang." in html


# --------------------------------------------------------------------------- #
# Bagian 03
# --------------------------------------------------------------------------- #
def test_action_table_menandai_baris_pertama_dan_meng_escape():
    html = ui.action_table(
        [
            {"aspect_label": "Pelayanan", "phrase": "lambat", "action": "Tambah <kasir>"},
            {"aspect_label": "Makanan", "phrase": "dingin", "action": "Cek suhu"},
        ]
    )
    assert html.count('class="is-first"') == 1
    assert "Tambah &lt;kasir&gt;" in html


def test_action_table_kosong_memberi_pesan():
    assert "Belum ada rekomendasi" in ui.action_table([])


# --------------------------------------------------------------------------- #
# Bagian 04
# --------------------------------------------------------------------------- #
def test_audit_panel_menyusun_rumus_bobot_waktu_dan_penelusuran():
    html = ui.audit_panel(
        weights={"volume": 0.4, "severity": 0.4, "diversity": 0.2},
        timings={"01_muat_data": 0.1205, "total": 1.9022},
        lines=["Hasil nomor 22 tersimpan."],
        footer_left="Berkas: rra.sqlite · 3,9 MB",
        footer_right="Dibuat: 19 Okt 2026, 21.24",
        total_label="Total durasi hasil nomor 22",
    )
    assert "w₁·volume" in html
    assert "0,40" in html and "0,20" in html
    assert "Memuat berkas ulasan" in html
    assert "120 ms" in html
    assert "Total durasi hasil nomor 22" in html
    assert "1,90 s" in html
    assert "Hasil nomor 22 tersimpan." in html


def test_audit_panel_tanpa_waktu_tidak_mencetak_tabel_kosong():
    html = ui.audit_panel(weights={}, timings={}, lines=[])
    assert "Waktu proses per tahap" not in html


# --------------------------------------------------------------------------- #
# Bilah samping
# --------------------------------------------------------------------------- #
def test_sidebar_status_memberi_kelas_mono_dan_accent():
    html = ui.sidebar_status(
        [
            {"label": "Basis data", "value": "rra.sqlite (3,9 MB)", "mono": True},
            {"label": "Model hasil ini", "value": "SVM", "accent": True},
            {"label": "Ulasan diproses", "value": "2.000 entri"},
        ]
    )
    assert 'class="mono"' in html
    assert 'class="accent"' in html
    assert "2.000 entri" in html


def test_sidebar_inset_dan_foot():
    html = ui.sidebar_inset("Status tanpa data:", "Penjelasan.", quote="Belum ada hasil.")
    assert "<q>Belum ada hasil.</q>" in html
    kaki = ui.sidebar_foot("Sidang skripsi S1 Teknik Informatika", "Versi komputasi v1.0.0")
    assert "v1.0.0" in kaki


def test_empty_card_memakai_nomor_nol():
    html = ui.empty_card("Belum ada hasil analisis", "Tekan Hitung ulang analisis.")
    assert "00" in html
    assert "Tekan Hitung ulang analisis." in html


# --------------------------------------------------------------------------- #
# Tema
# --------------------------------------------------------------------------- #
def test_tema_memuat_token_dan_tanpa_gradien():
    assert "var(--rra-accent)" in theme.CSS
    assert theme.PALETTE["accent"] in theme.CSS
    assert "gradient" not in theme.CSS
    assert "box-shadow: 0 1px" not in theme.CSS
    assert "--rra-topbar" in theme.CSS


def test_kontras_teks_sekunder_lolos_aa():
    def luminance(hex_color: str) -> float:
        komponen = [
            int(hex_color.lstrip("#")[i : i + 2], 16) / 255 for i in (0, 2, 4)
        ]
        linear = [
            c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
            for c in komponen
        ]
        return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

    def rasio(a: str, b: str) -> float:
        terang, gelap = sorted((luminance(a), luminance(b)), reverse=True)
        return (terang + 0.05) / (gelap + 0.05)

    for latar in (theme.PALETTE["canvas"], theme.PALETTE["surface"]):
        assert rasio(theme.PALETTE["secondary"], latar) >= 4.5
        assert rasio(theme.PALETTE["ink"], latar) >= 7.0
    assert rasio(theme.PALETTE["accent"], theme.PALETTE["accent_tint"]) >= 4.5
