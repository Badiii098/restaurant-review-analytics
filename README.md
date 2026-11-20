# Restaurant Review Analytics (RRA)

Sistem analitik ulasan pelanggan restoran berbasis **Aspect-Based Sentiment
Analysis (ABSA)** dengan **ekstraksi frasa keluhan dominan** untuk menghasilkan
**rekomendasi prioritas perbaikan layanan**.

Repositori ini adalah artefak rekayasa dari skripsi:

> **Rancang Bangun Sistem Analitik Ulasan Pelanggan Restoran Berbasis
> Aspect-Based Sentiment Analysis dengan Ekstraksi Frasa Keluhan Dominan untuk
> Rekomendasi Prioritas Perbaikan Layanan**

---

## 1. Masalah yang diselesaikan

Ulasan pelanggan restoran di Google Maps jumlahnya besar, tetapi bagi pemilik
usaha ia hanya tumpukan teks. Keluaran yang benar-benar dibutuhkan bukan
sekadar "sentimen positif/negatif", melainkan **urutan hal apa yang harus
diperbaiki lebih dahulu** beserta alasannya.

Rangkaian penalaran sistem:

```
ulasan mentah
  → aspek apa yang dibicarakan          (makanan, pelayanan, harga, suasana, fasilitas)
  → sentimen tiap aspek                  (positif / negatif / netral)
  → seberapa parah tiap keluhan          (diturunkan dari rating bintang, bukan dari model)
  → frasa keluhan yang paling sering     (per aspek, berbasis frekuensi + bobot TF-IDF)
  → skor prioritas perbaikan             (volume, keparahan, keragaman — eksplisit & dapat diaudit)
  → rekomendasi tindakan                 (tabel aturan DINESERV, bukan keluaran model)
```

## 2. Kontribusi yang dibuktikan di repositori ini

Kontribusi penelitian ini **bukan pada algoritmanya** — ABSA dengan SVM/TF-IDF
pada ulasan restoran Indonesia sudah terbukti (Firdaus dkk., 2024; Nofandi
dkk., 2023). Kontribusinya ada pada **rekayasa sistem**, dan tiap klaim di bawah
punya bukti yang dapat dijalankan. Penelitian memakai satu komponen model
(TF-IDF + SVM linear), sampel *purposive* 8 restoran di Jabodetabek, dan
500 ulasan berlabel dua anotator (κ Cohen).

| Klaim | Bukti di repositori |
|---|---|
| Arsitektur lima lapis dengan **kontrak data tetap** | `src/rra/contracts.py`, `docs/KONTRAK.md`, `tests/test_contracts.py` |
| Modul **skor prioritas eksplisit dan dapat diaudit** (skala tampil 0–100) | `src/rra/decision/priority.py`, komponen skor di `src/rra/storage/repository.py` |
| **Uji sensitivitas bobot ±10%** | `src/rra/decision/sensitivity.py`, `python -m rra.cli sensitivity` |
| **Kesesuaian dengan urutan pakar** (ρ per restoran + Wilcoxon) | `src/rra/analysis/expert.py`, `scripts/uji_pakar.py` |
| **Katalog FR/KNF terlacak 100%** ke kasus uji | `config/kebutuhan.yaml`, `tests/test_traceability.py` |
| **Pengujian rekayasa** unit, integrasi, sistem, peramban | `tests/`, `frontend/src/**/*.test.tsx`, `.github/workflows/ci.yml` |
| **Iterasi prototipe 1–2** dengan Macro-F1 tercatat | `src/rra/iterations.py`, `python -m rra.cli evaluate --iterasi N` |
| **Keputusan hipotesis H1–H3** dihitung dari bukti | `src/rra/analysis/hypotheses.py`, halaman Kesimpulan |
| Kinerja **non-fungsional terukur** | `scripts/benchmark.py` → `reports/benchmark.json` |

Rincian argumentasi, gap penelitian, dan perbandingan dengan penelitian
terdekat: [`docs/NOVELTY_DAN_GAP.md`](docs/NOVELTY_DAN_GAP.md).

## 3. Pemasangan

```bash
git clone https://github.com/Badiii098/restaurant-review-analytics.git
cd restaurant-review-analytics

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export PYTHONPATH=src
```

