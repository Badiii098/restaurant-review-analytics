"""LAPISAN 5 — Antarmuka pengguna berbasis Streamlit.

Antarmuka ini sengaja tipis: seluruh perhitungan berada pada lapisan di
bawahnya. Peran berkas ini hanya menampilkan keluaran Lapisan 4 dan
menyediakan pemilih komponen model.

Pemilih komponen model pada bilah samping bukan hiasan. Ia adalah
perwujudan kebaruan penelitian di hadapan pengguna: mengganti algoritma
cukup dengan memilih dari daftar, dan seluruh alur di bawahnya berjalan
tanpa perubahan kode.

Jalankan dengan::

    streamlit run app/streamlit_app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from rra.config import Config  # noqa: E402
from rra.decision.rules import rules_for  # noqa: E402
from rra.models.registry import available_models  # noqa: E402
from rra.pipeline import Pipeline, PipelineError  # noqa: E402

st.set_page_config(page_title="Analitik Ulasan Restoran", page_icon="🍽️", layout="wide")


# --------------------------------------------------------------------------- #
# Pemuat hasil (dengan singgahan agar tidak melatih ulang setiap kali klik)
# --------------------------------------------------------------------------- #
@st.cache_resource(show_spinner="Menjalankan alur analisis…")
def run_analysis(model_name: str, cache_key: int):
    cfg = Config.load(root=ROOT)
    cfg._data["model"]["name"] = model_name
    pipeline = Pipeline(cfg)
    output = pipeline.run()
    return {
        "model": output.model_name,
        "n_reviews": output.n_reviews,
        "timings": output.timings,
        "data_quality": output.data_quality,
        "priorities": pipeline.priorities_frame(output),
        "phrases": pipeline.phrases_frame(output),
        "predictions": pipeline.predictions_frame(output),
        "decision": output.decision,
    }


def main() -> None:
    st.title("Sistem Analitik Ulasan Pelanggan Restoran")
    st.caption(
        "Aspect-Based Sentiment Analysis dengan ekstraksi frasa keluhan dominan "
        "untuk rekomendasi prioritas perbaikan layanan."
    )

    models = available_models()

    with st.sidebar:
        st.header("Komponen model")
        chosen = st.selectbox(
            "Algoritma",
            options=list(models),
            format_func=lambda key: f"{models[key]} ({key})",
            help="Mengganti pilihan ini tidak mengubah satu baris kode pun.",
        )
        st.caption(
            "Penggantian komponen hanya mengubah nilai `model.name` pada "
            "konfigurasi. Diuji otomatis oleh `tests/test_modularity.py`."
        )
        if st.button("Jalankan ulang analisis"):
            st.cache_resource.clear()
            st.rerun()

    try:
        data = run_analysis(chosen, st.session_state.get("cache_key", 0))
    except PipelineError as error:
        st.error("Alur analisis belum dapat dijalankan.")
        st.code(str(error))
        st.info(
            "Jalankan `python -m rra.cli sample-data` lebih dahulu untuk "
            "menyiapkan data, atau letakkan data hasil pengumpulan Anda."
        )
        return

    decision = data["decision"]

    kolom = st.columns(4)
    kolom[0].metric("Komponen model", data["model"].upper())
    kolom[1].metric("Ulasan dianalisis", f"{data['n_reviews']:,}")
    kolom[2].metric("Ulasan bersentimen negatif", decision.n_negative_reviews)
    kolom[3].metric("Waktu analisis", f"{data['timings']['total']:.2f} s")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Prioritas perbaikan", "Frasa keluhan", "Rekomendasi tindakan", "Bahan audit"]
    )

    # ------------------------------------------------------------------ #
    with tab1:
        st.subheader("Peringkat prioritas perbaikan layanan")
        st.caption(
            "Skor = w₁·Volume + w₂·Keparahan + w₃·Keragaman, dengan "
            f"w₁={decision.weights['volume']}, w₂={decision.weights['severity']}, "
            f"w₃={decision.weights['diversity']}. Keparahan diturunkan dari rating "
            "bintang, bukan dari model."
        )
        frame = data["priorities"].copy()
        frame = frame.rename(columns={
            "peringkat": "Peringkat", "aspek": "Aspek", "skor_prioritas": "Skor",
            "volume": "Volume", "keparahan": "Keparahan", "keragaman": "Keragaman",
            "jumlah_keluhan": "Keluhan", "jumlah_dibahas": "Dibahas",
        })
        st.dataframe(frame, use_container_width=True, hide_index=True)
        st.bar_chart(
            data["priorities"].set_index("aspek")["skor_prioritas"],
            horizontal=True,
        )

    # ------------------------------------------------------------------ #
    with tab2:
        st.subheader("Frasa keluhan dominan per aspek")
        st.warning(
            "Frasa ini adalah yang paling **menonjol**, bukan bukti penyebab "
            "persoalan. Setiap frasa dapat ditelusuri ke ulasan asalnya melalui "
            "kolom contoh ulasan.",
            icon="⚠️",
        )
        for aspek in data["phrases"]["aspek"].unique():
            blok = data["phrases"][data["phrases"]["aspek"] == aspek]
            st.markdown(f"**{aspek.title()}**")
            st.dataframe(
                blok.rename(columns={
                    "peringkat_frasa": "#", "frasa": "Frasa", "frekuensi": "Frekuensi",
                    "bobot_tfidf": "Bobot TF-IDF", "skor": "Skor",
                    "contoh_ulasan": "Contoh ulasan",
                })[["#", "Frasa", "Frekuensi", "Bobot TF-IDF", "Skor", "Contoh ulasan"]],
                use_container_width=True, hide_index=True,
            )

    # ------------------------------------------------------------------ #
    with tab3:
        st.subheader("Rekomendasi tindakan")
        st.caption(
            "Tindakan diambil dari tabel aturan DINESERV yang dapat dibaca "
            "manusia (`src/rra/decision/rules.py`), bukan dihasilkan model."
        )
        baris = [
            {"Aspek": item.aspect, "Frasa pemicu": item.phrase, "Tindakan": item.action}
            for item in decision.recommendations
        ]
        st.dataframe(pd.DataFrame(baris), use_container_width=True, hide_index=True)

    # ------------------------------------------------------------------ #
    with tab4:
        st.subheader("Bahan audit peringkat")
        for baris_audit in decision.audit_lines():
            st.markdown(f"- {baris_audit}")

        st.subheader("Mutu data")
        st.json(data["data_quality"])

        st.subheader("Waktu proses per tahap")
        st.dataframe(
            pd.DataFrame(
                [{"Tahap": tahap, "Detik": detik} for tahap, detik in data["timings"].items()]
            ),
            use_container_width=True, hide_index=True,
        )

        with st.expander("Tabel aturan rekomendasi (dapat diperiksa)"):
            for aspek in ("makanan", "pelayanan", "harga", "suasana", "fasilitas"):
                st.markdown(f"**{aspek.title()}**")
                for kata_kunci, tindakan in rules_for(aspek):
                    st.markdown(f"- `{', '.join(kata_kunci)}` → {tindakan}")

        with st.expander("Komponen model yang terdaftar"):
            st.json({k: v for k, v in models.items()})


if __name__ == "__main__":
    main()
