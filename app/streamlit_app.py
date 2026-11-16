"""LAPISAN 5 — Antarmuka laporan prioritas perbaikan layanan.

Berkas ini hanya menyusun halaman. Ia tidak menghitung skor, tidak
melatih model, dan tidak membentuk HTML sendiri: perhitungan ada di
Lapisan 3–5 (``src/rra``), bentuk tampilan ada di ``app/components.py``,
dan seluruh angka dibaca dari basis data hasil (``rra.sqlite``).

Susunan halaman mengikuti draf desain Google Stitch:

    bilah atas → kepala laporan →
    angka ringkas → 01 peringkat → 02 frasa → 03 tindakan → 04 audit

Pipeline hanya dijalankan ketika pengguna menekan tombol hitung ulang;
memilih komponen model tidak memicu pelatihan.
"""

from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
ROOT = APP_DIR.parent
for candidate in (str(ROOT / "src"), str(APP_DIR)):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

import streamlit as st  # noqa: E402

import components as ui  # noqa: E402
import theme  # noqa: E402
from rra.config import Config  # noqa: E402
from rra.contracts import ASPECT_LABELS  # noqa: E402
from rra.storage.repository import ResultRepository  # noqa: E402

BULAN = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Mei", 6: "Jun",
    7: "Jul", 8: "Agu", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Des",
}

DEFAULT_MODEL = "svm"
JUDUL = "Prioritas perbaikan layanan"
NAMA_MODEL = {"svm": "Support Vector Machine (linear)", "nb": "Naive Bayes (arsip)"}


def waktu_indonesia(iso_text: str | None) -> str:
    """Ubah cap waktu ISO menjadi bentuk ringkas berwaktu lokal."""
    if not iso_text:
        return "–"
    try:
        stamp = datetime.fromisoformat(str(iso_text))
    except (TypeError, ValueError):
        return str(iso_text)
    local = stamp.astimezone()
    return (
        f"{local.day} {BULAN.get(local.month, local.month)} {local.year}, "
        f"{local.hour:02d}.{local.minute:02d}"
    )


def versi_komputasi(akar: Path = ROOT) -> str:
    """Baca nomor versi dari ``pyproject.toml`` agar tidak pernah menyimpang."""
    try:
        teks = (akar / "pyproject.toml").read_text(encoding="utf-8")
    except OSError:
        return "v–"
    cocok = re.search(r'^version\s*=\s*"([^"]+)"', teks, re.MULTILINE)
    return f"v{cocok.group(1)}" if cocok else "v–"


def keterangan_model(config: dict) -> str:
    """Kalimat singkat tentang komponen model, dirakit dari konfigurasi hasil."""
    blok = dict(config.get("model") or {})
    tfidf = dict(blok.get("tfidf") or {})
    nama = NAMA_MODEL.get(str(blok.get("name")), str(blok.get("name") or "–").upper())
    gram_mentah = list(tfidf.get("ngram_range") or (1, 1))
    gram = (
        int(gram_mentah[0]) if gram_mentah else 1,
        int(gram_mentah[-1]) if gram_mentah else 1,
    )
    bentuk = {(1, 1): "unigram", (1, 2): "unigram dan bigram"}.get(
        gram, f"n-gram {gram[0]}–{gram[1]}"
    )
    bagian = [f"{nama} dengan fitur TF-IDF {bentuk}"]
    if tfidf.get("max_features"):
        bagian.append(f"maks {ui.fmt_int(tfidf['max_features'])} fitur")
    if tfidf.get("min_df"):
        bagian.append(f"min_df {tfidf['min_df']}")
    if blok.get("aspect_threshold") is not None:
        bagian.append(f"ambang aspek {ui.fmt_score(blok['aspect_threshold'])}")
    return ", ".join(bagian) + "."


# --------------------------------------------------------------------------- #
# Akses data dan pipeline
# --------------------------------------------------------------------------- #
def buka_gudang(cfg: Config) -> ResultRepository:
    return ResultRepository(cfg.path("paths.db_path"))


