"""Isi BAB I PENDAHULUAN."""

from __future__ import annotations

from scripts.proposal.fakta import angka, fakta
from scripts.proposal.pustaka import c


def blok() -> list[tuple]:
    f = fakta()
    s = f["sampling"]
    n, kand, total = s["n"], f["n_restoran"], f["total"]
    tahun = f"{s['rentang'][0]}–{s['rentang'][1]}"
    sebaran = ", ".join(f"{k} {v}" for k, v in f["kota"].items())
    return [
    ("h1", "PENDAHULUAN"),
    ("h2", "Latar Belakang"),
    ("p", "Usaha penyediaan makanan dan minuman di Indonesia telah melampaui 5,2 juta unit, dan sekitar 2,5 juta di antaranya berupa restoran atau rumah makan " + c("kemenpar2026") + ". Jumlah usaha sebesar itu membuat mutu layanan menjadi pembeda utama, dan mutu layanan kini lebih banyak dinilai calon pelanggan melalui ulasan daring. Sebagian besar konsumen membaca ulasan sebelum memilih usaha lokal " + c("brightlocal2026") + ". Ulasan juga terbukti bernilai bagi usaha itu sendiri: sentimen per aspek pada ulasan daring memperbaiki ketepatan prediksi keberlangsungan restoran dibandingkan sentimen ulasan secara keseluruhan " + c("li2023") + "."),
    ("p", "Masalahnya, ulasan tumbuh jauh lebih cepat daripada kemampuan pemilik usaha membacanya. Penelitian pada skala besar menganalisis 112.412 ulasan restoran dalam enam bulan " + c("luo2021") + " dan 683.610 ulasan pada satu platform " + c("liu2022") + ". Pada skala restoran tunggal pun, satu ulasan dapat memuji makanan sekaligus mengeluhkan pelayanan, sehingga rata-rata bintang tidak menunjukkan aspek mana yang perlu diperbaiki lebih dahulu. Analisis sentimen berbasis aspek (*aspect-based sentiment analysis*, ABSA) menjawab persoalan ini dengan memisahkan setiap ulasan menjadi aspek yang dibicarakan beserta polaritasnya " + c("hua2024") + "."),
    ("p", "Penelitian ABSA pada ulasan restoran berbahasa Indonesia sudah mencapai ketepatan tinggi. Pembobotan TF-IDF dengan Support Vector Machine (SVM) mencapai akurasi rata-rata 92% pada ulasan Depot Bamara " + c("firdaus2024") + ", 92,74% pada ulasan rumah makan Ayam Goreng Nelongso " + c("salsabillah2024") + ", dan 0,9289 pada ulasan Tong Tji Tea House " + c("saputra2025") + ". Pendekatan lain memakai jaringan saraf tiruan dengan akurasi 89% " + c("brata2024") + " dan *fine-tuning* IndoBERT dengan akurasi 92,52–97,51% pada lima aspek " + c("latifah2026") + "."),
    ("p", "Ketepatan yang tinggi itu belum menjawab kebutuhan pengambil keputusan. Pada penelitian terdekat, rekomendasi perbaikan disusun melalui analisis akar masalah dan diskusi dengan pemangku kepentingan " + c("firdaus2024", "salsabillah2024") + ", sedangkan peringkat keluhan disusun dari urutan frekuensi ulasan negatif " + c("brata2024") + ". Keduanya tidak menyediakan rumus prioritas yang dapat diulang dan diaudit. Selain itu, tidak satu pun penelitian tersebut melaporkan pengujian perangkat lunaknya, padahal sistem pembelajaran mesin yang tidak dibangun dengan prinsip otomasi, reproduktibilitas, dan pemantauan sering gagal dipakai di luar eksperimen " + c("kreuzberger2023") + ". Tinjauan sistematis atas 727 studi ABSA juga menemukan kurangnya keragaman dataset dan domain: 78,20% pemakaian dataset terpusat pada empat dataset tolok ukur SemEval ulasan restoran dan laptop berbahasa Inggris " + c("hua2024") + "."),
    ("p", "Berdasarkan celah tersebut, penelitian ini merancang dan menguji prototipe perangkat lunak berarsitektur lima lapis yang mengubah ulasan Google Maps menjadi urutan prioritas perbaikan layanan. Kelima lapis tersebut adalah data, praproses teks bahasa Indonesia, komponen model, modul keputusan, dan penyajian, dengan kontrak data yang tetap di antara lapis. Lapis penyajian berbentuk klien-server: antarmuka pemrograman aplikasi (API) REST yang membaca hasil tersimpan dan aplikasi web yang menampilkan bukti setiap tahap penelitian, sehingga prototipe dapat diperiksa tahap demi tahap. Komponen model memakai satu algoritma, yaitu TF-IDF dengan SVM linear, karena algoritma ini konsisten memberi hasil terbaik pada penelitian restoran Indonesia dan bobot fiturnya dapat ditelusuri. Modul keputusan menghitung skor prioritas komposit dari volume keluhan, keparahan, dan keragaman frasa keluhan dengan rumus terbuka, lalu urutannya dibandingkan dengan urutan pakar. Penelitian ini adalah penelitian rekayasa perangkat lunak, sehingga yang diuji adalah rancangan, kelulusan pengujian unit, integrasi, dan sistem, kinerja non-fungsional, serta keterlacakan keputusan, bukan peningkatan akurasi model."),
    ("p", f"Objek penelitian adalah ulasan publik Google Maps berbahasa Indonesia pada {n} restoran sampel di Jabodetabek. Sampel dipilih secara *purposive* dari {kand} restoran kandidat berulasan banyak menurut kriteria tertulis, dan jumlah ulasan per restoran ditentukan dari data yang tersedia pada periode {tahun}. " + (f"Hingga Oktober 2026 terkumpul {angka(total)} ulasan berteks dari seluruh kandidat. " if total else "") + "Sebanyak 500 ulasan dilabeli oleh dua anotator, dan kesepakatannya diukur dengan koefisien kappa Cohen. Ulasan dinilai pada lima aspek layanan, yaitu makanan, pelayanan, harga, suasana, dan fasilitas. Kerangka pemikiran penelitian ditunjukkan pada Gambar 1.1."),
    ("gambar", "1.1", 15.5),
    ("h2", "Rumusan Masalah"),
    ("p", "Berdasarkan latar belakang tersebut, rumusan masalah penelitian ini ditetapkan tiga butir. Setiap butir dijawab oleh luaran berupa artefak atau angka pada Bab IV, sebagaimana dirangkum pada Tabel 1.1."),
    ("list", [
        "Bagaimana rancangan arsitektur lima lapis prototipe analisis sentimen berbasis aspek untuk ulasan restoran berbahasa Indonesia beserta katalog kebutuhan dan kontrak antarmuka JSON antar-lapis?",
        "Berapa persentase kasus uji unit, integrasi, dan sistem yang lulus, dan berapa waktu proses per 1.000 ulasan pada lingkungan uji yang dicatat, termasuk ketika jaringan tidak tersedia?",
        "Aspek layanan mana yang menjadi prioritas perbaikan pertama pada setiap restoran berdasarkan skor komposit 0–100, dan berapa korelasi peringkatnya terhadap urutan pakar?",
    ], "1"),
    ("tabel", "1.1"),
    ("h2", "Batasan Masalah"),
    ("p", "Batasan berikut ditetapkan agar setiap klaim pada rumusan masalah memiliki batas uji yang jelas."),
    ("list", [
        f"Data berupa ulasan publik Google Maps berbahasa Indonesia, termasuk campur kode, pada {n} restoran sampel di Jabodetabek. Sampel dipilih secara *purposive* dari {kand} restoran kandidat ({sebaran}) dengan urutan jumlah ulasan pada periode {tahun} dan paling banyak {s['maks_per_kategori']} restoran per kategori masakan. Kandidat lain dari daftar awal 25 restoran dikeluarkan karena ulasan yang terkumpul kurang atau kosong.",
        f"Target ulasan per restoran adalah jumlah ulasan yang tersedia pada periode {tahun}, dengan batas atas {angka(s['batas_target'])} ulasan. Restoran yang ulasannya di bawah batas tetap dianalisis dan kekurangannya dilaporkan. Nama restoran sampel dan realisasinya dilaporkan pada Bab IV.",
        "Data berlabel terdiri atas 500 ulasan yang dilabeli seluruhnya oleh dua anotator; jumlah ini cukup untuk mengukur kesepakatan dan melatih komponen model, tetapi kecil untuk kelas yang jarang, sehingga kinerja klasifikasi dilaporkan sebagai bukti pendukung, bukan klaim utama.",
        f"Periode ulasan {tahun}. Tanggal ulasan berupa perkiraan dari penanda relatif Google Maps, sehingga analisis tren bulanan tidak dilakukan. Pengambilan data berkala tidak dilakukan.",
        "Aspek yang dinilai terbatas pada lima aspek tetap, yaitu makanan, pelayanan, harga, suasana, dan fasilitas. Penemuan aspek secara otomatis tidak dilakukan.",
        "Sentimen dibagi menjadi tiga kelas, yaitu positif, negatif, dan netral. Sarkasme, emoji, dan ulasan berbahasa selain Indonesia tidak ditangani secara khusus.",
        "Komponen model terbatas pada satu algoritma, yaitu TF-IDF dengan SVM linear. Penelitian tidak membandingkan algoritma dan tidak menguji penukaran model. Transformer, *deep learning*, dan model bahasa besar hanya dibahas pada tinjauan pustaka.",
        "Skor prioritas memakai tiga komponen berbobot 0,40, 0,40, dan 0,20 yang ditetapkan peneliti, dengan uji sensitivitas pada pergeseran bobot ±10%. Pakar hanya menyusun urutan aspek, tidak menilai bobot.",
        "Frasa keluhan yang dihasilkan menunjukkan keluhan yang paling menonjol, bukan hubungan sebab-akibat.",
        "Pengujian perangkat lunak mencakup uji unit, integrasi, sistem, dan non-fungsional (waktu proses, tanpa jaringan, waktu muat halaman, peramban, lingkungan). Uji keamanan, penetrasi, beban ekstrem, dan skalabilitas cloud berada di luar lingkup.",
        "Penelitian tidak mencakup uji penerimaan pengguna, evaluasi usability, maupun analisis sistem informasi multi-pengguna.",
        "Sistem berupa prototipe web yang berjalan lokal tanpa akun pengguna, tanpa integrasi ke sistem kasir maupun API resmi Google, dan bukan produk produksi.",
    ], "a"),
    ("h2", "Tujuan dan Manfaat Penelitian"),
    ("h3", "Tujuan Penelitian"),
    ("p", "Tujuan umum penelitian ini adalah merancang dan menguji prototipe perangkat lunak berarsitektur berlapis yang mengubah ulasan restoran berbahasa Indonesia menjadi urutan prioritas perbaikan layanan yang dapat diaudit. Tujuan khususnya adalah sebagai berikut."),
    ("list", [
        "Menghasilkan rancangan arsitektur lima lapis, katalog kebutuhan fungsional dan non-fungsional, serta kontrak antarmuka antar-lapis. Rancangan dinyatakan lengkap bila seluruh kontrak lolos validasi dan seluruh kebutuhan terlacak ke kasus uji.",
        "Menguji prototipe pada tingkat unit, integrasi, dan sistem serta mengukur kinerja non-fungsionalnya. Kriterianya seluruh uji kritis lulus dan waktu proses rata-rata tidak melebihi 60 detik per 1.000 ulasan.",
        "Menghasilkan skor prioritas komposit 0–100 per restoran dan menguji kesesuaian urutannya dengan urutan pakar. Kriterianya median koefisien korelasi peringkat Spearman antar-restoran lebih besar dari 0,60.",
    ], "1"),
    ("h3", "Manfaat Penelitian"),
    ("list", [
        "Bagi pengembangan ilmu, penelitian ini memberikan contoh rancangan sistem ABSA yang memisahkan klasifikasi dari pengambilan keputusan dan menguji keduanya sebagai perangkat lunak.",
        "Bagi pemilik dan pengelola restoran, penelitian ini memberikan urutan aspek yang perlu diperbaiki lebih dahulu beserta angka penyusunnya, frasa keluhan, dan tindakan yang disarankan.",
        "Bagi peneliti berikutnya, penelitian ini menyediakan kontrak data, kasus uji, dan prosedur pengukuran yang dapat dipakai ulang.",
    ], "1"),
    ("h2", "Luaran Penelitian"),
    ("p", "Luaran penelitian dirinci pada Tabel 1.2. Setiap luaran terhubung dengan satu rumusan masalah dan dibahas pada Bab IV, sehingga keberhasilan penelitian dapat diperiksa butir demi butir."),
    ("tabel", "1.2"),
    ("h2", "Sistematika Penulisan"),
    ("p", "Sistematika penulisan laporan penelitian ini adalah sebagai berikut."),
    ("p", "**BAB I PENDAHULUAN.** Bab ini berisi latar belakang, rumusan masalah, batasan masalah, tujuan dan manfaat, luaran penelitian, serta sistematika penulisan."),
    ("p", "**BAB II TINJAUAN PUSTAKA.** Bab ini berisi teori analisis sentimen berbasis aspek, aspek layanan restoran, teknik penentuan sampel, praproses teks, TF-IDF, SVM, metrik evaluasi klasifikasi, skor prioritas, arsitektur berlapis dan klien-server, SDLC model prototipe, pengujian perangkat lunak, kesepakatan anotator dan uji statistik, perumusan hipotesis, dan penelitian terdahulu."),
    ("p", "**BAB III METODE PENELITIAN.** Bab ini berisi tahapan penelitian (identifikasi masalah, studi literatur, pengumpulan data, anotasi data, perancangan dan pembangunan sistem dengan SDLC model prototipe, pengujian perangkat lunak, validasi pakar, serta analisis dan kesimpulan), pengujian hipotesis, alat dan bahan, serta jadwal penelitian."),
    ("p", "**BAB IV HASIL DAN PEMBAHASAN.** Bab ini berisi sampel dan data berlabel beserta nilai kappa, rancangan arsitektur dan kontrak, hasil dua iterasi prototipe dengan Macro-F1, hasil pengujian perangkat lunak dan kinerja, peringkat prioritas beserta uji kesesuaiannya dengan pakar, dan pembahasan luaran L1–L14."),
    ("p", "**BAB V PENUTUP.** Bab ini berisi kesimpulan yang menjawab setiap rumusan masalah dan saran bagi pemilik restoran serta penelitian berikutnya."),
    ]
