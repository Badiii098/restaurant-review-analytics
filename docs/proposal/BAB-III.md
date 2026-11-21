# BAB III METODE PENELITIAN

Penelitian ini adalah penelitian rekayasa perangkat lunak dengan pendekatan kuantitatif. Tahapan penelitian ditunjukkan pada Gambar 3.1. Model pengembangan SDLC prototipe menjadi kerangka perancangan dan pembangunan sistem, sedangkan setiap rumusan masalah dijawab oleh satu hipotesis dengan prosedur dan kriteria keputusan yang dapat diulang.

> **[Sisipkan: Gambar 3.1 - Tahapan penelitian.png]**
> *Gambar 3.1 Tahapan penelitian*

## Tahapan Penelitian

### Identifikasi Masalah

Masalah diidentifikasi dari kebutuhan pemilik restoran untuk mengetahui aspek layanan yang perlu diperbaiki lebih dahulu dan dari celah penelitian terdahulu yang berhenti pada ketepatan model (Firdaus et al. 2024; Salsabillah et al. 2024; Brata et al. 2024). Keluaran tahap ini adalah tiga rumusan masalah, tujuan, dan luaran pada Bab I.

### Studi Literatur

Studi literatur difokuskan pada publikasi 2022–2026 tentang ABSA ulasan restoran, arsitektur sistem pembelajaran mesin, SDLC prototipe, dan pengujian perangkat lunak; buku teks rekayasa perangkat lunak dirujuk sebagai landasan konsep (Pressman dan Maxim 2020). Hasilnya adalah landasan teori dan pemetaan penelitian terdahulu pada Bab II, yang menetapkan pilihan TF-IDF dan SVM serta posisi kontribusi penelitian pada sisi rekayasa sistem.

### Pengumpulan Data

Data adalah ulasan publik Google Maps berbahasa Indonesia dari restoran di Jabodetabek. Sampel ditentukan dengan teknik *purposive sampling* dua tahap. Tahap pertama menyusun daftar kandidat restoran berulasan banyak dengan kategori masakan yang beragam (25 kandidat, 18 memenuhi syarat awal). Tahap kedua memilih **8 restoran** dengan kriteria tertulis: (1) diurutkan menurut jumlah ulasan berteks pada periode 2021–2026; (2) paling banyak 2 restoran per kategori agar sampel tidak didominasi satu jenis masakan; (3) bila batas kategori menyisakan kurang dari 8 restoran, urutan berikutnya dipakai untuk mencukupi. Pemilihan dijalankan oleh fungsi deterministik pada prototipe sehingga hasilnya dapat diulang.

Target ulasan per restoran ditetapkan dengan persamaan (3.1), yaitu jumlah ulasan yang tersedia pada periode 2021–2026 dengan batas atas 625 ulasan. Batas atas mencegah satu restoran mendominasi data latih, sedangkan restoran dengan ulasan lebih sedikit tetap dianalisis dan kekurangannya dicatat sebagai batasan.

`Targetᵢ = min(Tersediaᵢ, 625)`  **(3.1)**

Ulasan diambil dengan Playwright dari halaman Google Maps yang diurutkan berdasarkan ulasan terbaru, dengan jeda acak antar-gulir dan tanpa pengambilan paralel. Hanya ulasan publik yang diambil; nama penulis tidak dimuat dalam laporan. Kriteria inklusi adalah ulasan berteks berbahasa Indonesia, terbit 2021–2026, dan membahas minimal satu aspek. Ulasan tanpa teks, berisi simbol saja, duplikat, atau di luar rentang tahun ditandai, bukan dihapus, agar jumlah sebelum dan sesudah penyaringan dapat dilaporkan. Nama kedelapan restoran beserta jumlah ulasan yang tersedia ditetapkan setelah pengambilan data dengan prosedur di atas, dan dilaporkan pada Bab IV.

**Tabel 3.1** Sampel purposive 8 restoran dan target ulasan

| Kode | Restoran | Kota | Kategori | Ulasan 2021–2026 | Target |
|---|---|---|---|---|---|
| – | Ditetapkan setelah pengambilan data (scripts/pilih_restoran.py) | – | – | – | – |

