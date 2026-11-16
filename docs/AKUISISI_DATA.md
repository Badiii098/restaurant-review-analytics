# Akuisisi Data Ulasan Google Maps

Dokumen ini menjelaskan **rencana sampel** dan **cara mengambil data** ulasan publik
Google Maps untuk penelitian ABSA pada restoran. Skripnya:
`scripts/scraping/scrape_maps.py` (akuisisi) dan `scripts/scraping/preprocess_reviews.py`
(pembersihan).

---

## 1. Rencana sampel (mengacu Bab III)

| Butir | Ketetapan |
|---|---|
| Populasi | Ulasan publik berbahasa Indonesia pada restoran di Jabodetabek, terbit 2021–2026 |
| Kerangka sampel | Restoran dengan **≥ 300 ulasan** publik (agar memungkinkan pengambilan 400 ulasan) |
| Teknik | **Purposive stratified**: 25 restoran, distratifikasi menurut kota (Jakarta 17, Bekasi 2, Depok 2, Tangerang 2, Bogor 2) dan kategori (Padang, Sunda, Jepang, seafood, ayam/bebek, Betawi, bakmi/bakso, martabak, kafe) |
| Target per restoran | **400 ulasan** |
| Target total | **25 × 400 = 10.000 ulasan** (ambang minimum metodologi) |
| Urutan pengambilan | Urutkan **Terbaru** (*Newest*) agar periode 2021–2026 tercakup, bukan "Paling relevan" |
| Bila ulasan dalam rentang < 400 | Ambil seluruh yang tersedia dan catat kekurangan (shortfall) pada `*.meta.json` dan `ringkasan_per_restoran.csv` |
| Unit analisis | Satu ulasan (bukan satu restoran); restoran menjadi stratum pelaporan |

**Rasional 400 per restoran.** Dengan n = 400, proporsi sentimen negatif per restoran dapat
diduga dengan galat baku maksimum ± 4,9% pada tingkat kepercayaan 95% (p = 0,5). Bila satu
restoran memuat enam aspek, rata-rata tersedia ± 67 ulasan per aspek — cukup untuk
mengestimasi polaritas per aspek tanpa bergantung pada satu-dua ulasan.

**Jumlah per aspek untuk klasifikasi.** Pelatihan model memakai gabungan seluruh restoran
(≈10.000 ulasan), bukan per restoran, sehingga kelas minoritas (negatif) tetap terwakili.
Rasio kelas dilaporkan pada `laporan_kualitas.json` dan dipakai untuk menentukan bobot kelas
pada SVM.

## 2. Kriteria inklusi dan eksklusi

**Inklusi**
1. Ulasan publik (dapat dibaca tanpa login), teks berbahasa Indonesia.
2. Tanggal ulasan jatuh pada 1 Januari 2021 – 31 Desember 2026.
3. Panjang teks ≥ 15 karakter dan ≥ 3 kata.
4. Membahas minimal satu dari enam aspek layanan.

**Eksklusi (ditandai, tidak dihapus)**
1. Ulasan tanpa teks / hanya rating bintang → `flag_noise=tanpa_teks`.
2. Teks hanya emoji/simbol → `hanya_simbol`.
3. Duplikat (restoran + penulis + teks + tanggal sama) → `duplikat=True`.
4. Ulasan di luar rentang tahun → `dalam_rentang=False`.

Ulasan yang dieksklusi **tetap tersimpan** di `reviews_all.csv` agar jumlah sebelum dan
sesudah penyaringan dapat dilaporkan di Bab IV (bukan dihapus diam-diam).

## 3. Variabel yang direkam

| Kelompok | Kolom |
|---|---|
| Identitas tempat | `kode_restoran`, `nama_restoran_config`, `nama_tempat_maps`, `alamat`, `kota`, `kategori_config` |
| Identitas ulasan | `review_id`, `penulis`, `local_guide`, `suka_teks` |
| Polaritas | `rating`, `rating_label` |
| Waktu | `tanggal_teks`, `tanggal`, `tanggal_presisi` (`exact` / `relative` / `none`) |
| Isi | `teks` (asli), `teks_normal` (untuk deduplikasi) |
| Konteks | `respons_pemilik`, `sumber_url`, `diambil_pada` |
| Turunan | `panjang_karakter`, `jumlah_kata`, `flag_noise`, `alasan_noise`, `duplikat`, `dalam_rentang` |

