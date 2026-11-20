# Rancangan: Arsitektur Web Modern (FastAPI + React) dan Perombakan Naskah Bab III

Tanggal: 2026-11-20 · Sumber keputusan: diagram tahapan penelitian (SDLC Prototipe) dari Abdi,
percakapan sesi ini, dan rancangan pakem `2026-11-16-revisi-proposal-design.md`.

## 1. Maksud

Prototipe yang didemokan saat sidang harus menunjukkan alur penelitian pada diagram, tahap demi
tahap, dengan tampilan web modern. Setiap angka di layar harus berasal dari kode yang sama dengan
angka di naskah. Saat ini antarmuka (Streamlit) hanya menampilkan hasil prioritas. Data dan anotasi
(kappa), katalog FR/KNF, iterasi Macro-F1, hasil pengujian, dan validasi pakar tidak tampil, padahal
semuanya bukti untuk RM1–RM3. Naskah Bab III juga harus menggambarkan arsitektur baru ini dan urutan
tahap yang ada di diagram.

## 2. Pakem: tidak boleh berubah

| Topik | Isi pakem |
|---|---|
| Alur penelitian | Mulai → Identifikasi Masalah → Studi Literatur (2022–2026) → Pengumpulan Data (8 restoran) → Anotasi Data (500 ulasan, kappa) → Metode SDLC Prototipe → Analisis Kebutuhan (FR, KNF) → Desain Cepat (arsitektur, kontrak) → Pembangunan Prototipe dan Pemodelan NLP ⇄ Evaluasi Prototipe (Macro-F1, kebutuhan; iterasi 1–2) → Pengujian Perangkat Lunak (perbaikan kembali ke pembangunan) → Validasi Pakar (ρ Spearman, Wilcoxon) → Analisis Hasil dan Penarikan Kesimpulan → Selesai |
| RM dan hipotesis | 3 RM dan 3 hipotesis pada §4 rancangan 2026-11-16 (H1 kontrak dan keterlacakan 100%; H2 uji lulus dan ≤ 60 dtk/1.000 ulasan, uji-t; H3 median ρ > 0,60, Wilcoxon) |
| Arsitektur | Lima lapis dengan kontrak data tetap (`src/rra/contracts.py`) |
| Model | TF-IDF + SVM linear, parameter di `config/model_svm.yaml` dan `default.yaml` |
| Aspek dan sentimen | 5 aspek (makanan, pelayanan, harga, suasana, fasilitas), 3 kelas sentimen |
| Skor prioritas | Prioritas = 0,4·Volume + 0,4·Keparahan + 0,2·Keragaman, skala tampil 0–100 |
| Metrik | Macro-F1 (validasi silang), kappa Cohen, ρ Spearman per restoran, Wilcoxon satu sampel, Precision@K |
| Kebutuhan | FR-01..FR-08, KNF-01..KNF-05 dengan kriteria lulusnya |

Inti analitik L1–L4 (`io_layer`, `preprocess`, `models`, `decision`, `analysis`, `storage`) tidak
diubah perilakunya. Fungsi boleh dipindah atau diberi pembungkus, tetapi angka keluarannya harus sama.

## 3. Tujuan, bukan tujuan, anti-tujuan

**Tujuan**
1. Lapis 5 (penyajian) dibangun ulang sebagai **API FastAPI + SPA React (Vite + TypeScript)**.
2. Dashboard punya satu halaman per tahap diagram, dengan status dan buktinya.
3. Bukti RM dihitung otomatis oleh backend: keterlacakan FR/KNF → uji, kappa, iterasi Macro-F1,
   ringkasan pengujian dan benchmark, uji pakar, serta keputusan hipotesis H1–H3.
4. Satu perintah untuk menjalankan prototipe: `python -m rra.cli serve` (API + halaman di port 8000).
5. Isi `scripts/proposal/naskah_bab3.py` beserta gambar dan tabelnya ditulis ulang mengikuti diagram
   dan arsitektur baru.