def jalankan_analisis(cfg: Config, model_key: str) -> int:
    """Latih model terpilih, simpan hasilnya, kembalikan nomor hasil."""
    from rra.decision.severity import severity_map  # noqa: PLC0415
    from rra.pipeline import Pipeline  # noqa: PLC0415

    varian = Config.load(root=ROOT, sets={"model.name": model_key})
    pipeline = Pipeline(varian)
    keluaran = pipeline.run()
    if keluaran.decision is None:  # jaga-jaga: pipeline tanpa modul keputusan
        raise RuntimeError("Pipeline tidak menghasilkan modul keputusan.")

    gudang = buka_gudang(varian)
    ulasan = pipeline.load_reviews()
    run_id = gudang.save_run(
        model_name=keluaran.model_name,
        decision=keluaran.decision,
        severities=severity_map(ulasan),
        reviews=ulasan,
        timings=keluaran.timings,
        config=varian.as_dict(),
    )
    gudang.save_predictions(run_id, keluaran.predictions)
    return run_id


# --------------------------------------------------------------------------- #
# Penyusun potongan data
# --------------------------------------------------------------------------- #
def susun_kalimat_utama(prioritas: list[dict], n_ulasan: int) -> str:
    if not prioritas:
        return "Belum ada hasil analisis yang dapat ditampilkan."
    teratas = prioritas[0]
    return (
        f"Sistem menilai {ui.esc(ui.fmt_int(len(prioritas)))} aspek layanan dari "
        f"{ui.esc(ui.fmt_int(n_ulasan))} ulasan, lalu menyusun urutan perbaikan. "
        "Peringkat pertama adalah "
        f"<strong>{ui.esc(teratas['label'])}</strong> dengan skor "
        f"<strong>{ui.esc(ui.fmt_priority(teratas['priority']))}</strong>, dipicu "
        f"<strong>{ui.esc(ui.fmt_int(teratas['n_negative']))}</strong> ulasan negatif."
    )


def kelompokkan_frasa(
    prioritas: list[dict], frasa: list[dict], batas: int = 3
) -> list[dict]:
    """Ambil frasa teratas tiap aspek, diurutkan mengikuti peringkat aspek."""
    per_aspek: dict[str, list[dict]] = {}
    for baris in frasa:
        per_aspek.setdefault(str(baris["aspect"]), []).append(baris)

    hasil = []
    for posisi, baris in enumerate(prioritas):
        aspek = str(baris["aspect"])
        butir = sorted(per_aspek.get(aspek, []), key=lambda x: int(x["rank"]))[:batas]
        hasil.append(
            {
                "label": baris["label"],
                "n_negative": baris["n_negative"],
                "is_first": posisi == 0,
                "phrases": butir,
            }
        )
    return hasil


def baris_tindakan(prioritas: list[dict], rekomendasi: list[dict]) -> list[dict]:
    urutan = {str(item["aspect"]): int(item["rank"]) for item in prioritas}
    baris = [
        {**item, "aspect_label": ASPECT_LABELS.get(str(item["aspect"]), item["aspect"])}
        for item in rekomendasi
    ]
    return sorted(baris, key=lambda item: urutan.get(str(item["aspect"]), 99))


def ukuran_basis_data(cfg: Config) -> tuple[str, str]:
    """Nama dan ukuran berkas basis data, untuk kepala dan kaki laporan."""
    jalur = cfg.path("paths.db_path")
    nama = Path(jalur).name
    try:
        ukuran = ui.fmt_size(Path(jalur).stat().st_size)
    except OSError:
        ukuran = "–"
    return nama, ukuran