**Catatan presisi tanggal.** Google Maps menampilkan tanggal relatif ("2 tahun lalu").
Skrip menurunkan tanggal perkiraan dari hari pengambilan dan **menandainya** `relative`.
Untuk analisis tren per bulan, gunakan hanya baris `exact`; untuk klasifikasi sentimen,
seluruh baris dapat dipakai.

## 4. Prosedur pengambilan

> **Penting — batas 10 ulasan untuk pengunjung anonim.** Sejak 2026 Google Maps
> hanya menampilkan 10 ulasan bila belum masuk, lalu memasang dinding login saat
> tombol "Lihat ulasan lainnya" diklik. Karena itu sesi scraping **wajib login
> sekali**; setelah itu sesi tersimpan di profil `.browser-profile/` dan dipakai
> ulang pada run berikutnya.

```bash
# 0) sekali saja: dependensi + browser Chromium untuk Playwright
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/playwright install chromium

# 1) LOGIN SEKALI (jendela terbuka; login manual; skrip menunggu maks. 300 detik)
.venv/bin/python scripts/scraping/scrape_maps.py --login

# 2) uji kendali mutu pada 2 restoran (memastikan selector & urutan bekerja)
.venv/bin/python scripts/scraping/scrape_maps.py --pilot

# 2) periksa hasil uji: jumlah ulasan, nama tempat yang cocok, presisi tanggal
.venv/bin/python scripts/scraping/preprocess_reviews.py

# 3) pengambilan penuh (25 restoran × 400 ulasan)
.venv/bin/python scripts/scraping/scrape_maps.py

# 3b) alternatif: menumpang Brave yang sudah login lewat port debug
#     brave-browser --remote-debugging-port=9222 --user-data-dir="$HOME/.config/brave-debug" &
.venv/bin/python scripts/scraping/scrape_maps.py --cdp http://127.0.0.1:9222

# 4) pembersihan + rekap
.venv/bin/python scripts/scraping/preprocess_reviews.py --tahun-mulai 2021 --tahun-akhir 2026
```

Waktu perkiraan: ± 2–5 menit per restoran untuk 400 ulasan (12–20 putaran gulir, jeda acak 0,9–1,6 detik per putaran). Status `perlu_login` pada `*.meta.json` berarti sesi belum login.

## 5. Kendali mutu yang wajib dilaporkan

| Metrik | Sumber angka | Ambang |
|---|---|---|
| Jumlah ulasan terkumpul vs target | `logs/scraping/run_*.json` | ≥ 10.000 total |
| Persentase duplikat | `laporan_kualitas.json` | < 3% |
| Persentase noise (tanpa teks/terlalu pendek) | `laporan_kualitas.json` | dilaporkan apa adanya |
| Cakupan tanggal presisi `exact` | `laporan_kualitas.json` | dilaporkan; tren bulanan memakai subset ini |
| Sebaran ulasan per tahun 2021–2026 | `ringkasan_per_restoran.csv` | tidak kosong pada tiap tahun |
| Kesepakatan anotasi (Cohen's κ) | `scripts/compute_kappa.py` | ≥ 0,61 |

## 6. Menyambung ke pipeline ABSA

```bash
# seragamkan hasil scraping menjadi data/raw/reviews.csv yang dibaca sistem
.venv/bin/python scripts/import_reviews.py \
  --input data/processed/scraping/reviews_clean.csv \
  --id-column review_id --text-column teks --rating-column rating \
  --date-column tanggal --restaurant-column nama_tempat_maps
```

Setelah itu jalankan pipeline seperti biasa (`python -m rra.cli run`).

## 7. Etika, kepatuhan, dan batasan

1. Hanya ulasan **publik**; tidak menembus login, tidak mengambil data profil/foto.
2. Jeda acak antar-gulir dan antar-restoran; tanpa paralelisasi agresif.
3. Untuk publikasi, lampirkan **contoh** ulasan (bukan seluruh korpus) dan simpan korpus
   secara lokal.
4. Ulasan dapat berisi bias pemilihan (hanya pengguna yang termotivasi menulis) dan
   ulasan palsu; hal ini dinyatakan sebagai batasan penelitian, bukan diabaikan.
5. Perubahan antarmuka Google Maps dapat menghentikan pengambilan; selector pada
   `scrape_maps.py` perlu diperbarui bila hal itu terjadi (lihat README, bagian 6).