**Bukan tujuan**
- Menetapkan nama 8 restoran (didiskusikan nanti; lihat §6.6).
- Mengubah Bab I/II (hanya didaftar kalimat yang bertentangan, lihat §6.9).
- Autentikasi atau multi-pengguna (prototipe lokal satu pengguna).
- Membangun berkas .docx di sini, karena templat `3a.Template Skripsi.docx` tidak ada di repo.

**Anti-tujuan (gagal walau berjalan)**
- Angka di dashboard berbeda dengan angka di CLI atau laporan.
- Halaman memuat aset dari CDN/internet, sehingga KNF-02 (tanpa jaringan) gagal.
- Uji dilemahkan, dilewati, atau dihapus tanpa pengganti yang setara.
- Pakem pada §2 ikut berubah.

## 4. Pendekatan

| # | Pendekatan | Untung | Rugi | Status |
|---|---|---|---|---|
| 1 | FastAPI (backend) + React/Vite/TS (frontend), build statis disajikan FastAPI | paling modern; API terdokumentasi OpenAPI (bukti kontrak); backend dan frontend diuji terpisah; jalan tanpa internet | butuh Node untuk build; kode terbanyak | **Dipilih Abdi** |
| 2 | FastAPI + HTMX dengan templat Jinja | semua Python, ringan | kurang terasa SPA modern; grafik interaktif terbatas | ditolak |
| 3 | Next.js full-stack | ekosistem JS penuh | inti Python harus dipanggil lewat proses terpisah, sehingga lima lapis rusak (melanggar pakem) | dicoret |

## 5. Arsitektur

```
src/rra/            L1–L4 inti (tetap)       ← io_layer, preprocess, models, decision, analysis, storage
src/rra/services/   L5a layanan (baru)       ← fungsi per tahap, membaca storage + reports/*.json
src/rra/api/        L5a HTTP (baru)          ← FastAPI app, routers, skema Pydantic
frontend/           L5b klien (baru)         ← React + TS + Vite; build → frontend/dist
src/rra/cli.py      L5 CLI (tetap, + serve, + evaluate --iterasi)
```

Lapis 5 "Penyajian" dipecah menjadi **5a layanan/API** dan **5b klien web**. Jumlah lapis tetap
lima. Streamlit (`app/`) dipensiunkan dan dipindah ke `scripts/arsip/streamlit/` beserta ujinya
(`test_ui_*.py` diganti uji API dan uji frontend).

### 5.1 Kontrak dan skema
- Skema respons API adalah model Pydantic yang **dibangkitkan dari dataclass** `contracts.py`
  (`pydantic.TypeAdapter`), jadi kontrak tetap satu sumber.
- `/api/v1/openapi.json` diekspor ke `docs/openapi.json` oleh `scripts/export_contracts.py` dan
  menjadi lampiran bukti H1.

### 5.2 Endpoint (semua `GET` kecuali disebut)
| Tahap diagram | Endpoint | Sumber data |
|---|---|---|
| — | `/api/v1/status` | versi, basis data, hasil terakhir |
| Pengumpulan Data | `/api/v1/data` | `config/restaurants.csv`, `data/raw`, `sampling.n_restoran` |
| Anotasi Data | `/api/v1/anotasi` | `reports/kappa.json` + target 500 |
| Analisis Kebutuhan | `/api/v1/kebutuhan` | `config/kebutuhan.yaml` + `reports/pytest.xml` (status kasus uji) |
| Desain Cepat | `/api/v1/desain` | daftar lapis + skema kontrak |
| Prototipe & Evaluasi | `/api/v1/iterasi` | `reports/iterasi/iterasi-{1,2}.json` |
| Hasil analisis | `/api/v1/hasil/{run_id\|terakhir}`, `POST /api/v1/analisis` | `rra.sqlite` |
| Sensitivitas | `/api/v1/sensitivitas` | `reports/sensitivitas.json` |
| Pengujian | `/api/v1/pengujian` | `reports/pytest.xml`, `reports/benchmark.json` |
| Validasi Pakar | `/api/v1/pakar` | `data/reference/urutan_pakar.csv` + hasil terakhir |
| Analisis & Kesimpulan | `/api/v1/hipotesis` | keputusan H1–H3 dari semua sumber di atas |

