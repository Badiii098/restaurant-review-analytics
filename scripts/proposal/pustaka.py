"""Daftar pustaka naskah, mengikuti format templat skripsi FIK UPNVJ.

Sitasi dalam teks: ``(Firdaus et al. 2024)``; dua penulis ``(Amalia dan Winarko 2021)``.
Entri dengan ``folder=False`` adalah sumber yang PDF-nya belum ada di folder
REFERENSI; entri itu diberi tanda pada daftar pustaka agar dilengkapi.
"""

from __future__ import annotations

TANDA = " [PDF belum ada di folder REFERENSI]"

PUSTAKA: dict[str, dict] = {
    "amalia2021": {"sitasi": "Amalia dan Winarko 2021", "folder": True,
        "entri": "Amalia PR, Winarko E. 2021. Aspect-Based Sentiment Analysis on Indonesian Restaurant Review Using a Combination of Convolutional Neural Network and Contextualized Word Embedding. IJCCS (Indonesian Journal of Computing and Cybernetics Systems). 15(3):285–294. doi:10.22146/ijccs.67306."},
    "atmojo2025": {"sitasi": "Atmojo et al. 2025", "folder": True,
        "entri": "Atmojo FW, Atina V, Permatasari H. 2025. Analisis Sentimen Pelanggan pada Ulasan Google Maps Restoran Al-Ghiff Steak Menggunakan Model IndoBERT. Jurnal Sistem Informasi dan Teknik Komputer. 10(2)."},
    "brata2024": {"sitasi": "Brata et al. 2024", "folder": True,
        "entri": "Brata DW, Purnomo W, Nofandi A. 2024. Ekstraksi Ulasan Pelanggan Restoran dalam Menggali Aspek Layanan pada Google Review dan Tripadvisor sebagai Faktor Peningkatan Kualitas. Jurnal Ilmiah Teknologi Informasi Asia. 18(1)."},
    "carrasco2024": {"sitasi": "Carrasco dan Dias 2024", "folder": True,
        "entri": "Carrasco P, Dias S. 2024. Enhancing Restaurant Management through Aspect-Based Sentiment Analysis and NLP Techniques. Procedia Computer Science. 237:129–137. doi:10.1016/j.procs.2024.05.088."},
    "firdaus2024": {"sitasi": "Firdaus et al. 2024", "folder": True,
        "entri": "Firdaus MF, Ratnawati DE, Setiawan NY. 2024. Analisis Sentimen Berbasis Aspek pada Ulasan Pelanggan Restoran Menggunakan Algoritma Support Vector Machine (Studi Kasus: Depot Bamara). Jurnal Teknologi Informasi dan Ilmu Komputer (JTIIK). 11(6):1265–1272. doi:10.25126/jtiik.2024117564."},
    "hua2024": {"sitasi": "Hua et al. 2024", "folder": True,
        "entri": "Hua YC, Denny P, Wicker J, Taskova K. 2024. A Systematic Review of Aspect-Based Sentiment Analysis: Domains, Methods, and Trends. Artificial Intelligence Review. 57:296. doi:10.1007/s10462-024-10906-z."},
    "kreuzberger2023": {"sitasi": "Kreuzberger et al. 2023", "folder": True,
        "entri": "Kreuzberger D, Kühl N, Hirschl S. 2023. Machine Learning Operations (MLOps): Overview, Definition, and Architecture. IEEE Access. 11:31866–31879. doi:10.1109/ACCESS.2023.3262138."},
    "latifah2026": {"sitasi": "Latifah et al. 2026", "folder": True,
        "entri": "Latifah S, Erfina A, Warman C. 2026. Perbandingan Hasil Aspect-Based Sentiment Analysis pada Ulasan Google Review Restoran Sunda di Bogor Menggunakan Fine-Tuning IndoBERT. DINAMIK. 31(1)."},
    "li2023": {"sitasi": "Li et al. 2023", "folder": True,
        "entri": "Li H, Yu BXB, Li G, Gao H. 2023. Restaurant Survival Prediction Using Customer-Generated Content: An Aspect-Based Sentiment Analysis of Online Reviews. Tourism Management. 96:104707. doi:10.1016/j.tourman.2022.104707."},
    "liu2022": {"sitasi": "Liu et al. 2022", "folder": True,
        "entri": "Liu J, Yu Y, Mehraliyev F, Hu S, Chen J. 2022. What Affects the Online Ratings of Restaurant Consumers: A Research Perspective on Text-Mining Big Data Analysis. International Journal of Contemporary Hospitality Management. doi:10.1108/IJCHM-06-2021-0749."},
    "luo2021": {"sitasi": "Luo dan Xu 2021", "folder": True,
        "entri": "Luo Y, Xu X. 2021. Comparative Study of Deep Learning Models for Analyzing Online Restaurant Reviews in the Era of the COVID-19 Pandemic. International Journal of Hospitality Management. 94:102849. doi:10.1016/j.ijhm.2020.102849."},
    "perikos2024": {"sitasi": "Perikos dan Diamantopoulos 2024", "folder": True,
        "entri": "Perikos I, Diamantopoulos A. 2024. Explainable Aspect-Based Sentiment Analysis Using Transformer Models. Big Data and Cognitive Computing. 8(11):141. doi:10.3390/bdcc8110141."},
    "rahman2025": {"sitasi": "Rahman et al. 2025", "folder": True,
        "entri": "Rahman A, Khan MA, Bishnu KK, Rozario U, Ishraq A, Mridha MF, Aung Z. 2025. Multilingual Sentiment Analysis in Restaurant Reviews Using Aspect Focused Learning. Scientific Reports. 15:28371. doi:10.1038/s41598-025-12464-y."},
    "salsabillah2024": {"sitasi": "Salsabillah et al. 2024", "folder": True,
        "entri": "Salsabillah DF, Ratnawati DE, Setiawan NY. 2024. Analisis Sentimen Ulasan Rumah Makan Menggunakan Perbandingan Algoritma Support Vector Machine dengan Naïve Bayes (Studi Kasus: Ayam Goreng Nelongso Cabang Singosari, Malang). Jurnal Teknologi Informasi dan Ilmu Komputer (JTIIK). 11(1):107–116. doi:10.25126/jtiik.20241117584."},
    "saputra2025": {"sitasi": "Saputra dan Suria 2025", "folder": True,
        "entri": "Saputra FP, Suria O. 2025. Penggabungan Model SVM dan Naive Bayes dengan Pendekatan Soft Voting untuk Analisis Sentimen Tong Tji Tea House. Sistemasi: Jurnal Sistem Informasi. 14(5):2479–2491."},
    "singgalen2023": {"sitasi": "Singgalen 2023", "folder": True,
        "entri": "Singgalen YA. 2023. Analisis Sentimen Konsumen terhadap Food, Services, and Value di Restoran dan Rumah Makan Populer Kota Makassar Berdasarkan Rekomendasi Tripadvisor Menggunakan Metode CRISP-DM dan SERVQUAL. Building of Informatics, Technology and Science (BITS). 4(4):1899–1914. doi:10.47065/bits.v4i4.3231."},
    "sukwadi2025": {"sitasi": "Sukwadi et al. 2025", "folder": True,
        "entri": "Sukwadi R, Silitonga RM, Inderawati MMW, Octavian F, Jou YT, Thu NTB. 2025. Peningkatan Kualitas Layanan Jaringan Restoran Cepat Saji Indonesia: Analisis Sentimen dan Emosi Berbasis Aspek. Jurnal Teknologi Informasi dan Ilmu Komputer (JTIIK). 12(2):359–368. doi:10.25126/jtiik.2025129416."},
    "wu2023": {"sitasi": "Wu dan Li 2023", "folder": True,
        "entri": "Wu F, Li X. 2023. Local Dependency-Enhanced Graph Convolutional Network for Aspect-Based Sentiment Analysis. Applied Sciences. 13(17):9669. doi:10.3390/app13179669."},
    # ---- sumber yang PDF-nya belum ada di folder REFERENSI ----
    "brightlocal2026": {"sitasi": "BrightLocal 2026", "folder": False,
        "entri": "BrightLocal. 2026. Local Consumer Review Survey 2026. Diambil dari https://www.brightlocal.com/research/local-consumer-review-survey/."},
    "fahrezi2025": {"sitasi": "Fahrezi dan Prasetyo 2025", "folder": False,
        "entri": "Fahrezi RA, Prasetyo NA. 2025. Rancang Bangun Aplikasi Dashboard Laporan Pengaduan Kendala Sistem Internal pada PT. Telkom Indonesia Witel Purwokerto Berbasis Website Menggunakan Metode Prototype. Jurnal Informatika."},
    "franceschini2021": {"sitasi": "Franceschini dan Maisano 2021", "folder": False,
        "entri": "Franceschini F, Maisano D. 2021. Aggregating Multiple Ordinal Rankings in Engineering Design: The Best Model According to the Kendall's Coefficient of Concordance. Research in Engineering Design. 32(1):91–103."},
    "kemenpar2026": {"sitasi": "Kementerian Pariwisata 2026", "folder": False,
        "entri": "Kementerian Pariwisata. 2026. Statistik Usaha Penyediaan Makanan dan Minuman Tahun 2024. Diambil dari https://kemenpar.go.id/statistik-usaha-restoran/statistik-usaha-penyediaan-makanan-dan-minuman-tahun-2024."},
    "landis1977": {"sitasi": "Landis dan Koch 1977", "folder": False,
        "entri": "Landis JR, Koch GG. 1977. The Measurement of Observer Agreement for Categorical Data. Biometrics. 33(1):159–174."},
    "molon2025": {"sitasi": "Molon 2025", "folder": False,
        "entri": "Molon JN. 2025. Extreme Prototyping for a Community Health Worker Medical Application. Healthcare Informatics Research. 31(1):88–95. doi:10.4258/hir.2025.31.1.88."},
    "ningsih2023": {"sitasi": "Ningsih dan Nurfauziah 2023", "folder": False,
        "entri": "Ningsih W, Nurfauziah H. 2023. Perbandingan Model Waterfall dan Metode Prototype untuk Pengembangan Aplikasi pada Sistem Informasi. Jurnal Ilmiah METADATA. 5(1):83–95. doi:10.47652/metadata.v5i1.311."},
    "pressman2020": {"sitasi": "Pressman dan Maxim 2020", "folder": False,
        "entri": "Pressman RS, Maxim BR. 2020. Software Engineering: A Practitioner's Approach. Ed ke-9. New York: McGraw-Hill Education."},
    "siva2023": {"sitasi": "Siva et al. 2023", "folder": False,
        "entri": "Siva F, Assegaf SMU, Pahlevi SA, Yaqin MA. 2023. Survei Metode-Metode Software Development Life Cycle dengan Metode Systematic Literature Review. ILKOMNIKA: Journal of Computer Science and Applied Informatics. 5(1)."},
    "stevens1995": {"sitasi": "Stevens et al. 1995", "folder": False,
        "entri": "Stevens P, Knutson B, Patton M. 1995. DINESERV: A Tool for Measuring Service Quality in Restaurants. Cornell Hotel and Restaurant Administration Quarterly. 36(2):56–60."},
    "valerian2025": {"sitasi": "Valerian et al. 2025", "folder": False,
        "entri": "Valerian A, Bernady D, Wahyudi F, Pratama Dinatha J, Dhylan Barletyano O. 2025. Implementasi Unit Testing, Integration Testing, System Testing, dan Validation Testing pada Aplikasi Berbasis Website. JATI (Jurnal Mahasiswa Teknik Informatika). 9(4):6354–6362."},
}


def c(*keys: str) -> str:
    """Sitasi dalam teks, mis. c('firdaus2024', 'hua2024') → '(Firdaus et al. 2024; Hua et al. 2024)'."""
    return "(" + "; ".join(PUSTAKA[k]["sitasi"] for k in keys) + ")"


def daftar(dipakai: set[str]) -> list[str]:
    """Entri daftar pustaka untuk kunci yang dipakai, urut abjad."""
    entri = []
    for k in dipakai:
        p = PUSTAKA[k]
        entri.append(p["entri"] + ("" if p["folder"] else TANDA))
    return sorted(entri, key=str.lower)
