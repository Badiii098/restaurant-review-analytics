# Catatan tentang isi direktori ini

**Seluruh berkas di direktori ini dihasilkan dari data contoh, bukan dari data
penelitian.** Direktori `reports/` tidak disertakan pada repositori
(`.gitignore`), dan berkas-berkas ini hanya muncul setelah Anda menjalankan
`python -m rra.cli run`.

## Mengapa datanya "terlalu bagus"

`python -m rra.cli sample-data` membangkitkan ulasan dari **templat**: kalimat
disusun dari daftar frasa yang sudah terhubung dengan aspek dan sentimennya.
Akibatnya tugas klasifikasi menjadi nyaris terpisah sempurna dan angka
kinerjanya mendekati 1,00.

Itu **wajar dan disengaja**: tujuan data contoh adalah memastikan seluruh alur
(dari berkas mentah sampai rekomendasi) berjalan dan menghasilkan angka yang
dapat diperiksa, bukan mengukur kinerja model.

## Yang tidak boleh dilakukan

1. **Jangan melaporkan angka dari data contoh sebagai hasil penelitian.**
   Angka pada Bab IV harus berasal dari ulasan sesungguhnya yang Anda
   kumpulkan dan labeli secara manual.
2. **Jangan menyimpulkan model "terbaik" dari data contoh.** Perbandingan SVM
   dan Naive Bayes baru bermakna pada data nyata yang memuat variasi bahasa,
   salah tulis, dan campur kode.
3. **Jangan menyesuaikan ambang KNF setelah melihat angka ini.** Ambang sudah
   ditetapkan lebih dahulu pada `docs/PENGUJIAN.md`.

## Berkas yang muncul di sini

| Berkas | Isi |
|---|---|
| `prioritas-*.csv` | peringkat prioritas beserta komponen skornya |
| `frasa_keluhan-*.csv` | frasa keluhan dominan per aspek |
| `prediksi-*.csv` | aspek dan sentimen hasil klasifikasi per ulasan |
| `cakupan_aspek-*.csv` | sebaran aspek pada data |
| `laporan-*.md` | ringkasan lengkap dalam bentuk Markdown |
| `evaluasi.json` | 10-fold cross-validation, rincian per lipatan (bahan uji hipotesis) |
| `benchmark.json` | waktu latih, waktu analisis, milidetik per ulasan |
| `kappa.json` | kesepakatan antar-pemberi label |
| `sus.json` | rekap skor SUS |

Untuk memakai data Anda sendiri, ikuti urutan pada `docs/ALUR.md` bagian 6.
