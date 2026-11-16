"""Isi BAB III METODE PENELITIAN."""

from __future__ import annotations

from scripts.proposal.fakta import angka, fakta
from scripts.proposal.pustaka import c


def blok() -> list[tuple]:
    f = fakta()
    total = angka(f["total"])
    pct_rentang = angka(100 * f["dalam_rentang"] / f["total"], 1)
    return [
    ("h1", "METODE PENELITIAN"),
    ("p", "Penelitian ini adalah penelitian rekayasa perangkat lunak dengan pendekatan kuantitatif. Tahapan penelitian ditunjukkan pada Gambar 3.1. Model pengembangan prototipe ditempatkan pada tahap perancangan sistem, sedangkan setiap rumusan masalah dijawab oleh satu hipotesis dengan prosedur dan kriteria keputusan yang dapat diulang."),
    ("gambar", "3.1", 13),
    ("h2", "Tahapan Penelitian"),
    ("h3", "Identifikasi Masalah"),
    ("p", "Masalah diidentifikasi dari kebutuhan pemilik restoran untuk mengetahui aspek layanan yang perlu diperbaiki lebih dahulu dan dari celah penelitian terdahulu yang berhenti pada ketepatan model " + c("firdaus2024", "salsabillah2024", "brata2024") + ". Keluaran tahap ini adalah tiga rumusan masalah, tujuan, dan luaran pada Bab I."),
    ("h3", "Pengumpulan Data"),
    ("p", f"Data adalah ulasan publik Google Maps berbahasa Indonesia. Sampel dipilih secara *purposive* dari 25 restoran kandidat di Jabodetabek yang memiliki banyak ulasan. Sebanyak {f['n_restoran']} restoran dianalisis, sedangkan tujuh restoran dikeluarkan karena ulasan yang terkumpul kurang dari 210 atau kosong. Target ditetapkan {f['target_per_restoran']} ulasan per restoran, sehingga total target {angka(f['target_total'])} ulasan, di atas ambang minimum {angka(f['ambang_total'])}. Dengan 280 ulasan, proporsi ulasan negatif per restoran dapat diduga dengan margin galat maksimum ±5,9% pada tingkat kepercayaan 95%."),
    ("p", "Ulasan diambil dengan Playwright dari halaman Google Maps yang diurutkan berdasarkan ulasan terbaru, dengan jeda acak antar-gulir dan tanpa pengambilan paralel. Hanya ulasan publik yang diambil; nama penulis tidak dimuat dalam laporan. Kriteria inklusi adalah ulasan berteks berbahasa Indonesia, terbit 2021–2026, dan membahas minimal satu aspek. Ulasan tanpa teks, berisi simbol saja, duplikat, atau di luar rentang tahun ditandai, bukan dihapus, agar jumlah sebelum dan sesudah penyaringan dapat dilaporkan."),
    ("p", f"Hingga Oktober 2026 terkumpul {total} ulasan, dengan {angka(f['dalam_rentang'])} ulasan ({pct_rentang}%) berada pada periode 2021–2026. Seluruh tanggal berupa perkiraan dari penanda relatif seperti \"2 tahun lalu\". Rencana sampel dan realisasinya disajikan pada Tabel 3.1, Gambar 3.6, dan Gambar 3.7; hanya satu restoran yang berada di bawah target."),
    ("tabel", "3.1"),
    ("gambar", "3.6", 14),
    ("gambar", "3.7", 14),
    ("p", "Data latih diperoleh melalui anotasi oleh dua anotator secara terpisah dengan satu baris per pasangan ulasan dan aspek. Panduan anotasi memuat taksonomi pada Tabel 2.1 dan aturan keputusan untuk kasus sulit, misalnya keluhan berbentuk harapan dinilai negatif. Minimal 150 ulasan dinilai oleh kedua anotator untuk menghitung koefisien kappa aspek dan sentimen secara terpisah. Bila kappa kurang dari 0,61, aturan diperjelas dan anotasi diulang " + c("landis1977") + "."),
    ("h3", "Studi Literatur"),
    ("p", "Studi literatur dilakukan pada publikasi ABSA ulasan restoran, arsitektur sistem pembelajaran mesin, SDLC, dan pengujian perangkat lunak. Hasilnya adalah landasan teori dan pemetaan penelitian terdahulu pada Bab II, yang menetapkan pilihan TF-IDF dan SVM serta posisi kontribusi penelitian."),
    ("h3", "Perancangan Sistem"),
    ("p", "Perancangan sistem memakai SDLC model prototipe dengan dua iterasi sebagaimana Gambar 3.2. Iterasi pertama menghasilkan prototipe yang berjalan dari berkas ulasan sampai halaman peringkat; iterasi kedua memperbaiki temuan evaluasi pertama dan menghasilkan prototipe final yang diuji pada tahap berikutnya " + c("pressman2020", "ningsih2023") + "."),
    ("gambar", "3.2", 15),
    ("p", "**a. Analisis kebutuhan.** Kebutuhan dirumuskan dari rumusan masalah dan dicatat sebagai katalog kebutuhan fungsional (FR) dan non-fungsional (KNF). Setiap kebutuhan memiliki kriteria lulus dan kasus uji, sehingga keterlacakan kebutuhan ke pengujian dapat diperiksa. Katalog kebutuhan disajikan pada Tabel 3.2."),
    ("tabel", "3.2"),
    ("p", "**b. Desain cepat.** Desain mencakup arsitektur, kontrak data, modul keputusan, dan antarmuka. Arsitektur terdiri atas lima lapis sebagaimana Gambar 3.3. Lapis data memuat dan memvalidasi ulasan; lapis praproses membersihkan teks dan memecah klausa; lapis komponen model mengklasifikasikan aspek dan sentimen; lapis modul keputusan menghitung prioritas, frasa keluhan, dan rekomendasi; lapis antarmuka menampilkan hasil. Hasil setiap analisis beserta konfigurasi dan waktu per tahap disimpan di basis data SQLite lokal " + c("kreuzberger2023") + "."),
    ("gambar", "3.3", 14),
    ("p", "Data yang berpindah antar-lapis didefinisikan sebagai kontrak sebagaimana Gambar 3.4. Dokumen kontrak dibangkitkan langsung dari kode, sehingga dokumen dan implementasi tidak dapat berbeda. Modul keputusan menghitung skor prioritas dengan persamaan (2.4)–(2.6) sebagaimana Gambar 3.5, dan seluruh komponen skor disimpan agar setiap peringkat dapat diaudit."),
    ("gambar", "3.4", 15),
    ("gambar", "3.5", 13),
    ("p", "Antarmuka dirancang sebagai lembar laporan keputusan, bukan dasbor pemantauan. Halaman berurutan dari ringkasan, peringkat prioritas, frasa keluhan dominan, tindakan yang disarankan, sampai bahan audit sebagaimana Gambar 3.8. Antarmuka hanya membaca basis data dan tidak menghitung skor sendiri, sehingga angka di layar sama dengan arsip."),
    ("gambar", "3.8", 15),
    ("p", "**c. Pembangunan prototipe.** Prototipe dibangun dengan Python. Komponen model memakai TF-IDF (maksimum 20.000 fitur, n-gram 1–2, frekuensi dokumen minimum 2 dan maksimum 0,95, pembobotan sublinear) dan SVM linear dengan bobot kelas seimbang serta benih acak 42. Setiap perubahan kode disimpan di Git dalam *commit* kecil dan diuji otomatis melalui GitHub Actions."),
    ("p", "**d. Evaluasi dan perbaikan.** Pada akhir setiap iterasi, prototipe dijalankan pada data nyata dan diperiksa terhadap katalog kebutuhan. Temuan evaluasi, misalnya galat pada kasus data tertentu atau tampilan yang menyesatkan, dicatat dan diperbaiki pada iterasi berikutnya. Ketepatan klasifikasi dilaporkan dengan Macro-F1 dari validasi silang sepuluh lipatan yang dipisah per ulasan, sebagai bukti pendukung bahwa komponen klasifikasi layak dipakai, bukan sebagai hipotesis."),
    ("h3", "Pengujian"),
    ("p", "Prototipe final diuji pada tingkat unit, integrasi, dan sistem dengan pytest " + c("valerian2025") + ". Kasus uji dan berkas pengujiannya disajikan pada Tabel 3.4. Uji sistem antarmuka baris perintah dijalankan sebagai proses terpisah, dan uji halaman merender antarmuka dari basis data hasil yang sebenarnya."),
    ("tabel", "3.4"),
    ("p", "Pengujian non-fungsional dijalankan sesuai skenario pada Tabel 3.5. Waktu proses diukur lima kali pada 1.000 ulasan dengan cache dibersihkan antar-ulangan, dan dilaporkan sebagai rata-rata, simpangan baku, maksimum, serta waktu per tahap. Spesifikasi perangkat, versi perangkat lunak, dan versi peramban dicatat."),
    ("tabel", "3.5"),
    ("p", "Uji kesesuaian dengan pakar dilakukan dengan meminta pakar, yaitu pengelola atau pemilik restoran dan akademisi bidang layanan makanan, menyusun urutan lima aspek untuk setiap restoran berdasarkan pembacaan sampel ulasan. Urutan pakar dibandingkan dengan urutan sistem pada restoran yang sama. Uji sensitivitas menggeser setiap bobot ±10% dan melaporkan tau Kendall serta kesamaan aspek peringkat pertama."),
    ("h3", "Analisis Hasil dan Penarikan Kesimpulan"),
    ("p", "Hasil pengujian dianalisis dengan prosedur pada subbab 3.2. Setiap rumusan masalah dijawab oleh luaran pada Tabel 1.2, dan keterbatasan dibahas apa adanya, termasuk kekurangan ulasan pada restoran tertentu dan sifat frasa keluhan yang tidak menunjukkan sebab-akibat."),
    ("h2", "Pengujian Hipotesis"),
    ("p", "Setiap rumusan masalah memiliki satu pasangan hipotesis, satu prosedur uji, dan satu kriteria keputusan sebagaimana Tabel 3.3. Bila H0 tidak ditolak, hasil tetap dilaporkan sebagai temuan dan rekomendasi perbaikannya diuraikan."),
    ("tabel", "3.3"),
    ("p", "Hipotesis rumusan masalah kedua diuji dengan uji-t satu sampel satu sisi terhadap batas 60 detik pada persamaan (3.1), dengan *x̄* rata-rata waktu proses dari lima ulangan, *μ₀* = 60 detik, *s* simpangan baku, dan *n* = 5. H0 ditolak bila *t* lebih kecil dari −*t*(0,05; 4)."),
    ("rumus", "t = (x̄ − μ₀) / (s / √n)", "3.1"),
    ("p", "Hipotesis rumusan masalah ketiga diuji dengan uji peringkat bertanda Wilcoxon satu sampel pada persamaan (3.2), dengan *dᵢ* = ρᵢ − 0,60 untuk setiap restoran dan *R*(|*dᵢ*|) peringkat nilai mutlaknya. H0 ditolak bila nilai p satu sisi kurang dari 0,05. Uji ini dipilih karena ρ per restoran tidak dapat diasumsikan berdistribusi normal dan jumlah aspek terlalu sedikit untuk uji per restoran."),
    ("rumus", "W⁺ = Σ R(|dᵢ|)  untuk semua dᵢ > 0", "3.2"),
    ("h2", "Alat dan Bahan Penelitian"),
    ("p", "Alat penelitian terdiri atas perangkat keras dan perangkat lunak pada Tabel 3.6. Seluruh pelatihan berjalan pada prosesor tanpa kartu grafis, dan versi pustaka dikunci pada berkas kebutuhan agar lingkungan dapat dibangun ulang."),
    ("tabel", "3.6"),
    ("p", "Bahan penelitian disajikan pada Tabel 3.7."),
    ("tabel", "3.7"),
    ("h2", "Jadwal Penelitian"),
    ("p", "Penelitian direncanakan berlangsung tujuh bulan, dari November 2026 sampai Mei 2027, dengan urutan kegiatan mengikuti tahapan pada Gambar 3.1 sebagaimana Tabel 3.8."),
    ("tabel", "3.8"),
    ]