# --------------------------------------------------------------------------- #
# Bilah samping
# --------------------------------------------------------------------------- #
def bilah_samping(cfg: Config, run: dict | None, nama_db: str, ukuran_db: str) -> None:
    """Kendali analisis. Penelitian memakai satu komponen model (SVM linear)."""
    config = (run or {}).get("config") or cfg.as_dict()

    with st.sidebar:
        st.markdown(
            ui.sidebar_head(
                "Pengaturan analisis",
                "Komponen model dan panel pemeriksaan laporan operasional.",
            ),
            unsafe_allow_html=True,
        )
        st.caption(keterangan_model(config))

        st.text_input(
            "Sumber masukan",
            value=f"{cfg.get('paths.reviews_file')} (data contoh)",
            disabled=True,
        )

        if st.button("Hitung ulang analisis", type="primary"):
            with st.spinner("Melatih model dan menyusun prioritas…"):
                try:
                    nomor = jalankan_analisis(cfg, DEFAULT_MODEL)
                except Exception as galat:  # noqa: BLE001 - pesan untuk pengguna
                    st.error(f"Analisis gagal dijalankan: {galat}")
                else:
                    st.session_state["pesan"] = (
                        f"Analisis selesai dan tersimpan sebagai hasil nomor {nomor}."
                    )
                    st.rerun()

        total = (run or {}).get("timings") or {}
        st.caption(
            f"Waktu komputasi hasil terakhir: {ui.fmt_seconds(total.get('total'))}."
            if run
            else "Belum ada hasil tersimpan pada basis data ini."
        )

        if run:
            st.markdown(
                ui.sidebar_status(
                    [
                        {"label": "Basis data", "value": f"{nama_db} ({ukuran_db})", "mono": True},
                        {"label": "Hasil terakhir", "value": f"Nomor {run['run_id']}"},
                        {"label": "Model hasil ini",
                         "value": NAMA_MODEL.get(str(run["model_name"]),
                                                 str(run["model_name"]).upper()),
                         "accent": True},
                        {"label": "Ulasan diproses",
                         "value": f"{ui.fmt_int(run['n_reviews'])} entri"},
                        {"label": "Dibuat", "value": waktu_indonesia(run.get("created_at"))},
                    ]
                ),
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                ui.sidebar_inset(
                    "Status tanpa data:",
                    "Basis data belum memuat hasil komputasi. Antarmuka tidak "
                    "menghitung angka sendiri — ia menunggu pipeline menulis "
                    "barisnya lebih dahulu.",
                    quote="Belum ada hasil analisis. Tekan Hitung ulang analisis "
                    "untuk memulai.",
                ),
                unsafe_allow_html=True,
            )

        st.markdown(
            ui.sidebar_foot(
                "Sidang skripsi S1 Teknik Informatika",
                f"Versi komputasi {versi_komputasi()}",
            ),
            unsafe_allow_html=True,
        )


