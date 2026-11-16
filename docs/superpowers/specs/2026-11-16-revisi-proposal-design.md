# Rancangan: Revisi Proposal Skripsi dan Project restaurant-review-analytics

Tanggal: 2026-11-16 · Sumber keputusan: sheet "Revisi Terpadu" (artifact Asvn98G6uUzQ8iVqqaEgjy), transkrip meeting dosen, percakapan dengan Abdi.

## 1. Maksud
Naskah proposal (BAB I–III), gambar/tabel pendukung, dan kode project harus menyatakan hal yang sama dan mengikuti feedback dosen:
tiga RM pakem, fokus rekayasa perangkat lunak, satu model tanpa swap test, luaran terperinci, referensi hanya dari folder REFERENSI.

## 2. Keluaran
1. `1.PROPOSAL/DRAF/[DRAF] - BAB-I.docx`, `[DRAF] - BAB-II.docx`, `[DRAF] - BAB-III.docx` (versi lama diberi akhiran ` - lama`).
2. `1.PROPOSAL/GAMBAR/`: gambar PNG (300 dpi) + setiap tabel naskah sebagai PNG dan CSV, bernomor sama dengan naskah (mis. `Gambar 3.1 - Arsitektur lima lapis.png`).
3. Repo ini, branch `revisi/model-tunggal`, satu commit per butir, pytest lulus sebelum tiap commit.

## 3. Keputusan (sudah disetujui)
| Topik | Keputusan |
|---|---|
| Wilayah & sampel | Jabodetabek; 18 restoran berulasan terbanyak; 6.874 ulasan; target total 5.000 (≈280/restoran) |
| Restoran keluar | r06, r11, r14, r16, r18, r24, serta r20 yang tanpa data (`aktif=0` di config/restaurants.csv) |
| Sebaran 18 restoran | Jakarta Pusat 12, Jakarta Selatan 3, Jakarta Utara 1, Bekasi 1, Tangerang 1 |
| Model | TF-IDF + SVM linear saja; Naive Bayes dihapus dari kode, uji, CI, UI; hanya muncul di penelitian terdahulu |
| Swap test | Dihapus (RM, tujuan, batasan, hipotesis, kasus uji, test_modularity) |
| SUS / usability | Keluar dari naskah dan lingkup |
| Aspek | 5: makanan, pelayanan, harga, suasana, fasilitas (kebersihan dilebur sesuai ANOTASI.md) |
| Sentimen | 3 kelas: positif, negatif, netral |
| Referensi | Sitasi utama dari folder REFERENSI; sitasi yang PDF-nya belum ada di folder (SDLC: Pressman & Maxim, Siva dkk., Ningsih & Nurfauziah, Molon, Fahrezi & Prasetyo; Franceschini & Maisano; Kemenpar, BrightLocal, Google, Jakpat) tetap dipakai dan ditandai "[PDF belum ada di folder REFERENSI]" di daftar pustaka; sitasi tanpa kebutuhan dihapus (Hyzy 2022 ikut keluar bersama SUS) |
| Pakar RM3 | Urutan aspek per restoran dari pakar, seperti draf lama; jumlah & kriteria pakar ditulis sebagai rencana (keputusan pelaksana) |
| Judul | Bila judul memuat wilayah, diganti Jabodetabek (keputusan pelaksana) |
| Pekerjaan belum di-commit di main | Di-commit apa adanya sebagai commit pertama sebelum revisi |
| Pendekatan naskah | Ditulis ulang mengikuti susunan template; paragraf draf lama yang masih benar dipakai ulang |

