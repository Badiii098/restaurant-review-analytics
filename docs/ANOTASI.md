# Panduan Anotasi Data

Panduan ini menentukan bagaimana ulasan diberi label aspek dan sentimen, agar
hasilnya dapat dipercaya dan dapat diuji kesepakatannya. Tanpa panduan yang
tetap, dua pemberi label akan memakai ukuran berbeda dan nilai Cohen's κ
menjadi tidak bermakna.

## 1. Satuan analisis

**Unit analisis: 1 ulasan dapat memiliki banyak aspek.**

Satu ulasan menjadi beberapa baris pada berkas anotasi — satu baris untuk
setiap aspek yang dibicarakan. Contoh:

> "makanannya enak banget tapi pelayanannya lama, parkirnya juga susah"

menjadi tiga baris:

| review_id | aspect | sentiment |
|---|---|---|
| GM4f21a9c7e0 | makanan | positif |
| GM4f21a9c7e0 | pelayanan | negatif |
| GM4f21a9c7e0 | fasilitas | negatif |

## 2. Taksonomi aspek (DINESERV)

| Aspek | Cakupan | Contoh penanda |
|---|---|---|
| **makanan** | rasa, porsi, kesegaran, penyajian, variasi menu, suhu hidangan | `enak`, `hambar`, `porsi kecil`, `dingin`, `menu` |
| **pelayanan** | keramahan, kecepatan, ketepatan pesanan, perhatian petugas | `ramah`, `lambat`, `lupa pesanan`, `cuek` |
| **harga** | kewajaran harga, kesesuaian dengan porsi/mutu, biaya tambahan | `mahal`, `murah`, `worth it`, `biaya layanan` |
| **suasana** | kenyamanan ruang, kebisingan, musik, suhu, tata cahaya, aroma | `nyaman`, `berisik`, `gerah`, `adem` |
| **fasilitas** | parkir, toilet, wifi, colokan, tempat wudu, kebersihan area umum | `parkir susah`, `toilet kotor`, `wifi lambat` |

Aspek DINESERV asli juga memuat **empati** dan **keandalan**. Pada konteks
ulasan restoran daring, kedua hal itu umumnya melekat pada pelayanan, sehingga
jumlah aspek diringkas menjadi lima agar jumlah contoh per aspek tetap
memadai. Peringkasan ini dicatat sebagai batasan pada Bab III.

## 3. Taksonomi sentimen

| Label | Kriteria | Contoh |
|---|---|---|
| **positif** | ada pujian atau kepuasan eksplisit/implisit | "enaknya luar biasa" |
| **negatif** | ada keluhan, kekecewaan, atau harapan yang tidak terpenuhi | "pelayanannya lambat sekali" |
| **netral** | penyebutan tanpa penilaian, atau penilaian berimbang tanpa kecenderungan | "buka dari jam 10" / "tidak terlalu enak juga tidak buruk" |

## 4. Aturan keputusan

Aturan ini yang membuat dua pemberi label bisa sepakat. Urutannya mengikat:
periksa dari atas, pakai yang pertama berlaku.

| Keadaan | Keputusan |
|---|---|
| Aspek disebut **dengan** penilaian jelas | pakai penilaian itu |
| Aspek disebut **tanpa** penilaian | `netral` |
| Aspek disebut **hanya karena** menjadi bagian dari nama menu/tempat | tidak dibuat baris |
| Satu kalimat memuat dua aspek dengan **satu** penilaian | penilaian berlaku untuk aspek terdekat yang dinilai |
| Pujian diikuti keluhan pada aspek **sama** | pakai yang terakhir disebut |
| Keluhan disampaikan sebagai **harapan** ("semoga lebih cepat") | `negatif` — harapan itu muncul karena keadaannya belum terpenuhi |
| Sarkasme/bahasa kiasan yang jelas merendahkan | `negatif` |
| Sarkasme **meragukan** (tidak jelas arahnya) | tandai pada kolom `catatan` dan pakai `netral` |
| Ulasan hanya menilai harga tanpa embel-embel lain | `harga` (bukan `makanan`) |
| Keluhan bau/aroma ruangan | `suasana`, kecuali bila jelas berasal dari makanan → `makanan` |
| Kebersihan meja/alat makan | `fasilitas`; kebersihan yang jelas menyangkut rasa → `makanan` |
| Waktu menunggu pesanan | `pelayanan`; antrean parkir → `fasilitas` |
| Ulasan yang tidak menyebut aspek mana pun | tidak dibuat baris sama sekali |

