# Urgensi Masalah, Gap Penelitian, dan Kebaruan

Dokumen ini adalah versi ringkas dari argumentasi pada Bab I–II, ditulis
dengan sumber yang dapat diverifikasi dan dipetakan langsung ke kode.

---

## 1. Urgensi masalah

Urgensi dibangun sebagai rantai berjenjang, bukan sebagai pernyataan:

**a. Sektor usaha ini besar dan tumbuh.**
BPS mencatat sekitar **5,28 juta** usaha penyediaan makan minum, tumbuh
**8,71%**, dan **47,59%** di antaranya berupa restoran/rumah makan. Sektor
ekonomi kreatif menyumbang sekitar **38%** PDB dan menyerap **7,6 juta**
pekerjaan (Kementerian Ekraf). Artinya perbaikan mutu layanan pada skala ini
berdampak luas, bukan kasus tepi.

**b. Konsumen sudah menulis ulasan, dan ulasan itu menentukan pilihan.**
Survei BrightLocal menunjukkan sekitar **97%** konsumen membaca ulasan daring
sebelum memilih tempat makan. Dengan **229,4 juta** pengguna internet
(APJII), volume ulasan tumbuh jauh lebih cepat daripada kemampuan pemilik
usaha membacanya.

**c. Bentuk datanya tidak ramah keputusan.**
Satu ulasan dapat membicarakan beberapa aspek sekaligus dengan sentimen yang
berbeda ("makanannya enak, tapi pelayanannya lambat"). Sentimen tingkat
dokumen menyembunyikan perbedaan ini, sehingga angka "rata-rata bintang"
tidak menunjukkan **apa** yang harus diperbaiki.

**d. Yang dibutuhkan bukan diagnosis, melainkan urutan tindakan.**
Dengan sumber daya terbatas, pemilik usaha perlu tahu aspek mana yang
mendesak lebih dahulu. Peringkat yang dapat dipertanggungjawabkan itulah
keluaran yang bernilai.

**Rumusan urgensi.** Ada kesenjangan antara **volume ulasan yang tersedia**
dan **kemampuan mengubahnya menjadi urutan tindakan**. Kesenjangan itu bukan
kekurangan data, melainkan kekurangan sistem.

---

## 2. Penelusuran penelitian terdahulu

Penelusuran dilakukan pada **kombinasi** domain + metode + keluaran (ulasan
restoran Indonesia + ABSA + SVM/TF-IDF + keluaran prioritas), bukan pada
metode saja. Inilah yang paling sering terlewat: mencari "ABSA" akan
menghasilkan ratusan artikel internasional, sementara pencarian sempit itulah
yang menentukan ada atau tidaknya kebaruan.

### 2.1 Penelitian terdekat (ancaman kebaruan)

| Penelitian | Objek | Metode | Luaran |
|---|---|---|---|
| **Firdaus, Ratnawati & Setiawan (2024)**, *Jurnal Teknologi Informasi dan Ilmu Komputer* 11(6) | ulasan Depot Bamara | ABSA + SVM + TF-IDF | aspek & sentimen, akurasi ±92% |
| **Nofandi, Setiawan & Brata (2023)**, *Jurnal Pengembangan Teknologi Informasi dan Ilmu Komputer* 7(1) | ulasan Warung Wareg | ABSA + SVM + TF-IDF | aspek & sentimen, akurasi ±94% |
| **Anggina, Setiawan & Bachtiar (2022)**, *Jurnal Ilmu Statistik dan Aplikasinya* 10(2) | ulasan Formaggio Coffee and Resto | analisis sentimen aspek | pemetaan aspek layanan |

### 2.2 Konsekuensi yang harus diakui di muka

Kedua penelitian terdekat memakai **domain yang sama** (restoran Indonesia),
**data yang sama** (ulasan Google Maps), **metode yang sama** (ABSA + SVM +
TF-IDF), dan menghasilkan **luaran yang sejenis** (aspek + sentimen +
rekomendasi perbaikan). Artinya:

> **Kebaruan tidak dapat diletakkan pada algoritma.** Setiap klaim
> "menggunakan SVM untuk ABSA ulasan restoran" sudah terbukti dan tidak dapat
> dipertahankan sebagai kontribusi baru.