# --------------------------------------------------------------------------- #
# Halaman
# --------------------------------------------------------------------------- #
def main() -> None:
    st.set_page_config(
        page_title=JUDUL,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(theme.CSS, unsafe_allow_html=True)

    cfg = Config.load(root=ROOT)
    gudang = buka_gudang(cfg)
    run_id = gudang.latest_run_id()
    run = gudang.load_run(run_id) if run_id is not None else None
    nama_db, ukuran_db = ukuran_basis_data(cfg)

    bilah_samping(cfg, run, nama_db, ukuran_db)

    if st.session_state.get("pesan"):
        st.toast(st.session_state.pop("pesan"))

    st.markdown(
        ui.top_bar(
            title="RRA · Restaurant Review Analytics",
            subtitle="Tugas akhir sarjana informatika",
            db_label=nama_db,
            badge="Hasil tersimpan" if run else "Belum ada hasil",
            run_label=f"Hasil nomor {run['run_id']}" if run else "Basis data kosong",
        ),
        unsafe_allow_html=True,
    )

    if run is None:
        st.markdown(
            ui.report_head(
                JUDUL,
                "Belum ada hasil analisis pada basis data ini. Sistem tidak "
                "menampilkan angka perkiraan: seluruh isi laporan berasal dari "
                "baris hasil yang ditulis pipeline.",
                [
                    {"label": "Sumber data", "value": "Ulasan pelanggan (data contoh)"},
                    {"label": "Basis data", "value": nama_db},
                    {"label": "Hasil nomor", "value": "–"},
                    {"label": "Waktu analisis", "value": "–"},
                ],
            ),
            unsafe_allow_html=True,
        )
        st.markdown(
            ui.empty_card(
                "Belum ada hasil analisis",
                "Buka bilah kiri, pilih komponen model, lalu tekan Hitung ulang "
                "analisis. Sistem memuat ulasan, melatih komponen model, "
                "menghitung skor prioritas, dan menyimpan hasilnya ke basis data "
                "sebelum halaman ini menampilkan apa pun.",
            ),
            unsafe_allow_html=True,
        )
        st.markdown(ui.page_footer(
            "Laporan keputusan operasional · Tugas akhir software engineering: "
            "restaurant review analytics"
        ), unsafe_allow_html=True)
        return

    prioritas = gudang.load_priorities(run_id)
    frasa = gudang.load_phrases(run_id)
    rekomendasi = gudang.load_recommendations(run_id)

    bobot = run.get("weights") or {}
    waktu = run.get("timings") or {}
    teratas = prioritas[0] if prioritas else {}

    st.markdown(
        ui.report_head(
            JUDUL,
            susun_kalimat_utama(prioritas, run["n_reviews"]),
            [
                {"label": "Sumber data", "value": "Ulasan pelanggan (data contoh)"},
                {"label": "Komponen model", "value": str(run["model_name"]).upper()},
                {"label": "Hasil nomor", "value": str(run["run_id"])},
                {"label": "Waktu analisis", "value": waktu_indonesia(run["created_at"])},
            ],
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        ui.figures(
            [
                {"value": ui.fmt_int(run["n_reviews"]), "label": "Ulasan dianalisis"},
                {"value": ui.fmt_int(len(prioritas)), "label": "Aspek diperingkat"},
                {
                    "value": ui.fmt_int(teratas.get("n_negative", 0)),
                    "label": "Ulasan negatif pada "
                    + str(teratas.get("label", "–")).lower(),
                },
                {"value": ui.fmt_seconds(waktu.get("total")), "label": "Waktu komputasi"},
            ]
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        ui.section(
            1,
            "Peringkat prioritas",
            "Rentang skor 0–100 · makin tinggi makin mendesak",
            ui.priority_table(prioritas),
            foot=(
                "Skor bukan nilai kepuasan pelanggan, melainkan tingkat urgensi "
                "perbaikan: gabungan volume keluhan (w₁="
                f"{ui.esc(ui.fmt_score(bobot.get('volume', 0)))}), keparahan "
                f"(w₂={ui.esc(ui.fmt_score(bobot.get('severity', 0)))}), dan keragaman "
                f"frasa (w₃={ui.esc(ui.fmt_score(bobot.get('diversity', 0)))}). "
                "Bobot diambil dari hasil terakhir, bukan dari halaman ini."
            ),
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        ui.section(
            2,
            "Frasa keluhan dominan",
            "Tiga frasa teratas per aspek",
            ui.phrase_grid(kelompokkan_frasa(prioritas, frasa)),
            sub=(
                "Ekstraksi n-gram frasa pemicu sentimen negatif pada masing-masing "
                "aspek layanan, diurutkan menurut frekuensi kemunculan."
            ),
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        ui.section(
            3,
            "Tindakan yang disarankan",
            "Aturan kualitas layanan restoran",
            ui.action_table(baris_tindakan(prioritas, rekomendasi)),
            foot=(
                "Tindakan berasal dari aturan baku kualitas layanan restoran, bukan "
                "hasil prediksi model. Ia menunjukkan arah perbaikan, bukan jaminan "
                "hasil."
            ),
        ),
        unsafe_allow_html=True,
    )

    nama_berkas_masukan = str(cfg.get("paths.reviews_file"))
    st.markdown(
        ui.section(
            4,
            "Bahan audit",
            "Spesifikasi matematis dan penelusuran status komputasi",
            ui.audit_panel(
                weights=bobot,
                timings=waktu,
                lines=[
                    f"Hasil nomor {run['run_id']} tersimpan pada "
                    f"{ui.code(nama_db)}, tabel {ui.code('runs')}, baris "
                    f"{ui.code('run_id ' + str(run['run_id']))}.",
                    "Komponen model: "
                    f"<strong>{ui.esc(str(run['model_name']).upper())}</strong> — "
                    f"{ui.esc(keterangan_model(run.get('config') or {}))}",
                    f"Korpus masukan: {ui.fmt_int(run['n_reviews'])} ulasan dari "
                    f"{ui.code(nama_berkas_masukan)} (data contoh), "
                    f"{ui.fmt_int(len(prioritas))} aspek layanan.",
                    "Bobot w₁/w₂/w₃ = "
                    f"{ui.fmt_score(bobot.get('volume', 0))} / "
                    f"{ui.fmt_score(bobot.get('severity', 0))} / "
                    f"{ui.fmt_score(bobot.get('diversity', 0))}, tersimpan pada kolom "
                    f"{ui.code('weights_json')}.",
                    f"Waktu total {ui.fmt_seconds(waktu.get('total'))}; rincian tiap "
                    f"tahap pada kolom {ui.code('timings_json')}.",
                ],
                footer_left=f"Berkas: {ui.esc(nama_db)} · {ui.esc(ukuran_db)}",
                footer_right=f"Dibuat: {ui.esc(waktu_indonesia(run.get('created_at')))}",
                total_label=f"Total durasi hasil nomor {run['run_id']}",
            ),
            foot=(
                "Seluruh angka pada laporan ini dibaca dari baris basis data di atas. "
                "Antarmuka tidak menghitung ulang skor, sehingga angka pada layar dan "
                "angka pada arsip tidak dapat menyimpang."
            ),
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        ui.page_footer(
            "Laporan keputusan operasional · Tugas akhir software engineering: "
            "restaurant review analytics · Arsip hasil: " + nama_db
        ),
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
