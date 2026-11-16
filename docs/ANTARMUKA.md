# Rancangan Antarmuka (Lapisan 5)

Berkas ini mencatat keputusan rancangan antarmuka beserta alasannya.
Tujuannya dua: menjaga tampilan tetap konsisten saat dikembangkan, dan
menyediakan bahan Bab III pada bagian rancangan sistem.

## Tujuan antarmuka

Antarmuka bukan dasbor pemantauan, melainkan **lembar laporan keputusan**.
Keluarannya satu pertanyaan: aspek layanan mana yang diperbaiki lebih
dahulu, dan atas dasar apa. Karena itu halaman disusun berurutan, bukan
sebagai kumpulan panel yang dapat dibaca dari mana saja.

## Susunan halaman

| Bagian | Isi | Alasan keberadaannya |
| --- | --- | --- |
| Bilah atas | Identitas berkas, berkas basis data, status arsip, nomor hasil | Menandai bahwa halaman adalah dokumen hasil, bukan aplikasi tanpa konteks |
| Peringatan keselarasan | Kotak amber; tampil hanya bila model terpilih ≠ model hasil | Mencegah angka dibaca sebagai milik model yang salah |
| Kepala laporan | Judul, satu kalimat temuan utama, empat keterangan sumber | Pembaca tahu angka ini berasal dari mana sebelum membaca isinya |
| Angka ringkas | Ulasan, jumlah aspek, keluhan teratas, waktu proses | Konteks besaran sebelum peringkat |
| 01 Peringkat prioritas | Tabel peringkat + batang skor + rincian komponen | Inti sistem |
| 02 Frasa keluhan dominan | Tiga frasa teratas per aspek | Menjawab "apa yang dikeluhkan", bukan sekadar "berapa banyak" |
| 03 Tindakan disarankan | Pemicu, tindakan | Menutup jarak antara diagnosis dan tindakan |
| 04 Bahan audit | Rumus, bobot, waktu per tahap, baris penelusuran | Membuktikan skor dapat dipertanggungjawabkan |
| Bilah samping | Komponen model, sumber masukan, tombol hitung ulang, status sistem | Satu-satunya kendali; sengaja sempit dan tidak menonjol |

## Aturan visual

- Satu warna sorot (hijau laut dalam `#12564A`) yang hanya dipakai untuk
  peringkat pertama, nomor bagian, dan kendali utama.
- Radius sudut 2 px, tanpa bayangan, tanpa gradien, tanpa emoji.
- Angka memakai `tabular-nums` agar kolom tidak bergoyang saat nilai berubah.
- Warna teks sekunder (`#636C6A`) dipilih agar tetap memenuhi kontras
  WCAG AA pada latar terang (rasio 4,94 pada latar kanvas, 5,41 pada latar putih).
- Batang skor memakai lebar relatif terhadap nilai tertinggi, bukan skala
  tetap 0–1, supaya perbedaan antar-aspek tetap terbaca; nilai angkanya
  tetap dicantumkan agar tidak menyesatkan.
- Label huruf besar kecil (11,5 px, `letter-spacing` 0,04 em) hanya dipakai
  untuk nama kolom tabel, label keterangan, dan judul blok — bukan untuk
  kalimat.

## Asal desain: draf Google Stitch

Draf desain dibuat dari spesifikasi yang disusun untuk sistem ini
(proyek "Restaurant Review Analytics Dashboard"; layar 1440 px dan
390 px). Bagian berikut diambil apa adanya:

- **token warna** — kanvas `#F4F5F3`, permukaan `#FFFFFF`, tinta
  `#14181A`, teks sekunder `#636C6A`, garis rambut `#DCE1DD`, satu warna
  sorot `#12564A` beserta tint `#E8EFEB`, amber `#8A5A15` (`#FCF9F2`,
  `#E8DFC9`) untuk peringatan;
- **tipografi Inter**, radius 2 px, tanpa gradien dan bayangan;
- **bilah atas institusional** dengan pemisah vertikal dan chip status;
- **kepala laporan** berupa satu kalimat kesimpulan yang menyebut aspek
  peringkat pertama, skor, dan jumlah ulasan negatif;
- **tabel peringkat** dengan satu baris disorot (latar tint, garis kiri
  2 px, nilai tebal berwarna sorot) dan batang skor di dalam lintasan;
