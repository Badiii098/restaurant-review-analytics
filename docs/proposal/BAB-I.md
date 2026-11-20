# BAB I PENDAHULUAN

## Latar Belakang

Usaha penyediaan makanan dan minuman di Indonesia telah melampaui 5,2 juta unit, dan sekitar 2,5 juta di antaranya berupa restoran atau rumah makan (Kementerian Pariwisata 2026). Jumlah usaha sebesar itu membuat mutu layanan menjadi pembeda utama, dan mutu layanan kini lebih banyak dinilai calon pelanggan melalui ulasan daring. Sebagian besar konsumen membaca ulasan sebelum memilih usaha lokal (BrightLocal 2026). Ulasan juga terbukti bernilai bagi usaha itu sendiri: sentimen per aspek pada ulasan daring memperbaiki ketepatan prediksi keberlangsungan restoran dibandingkan sentimen ulasan secara keseluruhan (Li et al. 2023).

Masalahnya, ulasan tumbuh jauh lebih cepat daripada kemampuan pemilik usaha membacanya. Penelitian pada skala besar menganalisis 112.412 ulasan restoran dalam enam bulan (Luo dan Xu 2021) dan 683.610 ulasan pada satu platform (Liu et al. 2022). Pada skala restoran tunggal pun, satu ulasan dapat memuji makanan sekaligus mengeluhkan pelayanan, sehingga rata-rata bintang tidak menunjukkan aspek mana yang perlu diperbaiki lebih dahulu. Analisis sentimen berbasis aspek (*aspect-based sentiment analysis*, ABSA) menjawab persoalan ini dengan memisahkan setiap ulasan menjadi aspek yang dibicarakan beserta polaritasnya (Hua et al. 2024).

Penelitian ABSA pada ulasan restoran berbahasa Indonesia sudah mencapai ketepatan tinggi. Pembobotan TF-IDF dengan Support Vector Machine (SVM) mencapai akurasi rata-rata 92% pada ulasan Depot Bamara (Firdaus et al. 2024), 92,74% pada ulasan rumah makan Ayam Goreng Nelongso (Salsabillah et al. 2024), dan 0,9289 pada ulasan Tong Tji Tea House (Saputra dan Suria 2025). Pendekatan lain memakai jaringan saraf tiruan dengan akurasi 89% (Brata et al. 2024) dan *fine-tuning* IndoBERT dengan akurasi 92,52–97,51% pada lima aspek (Latifah et al. 2026).

Ketepatan yang tinggi itu belum menjawab kebutuhan pengambil keputusan. Pada penelitian terdekat, rekomendasi perbaikan disusun melalui analisis akar masalah dan diskusi dengan pemangku kepentingan (Firdaus et al. 2024; Salsabillah et al. 2024), sedangkan peringkat keluhan disusun dari urutan frekuensi ulasan negatif (Brata et al. 2024). Keduanya tidak menyediakan rumus prioritas yang dapat diulang dan diaudit. Selain itu, tidak satu pun penelitian tersebut melaporkan pengujian perangkat lunaknya, padahal sistem pembelajaran mesin yang tidak dibangun dengan prinsip otomasi, reproduktibilitas, dan pemantauan sering gagal dipakai di luar eksperimen (Kreuzberger et al. 2023). Tinjauan sistematis atas 727 studi ABSA juga menemukan kurangnya keragaman dataset dan domain: 78,20% pemakaian dataset terpusat pada empat dataset tolok ukur SemEval ulasan restoran dan laptop berbahasa Inggris (Hua et al. 2024).

Berdasarkan celah tersebut, penelitian ini merancang dan menguji prototipe perangkat lunak berarsitektur lima lapis yang mengubah ulasan Google Maps menjadi urutan prioritas perbaikan layanan. Kelima lapis tersebut adalah data, praproses teks bahasa Indonesia, komponen model, modul keputusan, dan penyajian, dengan kontrak data yang tetap di antara lapis. Lapis penyajian berbentuk klien-server: antarmuka pemrograman aplikasi (API) REST yang membaca hasil tersimpan dan aplikasi web yang menampilkan bukti setiap tahap penelitian, sehingga prototipe dapat diperiksa tahap demi tahap. Komponen model memakai satu algoritma, yaitu TF-IDF dengan SVM linear, karena algoritma ini konsisten memberi hasil terbaik pada penelitian restoran Indonesia dan bobot fiturnya dapat ditelusuri. Modul keputusan menghitung skor prioritas komposit dari volume keluhan, keparahan, dan keragaman frasa keluhan dengan rumus terbuka, lalu urutannya dibandingkan dengan urutan pakar. Penelitian ini adalah penelitian rekayasa perangkat lunak, sehingga yang diuji adalah rancangan, kelulusan pengujian unit, integrasi, dan sistem, kinerja non-fungsional, serta keterlacakan keputusan, bukan peningkatan akurasi model.