*Sumber: Kriteria: urut jumlah ulasan 2021–2026, maksimal 2 per kategori; target = min(tersedia, 625) (config/default.yaml, config/restaurants.csv, data/raw/maps)*

> **[Sisipkan: Gambar 3.6 - Ulasan per restoran sampel terhadap batas target.png]**
> *Gambar 3.6 Ulasan per restoran sampel terhadap batas target*

> **[Sisipkan: Gambar 3.7 - Sebaran restoran sampel per kota dan kategori.png]**
> *Gambar 3.7 Sebaran restoran sampel per kota dan kategori*

### Anotasi Data

Data latih diperoleh melalui anotasi **500 ulasan** yang diambil secara acak berstrata proporsional menurut restoran dari ulasan kedelapan restoran sampel. Dua anotator melabeli seluruh 500 ulasan yang sama secara terpisah, dengan satu baris per pasangan ulasan dan aspek. Panduan anotasi memuat taksonomi lima aspek pada Tabel 2.1, tiga kelas sentimen, dan aturan keputusan untuk kasus sulit, misalnya keluhan berbentuk harapan dinilai negatif.

Kesepakatan antar-anotator diukur dengan koefisien kappa Cohen pada dua tingkat sebagaimana persamaan (3.2): tingkat aspek, sebagai penandaan ada atau tidak ada untuk setiap pasangan ulasan dan aspek, dan tingkat sentimen, hanya pada pasangan yang ditandai oleh kedua anotator. *Pₒ* adalah proporsi kesepakatan teramati dan *Pₑ* proporsi kesepakatan yang diharapkan karena kebetulan. Nilai κ ditafsirkan menurut Landis dan Koch; label yang berbeda diselesaikan melalui diskusi sebelum data dipakai untuk pelatihan.

`κ = (Pₒ − Pₑ) / (1 − Pₑ)`  **(3.2)**

### Perancangan dan Pembangunan Sistem dengan SDLC Prototipe

Perancangan dan pembangunan sistem memakai SDLC model prototipe dengan dua iterasi sebagaimana Gambar 3.2 (Pressman dan Maxim 2020; Ningsih dan Nurfauziah 2023). Iterasi pertama menghasilkan prototipe yang berjalan dari berkas ulasan sampai halaman prioritas; iterasi kedua memperbaiki temuan evaluasi pertama dan menghasilkan prototipe final yang diuji pada tahap berikutnya.

> **[Sisipkan: Gambar 3.2 - Siklus SDLC prototipe dengan dua iterasi.png]**
> *Gambar 3.2 Siklus SDLC prototipe dengan dua iterasi*

**a. Analisis kebutuhan.** Kebutuhan dirumuskan dari rumusan masalah dan dicatat sebagai katalog kebutuhan fungsional (FR) dan non-fungsional (KNF) pada Tabel 3.2. Setiap kebutuhan memiliki kriteria lulus dan minimal satu kasus uji. Katalog disimpan sebagai satu berkas konfigurasi yang dibaca oleh kode, oleh pengujian keterlacakan, dan oleh naskah ini, sehingga persentase kebutuhan yang terlacak ke kasus uji dihitung otomatis.

**Tabel 3.2** Katalog kebutuhan fungsional dan non-fungsional

