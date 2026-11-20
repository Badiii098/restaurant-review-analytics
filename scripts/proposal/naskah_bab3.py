"""Isi BAB III METODE PENELITIAN.

Urutan subbab 3.1 mengikuti diagram tahapan penelitian (Gambar 3.1):
identifikasi masalah → studi literatur → pengumpulan data → anotasi data →
SDLC prototipe (analisis kebutuhan, desain cepat, pembangunan prototipe dan
pemodelan NLP, evaluasi prototipe; iterasi 1–2) → pengujian perangkat lunak →
validasi pakar → analisis hasil dan penarikan kesimpulan.

Angka data dibangkitkan dari ``fakta()`` dan ``config/``; bila data mentah
belum ada di mesin pembangun, kalimat realisasi diganti kalimat rencana,
bukan diisi angka karangan.
"""

from __future__ import annotations

from scripts.proposal.fakta import angka, fakta
from scripts.proposal.pustaka import c


def _kalimat_realisasi(f: dict) -> str:
    s = f["sampling"]
    if not s["restoran"]:
        return ("Nama kedelapan restoran beserta jumlah ulasan yang tersedia ditetapkan setelah "
                "pengambilan data dengan prosedur di atas, dan dilaporkan pada Bab IV.")
    kurang = [r for r in s["restoran"] if r["tersedia"] < s["batas_target"]]
    teks = (f"Penerapan kriteria pada data yang terkumpul menghasilkan {len(s['restoran'])} restoran "
            f"dengan target total {angka(s['target_total'])} ulasan sebagaimana Tabel 3.1, Gambar 3.6, dan Gambar 3.7.")
    if kurang:
        teks += (f" Sebanyak {len(kurang)} restoran memiliki ulasan dalam rentang tahun kurang dari "
                 f"{angka(s['batas_target'])}, sehingga targetnya sama dengan jumlah yang tersedia.")
    return teks