Objek penelitian adalah ulasan publik Google Maps berbahasa Indonesia pada 8 restoran sampel di Jabodetabek. Sampel dipilih secara *purposive* dari 18 restoran kandidat berulasan banyak menurut kriteria tertulis, dan jumlah ulasan per restoran ditentukan dari data yang tersedia pada periode 2021–2026. Sebanyak 500 ulasan dilabeli oleh dua anotator, dan kesepakatannya diukur dengan koefisien kappa Cohen. Ulasan dinilai pada lima aspek layanan, yaitu makanan, pelayanan, harga, suasana, dan fasilitas. Kerangka pemikiran penelitian ditunjukkan pada Gambar 1.1.

> **[Sisipkan: Gambar 1.1 - Kerangka pemikiran penelitian.png]**
> *Gambar 1.1 Kerangka pemikiran penelitian*

## Rumusan Masalah

Berdasarkan latar belakang tersebut, rumusan masalah penelitian ini ditetapkan tiga butir. Setiap butir dijawab oleh luaran berupa artefak atau angka pada Bab IV, sebagaimana dirangkum pada Tabel 1.1.

1. Bagaimana rancangan arsitektur lima lapis prototipe analisis sentimen berbasis aspek untuk ulasan restoran berbahasa Indonesia beserta katalog kebutuhan dan kontrak antarmuka JSON antar-lapis?
2. Berapa persentase kasus uji unit, integrasi, dan sistem yang lulus, dan berapa waktu proses per 1.000 ulasan pada lingkungan uji yang dicatat, termasuk ketika jaringan tidak tersedia?
3. Aspek layanan mana yang menjadi prioritas perbaikan pertama pada setiap restoran berdasarkan skor komposit 0–100, dan berapa korelasi peringkatnya terhadap urutan pakar?

**Tabel 1.1** Rumusan masalah, tujuan khusus, dan luaran konkret

| No | Rumusan masalah | Tujuan khusus | Luaran konkret (dijawab di Bab IV) |
|---|---|---|---|
| 1 | Bagaimana rancangan arsitektur lima lapis prototipe analisis sentimen berbasis aspek untuk ulasan restoran berbahasa Indonesia beserta katalog kebutuhan dan kontrak antarmuka JSON antar-lapis? | Menghasilkan rancangan arsitektur, katalog kebutuhan fungsional dan non-fungsional, serta kontrak antarmuka antar-lapis | Diagram arsitektur lima lapis; katalog kebutuhan FR dan KNF bernomor; dokumen kontrak JSON per batas lapis (4.1) |
| 2 | Berapa persentase kasus uji unit, integrasi, dan sistem yang lulus, dan berapa waktu proses per 1.000 ulasan pada lingkungan uji yang dicatat, termasuk ketika jaringan tidak tersedia? | Menguji prototipe pada tingkat unit, integrasi, dan sistem serta mengukur kinerja non-fungsionalnya | Persentase lulus per tingkat uji; rata-rata dan simpangan baku waktu proses dari lima ulangan; status uji tanpa jaringan, waktu muat halaman, dan peramban (4.2) |
| 3 | Aspek layanan mana yang menjadi prioritas perbaikan pertama pada setiap restoran berdasarkan skor komposit 0–100, dan berapa korelasi peringkatnya terhadap urutan pakar? | Menghasilkan skor prioritas komposit dan menguji kesesuaian urutannya dengan urutan pakar | Tabel peringkat aspek per restoran beserta komponen skor; tiga frasa keluhan dominan per aspek; ρ per restoran, median ρ, dan hasil uji Wilcoxon (4.3) |

*Sumber: Rancangan penelitian (2026)*

## Batasan Masalah

Batasan berikut ditetapkan agar setiap klaim pada rumusan masalah memiliki batas uji yang jelas.