| Kode | Kebutuhan | Kriteria lulus | Kasus uji |
|---|---|---|---|
| FR-01 | Memuat dan memvalidasi berkas ulasan (review_id, teks, rating, tanggal, restoran) | Berkas tidak sah ditolak dengan pesan yang menuntun | U-01, U-09, S-01 |
| FR-02 | Membersihkan teks berbahasa Indonesia dan memecah klausa | Negasi tidak melintasi batas klausa; singkatan dipetakan | U-02 |
| FR-03 | Mengklasifikasi aspek (multi-label) dan sentimen per aspek | Setiap ulasan memperoleh prediksi sesuai kontrak | U-03, U-10, U-11, I-01 |
| FR-04 | Menghitung skor prioritas lima aspek dan menyimpan komponennya | 100% baris prioritas memuat volume, keparahan, keragaman, bobot | U-04, I-02 |
| FR-05 | Mengekstraksi frasa keluhan dominan per aspek | Lima frasa teratas per aspek, dapat ditelusuri ke ulasan | U-05 |
| FR-06 | Menyusun rekomendasi tindakan dari frasa pemicu | Setiap rekomendasi memuat aspek, pemicu, tindakan | U-06 |
| FR-07 | Menyimpan hasil ke basis data lokal dan menampilkannya di halaman | Halaman memuat hasil terakhir tanpa menghitung ulang | S-02, S-03 |
| FR-08 | Menguji sensitivitas bobot dan kesesuaian dengan pakar | Enam skenario sensitivitas; ρ per restoran dan uji Wilcoxon | U-07, U-08, U-12 |
| KNF-01 | Waktu analisis 1.000 ulasan | Rata-rata ≤ 60 detik dari lima ulangan | N-01 |
| KNF-02 | Berjalan tanpa jaringan | Halaman dan analisis ulang berjalan dengan jaringan dimatikan | N-02 |
| KNF-03 | Waktu muat halaman | ≤ 3 detik sampai peringkat tampil | N-03 |
| KNF-04 | Kompatibilitas peramban | Tampil benar di Chrome, Firefox, Edge | N-04 |
| KNF-05 | Lingkungan | Uji lulus di Python 3.11 dan 3.12 serta perangkat uji yang dicatat | N-05 |

*Sumber: Rancangan penelitian (2026), docs/PENGUJIAN.md*

**b. Desain cepat.** Desain mencakup arsitektur, kontrak data, modul keputusan, dan antarmuka. Arsitektur berbentuk klien-server dengan lima lapis sebagaimana Gambar 3.3. Lapis 1 memuat dan memvalidasi ulasan; lapis 2 membersihkan teks dan memecah klausa; lapis 3 mengklasifikasikan aspek dan sentimen; lapis 4 menghitung prioritas, frasa keluhan, dan rekomendasi; lapis 5 menyajikan hasil melalui antarmuka pemrograman aplikasi (API) REST berbasis FastAPI (5a) dan aplikasi web satu halaman berbasis React (5b), serta antarmuka baris perintah. Hasil setiap analisis beserta konfigurasi dan waktu per tahap disimpan di basis data SQLite lokal (Kreuzberger et al. 2023).

> **[Sisipkan: Gambar 3.3 - Arsitektur klien-server lima lapis prototipe.png]**
> *Gambar 3.3 Arsitektur klien-server lima lapis prototipe*

Data yang berpindah antar-lapis didefinisikan sebagai kontrak sebagaimana Gambar 3.4. Dokumen kontrak dan skema OpenAPI dibangkitkan langsung dari kode, dan respons API untuk hasil prioritas memakai struktur kontrak yang sama, sehingga dokumen, API, dan implementasi tidak dapat berbeda. Modul keputusan menghitung skor prioritas dengan persamaan (2.4)–(2.6) sebagaimana Gambar 3.5, dan seluruh komponen skor disimpan agar setiap peringkat dapat diaudit.

> **[Sisipkan: Gambar 3.4 - Alur data dan kontrak antar-lapis.png]**
> *Gambar 3.4 Alur data dan kontrak antar-lapis*

> **[Sisipkan: Gambar 3.5 - Komponen skor prioritas aspek.png]**
> *Gambar 3.5 Komponen skor prioritas aspek*

Antarmuka dirancang mengikuti tahapan penelitian: setiap halaman menyajikan bukti satu tahap, yaitu data, anotasi, kebutuhan, desain, iterasi prototipe, hasil prioritas, pengujian, validasi pakar, dan kesimpulan, sebagaimana Gambar 3.8. Halaman hanya membaca hasil yang tersimpan; bila bukti suatu tahap belum ada, halaman menampilkan perintah untuk membuatnya, bukan angka perkiraan. Seluruh aset antarmuka dibundel bersama aplikasi sehingga dapat berjalan tanpa jaringan.

> **[Sisipkan: Gambar 3.8 - Antarmuka web prototipe pada halaman hasil dan prioritas.png]**
> *Gambar 3.8 Antarmuka web prototipe pada halaman hasil dan prioritas*