Bila suatu berkas sumber belum ada, endpoint mengembalikan `{"status": "belum_tersedia", "langkah": "<perintah untuk membuatnya>"}`.
Endpoint tidak memalsukan angka.

### 5.3 Modul backend baru atau dipindah
- `rra.analysis.agreement`: `cohen_kappa` dan `compare` dipindah dari `scripts/compute_kappa.py`.
  Skrip menjadi pembungkus CLI. Angkanya tetap sama.
- `rra.analysis.hypotheses`: H1 (kontrak lolos dan kebutuhan terlacak), H2 (uji-t satu sampel atas
  benchmark dan rasio lulus uji kritis), H3 (memakai `expert.uji_median_rho`).
- `rra.requirements`: memuat `config/kebutuhan.yaml`, katalog tunggal FR/KNF yang juga dibaca oleh
  `scripts/proposal/tabel.py`, sehingga naskah dan kode tidak berbeda.
- Keterlacakan: uji diberi penanda `@pytest.mark.req("FR-01", ...)`. Uji `test_traceability.py`
  gagal bila ada FR/KNF tanpa uji (bukti H1 otomatis). `pytest --junitxml=reports/pytest.xml`
  menyimpan status untuk dashboard.
- Iterasi: `rra.cli evaluate --iterasi N --catatan "..."` menulis `reports/iterasi/iterasi-N.json`
  (Macro-F1 aspek dan sentimen, rerata ± sd, per aspek, catatan perbaikan, waktu, hash commit).
  Endpoint `/iterasi` menampilkan Δ iterasi 2 − iterasi 1.
- `rra.cli serve [--port 8000]` menjalankan uvicorn dan menyajikan `frontend/dist` di `/`.

### 5.4 Frontend
- React 18 + TypeScript + Vite, React Router, TanStack Query, Recharts. Semua aset dibundel,
  tanpa CDN atau font daring (KNF-02).
- Token warna diambil dari `app/theme.py` agar identitas visual tetap. Mendukung mode terang/gelap
  dan lebar ponsel.
- Halaman (urut seperti diagram, navigasi samping berupa garis tahapan dengan status ✓/○):
  1. **Ringkasan**: diagram alur interaktif dengan status tiap tahap dan keputusan H1–H3.
  2. **Data**: 8 restoran (atau peringatan bila konfigurasi ≠ 8), jumlah ulasan, sebaran tahun dan rating.
  3. **Anotasi**: progres terhadap 500 ulasan, kappa per aspek dan sentimen beserta interpretasinya.
  4. **Kebutuhan**: matriks FR/KNF → kasus uji → status lulus.
  5. **Desain**: diagram lima lapis dan tabel kontrak.
  6. **Prototipe & Iterasi**: Macro-F1 iterasi 1 vs 2 (grafik batang per aspek), catatan perbaikan.
  7. **Hasil & Prioritas**: peringkat 0–100, frasa keluhan, rekomendasi, sensitivitas, tombol analisis ulang.
  8. **Pengujian**: jumlah uji unit/integrasi/sistem, KNF-01 benchmark + uji-t, status KNF lain.
  9. **Validasi Pakar**: ρ per restoran, Wilcoxon, kesesuaian peringkat 1.
  10. **Kesimpulan**: jawaban RM1–RM3, H0 ditolak/tidak, dan rekomendasi bila tidak ditolak.

### 5.5 Pengujian
- Python: uji inti tetap; uji API baru (`fastapi.testclient`) per endpoint; `test_traceability.py`.
- Frontend: Vitest + Testing Library untuk komponen; uji sistem Playwright (Chromium) yang membuka
  `serve`, memeriksa tiap halaman tampil, dan mengukur waktu sampai peringkat tampil (KNF-03 ≤ 3 dtk).