a) Data berupa ulasan publik Google Maps berbahasa Indonesia, termasuk campur kode, pada 8 restoran sampel di Jabodetabek. Sampel dipilih secara *purposive* dari 18 restoran kandidat (Jakarta Pusat 12, Jakarta Selatan 3, Jakarta Utara 1, Bekasi 1, Tangerang 1) dengan urutan jumlah ulasan pada periode 2021–2026 dan paling banyak 2 restoran per kategori masakan. Kandidat lain dari daftar awal 25 restoran dikeluarkan karena ulasan yang terkumpul kurang atau kosong.
b) Target ulasan per restoran adalah jumlah ulasan yang tersedia pada periode 2021–2026, dengan batas atas 625 ulasan. Restoran yang ulasannya di bawah batas tetap dianalisis dan kekurangannya dilaporkan. Nama restoran sampel dan realisasinya dilaporkan pada Bab IV.
c) Data berlabel terdiri atas 500 ulasan yang dilabeli seluruhnya oleh dua anotator; jumlah ini cukup untuk mengukur kesepakatan dan melatih komponen model, tetapi kecil untuk kelas yang jarang, sehingga kinerja klasifikasi dilaporkan sebagai bukti pendukung, bukan klaim utama.
d) Periode ulasan 2021–2026. Tanggal ulasan berupa perkiraan dari penanda relatif Google Maps, sehingga analisis tren bulanan tidak dilakukan. Pengambilan data berkala tidak dilakukan.
e) Aspek yang dinilai terbatas pada lima aspek tetap, yaitu makanan, pelayanan, harga, suasana, dan fasilitas. Penemuan aspek secara otomatis tidak dilakukan.
f) Sentimen dibagi menjadi tiga kelas, yaitu positif, negatif, dan netral. Sarkasme, emoji, dan ulasan berbahasa selain Indonesia tidak ditangani secara khusus.
g) Komponen model terbatas pada satu algoritma, yaitu TF-IDF dengan SVM linear. Penelitian tidak membandingkan algoritma dan tidak menguji penukaran model. Transformer, *deep learning*, dan model bahasa besar hanya dibahas pada tinjauan pustaka.
h) Skor prioritas memakai tiga komponen berbobot 0,40, 0,40, dan 0,20 yang ditetapkan peneliti, dengan uji sensitivitas pada pergeseran bobot ±10%. Pakar hanya menyusun urutan aspek, tidak menilai bobot.
i) Frasa keluhan yang dihasilkan menunjukkan keluhan yang paling menonjol, bukan hubungan sebab-akibat.
j) Pengujian perangkat lunak mencakup uji unit, integrasi, sistem, dan non-fungsional (waktu proses, tanpa jaringan, waktu muat halaman, peramban, lingkungan). Uji keamanan, penetrasi, beban ekstrem, dan skalabilitas cloud berada di luar lingkup.
k) Penelitian tidak mencakup uji penerimaan pengguna, evaluasi usability, maupun analisis sistem informasi multi-pengguna.
l) Sistem berupa prototipe web yang berjalan lokal tanpa akun pengguna, tanpa integrasi ke sistem kasir maupun API resmi Google, dan bukan produk produksi.

## Tujuan dan Manfaat Penelitian

### Tujuan Penelitian

Tujuan umum penelitian ini adalah merancang dan menguji prototipe perangkat lunak berarsitektur berlapis yang mengubah ulasan restoran berbahasa Indonesia menjadi urutan prioritas perbaikan layanan yang dapat diaudit. Tujuan khususnya adalah sebagai berikut.

1. Menghasilkan rancangan arsitektur lima lapis, katalog kebutuhan fungsional dan non-fungsional, serta kontrak antarmuka antar-lapis. Rancangan dinyatakan lengkap bila seluruh kontrak lolos validasi dan seluruh kebutuhan terlacak ke kasus uji.
2. Menguji prototipe pada tingkat unit, integrasi, dan sistem serta mengukur kinerja non-fungsionalnya. Kriterianya seluruh uji kritis lulus dan waktu proses rata-rata tidak melebihi 60 detik per 1.000 ulasan.
3. Menghasilkan skor prioritas komposit 0–100 per restoran dan menguji kesesuaian urutannya dengan urutan pakar. Kriterianya median koefisien korelasi peringkat Spearman antar-restoran lebih besar dari 0,60.

### Manfaat Penelitian

1. Bagi pengembangan ilmu, penelitian ini memberikan contoh rancangan sistem ABSA yang memisahkan klasifikasi dari pengambilan keputusan dan menguji keduanya sebagai perangkat lunak.
2. Bagi pemilik dan pengelola restoran, penelitian ini memberikan urutan aspek yang perlu diperbaiki lebih dahulu beserta angka penyusunnya, frasa keluhan, dan tindakan yang disarankan.
3. Bagi peneliti berikutnya, penelitian ini menyediakan kontrak data, kasus uji, dan prosedur pengukuran yang dapat dipakai ulang.

## Luaran Penelitian

Luaran penelitian dirinci pada Tabel 1.2. Setiap luaran terhubung dengan satu rumusan masalah dan dibahas pada Bab IV, sehingga keberhasilan penelitian dapat diperiksa butir demi butir.

**Tabel 1.2** Luaran penelitian terperinci