Bila memakai [uv](https://docs.astral.sh/uv/):

```bash
uv venv .venv && uv pip install --python .venv/bin/python -r requirements.txt
```

## 4. Menjalankan

```bash
export PYTHONPATH=src

# 1. Data contoh yang dapat diulang (2.000 ulasan, benih 42)
python -m rra.cli sample-data --n 2000 --seed 42

# 2. Alur end-to-end → CSV, Markdown, dan basis data SQLite
python -m rra.cli run

# 3. Evaluasi komponen model (validasi silang, pendukung)
python -m rra.cli evaluate --folds 10 --out reports/evaluasi.json

# 4. Ukur kinerja non-fungsional
python -m rra.cli benchmark --repeat 5

# 5. Uji sensitivitas bobot dan kesesuaian dengan pakar
python -m rra.cli sensitivity --out reports/sensitivitas.json
python scripts/uji_pakar.py --pakar data/reference/urutan_pakar.csv
```

Antarmuka pengguna:

```bash
# sekali: bangun klien web (Node ≥ 22)
npm --prefix frontend install
npm --prefix frontend run build

# API + dashboard di http://127.0.0.1:8000 (dokumentasi API: /api/v1/docs)
python -m rra.cli serve
```

Pengembangan antarmuka dengan *hot reload*: jalankan `python -m rra.cli serve`
lalu `npm --prefix frontend run dev` (Vite mem-proxy `/api` ke port 8000).

Dashboard memiliki satu halaman per tahap diagram penelitian: Data, Anotasi,
Kebutuhan, Desain, Iterasi, Hasil, Pengujian, Validasi Pakar, Kesimpulan.
Bukti tiap halaman dibuat dengan:

```bash
python scripts/pilih_restoran.py --tulis                   # sampel 8 restoran (butuh data/raw/maps)
python -m rra.cli evaluate --iterasi 1 --catatan "awal"     # catatan iterasi prototipe
python -m rra.cli benchmark --repeat 5                       # KNF-01
python -m rra.cli sensitivity --out reports/sensitivitas.json
pytest tests --junitxml=reports/pytest.xml                   # status kasus uji (H1, H2)
```

Berkas keluaran ditulis ke:

| Lokasi | Isi |
|---|---|
| `reports/*.csv`, `reports/*.md` | prioritas perbaikan, frasa keluhan, rekomendasi |
| `reports/evaluasi.json` | kinerja komponen model (F1, Precision@K, rincian per lipatan) |
| `reports/benchmark.json` | waktu pelatihan, waktu analisis, milidetik per ulasan |
| `data/processed/rra.sqlite` | hasil tiap jalan beserta komponen skornya (bahan audit) |

## 5. Memakai data Anda sendiri

```bash
# Seragamkan berkas hasil pengumpulan (CSV/JSONL)
python scripts/import_reviews.py --input ~/unduhan/maps_export.csv \
    --text-column reviewText --rating-column stars

# Siapkan berkas kerja anotasi untuk dua pemberi label
python scripts/make_annotation_template.py --overlap 500 --each 500

# Hitung kesepakatan antar-pemberi label (WAJIB dilaporkan di Bab IV)
python scripts/compute_kappa.py --first data/reference/anotator_1.csv \
    --second data/reference/anotator_2.csv --out reports/kappa.json

# Gabungkan menjadi data berlabel
python scripts/merge_labels.py
```

Panduan anotasi lengkap: [`docs/ANOTASI.md`](docs/ANOTASI.md).

### 5.1 Mengambil data langsung dari Google Maps

Bila data belum ada, gunakan skrip akuisisi berbasis **Brave + Playwright**:

```bash
# sekali saja: browser Chromium untuk Playwright
.venv/bin/playwright install chromium

# WAJIB sekali: login manual (Google membatasi 10 ulasan untuk pengunjung anonim)
.venv/bin/python scripts/scraping/scrape_maps.py --login

# uji: 2 restoran × 60 ulasan
.venv/bin/python scripts/scraping/scrape_maps.py --pilot

# penuh: 25 restoran × 400 ulasan (daftar di config/restaurants.csv)
.venv/bin/python scripts/scraping/scrape_maps.py

# alternatif: menumpang Brave yang sudah login (port debug)
.venv/bin/python scripts/scraping/scrape_maps.py --cdp http://127.0.0.1:9222

# bersihkan + rekap (duplikat, noise, presisi tanggal, sebaran tahun)
.venv/bin/python scripts/scraping/preprocess_reviews.py
```

Keluaran: `data/raw/maps/*.jsonl` (mentah) dan `data/processed/scraping/reviews_clean.csv`
(siap diimpor). Rencana sampel 25 × 400, kriteria inklusi/eksklusi, dan kendali mutu:
[`docs/AKUISISI_DATA.md`](docs/AKUISISI_DATA.md).

## 6. Struktur repositori

```
restaurant-review-analytics/
├── frontend/                     Lapisan 5b — klien web React + TypeScript (Vite)
├── config/
│   ├── default.yaml              konfigurasi dasar (semua jalur & parameter)
│   ├── model_svm.yaml            parameter SVM + TF-IDF
│   ├── kebutuhan.yaml            katalog FR/KNF dan kasus uji (satu sumber)
│   └── restaurants.csv           kandidat restoran; kolom sampel diisi pilih_restoran.py
├── data/
│   ├── raw/                      data mentah
│   ├── reference/                data berlabel acuan
│   └── processed/                basis data hasil olahan
├── docs/                         arsitektur, alur, novelty, anotasi, pengujian
├── reports/                      laporan keluaran (CSV, Markdown, JSON)
├── scripts/                      skrip bantu yang dapat dijalankan sendiri
├── src/rra/
│   ├── contracts.py              kontrak data antar-lapisan
│   ├── config.py                 pemuatan & penimpaan konfigurasi
│   ├── io_layer/                 Lapisan 1 — muat & validasi data
│   ├── preprocess/               Lapisan 2 — praproses teks Bahasa Indonesia
│   ├── models/                   Lapisan 3 — komponen model (SVM linear)
│   ├── decision/                 Lapisan 4 — frasa, skor prioritas, aturan, sensitivitas
│   ├── analysis/                 uji kesesuaian peringkat dengan pakar (RM3)
│   ├── api/, services/           Lapisan 5a — API FastAPI dan layanan per tahap
│   ├── evaluate.py               protokol evaluasi (satu sumber angka Bab IV)
│   ├── pipeline.py               perangkai kelima lapisan
│   ├── storage/repository.py     penyimpanan hasil & bahan audit
│   ├── report/report.py          penulis laporan
│   └── cli.py                    antarmuka baris perintah
└── tests/                        uji unit, integrasi, sistem (kotak hitam)
```

Penjelasan tiap lapisan dan kontraknya: [`docs/ARSITEKTUR.md`](docs/ARSITEKTUR.md).
Urutan pemrosesan dari berkas mentah sampai rekomendasi:
[`docs/ALUR.md`](docs/ALUR.md).

## 7. Pengujian

```bash
export PYTHONPATH=src
pytest tests -q
```

| Berkas uji | Yang dijaga |
|---|---|
| `test_contracts.py` | bentuk data antar-lapisan tidak berubah diam-diam |
| `test_preprocess.py` | praproses Bahasa Indonesia: negasi, batas klausa, singkatan |
| `test_models.py` | komponen SVM memenuhi kontrak & memuat metadata tampilan |
| `test_sensitivity.py` | peringkat stabil terhadap geseran bobot ±10% |
| `test_expert.py` | ρ Spearman per restoran, uji Wilcoxon, kesesuaian peringkat 1 |
| `test_data_scope.py` | kandidat aktif, pemilihan sampel purposive 8 restoran, target min(tersedia, 625) |
| `test_agreement.py` | κ Cohen tingkat aspek dan sentimen |
| `test_iterations.py` | catatan iterasi prototipe dan selisih Macro-F1 |
| `test_hypotheses.py` | keputusan H1–H3 dan status "belum tersedia" tanpa bukti |
| `test_traceability.py` | 100% kebutuhan terlacak ke kasus uji |
| `test_decision.py` | keparahan, skor prioritas, aturan rekomendasi, frasa keluhan |
| `test_pipeline.py` | alur menyeluruh & pesan galat yang menuntun |
| `test_evaluate.py` | kejujuran pelaporan metrik (aspek tanpa dukungan dihitung nol) |
| `test_cli.py` | antarmuka baris perintah diuji sebagai kotak hitam |
| `test_api.py` | setiap endpoint API, kesamaan angka dengan basis data, 409 analisis bersamaan |
| `test_e2e_web.py` | sepuluh halaman di peramban (Playwright) dan KNF-03 ≤ 3 detik |
| `frontend/src/**/*.test.tsx` | komponen antarmuka (Vitest): skor 0–100, navigasi tahapan |

Hipotesis, kriteria kelulusan, dan kebutuhan non-fungsional:
[`docs/PENGUJIAN.md`](docs/PENGUJIAN.md).

## 8. Peta berkas skripsi

| Berkas | Sumber di repositori |
|---|---|
| Tabel kebutuhan fungsional | `src/rra/cli.py`, `src/rra/decision/module.py` |
| Tabel kebutuhan non-fungsional | `scripts/benchmark.py`, `docs/PENGUJIAN.md` |
| Angka kinerja model (Bab IV) | `reports/evaluasi.json` |
| Nilai Cohen's κ (Bab IV) | `reports/kappa.json` |
| Gambar arsitektur berlapis | `docs/ARSITEKTUR.md` |
| Gambar alur sistem | `docs/ALUR.md` |

## 9. Batasan yang diakui

Batasan ini disebutkan apa adanya dan dibahas pada Bab IV:

1. **Polaritas tingkat klausa memakai leksikon**, bukan model kedua. Alasannya
   dapat diaudit dan tidak mengaburkan asal keputusan, tetapi ia belum
   mengenali sarkasme.
2. **Keparahan diturunkan dari rating bintang**, bukan dari teks. Ini
   disengaja: kesalahan model tidak merambat ke skor prioritas tanpa kendali.
3. **"Frasa keluhan dominan" bukan "akar masalah definitif"**. Frekuensi
   menunjukkan sesuatu yang menonjol, bukan hubungan sebab-akibat. Sistem
   tidak mengklaim mengetahui penyebab.
4. **Aturan rekomendasi berasal dari pengetahuan domain DINESERV**, bukan
   dipelajari dari data, sehingga tetap dapat dipertanggungjawabkan.
5. Data contoh dibangkitkan secara sintetis; angka pada `reports/` hasil data
   contoh **bukan** temuan penelitian dan tidak boleh dilaporkan sebagai hasil.

## 10. Lisensi

MIT — lihat [`LICENSE`](LICENSE).
