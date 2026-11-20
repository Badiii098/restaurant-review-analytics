"""Isi seluruh tabel naskah proposal. Dipakai oleh buat_tabel.py dan buat_naskah.py.

Setiap tabel: judul (tanpa nomor), kolom, baris, sumber, dan lebar relatif kolom.
"""

from __future__ import annotations

from scripts.proposal.fakta import ROOT, angka, fakta


def _katalog():
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    from rra.requirements import muat_katalog
    return muat_katalog(ROOT / "config" / "kebutuhan.yaml")


def _baris_kebutuhan() -> list[list[str]]:
    """Tabel 3.2 dibaca dari config/kebutuhan.yaml agar naskah dan kode tidak berbeda."""
    return [[k["kode"], k["uraian"], k["kriteria"], ", ".join(k["kasus"])]
            for k in _katalog().kebutuhan]


def _baris_kasus() -> list[list[str]]:
    """Tabel 3.4: kasus uji otomatis beserta berkasnya dan kebutuhan yang diuji."""
    kat = _katalog()
    tingkat = {"unit": "Unit", "integrasi": "Integrasi", "sistem": "Sistem",
               "nonfungsional": "Non-fungsional"}
    return [[c["kode"], tingkat[c["tingkat"]], c["nama"], c.get("berkas") or c.get("bukti", ""),
             ", ".join(k["kode"] for k in kat.kebutuhan if c["kode"] in k["kasus"])]
            for c in kat.kasus if c["jenis"] == "otomatis"]


def _sampel() -> dict:
    """Tabel 3.1: kriteria purposive dan realisasi delapan restoran sampel."""
    s = fakta()["sampling"]
    def _a(v):  # noqa: ANN001, ANN202
        return "–" if v is None else angka(v)
    baris = [[r["kode"], r["nama"], r["kota"], r["kategori"], _a(r["tersedia"]), _a(r["target"])]
             for r in s["restoran"]]
    if baris:
        tersedia = [r["tersedia"] for r in s["restoran"]]
        baris.append(["", f"Jumlah {len(baris)} restoran", "", "",
                      "–" if None in tersedia else angka(sum(tersedia)), angka(s["target_total"])])
    else:
        baris.append(["–", "Ditetapkan setelah pengambilan data (scripts/pilih_restoran.py)", "–", "–", "–", "–"])
    return {"judul": f"Sampel purposive {s['n']} restoran dan target ulasan",
            "kolom": ["Kode", "Restoran", "Kota", "Kategori", f"Ulasan {s['rentang'][0]}–{s['rentang'][1]}", "Target"],
            "baris": baris, "lebar": [1.0, 3.6, 1.8, 2.2, 1.6, 1.2], "footer": bool(s["restoran"]),
            "sumber": (f"Kriteria: urut jumlah ulasan {s['rentang'][0]}–{s['rentang'][1]}, maksimal "
                       f"{s['maks_per_kategori']} per kategori; target = min(tersedia, {angka(s['batas_target'])}) "
                       "(config/default.yaml, config/restaurants.csv, data/raw/maps)")}