| Kode | Luaran | Spesifikasi | RM |
|---|---|---|---|
| L1 | Diagram arsitektur | Lima lapis (data, praproses, komponen model, modul keputusan, penyajian berupa API dan klien web) beserta aliran data dan batas kontrak antar-lapis | 1 |
| L2 | Katalog kebutuhan | Kebutuhan fungsional (FR) dan non-fungsional (KNF) bernomor, masing-masing dengan kriteria lulus dan kode kasus uji, serta matriks keterlacakan | 1 |
| L3 | Kontrak antarmuka JSON | Satu skema per batas lapis: ulasan mentah, ulasan bersih, prediksi aspek-sentimen, statistik aspek, prioritas, frasa keluhan, rekomendasi; dokumen kontrak dan skema OpenAPI API dibangkitkan dari kode | 1 |
| L4 | Pipeline klasifikasi | TF-IDF (maksimum 20.000 fitur, n-gram 1–2, min_df 2, max_df 0,95, sublinear) dan SVM linear satu-lawan-semua; satu model; seed 42; Macro-F1 validasi silang tercatat untuk iterasi 1 dan 2 | 1 |
| L5 | Laporan uji unit dan integrasi | Persentase lulus per berkas uji dan per lapis, diambil dari keluaran pytest | 2 |
| L6 | Laporan uji sistem | Alur end-to-end dari berkas ulasan sampai halaman peringkat, termasuk masukan tidak sempurna (rating kosong, duplikat, ulasan tanpa aspek), pemanggilan setiap titik akhir API, dan pembukaan setiap halaman di peramban | 2 |
| L7 | Laporan uji non-fungsional | Waktu proses per 1.000 ulasan (lima ulangan, rata-rata, simpangan, maksimum, waktu per tahap), mode tanpa jaringan, waktu muat halaman, tiga peramban, spesifikasi perangkat | 2 |
| L8 | Prototipe web | API REST (FastAPI) dan aplikasi web (React) dengan satu halaman per tahap penelitian: data, anotasi, kebutuhan, desain, iterasi, hasil, pengujian, validasi pakar, dan kesimpulan; membaca hasil tersimpan, tombol hitung ulang, tanpa akun pengguna | 2 |
| L9 | Modul skor prioritas | Prioritas = 0,4·Volume + 0,4·Keparahan + 0,2·Keragaman, skala tampil 0–100, komponen tersimpan per hasil | 3 |
| L10 | Uji sensitivitas bobot | Setiap bobot digeser ±10%, dilaporkan tau Kendall dan kesamaan aspek peringkat pertama | 3 |
| L11 | Frasa keluhan dominan | n-gram hingga tiga kata pada klausa bernada keluhan, frekuensi minimum tiga, lima teratas per aspek, dapat ditelusuri ke ulasan asal | 3 |
| L12 | Rekomendasi berbasis aturan | Pemetaan frasa pemicu ke tindakan menurut aspek layanan | 3 |
| L13 | Data penelitian dan data berlabel | Sampel purposive 8 restoran Jabodetabek (dari 18 kandidat) dengan target ulasan per restoran min(tersedia, 625); 500 ulasan berlabel dua anotator dengan koefisien kappa aspek dan sentimen | 3 |
| L14 | Uji kesesuaian dengan pakar | Urutan aspek pakar per restoran, ρ per restoran, median ρ, uji Wilcoxon, kesesuaian aspek peringkat pertama | 3 |

*Sumber: Rancangan penelitian (2026)*

## Sistematika Penulisan

Sistematika penulisan laporan penelitian ini adalah sebagai berikut.

**BAB I PENDAHULUAN.** Bab ini berisi latar belakang, rumusan masalah, batasan masalah, tujuan dan manfaat, luaran penelitian, serta sistematika penulisan.

**BAB II TINJAUAN PUSTAKA.** Bab ini berisi teori analisis sentimen berbasis aspek, aspek layanan restoran, teknik penentuan sampel, praproses teks, TF-IDF, SVM, metrik evaluasi klasifikasi, skor prioritas, arsitektur berlapis dan klien-server, SDLC model prototipe, pengujian perangkat lunak, kesepakatan anotator dan uji statistik, perumusan hipotesis, dan penelitian terdahulu.

**BAB III METODE PENELITIAN.** Bab ini berisi tahapan penelitian (identifikasi masalah, studi literatur, pengumpulan data, anotasi data, perancangan dan pembangunan sistem dengan SDLC model prototipe, pengujian perangkat lunak, validasi pakar, serta analisis dan kesimpulan), pengujian hipotesis, alat dan bahan, serta jadwal penelitian.

**BAB IV HASIL DAN PEMBAHASAN.** Bab ini berisi sampel dan data berlabel beserta nilai kappa, rancangan arsitektur dan kontrak, hasil dua iterasi prototipe dengan Macro-F1, hasil pengujian perangkat lunak dan kinerja, peringkat prioritas beserta uji kesesuaiannya dengan pakar, dan pembahasan luaran L1–L14.

**BAB V PENUTUP.** Bab ini berisi kesimpulan yang menjawab setiap rumusan masalah dan saran bagi pemilik restoran serta penelitian berikutnya.