Menempatkan kebaruan di sana akan terbantah oleh satu pertanyaan di sidang.
Karena itu kontribusi dipindahkan ke **rekayasa sistem**, yaitu pada apa yang
belum menjadi perhatian penelitian terdekat: bagaimana sistem seperti itu
dirancang agar **komponennya dapat diganti, keputusannya dapat diaudit, dan
mutunya dapat diukur di luar ketepatan model**.

---

## 3. Peta gap penelitian

| Jenis gap | Uraian | Bukti | Kekuatan |
|---|---|---|---|
| **Gap artefak** | penelitian terdekat berhenti pada "aspek + sentimen + daftar saran"; belum ada pemisahan tegas antara **komponen klasifikasi** dan **modul keputusan** yang dapat diaudit | bagian metode kedua penelitian terdekat tidak memisahkan keduanya | kuat |
| **Gap metodologis** | belum ada **uji penggantian komponen model** sebagai bukti modularitas; klaim "sistem modular" umumnya hanya dinyatakan, tidak diuji | kedua penelitian terdekat memakai satu algoritma tetap | kuat |
| **Gap metodologis** | metrik yang dilaporkan terbatas pada akurasi/F1; **kinerja non-fungsional** (waktu latih, waktu analisis, rasa pengguna) tidak diukur | tidak ada pelaporan waktu proses atau SUS | sedang |
| **Gap empiris** | peringkat tindakan umumnya berupa daftar berurut tanpa rumus yang dapat ditelusuri; **tidak ada komponen skor yang disimpan** untuk audit | bagian hasil tidak menyertakan penyusun skor | sedang |
| **Gap domain** | "akar masalah" sering diambil dari ekstraksi kata kunci berbasis **kemenonjolan**, bukan sebab-akibat, tanpa mengakui batas ini | pemakaian RAKE/KeyBERT tanpa pembahasan kausalitas | sedang |

---

## 4. Kebaruan yang diajukan (dan buktinya)

Kebaruan dirumuskan pada tataran **artefak + metodologis** — dua kategori
terkuat yang dapat dipertahankan tanpa klaim algoritmik:

### K1. Arsitektur berlapis dengan kontrak antarmuka tetap, dibuktikan lewat uji penggantian komponen

*Pernyataan.* Sistem disusun lima lapisan dengan kontrak data yang tidak
berubah; komponen model dipilih lewat konfigurasi, bukan lewat impor di kode
pemanggil.

*Bukti.* `tests/test_modularity.py` mencatat sidik jari SHA-256 seluruh berkas
`src/rra/**/*.py` sebelum dan sesudah penggantian model SVM → Naive Bayes;
sidik jari wajib identik. Berkas konfigurasi kedua model diuji hanya berbeda
pada satu kunci (`model.name`).

*Mengapa ini kebaruan, bukan hal biasa.* Pada kedua penelitian terdekat
klaim modularitas hanya dinyatakan pada narasi. Di sini klaim itu menjadi
**pernyataan yang dapat gagal**, dan karenanya bermakna.

### K2. Modul skor prioritas yang eksplisit dan dapat diaudit

*Pernyataan.* Prioritas perbaikan dihitung dengan rumus terbuka
`Prioritas(a) = w₁·Volume + w₂·Keparahan + w₃·Keragaman`, dan setiap komponen
skor disimpan per hasil.

*Bukti.* `src/rra/decision/priority.py`; tabel `priorities` di
`data/processed/rra.sqlite` memuat volume, keparahan, keragaman, bobot, dan
perubahan peringkat.

*Mengapa ini kebaruan.* Keluaran "rekomendasi prioritas" pada penelitian
terdekat adalah daftar berurut. Mengurutkan **deskriptif**; memutuskan butuh
mekanisme. Dengan rumus terbuka dan komponen tersimpan, setiap peringkat
dapat ditelusuri sampai angka penyusunnya — dan dapat diaudit oleh pembimbing
tanpa membuka kode.

### K3. Pengukuran kinerja non-fungsional dan penerimaan pengguna

*Pernyataan.* Selain ketepatan model, sistem diukur pada waktu latih, waktu
analisis, milidetik per ulasan, serta penerimaan pengguna dengan kuesioner
SUS.

*Bukti.* `scripts/benchmark.py` → `reports/benchmark.json`; kuesioner dan
kriteria pada `docs/PENGUJIAN.md`.

*Mengapa ini kebaruan.* Sistem analitik bermanfaat hanya bila cukup cepat
dipakai berulang. Metrik ini absen dari penelitian terdekat, sehingga
perbandingannya menjadi kontribusi yang jelas.