**c. Pembangunan prototipe dan pemodelan NLP.** Inti analitik dibangun dengan Python, API dengan FastAPI, dan antarmuka dengan React dan TypeScript. Komponen NLP memakai TF-IDF (maksimum 20.000 fitur, n-gram 1–2, frekuensi dokumen minimum 2 dan maksimum 0,95, pembobotan sublinear) dan SVM linear dengan bobot kelas seimbang serta benih acak 42. Setiap perubahan kode disimpan di Git dalam *commit* kecil dan diuji otomatis melalui GitHub Actions.

**d. Evaluasi prototipe.** Pada akhir setiap iterasi, prototipe diperiksa terhadap katalog kebutuhan dan ketepatan klasifikasinya diukur dengan Macro-F1 dari validasi silang sepuluh lipatan yang dipisah per ulasan. Hasil setiap iterasi dicatat bersama nomor *commit* dan catatan perbaikannya, sehingga selisih Macro-F1 antara iterasi pertama dan kedua dapat ditelusuri ke perubahan yang menyebabkannya. Macro-F1 adalah bukti pendukung bahwa komponen klasifikasi layak dipakai, bukan hipotesis penelitian. Temuan evaluasi yang menuntut perubahan kebutuhan dikembalikan ke analisis kebutuhan, sedangkan temuan pengujian dikembalikan ke pembangunan prototipe.

### Pengujian Perangkat Lunak

Prototipe final diuji pada tingkat unit, integrasi, dan sistem dengan pytest (Valerian et al. 2025) sebagaimana Tabel 3.4. Uji sistem menjalankan antarmuka baris perintah sebagai proses terpisah, memanggil setiap titik akhir API, dan membuka setiap halaman antarmuka di peramban dengan Playwright. Setiap uji diberi penanda kode kasus sehingga status setiap kebutuhan dapat dibaca dari laporan pengujian. **Uji kritis** didefinisikan sebagai seluruh kasus uji yang terpetakan ke kebutuhan fungsional FR-01 sampai FR-08.

**Tabel 3.4** Kasus uji dan berkas pengujian

| Kode | Tingkat | Yang diuji | Berkas uji | Kebutuhan |
|---|---|---|---|---|
| U-01 | Unit | Kontrak data antar-lapis tidak berubah diam-diam | test_contracts.py | FR-01 |
| U-02 | Unit | Praproses: negasi, batas klausa, singkatan | test_preprocess.py | FR-02 |
| U-03 | Unit | Komponen SVM memenuhi kontrak | test_models.py | FR-03 |
| U-04 | Unit | Keparahan monoton terhadap rating; skor prioritas dan normalisasi | test_decision.py | FR-04 |
| U-05 | Unit | Frasa keluhan dominan per aspek | test_decision.py | FR-05 |
| U-06 | Unit | Aturan rekomendasi | test_decision.py | FR-06 |
| U-07 | Unit | Sensitivitas bobot ±10% dan normalisasi bobot | test_sensitivity.py | FR-08 |
| U-08 | Unit | ρ per restoran, uji Wilcoxon, kesesuaian peringkat pertama | test_expert.py | FR-08 |
| U-09 | Unit | Cakupan kandidat, pemilihan sampel purposive 8 restoran, laporan kekurangan | test_data_scope.py | FR-01 |
| U-10 | Unit | Kesepakatan antar-anotator (κ Cohen) | test_agreement.py | FR-03 |
| U-11 | Unit | Catatan iterasi prototipe dan selisih Macro-F1 | test_iterations.py | FR-03 |
| U-12 | Unit | Keputusan hipotesis RM1–RM3 | test_hypotheses.py | FR-08 |
| U-13 | Unit | Keterlacakan kebutuhan ke kasus uji | test_traceability.py |  |
| I-01 | Integrasi | Validasi silang dan metrik (aspek tanpa dukungan dihitung nol) | test_evaluate.py | FR-03 |
| I-02 | Integrasi | Alur menyeluruh dan masukan tidak sempurna | test_pipeline.py | FR-04 |
| S-01 | Sistem | Perintah baris perintah dijalankan sebagai proses terpisah | test_cli.py | FR-01 |
| S-02 | Sistem | API menyajikan setiap tahap dan hasil yang sama dengan basis data | test_api.py | FR-07 |
| S-03 | Sistem | Setiap halaman web tampil di peramban dan sama dengan API | test_e2e_web.py | FR-07 |
| N-03 | Non-fungsional | Waktu sampai peringkat tampil ≤ 3 detik (rata-rata 5 ulangan) | test_e2e_web.py | KNF-03 |