def blok() -> list[tuple]:
    f = fakta()
    s = f["sampling"]
    tahun = f"{s['rentang'][0]}–{s['rentang'][1]}"
    return [
    ("h1", "METODE PENELITIAN"),
    ("p", "Penelitian ini adalah penelitian rekayasa perangkat lunak dengan pendekatan kuantitatif. Tahapan penelitian ditunjukkan pada Gambar 3.1. Model pengembangan SDLC prototipe menjadi kerangka perancangan dan pembangunan sistem, sedangkan setiap rumusan masalah dijawab oleh satu hipotesis dengan prosedur dan kriteria keputusan yang dapat diulang."),
    ("gambar", "3.1", 15),
    ("h2", "Tahapan Penelitian"),
    ("h3", "Identifikasi Masalah"),
    ("p", "Masalah diidentifikasi dari kebutuhan pemilik restoran untuk mengetahui aspek layanan yang perlu diperbaiki lebih dahulu dan dari celah penelitian terdahulu yang berhenti pada ketepatan model " + c("firdaus2024", "salsabillah2024", "brata2024") + ". Keluaran tahap ini adalah tiga rumusan masalah, tujuan, dan luaran pada Bab I."),
    ("h3", "Studi Literatur"),
    ("p", "Studi literatur difokuskan pada publikasi 2022–2026 tentang ABSA ulasan restoran, arsitektur sistem pembelajaran mesin, SDLC prototipe, dan pengujian perangkat lunak; buku teks rekayasa perangkat lunak dirujuk sebagai landasan konsep " + c("pressman2020") + ". Hasilnya adalah landasan teori dan pemetaan penelitian terdahulu pada Bab II, yang menetapkan pilihan TF-IDF dan SVM serta posisi kontribusi penelitian pada sisi rekayasa sistem."),
    ("h3", "Pengumpulan Data"),
    ("p", f"Data adalah ulasan publik Google Maps berbahasa Indonesia dari restoran di Jabodetabek. Sampel ditentukan dengan teknik *purposive sampling* dua tahap. Tahap pertama menyusun daftar kandidat restoran berulasan banyak dengan kategori masakan yang beragam ({f['n_kandidat']} kandidat, {f['n_restoran']} memenuhi syarat awal). Tahap kedua memilih **{s['n']} restoran** dengan kriteria tertulis: (1) diurutkan menurut jumlah ulasan berteks pada periode {tahun}; (2) paling banyak {s['maks_per_kategori']} restoran per kategori agar sampel tidak didominasi satu jenis masakan; (3) bila batas kategori menyisakan kurang dari {s['n']} restoran, urutan berikutnya dipakai untuk mencukupi. Pemilihan dijalankan oleh fungsi deterministik pada prototipe sehingga hasilnya dapat diulang."),
    ("p", f"Target ulasan per restoran ditetapkan dengan persamaan (3.1), yaitu jumlah ulasan yang tersedia pada periode {tahun} dengan batas atas {angka(s['batas_target'])} ulasan. Batas atas mencegah satu restoran mendominasi data latih, sedangkan restoran dengan ulasan lebih sedikit tetap dianalisis dan kekurangannya dicatat sebagai batasan."),
    ("rumus", f"Targetᵢ = min(Tersediaᵢ, {angka(s['batas_target'])})", "3.1"),
    ("p", f"Ulasan diambil dengan Playwright dari halaman Google Maps yang diurutkan berdasarkan ulasan terbaru, dengan jeda acak antar-gulir dan tanpa pengambilan paralel. Hanya ulasan publik yang diambil; nama penulis tidak dimuat dalam laporan. Kriteria inklusi adalah ulasan berteks berbahasa Indonesia, terbit {tahun}, dan membahas minimal satu aspek. Ulasan tanpa teks, berisi simbol saja, duplikat, atau di luar rentang tahun ditandai, bukan dihapus, agar jumlah sebelum dan sesudah penyaringan dapat dilaporkan. " + _kalimat_realisasi(f)),
    ("tabel", "3.1"),
    ("gambar", "3.6", 14),
    ("gambar", "3.7", 14),
    ("h3", "Anotasi Data"),
    ("p", "Data latih diperoleh melalui anotasi **500 ulasan** yang diambil secara acak berstrata dari kedelapan restoran. Dua anotator melabeli seluruh 500 ulasan yang sama secara terpisah, dengan satu baris per pasangan ulasan dan aspek. Panduan anotasi memuat taksonomi lima aspek pada Tabel 2.1, tiga kelas sentimen, dan aturan keputusan untuk kasus sulit, misalnya keluhan berbentuk harapan dinilai negatif."),
    ("p", "Kesepakatan antar-anotator diukur dengan koefisien kappa Cohen pada dua tingkat sebagaimana persamaan (3.2): tingkat aspek, sebagai penandaan ada atau tidak ada untuk setiap pasangan ulasan dan aspek, dan tingkat sentimen, hanya pada pasangan yang ditandai oleh kedua anotator. *Pₒ* adalah proporsi kesepakatan teramati dan *Pₑ* proporsi kesepakatan yang diharapkan karena kebetulan. Nilai κ ditafsirkan menurut Landis dan Koch; label yang berbeda diselesaikan melalui diskusi sebelum data dipakai untuk pelatihan."),
    ("rumus", "κ = (Pₒ − Pₑ) / (1 − Pₑ)", "3.2"),
    ("h3", "Perancangan dan Pembangunan Sistem dengan SDLC Prototipe"),
    ("p", "Perancangan dan pembangunan sistem memakai SDLC model prototipe dengan dua iterasi sebagaimana Gambar 3.2 " + c("pressman2020", "ningsih2023") + ". Iterasi pertama menghasilkan prototipe yang berjalan dari berkas ulasan sampai halaman prioritas; iterasi kedua memperbaiki temuan evaluasi pertama dan menghasilkan prototipe final yang diuji pada tahap berikutnya."),
    ("gambar", "3.2", 15),
    ("p", "**a. Analisis kebutuhan.** Kebutuhan dirumuskan dari rumusan masalah dan dicatat sebagai katalog kebutuhan fungsional (FR) dan non-fungsional (KNF) pada Tabel 3.2. Setiap kebutuhan memiliki kriteria lulus dan minimal satu kasus uji. Katalog disimpan sebagai satu berkas konfigurasi yang dibaca oleh kode, oleh pengujian keterlacakan, dan oleh naskah ini, sehingga persentase kebutuhan yang terlacak ke kasus uji dihitung otomatis."),
    ("tabel", "3.2"),
    ("p", "**b. Desain cepat.** Desain mencakup arsitektur, kontrak data, modul keputusan, dan antarmuka. Arsitektur berbentuk klien-server dengan lima lapis sebagaimana Gambar 3.3. Lapis 1 memuat dan memvalidasi ulasan; lapis 2 membersihkan teks dan memecah klausa; lapis 3 mengklasifikasikan aspek dan sentimen; lapis 4 menghitung prioritas, frasa keluhan, dan rekomendasi; lapis 5 menyajikan hasil melalui antarmuka pemrograman aplikasi (API) REST berbasis FastAPI (5a) dan aplikasi web satu halaman berbasis React (5b), serta antarmuka baris perintah. Hasil setiap analisis beserta konfigurasi dan waktu per tahap disimpan di basis data SQLite lokal " + c("kreuzberger2023") + "."),
    ("gambar", "3.3", 14),
    ("p", "Data yang berpindah antar-lapis didefinisikan sebagai kontrak sebagaimana Gambar 3.4. Dokumen kontrak dan skema OpenAPI dibangkitkan langsung dari kode, dan respons API untuk hasil prioritas memakai struktur kontrak yang sama, sehingga dokumen, API, dan implementasi tidak dapat berbeda. Modul keputusan menghitung skor prioritas dengan persamaan (2.4)–(2.6) sebagaimana Gambar 3.5, dan seluruh komponen skor disimpan agar setiap peringkat dapat diaudit."),
    ("gambar", "3.4", 15),
    ("gambar", "3.5", 13),
    ("p", "Antarmuka dirancang mengikuti tahapan penelitian: setiap halaman menyajikan bukti satu tahap, yaitu data, anotasi, kebutuhan, desain, iterasi prototipe, hasil prioritas, pengujian, validasi pakar, dan kesimpulan, sebagaimana Gambar 3.8. Halaman hanya membaca hasil yang tersimpan; bila bukti suatu tahap belum ada, halaman menampilkan perintah untuk membuatnya, bukan angka perkiraan. Seluruh aset antarmuka dibundel bersama aplikasi sehingga dapat berjalan tanpa jaringan."),
    ("gambar", "3.8", 15),
    ("p", "**c. Pembangunan prototipe dan pemodelan NLP.** Inti analitik dibangun dengan Python, API dengan FastAPI, dan antarmuka dengan React dan TypeScript. Komponen NLP memakai TF-IDF (maksimum 20.000 fitur, n-gram 1–2, frekuensi dokumen minimum 2 dan maksimum 0,95, pembobotan sublinear) dan SVM linear dengan bobot kelas seimbang serta benih acak 42. Setiap perubahan kode disimpan di Git dalam *commit* kecil dan diuji otomatis melalui GitHub Actions."),
    ("p", "**d. Evaluasi prototipe.** Pada akhir setiap iterasi, prototipe diperiksa terhadap katalog kebutuhan dan ketepatan klasifikasinya diukur dengan Macro-F1 dari validasi silang sepuluh lipatan yang dipisah per ulasan. Hasil setiap iterasi dicatat bersama nomor *commit* dan catatan perbaikannya, sehingga selisih Macro-F1 antara iterasi pertama dan kedua dapat ditelusuri ke perubahan yang menyebabkannya. Macro-F1 adalah bukti pendukung bahwa komponen klasifikasi layak dipakai, bukan hipotesis penelitian. Temuan evaluasi yang menuntut perubahan kebutuhan dikembalikan ke analisis kebutuhan, sedangkan temuan pengujian dikembalikan ke pembangunan prototipe."),
    ("h3", "Pengujian Perangkat Lunak"),
    ("p", "Prototipe final diuji pada tingkat unit, integrasi, dan sistem dengan pytest " + c("valerian2025") + " sebagaimana Tabel 3.4. Uji sistem menjalankan antarmuka baris perintah sebagai proses terpisah, memanggil setiap titik akhir API, dan membuka setiap halaman antarmuka di peramban dengan Playwright. Setiap uji diberi penanda kode kasus sehingga status setiap kebutuhan dapat dibaca dari laporan pengujian. **Uji kritis** didefinisikan sebagai seluruh kasus uji yang terpetakan ke kebutuhan fungsional FR-01 sampai FR-08."),
    ("tabel", "3.4"),
    ("p", "Pengujian non-fungsional dijalankan sesuai skenario pada Tabel 3.5. Waktu proses diukur lima kali dan dinormalisasi per 1.000 ulasan, lalu dilaporkan sebagai rata-rata, simpangan baku, maksimum, serta waktu per tahap. Waktu muat halaman diukur otomatis dari permintaan halaman sampai baris peringkat pertama tampil. Spesifikasi perangkat, versi perangkat lunak, dan versi peramban dicatat."),
    ("tabel", "3.5"),
    ("h3", "Validasi Pakar"),
    ("p", "Validasi pakar dilakukan dengan meminta pakar, yaitu pengelola atau pemilik restoran dan akademisi bidang layanan makanan, menyusun urutan lima aspek untuk setiap restoran sampel berdasarkan pembacaan sampel ulasan. Urutan pakar dibandingkan dengan urutan sistem pada restoran yang sama memakai korelasi peringkat Spearman, lalu median ρ diuji dengan uji peringkat bertanda Wilcoxon (subbab 3.2). Uji sensitivitas menggeser setiap bobot ±10% dan melaporkan tau Kendall serta kesamaan aspek peringkat pertama."),
    ("p", f"Dua keterbatasan dicatat sejak awal. Pertama, dengan lima aspek per restoran, ρ hanya dapat bernilai pada langkah 0,1, sehingga satu pertukaran urutan sudah mengubah ρ secara nyata. Kedua, dengan n = {s['n']} restoran, nilai p satu sisi terkecil yang dapat dicapai uji Wilcoxon adalah 1/2⁸ ≈ 0,0039, yaitu bila seluruh ρ melebihi 0,60; satu atau dua restoran yang tidak sesuai sudah dapat membuat H0 tidak ditolak. Hasil demikian tetap dilaporkan sebagai temuan."),
    ("h3", "Analisis Hasil dan Penarikan Kesimpulan"),
    ("p", "Hasil pengujian dianalisis dengan prosedur pada subbab 3.2. Keputusan hipotesis dihitung oleh prototipe dari bukti yang tersimpan (laporan pengujian, hasil pengukuran waktu, dan urutan pakar) dan ditampilkan pada halaman kesimpulan. Setiap rumusan masalah dijawab oleh luaran pada Tabel 1.2, dan keterbatasan dibahas apa adanya, termasuk kekurangan ulasan pada restoran tertentu dan sifat frasa keluhan yang tidak menunjukkan sebab-akibat."),
    ("h2", "Pengujian Hipotesis"),
    ("p", "Setiap rumusan masalah memiliki satu pasangan hipotesis, satu prosedur uji, dan satu kriteria keputusan sebagaimana Tabel 3.3. Bila H0 tidak ditolak, hasil tetap dilaporkan sebagai temuan dan rekomendasi perbaikannya diuraikan."),
    ("tabel", "3.3"),
    ("p", "Hipotesis rumusan masalah kedua diuji dengan uji-t satu sampel satu sisi terhadap batas 60 detik pada persamaan (3.3), dengan *x̄* rata-rata waktu proses per 1.000 ulasan dari lima ulangan, *μ₀* = 60 detik, *s* simpangan baku, dan *n* = 5. H0 ditolak bila *t* lebih kecil dari −*t*(0,05; 4) dan seluruh uji kritis lulus."),
    ("rumus", "t = (x̄ − μ₀) / (s / √n)", "3.3"),
    ("p", "Hipotesis rumusan masalah ketiga diuji dengan uji peringkat bertanda Wilcoxon satu sampel pada persamaan (3.4), dengan *dᵢ* = ρᵢ − 0,60 untuk setiap restoran dan *R*(|*dᵢ*|) peringkat nilai mutlaknya. H0 ditolak bila nilai p satu sisi kurang dari 0,05. Uji ini dipilih karena ρ per restoran tidak dapat diasumsikan berdistribusi normal dan jumlah aspek terlalu sedikit untuk uji per restoran."),
    ("rumus", "W⁺ = Σ R(|dᵢ|)  untuk semua dᵢ > 0", "3.4"),
    ("h2", "Alat dan Bahan Penelitian"),
    ("p", "Alat penelitian terdiri atas perangkat keras dan perangkat lunak pada Tabel 3.6. Seluruh pelatihan berjalan pada prosesor tanpa kartu grafis, dan versi pustaka Python serta JavaScript dikunci pada berkas kebutuhan agar lingkungan dapat dibangun ulang."),
    ("tabel", "3.6"),
    ("p", "Bahan penelitian disajikan pada Tabel 3.7."),
    ("tabel", "3.7"),
    ("h2", "Jadwal Penelitian"),
    ("p", "Penelitian direncanakan berlangsung tujuh bulan, dari November 2026 sampai Mei 2027, dengan urutan kegiatan mengikuti tahapan pada Gambar 3.1 sebagaimana Tabel 3.8."),
    ("tabel", "3.8"),
    ]