## 4. RM, hipotesis, kriteria (pakem)
1. Bagaimana rancangan arsitektur lima lapis prototipe ABSA ulasan restoran berbahasa Indonesia beserta katalog kebutuhan dan kontrak antarmuka JSON antar-lapis? → diagram, katalog FR/KNF, dokumen kontrak. H1: 100% kontrak lolos validasi skema dan 100% kebutuhan terlacak ke kasus uji.
2. Berapa persentase kasus uji unit, integrasi, sistem yang lulus dan berapa waktu proses per 1.000 ulasan pada lingkungan yang dicatat, termasuk tanpa jaringan? → H1: semua uji kritis lulus dan rata-rata ≤ 60 dtk/1.000 ulasan (uji-t satu sampel, α 0,05).
3. Aspek mana yang menjadi prioritas perbaikan pertama di tiap restoran berdasar skor komposit 0–100, dan berapa korelasi peringkatnya dengan urutan pakar? → H1: median ρ Spearman antar-restoran > 0,60 (Wilcoxon satu sampel satu sisi, α 0,05) + kesesuaian aspek peringkat 1.
Tiap H0 yang tidak ditolak punya rekomendasi (lihat sheet RM-Hipotesis Final).

## 5. Isi naskah
- BAB I: 1.1 latar belakang (urgensi → gap → kontribusi rekayasa), 1.2 tiga RM bernomor, 1.3 batasan terperinci (B1–B5 + data), 1.4 tujuan & manfaat, 1.5 luaran terperinci L1–L14, 1.6 sistematika.
- BAB II: ABSA, aspek layanan (DINESERV), praproses, TF-IDF, SVM, metrik evaluasi (pendukung), skor prioritas komposit, arsitektur berlapis & kontrak, SDLC prototype, pengujian perangkat lunak (unit/integrasi/sistem/non-fungsional), korelasi Spearman & Wilcoxon, perumusan hipotesis, penelitian terdahulu (tabel).
- BAB III: 3.1 tahapan penelitian (identifikasi masalah → pengumpulan data → studi literatur → perancangan sistem [SDLC prototype: kebutuhan → desain cepat → bangun → evaluasi → perbaikan, 2 iterasi] → pengujian → analisis & penarikan simpulan), tiap lapis dirinci; 3.2 pengujian hipotesis; 3.3 rancangan pengujian perangkat lunak (tabel kasus uji dipetakan ke berkas pytest) dan non-fungsional KNF-01..05 (waktu proses, offline, latency halaman, lintas peramban, lingkungan); 3.4 alat & bahan; 3.5 jadwal.
- Format: Times New Roman 12, spasi 1,5, rata kiri-kanan, judul bab 14 tebal tengah, keterangan tabel di atas, gambar di bawah.
- Angka yang belum ada (κ, Macro-F1 data nyata, benchmark data nyata) tidak ditulis sebagai hasil; ditulis sebagai rencana dan kriteria.

## 6. Gambar & tabel
Gambar: alur penelitian, siklus prototype 2 iterasi, arsitektur lima lapis, alur data & kontrak, rumus skor prioritas (komponen), sebaran ulasan per restoran (data nyata 18 restoran), sebaran per kota, rancangan halaman antarmuka (tangkapan wireframe dari ANTARMUKA.md).
Tabel: rencana sampel per restoran, RM–luaran–hipotesis, luaran L1–L14, batasan, kebutuhan FR/KNF, kasus uji ↔ berkas uji, skenario non-fungsional, penelitian terdahulu, alat & bahan, jadwal.

## 7. Perubahan project
Butir 1–15 sheet "Perubahan Proyek", ditambah: restaurants.csv (18 aktif, target 280), default.yaml (wilayah Jabodetabek, target 5.000), `scripts/uji_pakar.py` (ρ per restoran + Wilcoxon), skala 0–100 di lapis penyajian, uji sensitivitas bobot ±10%, `docs/KONTRAK.md` dari dataclass kontrak, rancangan ini di `docs/superpowers/specs/`.

## 8. Bukan tujuan / anti-tujuan
- Bukan menaikkan akurasi; bukan membandingkan algoritma; bukan uji usability.
- Gagal bila: naskah dan kode berbeda angka/aspek/model; angka sintetis muncul sebagai hasil; sitasi di luar folder REFERENSI tanpa tanda; commit merusak uji.

## 9. Diserahkan ke pelaksana
Kalimat persis, urutan paragraf, gaya gambar, nama fungsi baru, isi jadwal (bulan Nov 2026 – Mei 2027).