- CI: job Python (3.11, 3.12) seperti sekarang + job Node (build, vitest) + job e2e.

## 6. Keputusan yang diambil pelaksana (dapat dikoreksi)

1. **Lokasi kode:** backend di `src/rra/api` dan `src/rra/services` agar `PYTHONPATH=src` tetap
   cukup; frontend di `frontend/`.
2. **Streamlit dipensiunkan** (diarsipkan, tidak dihapus dari riwayat), supaya tidak ada dua antarmuka
   yang harus dijaga angkanya.
3. **`frontend/dist` tidak di-commit.** `serve` memberi pesan jelas bila build belum ada
   (`npm --prefix frontend run build`).
4. **Anotasi 500 ulasan:** kedua anotator melabeli seluruh 500 ulasan yang sama, dan kappa dihitung
   atas 500 ulasan itu. Ini bacaan paling langsung dari "500 ulasan, kappa" pada diagram. Bawaan
   `make_annotation_template.py` menjadi `--overlap 500 --each 500`.
5. **8 restoran:** `config/default.yaml` mendapat `sampling: {n_restoran: 8, teknik: purposive,
   kriteria: [...]}`. `restaurants.csv` tidak diubah sekarang, dan dashboard menandai bila jumlah
   restoran aktif ≠ 8.
6. **Nama restoran di naskah:** Bab III memuat teknik *purposive sampling*, kriteria
   inklusi/eksklusi, n = 8, dan target ulasan. Nama restoran dan realisasinya masuk Bab IV/lampiran.
   `fakta.py` mengambil n dari konfigurasi.
7. **Iterasi 1 dan 2:** iterasi 1 adalah keadaan kode inti saat ini; iterasi 2 setelah perbaikan dari
   evaluasi. Dengan data contoh, catatan iterasi ditandai `data_contoh: true` agar tidak dikutip
   sebagai hasil penelitian.
8. **Bab III dirombak** mengikuti urutan diagram (studi literatur sebelum pengumpulan data, anotasi
   sebagai subbab sendiri, SDLC Prototipe dengan empat langkahnya, pengujian, validasi pakar,
   analisis). Gambar 3.1 dibangkitkan ulang sesuai diagram; Gambar 3.3 (arsitektur) dan 3.8
   (antarmuka) diganti; Tabel 3.2 dibaca dari `kebutuhan.yaml`; Tabel 3.4 dan 3.6 diperbarui
   (FastAPI, React, Node, Playwright).
9. **Bab I/II tidak disentuh.** Kalimat yang bertentangan (mis. "18 restoran") didaftar di
   `docs/superpowers/specs/` untuk diputuskan Abdi.
10. **Commit:** di branch `claude/practical-rubin-ft5ib8`, kecil dan atomik dengan format
    `tipe(scope): pesan`, dan pytest lulus sebelum tiap commit (aturan repo).

## 7. Diserahkan ke pelaksana
Nama berkas internal, susunan komponen React, pustaka ikon, gaya grafik (mengikuti skill dataviz),
detail tata letak per halaman, dan pembagian commit.

## 8. Selesai bila
- `pytest` lulus (termasuk keterlacakan 100%), `npm run build` dan `vitest` lulus, dan uji e2e lulus.
- `python -m rra.cli serve` menyajikan kesepuluh halaman dari data contoh tanpa akses internet, dengan
  tangkapan layar tiap halaman diperiksa.
- Metrik tersedia: Macro-F1 iterasi 1 dan 2, kappa (bila berkas anotasi ada), benchmark KNF-01, ρ dan
  Wilcoxon (bila urutan pakar ada), serta keputusan H1–H3.
- `naskah_bab3.py`, gambar, dan tabel Bab III diperbarui; README, ARSITEKTUR, ANTARMUKA, PENGUJIAN, ANOTASI selaras.