*Sumber: Repositori restaurant-review-analytics, folder tests (2026)*

Pengujian non-fungsional dijalankan sesuai skenario pada Tabel 3.5. Waktu proses diukur lima kali dan dinormalisasi per 1.000 ulasan, lalu dilaporkan sebagai rata-rata, simpangan baku, maksimum, serta waktu per tahap. Waktu muat halaman diukur otomatis dari permintaan halaman sampai baris peringkat pertama tampil. Spesifikasi perangkat, versi perangkat lunak, dan versi peramban dicatat.

**Tabel 3.5** Skenario pengujian non-fungsional

| Kode | Kondisi | Langkah | Kriteria lulus | Bukti |
|---|---|---|---|---|
| N-01 | 1.000 ulasan, perangkat uji Tabel 3.6 | Jalankan benchmark lima kali, cache dibersihkan antar-ulangan | Rata-rata ≤ 60 detik | reports/benchmark.json |
| N-02 | Jaringan dimatikan | Buka halaman, tekan hitung ulang analisis | Peringkat tampil dan hasil baru tersimpan | reports/manual/N-02.json, baris runs baru |
| N-03 | Basis data berisi hasil | Uji Playwright otomatis: waktu dari permintaan halaman sampai baris peringkat pertama tampil, lima ulangan | Rata-rata ≤ 3 detik | reports/pytest.xml (test_e2e_web.py) |
| N-04 | Chrome, Firefox, Edge versi terbaru | Buka sepuluh halaman tahapan, periksa tampilan dan galat konsol | Seluruh halaman tampil tanpa galat | reports/manual/N-04.json + tangkapan layar |
| N-05 | Python 3.11 dan 3.12 | Jalankan seluruh uji pada CI dan perangkat uji | Seluruh uji lulus | Riwayat GitHub Actions |

*Sumber: Rancangan penelitian (2026), docs/PENGUJIAN.md*

### Validasi Pakar

Validasi pakar dilakukan dengan meminta pakar, yaitu pengelola atau pemilik restoran dan akademisi bidang layanan makanan, menyusun urutan lima aspek untuk setiap restoran sampel berdasarkan pembacaan sampel ulasan. Urutan pakar dibandingkan dengan urutan sistem pada restoran yang sama memakai korelasi peringkat Spearman, lalu median ρ diuji dengan uji peringkat bertanda Wilcoxon (subbab 3.2). Uji sensitivitas menggeser setiap bobot ±10% dan melaporkan tau Kendall serta kesamaan aspek peringkat pertama.

Dua keterbatasan dicatat sejak awal. Pertama, dengan lima aspek per restoran, ρ hanya dapat bernilai pada langkah 0,1, sehingga satu pertukaran urutan sudah mengubah ρ secara nyata. Kedua, dengan n = 8 restoran, nilai p satu sisi terkecil yang dapat dicapai uji Wilcoxon adalah 1/2⁸ ≈ 0,0039, yaitu bila seluruh ρ melebihi 0,60; satu atau dua restoran yang tidak sesuai sudah dapat membuat H0 tidak ditolak. Hasil demikian tetap dilaporkan sebagai temuan.

### Analisis Hasil dan Penarikan Kesimpulan

Hasil pengujian dianalisis dengan prosedur pada subbab 3.2. Keputusan hipotesis dihitung oleh prototipe dari bukti yang tersimpan (laporan pengujian, hasil pengukuran waktu, dan urutan pakar) dan ditampilkan pada halaman kesimpulan. Setiap rumusan masalah dijawab oleh luaran pada Tabel 1.2, dan keterbatasan dibahas apa adanya, termasuk kekurangan ulasan pada restoran tertentu dan sifat frasa keluhan yang tidak menunjukkan sebab-akibat.

## Pengujian Hipotesis

