# Rencana Pengujian

Dokumen ini memuat kriteria kelulusan, cara pengumpulan bukti, dan kuesioner
yang dipakai. Seluruh angka dari dokumen ini menjadi lampiran Bab IV.

---

## 1. Kriteria keberhasilan rekayasa

Tiga kriteria rekayasa (berbeda dari hipotesis statistik) yang menentukan
apakah sistem dianggap berhasil:

| Kode | Kriteria | Ambang | Cara memperoleh bukti |
|---|---|---|---|
| KR-1 | **Keterpilahan komponen** — penggantian komponen model tidak mengubah modul lain | sidik jari `src/rra/**/*.py` identik sebelum & sesudah penggantian; berkas konfigurasi berbeda hanya pada `model.name` | `tests/test_modularity.py` |
| KR-2 | **Keterlacakan keputusan** — setiap peringkat prioritas dapat ditelusuri ke komponen penyusunnya | 100% baris prioritas memuat `volume`, `severity`, `diversity`, bobot, dan peringkat | tabel `priorities` di `data/processed/rra.sqlite` |
| KR-3 | **Ketahanan masukan** — sistem menerima data tidak sempurna tanpa berhenti | alur selesai pada data uji yang memuat rating kosong, teks duplikat, dan ulasan tanpa aspek | `tests/test_pipeline.py` + pengujian manual |

## 2. Kebutuhan non-fungsional

| Kode | Kebutuhan | Ambang | Cara mengukur |
|---|---|---|---|
| KNF-01 | Waktu analisis untuk 1.000 ulasan | ≤ 60 detik | `python -m rra.cli benchmark --repeat 5` |
| KNF-02 | Waktu analisis per ulasan | ≤ 60 ms | kolom `klasifikasi_ms_per_ulasan` pada `reports/benchmark.json` |
| KNF-03 | Keterpakaian (SUS) | ≥ 68 (di atas rata-rata) | kuesioner Bagian 5, minimal 10 responden |
| KNF-04 | Daya angkat (portabilitas) | berjalan di Linux/Windows/macOS, Python ≥ 3.11 | berkas CI GitHub Actions |

Ambang KNF-01 dan KNF-02 sengaja ditetapkan **sebelum** pengukuran. Menetapkan
ambang setelah melihat hasil adalah praktik yang tidak dapat
dipertanggungjawabkan.

## 3. Protokol evaluasi model

| Aspek protokol | Ketetapan |
|---|---|
| Pembagian data | **10-fold cross-validation** untuk pelaporan utama; hold-out 80/20 hanya untuk pemeriksaan cepat |
| Pembagian pada data multilabel | pembagian dilakukan per **ulasan**, bukan per baris aspek — mencegah satu ulasan muncul di data latih sekaligus data uji |
| Metrik utama | Macro-F1 aspek dan Macro-F1 sentimen (rata-rata per lipatan ± simpangan baku) |
| Metrik pendukung | micro-F1, precision/recall per aspek, matriks kebingungan |
| Metrik keluaran keputusan | Precision@K frasa keluhan (K = 5) terhadap daftar acuan |
| Uji beda | uji-t berpasangan atas 10 nilai lipatan untuk membandingkan dua komponen model |
| Benih pengacakan | tetap (42), dinyatakan pada naskah |

**Dua angka Macro-F1.** Sistem melaporkan `macro_f1` (menghitung aspek tanpa
dukungan sebagai nol — **inilah angka resmi**) dan `macro_f1_aktif` (hanya
aspek yang punya contoh). Angka pertama bersifat ketat dan jujur; angka kedua
membantu menjelaskan sumber kesalahan. Melaporkan hanya angka kedua akan
membuat kinerja terlihat lebih tinggi daripada kenyataannya.

## 4. Uji fungsional

```bash
export PYTHONPATH=src
pytest tests -q
```

| Fungsi | Berkas uji | Diharapkan |
|---|---|---|
| Muat & validasi data | `test_contracts.py` | bentuk data antar-lapisan tidak berubah diam-diam |
| Praproses Bahasa Indonesia | `test_preprocess.py` | negasi tidak melintasi batas klausa; singkatan dipetakan; klausa utuh |
| Komponen model | `test_models.py` | kedua model memenuhi kontrak; jumlah skor = jumlah kelas |
| **Modularitas** | `test_modularity.py` | sidik jari modul identik setelah penggantian model |
| Modul keputusan | `test_decision.py` | keparahan monoton turun terhadap rating; skor prioritas & aturan benar |
| Alur menyeluruh | `test_pipeline.py` | alur selesai; pesan galat menuntun saat data kurang |
| Evaluasi | `test_evaluate.py` | metrik jujur; aspek tanpa dukungan dihitung nol |
| Antarmuka baris perintah | `test_cli.py` | kotak hitam: `sample-data`, `run`, `models`, `explain` berperilaku benar |