### K4. Kejujuran klaim sebagai keputusan perancangan

*Pernyataan.* Istilah yang dipakai adalah **"frasa keluhan dominan"**, bukan
"akar masalah". Sistem tidak mengklaim mengetahui penyebab.

*Bukti.* `decision/phrases.py` (penamaan dan pendokumentasian batasnya),
`decision/polarity.py` (mengapa leksikon, bukan model kedua).

*Mengapa ini dicatat sebagai kontribusi.* Mengganti klaim yang lebih kuat
dengan klaim yang benar adalah keputusan perancangan, bukan kelemahan. Ia
juga menghilangkan satu serangan yang pasti datang di sidang.

---

## 5. Tabel pembanding dengan penelitian terdekat

| Kriteria | Firdaus dkk. (2024) | Nofandi dkk. (2023) | Sistem ini |
|---|---|---|---|
| Domain | restoran Indonesia | restoran Indonesia | restoran Indonesia |
| Metode ABSA | SVM + TF-IDF | SVM + TF-IDF | SVM + TF-IDF (**dapat diganti**) |
| Aspek | multi-aspek | multi-aspek | 5 aspek DINESERV |
| Peringkat prioritas | daftar berurut | daftar berurut | **rumus terbuka + komponen tersimpan** |
| Arsitektur berlapis | dinyatakan | dinyatakan | **diuji (sidik jari SHA-256)** |
| Uji penggantian model | — | — | **ada (SVM ↔ Naive Bayes)** |
| Evaluasi non-fungsional | — | — | **waktu latih, waktu analisis, ms/ulasan** |
| Penerimaan pengguna | — | — | **SUS** |
| Klaim kausalitas | tidak dibahas | tidak dibahas | **batas dinyatakan tegas** |

---

## 6. Kalimat yang dipakai saat mempertahankan

> Kebaruan penelitian ini bukan pada algoritmanya. ABSA dengan SVM dan TF-IDF
> pada ulasan restoran Indonesia sudah terbukti — Firdaus dkk. (2024) dan
> Nofandi dkk. (2023). Kontribusi penelitian ini ada pada rekayasa sistemnya:
> arsitektur berlapis dengan kontrak antarmuka tetap, yang dibuktikan dengan
> mengganti komponen model dari SVM ke Naive Bayes tanpa mengubah satu pun
> modul lain — dan bukti itu dijalankan otomatis pada setiap perubahan kode.
> Selain itu, prioritas perbaikan dihitung dengan rumus yang dapat ditelusuri
> sampai komponen penyusunnya, serta kinerja non-fungsional dan penerimaan
> pengguna ikut diukur.

---

## 7. Rujukan

| Sumber | Dipakai untuk |
|---|---|
| Badan Pusat Statistik (2024) — statistik usaha penyediaan makan minum | skala & pertumbuhan sektor |
| Kementerian Ekraf (2025) — kontribusi ekonomi kreatif | besaran dampak ekonomi |
| BrightLocal (2023) — perilaku konsumen terhadap ulasan daring | perilaku konsumen |
| APJII (2024) — profil pengguna internet Indonesia | penetrasi pengguna |
| Firdaus, Ratnawati & Setiawan (2024), JTIIK 11(6) | penelitian terdekat |
| Nofandi, Setiawan & Brata (2023), J-PTIIK 7(1) | penelitian terdekat |
| Anggina, Setiawan & Bachtiar (2022), Jurnal AISTHEBEST 10(2) | penelitian terdahulu |
| Hua, Denny, Taskova & Wicker (2024), *Artificial Intelligence Review* 57(11), DOI 10.1007/s10462-024-10906-z | tinjauan sistematis ABSA |
| Amou Najafabadi, Bogner, Gerostathopoulos & Lago (2024), ECSA 2024, LNCS hlm. 69–84 | arsitektur MLOps & modularitas |
| Stevens, Knutson & Patton (1995) — DINESERV | taksonomi lima aspek layanan |
| Landis & Koch (1977) — tafsiran Cohen's κ | mutu data berlabel |

> **Catatan kejujuran ilmiah.** Angka pada tabel di atas diambil dari
> publikasi masing-masing dan perlu dikutip ulang dengan nomor halaman saat
> dimasukkan ke naskah skripsi. Angka apa pun pada `reports/` yang dihasilkan
> dari data contoh **bukan** temuan penelitian dan tidak boleh dilaporkan
> sebagai hasil.