Setiap rumusan masalah memiliki satu pasangan hipotesis, satu prosedur uji, dan satu kriteria keputusan sebagaimana Tabel 3.3. Bila H0 tidak ditolak, hasil tetap dilaporkan sebagai temuan dan rekomendasi perbaikannya diuraikan.

**Tabel 3.3** Hipotesis, prosedur uji, dan kriteria keputusan

| RM | H0 | H1 | Prosedur dan kriteria | Bila H0 tidak ditolak |
|---|---|---|---|---|
| 1 | Ada kontrak antar-lapis yang gagal validasi atau kebutuhan yang tidak terlacak ke kasus uji | 100% kontrak lolos validasi dan 100% kebutuhan terlacak ke minimal satu kasus uji | Validasi kontrak pada keluaran tiap lapis dan matriks keterlacakan Tabel 3.2; H1 diterima bila kedua proporsi 100% | Perbaiki kontrak atau tambah kasus uji pada iterasi prototipe berikutnya |
| 2 | Ada uji kritis yang gagal, atau rata-rata waktu proses > 60 detik per 1.000 ulasan | Seluruh uji kritis lulus dan rata-rata waktu ≤ 60 detik per 1.000 ulasan | pytest; benchmark lima ulangan; uji-t satu sampel satu sisi terhadap 60 detik, α = 0,05 | Telusuri tahap terlambat dari waktu per tahap, perbaiki, ukur ulang |
| 3 | Median ρ Spearman antar-restoran ≤ 0,60 | Median ρ Spearman antar-restoran > 0,60 | ρ per restoran; uji peringkat bertanda Wilcoxon satu sampel satu sisi terhadap 0,60, α = 0,05; kesesuaian aspek peringkat pertama | Laporkan sebagai temuan; tinjau bobot melalui uji sensitivitas, definisi komponen, atau cakupan frasa |

*Sumber: Rancangan penelitian (2026)*

Hipotesis rumusan masalah kedua diuji dengan uji-t satu sampel satu sisi terhadap batas 60 detik pada persamaan (3.3), dengan *x̄* rata-rata waktu proses per 1.000 ulasan dari lima ulangan, *μ₀* = 60 detik, *s* simpangan baku, dan *n* = 5. H0 ditolak bila *t* lebih kecil dari −*t*(0,05; 4) dan seluruh uji kritis lulus.

`t = (x̄ − μ₀) / (s / √n)`  **(3.3)**

Hipotesis rumusan masalah ketiga diuji dengan uji peringkat bertanda Wilcoxon satu sampel pada persamaan (3.4), dengan *dᵢ* = ρᵢ − 0,60 untuk setiap restoran dan *R*(|*dᵢ*|) peringkat nilai mutlaknya. H0 ditolak bila nilai p satu sisi kurang dari 0,05. Uji ini dipilih karena ρ per restoran tidak dapat diasumsikan berdistribusi normal dan jumlah aspek terlalu sedikit untuk uji per restoran.

`W⁺ = Σ R(|dᵢ|)  untuk semua dᵢ > 0`  **(3.4)**

## Alat dan Bahan Penelitian

Alat penelitian terdiri atas perangkat keras dan perangkat lunak pada Tabel 3.6. Seluruh pelatihan berjalan pada prosesor tanpa kartu grafis, versi minimum pustaka Python dicatat pada berkas kebutuhan, versi pustaka JavaScript dikunci pada berkas kunci paket, dan versi yang benar-benar terpasang dicatat saat pengujian agar lingkungan dapat dibangun ulang.

**Tabel 3.6** Alat penelitian