Pengujian kotak hitam dijalankan sebagai proses terpisah (`subprocess`), bukan
memanggil fungsi langsung — inilah wujud **black-box testing** pada pemetaan
peminatan Software Engineering.

## 5. Kuesioner SUS (System Usability Scale)

Sepuluh pernyataan, dijawab pada skala 1–5 (1 = sangat tidak setuju,
5 = sangat setuju). Susunannya wajib berselang-seling positif dan negatif.

| No | Pernyataan | Sifat |
|---|---|---|
| 1 | Saya ingin sering menggunakan sistem ini | positif |
| 2 | Sistem ini terasa rumit tanpa alasan yang perlu | negatif |
| 3 | Sistem ini mudah digunakan | positif |
| 4 | Saya perlu bantuan teknis untuk dapat menggunakan sistem ini | negatif |
| 5 | Fitur-fitur pada sistem ini berjalan selaras | positif |
| 6 | Terlalu banyak ketidaksesuaian pada sistem ini | negatif |
| 7 | Saya membayangkan orang lain akan cepat terbiasa dengan sistem ini | positif |
| 8 | Sistem ini terasa membingungkan saat digunakan | negatif |
| 9 | Saya merasa percaya diri saat menggunakan sistem ini | positif |
| 10 | Saya perlu mempelajari banyak hal sebelum dapat memakai sistem ini | negatif |

Responden wajib mencoba sistem terlebih dahulu (menganalisis satu berkas
ulasan, membaca peringkat, dan menelusuri satu rekomendasi sampai komponen
skornya). Kuesioner tanpa percobaan langsung tidak mengukur apa pun.

## 6. Perhitungan SUS

Untuk pernyataan **positif** (1, 3, 5, 7, 9): `nilai − 1`.
Untuk pernyataan **negatif** (2, 4, 6, 8, 10): `5 − nilai`.

Jumlahkan kesepuluh nilai (rentang 0–40), lalu kalikan **2,5** → skor 0–100.

```
SUS = 2,5 × Σ (kontribusi tiap pernyataan)
```

| Skor SUS | Tafsiran |
|---|---|
| ≥ 80,3 | sangat baik (peringkat A) |
| 68 – 80,2 | baik (peringkat B–C) |
| 51 – 67,9 | cukup (peringkat D) |
| < 51 | kurang (peringkat E–F) |

Rumus perhitungan sudah disediakan pada `scripts/hitung_sus.py`; angkanya
tetap harus dibaca manusia — SUS mengukur persepsi, bukan kebenaran.

## 7. Tabel rekap bukti

| Kode | Berkas bukti | Perintah penghasil |
|---|---|---|
| KR-1 | keluaran `pytest tests/test_modularity.py -v` | `pytest tests -q` |
| KR-2 | ekspor tabel `priorities` | `sqlite3 data/processed/rra.sqlite ".mode csv" "select * from priorities where run_id=1"` |
| KR-3 | keluaran `pytest tests/test_pipeline.py -v` | `pytest tests -q` |
| KNF-01, KNF-02 | `reports/benchmark.json` | `python -m rra.cli benchmark --repeat 5` |
| KNF-03 | rekap kuesioner | `python scripts/hitung_sus.py --input data/sus_jawaban.csv` |
| KNF-04 | riwayat GitHub Actions | otomatis pada setiap dorongan |
| Kinerja model | `reports/evaluasi.json` | `python -m rra.cli evaluate --folds 10 --compare` |
| Mutu data berlabel | `reports/kappa.json` | `python scripts/compute_kappa.py …` |

## 8. Uji hipotesis

| Hipotesis | Uji statistik | Kriteria penerimaan |
|---|---|---|
| H1 — SVM berbasis TF-IDF mencapai Macro-F1 ≥ 0,80 pada klasifikasi aspek | uji-t satu sampel atas 10 nilai lipatan | p < 0,05 |
| H2 — ada perbedaan bermakna antara SVM dan Naive Bayes | uji-t **berpasangan** atas 10 nilai lipatan | p < 0,05 |
| H3 — prioritas sistem berkorelasi dengan penilaian pakar | korelasi peringkat Spearman | ρ ≥ 0,60 dan p < 0,05 |
| H4 — skor SUS berada di atas rata-rata | uji-t satu sampel terhadap nilai 68 | p < 0,05 |

H2 sengaja diuji berpasangan karena kedua model diuji pada **lipatan yang
sama**. Menguji keduanya sebagai dua kelompok bebas akan membuang manfaat
pengendalian variasi antar-lipatan.

## 9. Yang tidak boleh disederhanakan

Tiga hal ini tetap wajib ada, seberapa pun scope dipangkas:

1. **Nilai Cohen's κ** — tanpa ini mutu data berlabel tidak dapat
   dipertanggungjawabkan.
2. **Protokol pembagian data latih/uji** — tanpa ini angka kinerja tidak sah.
3. **Kejujuran klaim** — "frasa keluhan dominan", bukan "akar masalah
   definitif".