## 5. Prosedur

1. Bentuk berkas kerja:

   ```bash
   python scripts/make_annotation_template.py --overlap 150 --each 400
   ```

   Menghasilkan `data/reference/anotator_1.csv` dan `anotator_2.csv`. Sebanyak
   150 ulasan (dapat diubah) muncul di **kedua** berkas; sisanya berbeda.
   Bagian tumpang tindih itulah bahan penghitungan κ.

2. Pemberi label **bekerja terpisah** dan **tidak** mendiskusikan ulasan yang
   sedang dinilai. Berdiskusi sebelum menghitung κ akan menggelembungkan
   nilainya dan menghilangkan gunanya.

3. Latihan pembuka: kedua pemberi label menilai 20 ulasan yang sama,
   membandingkan hasil, dan menyepakati penafsiran atas aturan pada Bagian 4.
   Hasil latihan **tidak** dihitung sebagai bagian κ.

4. Mengisi berkas: satu baris per aspek, kolom `aspect` dan `sentiment`
   dihuruf kecil. Baris dengan `aspect` kosong diabaikan. Kolom `text` harus
   tetap apa adanya (jangan diubah).

5. Hitung kesepakatan:

   ```bash
   python scripts/compute_kappa.py \
       --first data/reference/anotator_1.csv \
       --second data/reference/anotator_2.csv \
       --out reports/kappa.json
   ```

6. Bila κ < 0,61: bahas pertentangan, perjelas aturan Bagian 4, ulangi
   langkah 2–5 pada ulasan yang sama. Jangan naikkan κ dengan mengurangi
   jumlah ulasan tumpang tindih.

7. Gabungkan menjadi data berlabel:

   ```bash
   python scripts/merge_labels.py
   ```

## 6. Pelaporan nilai κ

| Nilai κ | Tafsiran (Landis & Koch, 1977) |
|---|---|
| 0,81 – 1,00 | sangat kuat |
| 0,61 – 0,80 | kuat |
| 0,41 – 0,60 | sedang |
| 0,21 – 0,40 | cukup |
| 0,00 – 0,20 | lemah |

Nilai κ untuk **aspek** dan **sentimen** dilaporkan terpisah, karena
keduanya memiliki tingkat kesulitan yang berbeda. Nilai κ aspek biasanya
lebih rendah, dan itu wajar — menyatakan aspek mana yang dibicarakan memang
lebih kabur daripada menilai nada kalimatnya.

## 7. Jumlah data yang disarankan

| Keperluan | Jumlah ulasan |
|---|---|
| Uji coba alur (bukan hasil penelitian) | 200 |
| Minimum untuk pelaporan | 500 berlabel |
| Memadai (banyak aspek, kelas tidak seimbang) | 1.500 – 3.000 |
| Tumpang tindih untuk κ | 10–20% dari total, minimal 100 |

Ulasan mentah sebaiknya dikumpulkan **3–4×** jumlah yang akan dilabeli, karena
ulasan yang tidak menyebut aspek apa pun tidak menghasilkan baris label.

## 8. Kesalahan yang paling sering terjadi

| Kesalahan | Akibat | Pencegahan |
|---|---|---|
| Melabeli sentimen tingkat dokumen, bukan per aspek | model belajar pola yang salah | satu baris per aspek, selalu |
| Memperbaiki ejaan pada kolom `text` | praproses jadi tidak teruji wajar | jangan sentuh kolom `text` |
| Mendiskusikan ulasan sebelum menghitung κ | κ menggelembung, tidak bermakna | kerjakan terpisah |
| Menambah ulasan tumpang tindih demi menaikkan κ | κ tidak lagi mewakili | tetapkan jumlah tumpang tindih di muka |
| Menghapus baris sulit | data miring ke kasus mudah | catat pada kolom `catatan`, tetap masukkan |
| Satu ulasan hanya diberi satu aspek padahal memuat tiga | kehilangan informasi | baca ulasan sampai selesai sebelum mengisi |