- **dua kolom frasa** dengan blok terakhir melebar penuh ketika jumlah
  aspek ganjil;
- **panel audit dua kolom**: rumus dan bobot di kiri, penelusuran status
  di kanan.

## Yang sengaja berbeda dari draf

Draf Stitch memuat beberapa keterangan yang tidak benar untuk sistem ini.
Semuanya diganti dengan keterangan yang dapat dilacak ke basis data,
karena keterangan yang salah lebih berbahaya daripada tampilan yang
kurang meyakinkan:

| Teks draf | Kenyataan sistem | Pengganti |
| --- | --- | --- |
| "Integritas arsip: SHA-256 valid" | Tidak ada pemeriksaan hash di pipeline | Waktu pembuatan hasil (`created_at`) |
| "Diperiksa oleh: Sistem evaluator tesis" | Tidak ada peran pemeriksa | "Dibuat: <waktu hasil>" |
| Bobot 0,40 / 0,35 / 0,25 | Bobot nyata 0,40 / 0,40 / 0,20 | Dibaca dari `weights_json` hasil |
| Waktu 0,42 detik | Waktu nyata ±1,90 detik untuk 2.000 ulasan | Dibaca dari `timings_json` hasil |
| "Skor dihitung ulang tanpa menjalankan model" | Perubahan bobot ikut pada hasil berikutnya | "Bobot diambil dari hasil terakhir, bukan dari halaman ini" |
| Angka contoh (714, 320, 295, …) | Berubah setiap kali analisis dijalankan | Seluruh angka dari `rra.sqlite` |

Kotak "Status tanpa data" pada draf dipakai sebagai **keadaan kosong
yang sungguhan**: ia hanya tampil bila basis data belum memuat hasil,
bukan sebagai contoh di layar yang sudah berisi data.

## Tanggung jawab kode

| Berkas | Tanggung jawab |
| --- | --- |
| `app/theme.py` | Token warna/ukuran dan gaya global; satu-satunya tempat warna ditulis |
| `app/components.py` | Fungsi murni pembentuk HTML; tanpa Streamlit, tanpa akses data |
| `app/streamlit_app.py` | Menyusun halaman, memanggil pipeline saat tombol ditekan, membaca hasil |
| `src/rra/storage/repository.py` | Satu-satunya pintu baca/tulis `rra.sqlite` |
| `.streamlit/config.toml` | Tema dasar aplikasi (warna, tanpa menu bawaan) |

Pemisahan ini bertujuan agar tampilan dapat diuji tanpa menyalakan server
(`tests/test_ui_components.py`) dan agar Lapisan 4 tetap menjadi
satu-satunya tempat skor dihitung.

## Alur data saat halaman dibuka

1. Halaman membaca hasil **terakhir** dari `data/processed/rra.sqlite`
   (`runs`, `priorities`, `phrases`, `recommendations`).
2. Pipeline tidak dijalankan. Pelatihan hanya terjadi bila pengguna
   menekan tombol **Hitung ulang analisis** di bilah samping; hasilnya
   ditulis sebagai baris `runs` baru beserta prioritas, frasa,
   rekomendasi, dan prediksinya.
3. Bila komponen model yang dipilih berbeda dari model hasil terakhir,
   halaman menampilkan peringatan bahwa angka yang tampil berasal dari
   model lain.

Konsekuensinya: membuka halaman tidak pernah mengubah isi basis data, dan
setiap nomor hasil tetap dapat dibandingkan setelah komponen model diganti.
Antarmuka tidak pernah menghitung skor sendiri — seluruh angka yang tampil
adalah isi kolom tabel, sehingga layar dan arsip tidak dapat menyimpang.

## Aksesibilitas dan tanggap ukuran

- Kontras teks sekunder lolos WCAG AA; cincin fokus 2 px pada kendali;
- peringatan memakai tiga isyarat (warna, garis kiri tebal, judul teks),
  tidak bergantung pada warna saja;
- `prefers-reduced-motion` mematikan seluruh transisi;
- lebar isi 1160 px, bilah samping 280 px, bilah atas 44 px; pada lebar
  < 1100 px grid empat kolom melipat menjadi dua dan panel frasa/audit
  menjadi satu kolom.