| Jenis | Nama | Versi atau spesifikasi | Kegunaan |
|---|---|---|---|
| Perangkat keras | Prosesor | Intel Core i5-12450H, 8 inti, 12 thread | Pelatihan dan pengujian |
| Perangkat keras | Memori | 14 GB DDR4 | Pemrosesan data |
| Perangkat keras | Kartu grafis | NVIDIA GeForce RTX 4050 6 GB (tidak dipakai) | – |
| Perangkat keras | Sistem operasi | Ubuntu 26.04 LTS 64 bit | Lingkungan uji |
| Perangkat lunak | Python | ≥ 3.11 | Bahasa pemrograman |
| Perangkat lunak | scikit-learn | ≥ 1.5 | TF-IDF, SVM linear, validasi silang |
| Perangkat lunak | pandas, NumPy, SciPy | ≥ 2.2, ≥ 2.0, ≥ 1.13 | Pengolahan data dan uji statistik |
| Perangkat lunak | FastAPI dan Uvicorn | ≥ 0.115, ≥ 0.30 | API REST lapis 5a dan skema OpenAPI |
| Perangkat lunak | React, TypeScript, Vite | 18.3, 5.6, 5.4 | Antarmuka web lapis 5b |
| Perangkat lunak | Node.js | ≥ 22 | Membangun antarmuka web |
| Perangkat lunak | Vitest | 2.1 | Uji komponen antarmuka |
| Perangkat lunak | SQLite | ≥ 3.40 | Basis data hasil dan jejak audit |
| Perangkat lunak | pytest | ≥ 8.0 | Uji unit, integrasi, sistem |
| Perangkat lunak | Playwright | ≥ 1.45 | Pengambilan data Google Maps dan uji sistem di peramban |
| Perangkat lunak | Git dan GitHub Actions | ≥ 2.40 | Kendali versi dan integrasi berkelanjutan |
| Perangkat lunak | Chrome, Firefox, Edge | Versi terbaru | Uji kompatibilitas peramban |

*Sumber: Dokumentasi perangkat penelitian dan requirements.txt (2026)*

Bahan penelitian disajikan pada Tabel 3.7.

**Tabel 3.7** Bahan penelitian

| Bahan | Jumlah | Keterangan |
|---|---|---|
| Restoran kandidat | 18 restoran | Restoran berulasan banyak di Jabodetabek yang lolos syarat awal (dari 25 kandidat) |
| Restoran sampel | 8 restoran | Purposive: urut jumlah ulasan dalam rentang tahun, maksimal dua per kategori |
| Target ulasan | ditetapkan dari data | min(tersedia, 625) per restoran sampel |
| Ulasan terkumpul | – | Ulasan berteks; tanggal berupa perkiraan dari penanda relatif Google Maps |
| Ulasan berlabel | 500 ulasan | Dilabeli dua anotator secara terpisah; kappa Cohen tingkat aspek dan sentimen |
| Aspek layanan | 5 aspek | Makanan, pelayanan, harga, suasana, fasilitas |
| Kelas sentimen | 3 kelas | Positif, negatif, netral |
| Data berlabel | Direncanakan | Dua anotator, minimal 150 ulasan tumpang tindih untuk koefisien kappa |
| Urutan pakar | 8 restoran | Urutan lima aspek per restoran sampel dari pakar |

*Sumber: Hasil pengumpulan data penelitian, Oktober 2026*

## Jadwal Penelitian

Penelitian direncanakan berlangsung tujuh bulan, dari November 2026 sampai Mei 2027, dengan urutan kegiatan mengikuti tahapan pada Gambar 3.1 sebagaimana Tabel 3.8.

**Tabel 3.8** Jadwal penelitian

| Kegiatan | Nov | Des | Jan | Feb | Mar | Apr | Mei |
|---|---|---|---|---|---|---|---|
| Identifikasi masalah dan studi literatur | ■ |  |  |  |  |  |  |
| Pengumpulan data (8 restoran) dan anotasi 500 ulasan | ■ | ■ |  |  |  |  |  |
| Perancangan sistem: analisis kebutuhan dan desain cepat | ■ | ■ |  |  |  |  |  |
| Iterasi prototipe 1: bangun dan evaluasi |  | ■ | ■ |  |  |  |  |
| Iterasi prototipe 2: perbaikan dan evaluasi |  |  | ■ | ■ |  |  |  |
| Pengujian unit, integrasi, sistem |  |  |  | ■ | ■ |  |  |
| Pengujian non-fungsional dan validasi pakar |  |  |  |  | ■ | ■ |  |
| Analisis hasil dan penulisan laporan |  |  |  |  |  | ■ | ■ |

*Sumber: Rencana penelitian November 2026 – Mei 2027*