def tabel() -> dict[str, dict]:
    f = fakta()
    return {
    "1.1": {"judul": "Rumusan masalah, tujuan khusus, dan luaran konkret",
        "kolom": ["No", "Rumusan masalah", "Tujuan khusus", "Luaran konkret (dijawab di Bab IV)"],
        "lebar": [0.7, 4.2, 3.3, 3.9],
        "baris": [
            ["1", "Bagaimana rancangan arsitektur lima lapis prototipe analisis sentimen berbasis aspek untuk ulasan restoran berbahasa Indonesia beserta katalog kebutuhan dan kontrak antarmuka JSON antar-lapis?",
             "Menghasilkan rancangan arsitektur, katalog kebutuhan fungsional dan non-fungsional, serta kontrak antarmuka antar-lapis",
             "Diagram arsitektur lima lapis; katalog kebutuhan FR dan KNF bernomor; dokumen kontrak JSON per batas lapis (4.1)"],
            ["2", "Berapa persentase kasus uji unit, integrasi, dan sistem yang lulus, dan berapa waktu proses per 1.000 ulasan pada lingkungan uji yang dicatat, termasuk ketika jaringan tidak tersedia?",
             "Menguji prototipe pada tingkat unit, integrasi, dan sistem serta mengukur kinerja non-fungsionalnya",
             "Persentase lulus per tingkat uji; rata-rata dan simpangan baku waktu proses dari lima ulangan; status uji tanpa jaringan, waktu muat halaman, dan peramban (4.2)"],
            ["3", "Aspek layanan mana yang menjadi prioritas perbaikan pertama pada setiap restoran berdasarkan skor komposit 0–100, dan berapa korelasi peringkatnya terhadap urutan pakar?",
             "Menghasilkan skor prioritas komposit dan menguji kesesuaian urutannya dengan urutan pakar",
             "Tabel peringkat aspek per restoran beserta komponen skor; tiga frasa keluhan dominan per aspek; ρ per restoran, median ρ, dan hasil uji Wilcoxon (4.3)"],
        ], "sumber": "Rancangan penelitian (2026)"},
    "1.2": {"judul": "Luaran penelitian terperinci",
        "kolom": ["Kode", "Luaran", "Spesifikasi", "RM"],
        "lebar": [1.1, 2.6, 7.0, 0.8],
        "baris": [
            ["L1", "Diagram arsitektur", "Lima lapis (data, praproses, komponen model, modul keputusan, penyajian berupa API dan klien web) beserta aliran data dan batas kontrak antar-lapis", "1"],
            ["L2", "Katalog kebutuhan", "Kebutuhan fungsional (FR) dan non-fungsional (KNF) bernomor, masing-masing dengan kriteria lulus dan kode kasus uji, serta matriks keterlacakan", "1"],
            ["L3", "Kontrak antarmuka JSON", "Satu skema per batas lapis: ulasan mentah, ulasan bersih, prediksi aspek-sentimen, statistik aspek, prioritas, frasa keluhan, rekomendasi; dokumen kontrak dan skema OpenAPI API dibangkitkan dari kode", "1"],
            ["L4", "Pipeline klasifikasi", "TF-IDF (maksimum 20.000 fitur, n-gram 1–2, min_df 2, max_df 0,95, sublinear) dan SVM linear satu-lawan-semua; satu model; seed 42; Macro-F1 validasi silang tercatat untuk iterasi 1 dan 2", "1"],
            ["L5", "Laporan uji unit dan integrasi", "Persentase lulus per berkas uji dan per lapis, diambil dari keluaran pytest", "2"],
            ["L6", "Laporan uji sistem", "Alur end-to-end dari berkas ulasan sampai halaman peringkat, termasuk masukan tidak sempurna (rating kosong, duplikat, ulasan tanpa aspek), pemanggilan setiap titik akhir API, dan pembukaan setiap halaman di peramban", "2"],
            ["L7", "Laporan uji non-fungsional", "Waktu proses per 1.000 ulasan (lima ulangan, rata-rata, simpangan, maksimum, waktu per tahap), mode tanpa jaringan, waktu muat halaman, tiga peramban, spesifikasi perangkat", "2"],
            ["L8", "Prototipe web", "API REST (FastAPI) dan aplikasi web (React) dengan satu halaman per tahap penelitian: data, anotasi, kebutuhan, desain, iterasi, hasil, pengujian, validasi pakar, dan kesimpulan; membaca hasil tersimpan, tombol hitung ulang, tanpa akun pengguna", "2"],
            ["L9", "Modul skor prioritas", "Prioritas = 0,4·Volume + 0,4·Keparahan + 0,2·Keragaman, skala tampil 0–100, komponen tersimpan per hasil", "3"],
            ["L10", "Uji sensitivitas bobot", "Setiap bobot digeser ±10%, dilaporkan tau Kendall dan kesamaan aspek peringkat pertama", "3"],
            ["L11", "Frasa keluhan dominan", "n-gram hingga tiga kata pada klausa bernada keluhan, frekuensi minimum tiga, lima teratas per aspek, dapat ditelusuri ke ulasan asal", "3"],
            ["L12", "Rekomendasi berbasis aturan", "Pemetaan frasa pemicu ke tindakan menurut aspek layanan", "3"],
            ["L13", "Data penelitian dan data berlabel", f"Sampel purposive {f['sampling']['n']} restoran Jabodetabek (dari {f['n_restoran']} kandidat) dengan target ulasan per restoran min(tersedia, {angka(f['sampling']['batas_target'])}); 500 ulasan berlabel dua anotator dengan koefisien kappa aspek dan sentimen", "3"],
            ["L14", "Uji kesesuaian dengan pakar", "Urutan aspek pakar per restoran, ρ per restoran, median ρ, uji Wilcoxon, kesesuaian aspek peringkat pertama", "3"],
        ], "sumber": "Rancangan penelitian (2026)"},
    "2.1": {"judul": "Aspek layanan restoran dan cakupannya",
        "kolom": ["Aspek", "Cakupan", "Contoh penanda pada ulasan"],
        "lebar": [1.8, 6.0, 4.0],
        "baris": [
            ["Makanan", "rasa, porsi, kesegaran, penyajian, variasi menu, suhu hidangan", "enak, hambar, porsi kecil, dingin"],
            ["Pelayanan", "keramahan, kecepatan, ketepatan pesanan, perhatian petugas", "ramah, lambat, lupa pesanan, cuek"],
            ["Harga", "kewajaran harga, kesesuaian dengan porsi dan mutu, biaya tambahan", "mahal, murah, worth it"],
            ["Suasana", "kenyamanan ruang, kebisingan, musik, suhu, aroma", "nyaman, berisik, gerah, adem"],
            ["Fasilitas", "parkir, toilet, wifi, colokan, tempat ibadah, kebersihan area umum", "parkir susah, toilet kotor, wifi lambat"],
        ], "sumber": "Diadaptasi dari Latifah et al. (2026) dan docs/ANOTASI.md"},
    "2.2": {"judul": "Ringkasan penelitian terdahulu",
        "kolom": ["Peneliti", "Objek dan data", "Metode", "Hasil", "Celah terhadap penelitian ini"],
        "lebar": [2.0, 2.8, 2.4, 2.8, 3.0],
        "baris": [
            ["Firdaus et al. (2024)", "Depot Bamara, 1.029 ulasan Google Review 2021–2022", "TF-IDF + SVM, k-fold, root cause analysis", "Akurasi rata-rata 92%; aspek harga 96%", "Rekomendasi disusun lewat diskusi dengan pemangku kepentingan, tanpa skor yang dapat diulang"],
            ["Salsabillah et al. (2024)", "Ayam Goreng Nelongso Singosari", "SVM dibandingkan Naive Bayes, root cause analysis", "SVM 92,74%; Naive Bayes 91,67%", "Berhenti pada akurasi dan analisis akar masalah manual"],
            ["Saputra dan Suria (2025)", "Tong Tji Tea House, Google Maps (2.676 positif, 670 netral, 251 negatif)", "SVM, Naive Bayes, ensemble soft voting", "SVM linear C=10 akurasi 0,9289; ensemble 0,9344", "Tidak ada keluaran prioritas perbaikan"],
            ["Brata et al. (2024)", "2.065 ulasan Google Review dan Tripadvisor", "TF-IDF + ANN, undersampling, GridSearchCV", "Akurasi 89%; perankingan ulasan negatif", "Peringkat berupa urutan frekuensi, tanpa rumus tersimpan"],
            ["Latifah et al. (2026)", "Lima restoran Sunda Bogor, 3.010 ulasan", "Fine-tuning IndoBERT, lima aspek, tiga kelas", "Akurasi 92,52–97,51%; F1 makro > 0,91", "Fokus kinerja model; tidak menguji perangkat lunak"],
            ["Sukwadi et al. (2025)", "Restoran cepat saji Indonesia, Google Review dan 100 responden", "ABSA, analisis emosi, IPA tiga dimensi", "Sebagian besar aspek bersentimen positif", "Analisis deskriptif, bukan sistem yang dapat dipakai berulang"],
            ["Atmojo et al. (2025)", "Al-Ghiff Steak Cirebon, Google Maps", "IndoBERT, tiga kelas sentimen", "Akurasi 83,89%", "Sentimen tingkat dokumen, tanpa aspek"],
            ["Amalia dan Winarko (2021)", "Ulasan restoran berbahasa Indonesia", "BERT-CNN, ELMo-CNN, Word2vec-CNN", "F1 aspek 0,86 (ELMo-CNN); F1 sentimen 0,91 (BERT-CNN)", "Model berat; tidak ada keluaran keputusan"],
            ["Singgalen (2023)", "Sepuluh restoran Makassar, Tripadvisor", "CRISP-DM dan SERVQUAL", "Sentimen terhadap makanan, layanan, nilai", "Kerangka penambangan data, bukan rekayasa perangkat lunak"],
            ["Carrasco dan Dias (2024)", "1.581 restoran Algarve, 880.000 ulasan", "ABSA berbasis model transformer, aplikasi web", "Metode menyamai klasifikasi manusia", "Tidak ada skor prioritas yang dapat diaudit"],
            ["Li et al. (2023)", "Restoran di dua destinasi wisata AS", "ABSA lima kategori, conditional survival forest", "Sentimen aspek memperbaiki prediksi keberlangsungan restoran", "Menegaskan nilai sentimen per aspek, bukan sistem keputusan"],
            ["Hua et al. (2024)", "727 studi primer dari 8.550 hasil penelusuran", "Tinjauan pustaka sistematis ABSA", "Kurangnya keragaman dataset dan domain; 78,20% pemakaian dataset pada empat dataset SemEval restoran dan laptop", "Menunjukkan perlunya data lokal dan sistem di luar tolok ukur"],
        ], "sumber": "Diolah dari publikasi masing-masing (folder REFERENSI)"},
    "3.1": _sampel(),
    "3.2": {"judul": "Katalog kebutuhan fungsional dan non-fungsional",
        "kolom": ["Kode", "Kebutuhan", "Kriteria lulus", "Kasus uji"],
        "lebar": [1.4, 4.4, 4.4, 1.6],
        "baris": _baris_kebutuhan(), "sumber": "Rancangan penelitian (2026), docs/PENGUJIAN.md"},
    "3.3": {"judul": "Hipotesis, prosedur uji, dan kriteria keputusan",
        "kolom": ["RM", "H0", "H1", "Prosedur dan kriteria", "Bila H0 tidak ditolak"],
        "lebar": [0.8, 2.6, 2.6, 3.6, 2.6],
        "baris": [
            ["1", "Ada kontrak antar-lapis yang gagal validasi atau kebutuhan yang tidak terlacak ke kasus uji", "100% kontrak lolos validasi dan 100% kebutuhan terlacak ke minimal satu kasus uji", "Validasi kontrak pada keluaran tiap lapis dan matriks keterlacakan Tabel 3.2; H1 diterima bila kedua proporsi 100%", "Perbaiki kontrak atau tambah kasus uji pada iterasi prototipe berikutnya"],
            ["2", "Ada uji kritis yang gagal, atau rata-rata waktu proses > 60 detik per 1.000 ulasan", "Seluruh uji kritis lulus dan rata-rata waktu ≤ 60 detik per 1.000 ulasan", "pytest; benchmark lima ulangan; uji-t satu sampel satu sisi terhadap 60 detik, α = 0,05", "Telusuri tahap terlambat dari waktu per tahap, perbaiki, ukur ulang"],
            ["3", "Median ρ Spearman antar-restoran ≤ 0,60", "Median ρ Spearman antar-restoran > 0,60", "ρ per restoran; uji peringkat bertanda Wilcoxon satu sampel satu sisi terhadap 0,60, α = 0,05; kesesuaian aspek peringkat pertama", "Laporkan sebagai temuan; tinjau bobot melalui uji sensitivitas, definisi komponen, atau cakupan frasa"],
        ], "sumber": "Rancangan penelitian (2026)"},
    "3.4": {"judul": "Kasus uji dan berkas pengujian",
        "kolom": ["Kode", "Tingkat", "Yang diuji", "Berkas uji", "Kebutuhan"],
        "lebar": [1.1, 1.4, 4.2, 3.0, 1.4],
        "baris": _baris_kasus(), "sumber": "Repositori restaurant-review-analytics, folder tests (2026)"},
    "3.5": {"judul": "Skenario pengujian non-fungsional",
        "kolom": ["Kode", "Kondisi", "Langkah", "Kriteria lulus", "Bukti"],
        "lebar": [1.1, 2.5, 3.5, 2.4, 2.3],
        "baris": [
            ["N-01", "1.000 ulasan, perangkat uji Tabel 3.6", "Jalankan benchmark lima kali, cache dibersihkan antar-ulangan", "Rata-rata ≤ 60 detik", "reports/benchmark.json"],
            ["N-02", "Jaringan dimatikan", "Buka halaman, tekan hitung ulang analisis", "Peringkat tampil dan hasil baru tersimpan", "reports/manual/N-02.json, baris runs baru"],
            ["N-03", "Basis data berisi hasil", "Uji Playwright otomatis: waktu dari permintaan halaman sampai baris peringkat pertama tampil, lima ulangan", "Rata-rata ≤ 3 detik", "reports/pytest.xml (test_e2e_web.py)"],
            ["N-04", "Chrome, Firefox, Edge versi terbaru", "Buka sepuluh halaman tahapan, periksa tampilan dan galat konsol", "Seluruh halaman tampil tanpa galat", "reports/manual/N-04.json + tangkapan layar"],
            ["N-05", "Python 3.11 dan 3.12", "Jalankan seluruh uji pada CI dan perangkat uji", "Seluruh uji lulus", "Riwayat GitHub Actions"],
        ], "sumber": "Rancangan penelitian (2026), docs/PENGUJIAN.md"},
    "3.6": {"judul": "Alat penelitian",
        "kolom": ["Jenis", "Nama", "Versi atau spesifikasi", "Kegunaan"],
        "lebar": [1.6, 2.6, 3.6, 4.0],
        "baris": [
            ["Perangkat keras", "Prosesor", "Intel Core i5-12450H, 8 inti, 12 thread", "Pelatihan dan pengujian"],
            ["Perangkat keras", "Memori", "14 GB DDR4", "Pemrosesan data"],
            ["Perangkat keras", "Kartu grafis", "NVIDIA GeForce RTX 4050 6 GB (tidak dipakai)", "–"],
            ["Perangkat keras", "Sistem operasi", "Ubuntu 26.04 LTS 64 bit", "Lingkungan uji"],
            ["Perangkat lunak", "Python", "≥ 3.11", "Bahasa pemrograman"],
            ["Perangkat lunak", "scikit-learn", "≥ 1.5", "TF-IDF, SVM linear, validasi silang"],
            ["Perangkat lunak", "pandas, NumPy, SciPy", "≥ 2.2, ≥ 2.0, ≥ 1.13", "Pengolahan data dan uji statistik"],
            ["Perangkat lunak", "FastAPI dan Uvicorn", "≥ 0.115, ≥ 0.30", "API REST lapis 5a dan skema OpenAPI"],
            ["Perangkat lunak", "React, TypeScript, Vite", "18.3, 5.6, 5.4", "Antarmuka web lapis 5b"],
            ["Perangkat lunak", "Node.js", "≥ 22", "Membangun antarmuka web"],
            ["Perangkat lunak", "Vitest", "2.1", "Uji komponen antarmuka"],
            ["Perangkat lunak", "SQLite", "≥ 3.40", "Basis data hasil dan jejak audit"],
            ["Perangkat lunak", "pytest", "≥ 8.0", "Uji unit, integrasi, sistem"],
            ["Perangkat lunak", "Playwright", "≥ 1.45", "Pengambilan data Google Maps dan uji sistem di peramban"],
            ["Perangkat lunak", "Git dan GitHub Actions", "≥ 2.40", "Kendali versi dan integrasi berkelanjutan"],
            ["Perangkat lunak", "Chrome, Firefox, Edge", "Versi terbaru", "Uji kompatibilitas peramban"],
        ], "sumber": "Dokumentasi perangkat penelitian dan requirements.txt (2026)"},
    "3.7": {"judul": "Bahan penelitian",
        "kolom": ["Bahan", "Jumlah", "Keterangan"],
        "lebar": [3.6, 2.2, 6.0],
        "baris": [
            ["Restoran kandidat", f"{f['n_restoran']} restoran", f"Restoran berulasan banyak di Jabodetabek yang lolos syarat awal (dari {f['n_kandidat']} kandidat)"],
            ["Restoran sampel", f"{f['sampling']['n']} restoran", "Purposive: urut jumlah ulasan dalam rentang tahun, maksimal dua per kategori"],
            ["Target ulasan", f"{angka(f['sampling']['target_total'])} ulasan" if f['sampling']['restoran'] else "ditetapkan dari data",
             f"min(tersedia, {angka(f['sampling']['batas_target'])}) per restoran sampel"],
            ["Ulasan terkumpul", f"{angka(f['total'])} ulasan" if f['total'] else "–", "Ulasan berteks; tanggal berupa perkiraan dari penanda relatif Google Maps"],
            ["Ulasan berlabel", "500 ulasan", "Dilabeli dua anotator secara terpisah; kappa Cohen tingkat aspek dan sentimen"],
            ["Aspek layanan", "5 aspek", "Makanan, pelayanan, harga, suasana, fasilitas"],
            ["Kelas sentimen", "3 kelas", "Positif, negatif, netral"],
            ["Data berlabel", "Direncanakan", "Dua anotator, minimal 150 ulasan tumpang tindih untuk koefisien kappa"],
            ["Urutan pakar", f"{f['sampling']['n']} restoran", "Urutan lima aspek per restoran sampel dari pakar"],
        ], "sumber": "Hasil pengumpulan data penelitian, Oktober 2026"},
    "3.8": {"judul": "Jadwal penelitian",
        "kolom": ["Kegiatan", "Nov", "Des", "Jan", "Feb", "Mar", "Apr", "Mei"],
        "lebar": [4.4, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9],
        "baris": [
            ["Identifikasi masalah dan studi literatur", "■", "", "", "", "", "", ""],
            ["Pengumpulan data (8 restoran) dan anotasi 500 ulasan", "■", "■", "", "", "", "", ""],
            ["Perancangan sistem: analisis kebutuhan dan desain cepat", "■", "■", "", "", "", "", ""],
            ["Iterasi prototipe 1: bangun dan evaluasi", "", "■", "■", "", "", "", ""],
            ["Iterasi prototipe 2: perbaikan dan evaluasi", "", "", "■", "■", "", "", ""],
            ["Pengujian unit, integrasi, sistem", "", "", "", "■", "■", "", ""],
            ["Pengujian non-fungsional dan validasi pakar", "", "", "", "", "■", "■", ""],
            ["Analisis hasil dan penulisan laporan", "", "", "", "", "", "■", "■"],
        ], "sumber": "Rencana penelitian November 2026 – Mei 2027", "tengah_dari": 1},
    }
