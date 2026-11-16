# Urgensi Masalah, Gap Penelitian, dan Kontribusi

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

Menempatkan kontribusi di sana akan terbantah oleh satu pertanyaan di sidang.
Karena itu kontribusi dipindahkan ke **rekayasa sistem**, yaitu pada apa yang
belum menjadi perhatian penelitian terdekat: bagaimana sistem seperti itu
dirancang agar **komponennya dapat diganti, keputusannya dapat diaudit, dan
mutunya dapat diukur di luar ketepatan model**.

---

## 3. Peta gap penelitian

| Jenis gap | Uraian | Bukti | Kekuatan |
|---|---|---|---|
| **Gap artefak** | penelitian terdekat berhenti pada "aspek + sentimen + daftar saran"; belum ada pemisahan tegas antara **komponen klasifikasi** dan **modul keputusan** yang dapat diaudit | bagian metode kedua penelitian terdekat tidak memisahkan keduanya | kuat |
| **Gap metodologis** | klaim "sistem berlapis" umumnya hanya dinyatakan; **kontrak data antar-lapis** tidak didokumentasikan dan tidak diuji | tidak ada spesifikasi antarmuka pada penelitian terdekat | kuat |
| **Gap metodologis** | evaluasi terbatas pada akurasi/F1; **pengujian rekayasa** (unit, integrasi, sistem) dan **kinerja non-fungsional** (waktu proses, tanpa jaringan, peramban) tidak dilaporkan | tidak ada pelaporan pengujian perangkat lunak | sedang |
| **Gap empiris** | peringkat tindakan berupa daftar berurut tanpa rumus yang dapat ditelusuri dan tanpa pembanding pakar | bagian hasil tidak menyertakan penyusun skor | sedang |
| **Gap domain** | "akar masalah" diambil dari kata kunci yang menonjol, tanpa mengakui bahwa kemenonjolan bukan sebab-akibat | pemakaian ekstraksi kata kunci tanpa pembahasan kausalitas | sedang |

---

## 4. Kontribusi yang diajukan (dan buktinya)

Kontribusi dirumuskan pada tataran **artefak + metodologis**, tanpa klaim algoritmik.

### K1. Arsitektur lima lapis dengan kontrak data tetap

*Pernyataan.* Sistem disusun lima lapis (data, praproses, komponen model,
modul keputusan, antarmuka); objek yang berpindah lapis didefinisikan pada
satu berkas kontrak.

*Bukti.* `src/rra/contracts.py`, dokumen `docs/KONTRAK.md` yang dibangkitkan
dari kode, dan `tests/test_contracts.py`.

### K2. Modul skor prioritas yang eksplisit dan dapat diaudit

*Pernyataan.* `Prioritas(a) = 0,4·Volume + 0,4·Keparahan + 0,2·Keragaman`,
ditampilkan pada skala 0–100; setiap komponen disimpan per hasil, diuji
sensitivitasnya terhadap geseran bobot ±10%, dan dibandingkan dengan urutan
pakar per restoran.

*Bukti.* `src/rra/decision/priority.py`, `sensitivity.py`,
`src/rra/analysis/expert.py`; tabel `priorities` di `rra.sqlite`.

### K3. Pengujian rekayasa perangkat lunak yang terukur

*Pernyataan.* Prototipe diuji pada tingkat unit, integrasi, dan sistem, serta
pada kebutuhan non-fungsional: waktu proses per 1.000 ulasan, operasi tanpa
jaringan, latency halaman, kompatibilitas peramban, dan lingkungan.

*Bukti.* `tests/`, `scripts/benchmark.py`, `.github/workflows/ci.yml`,
`docs/PENGUJIAN.md`.

### K4. Kejujuran klaim sebagai keputusan perancangan

*Pernyataan.* Istilah yang dipakai adalah **"frasa keluhan dominan"**, bukan
"akar masalah".

*Bukti.* `decision/phrases.py`, `decision/polarity.py`.

---

## 5. Tabel pembanding dengan penelitian terdekat

| Kriteria | Firdaus dkk. (2024) | Nofandi dkk. (2023) | Sistem ini |
|---|---|---|---|
| Domain | restoran Indonesia | restoran Indonesia | 18 restoran Jabodetabek |
| Metode ABSA | SVM + TF-IDF | SVM + TF-IDF | SVM + TF-IDF |
| Aspek | multi-aspek | multi-aspek | 5 aspek DINESERV |
| Peringkat prioritas | daftar berurut | daftar berurut | **rumus terbuka, komponen tersimpan, uji sensitivitas, uji pakar** |
| Arsitektur | dinyatakan | dinyatakan | **lima lapis + kontrak terdokumentasi dan teruji** |
| Pengujian perangkat lunak | — | — | **unit, integrasi, sistem** |
| Evaluasi non-fungsional | — | — | **waktu proses, tanpa jaringan, latency, peramban** |
| Klaim kausalitas | tidak dibahas | tidak dibahas | **batas dinyatakan tegas** |

---

## 6. Kalimat yang dipakai saat mempertahankan

> Kontribusi penelitian ini bukan pada algoritmanya. ABSA dengan SVM dan
> TF-IDF pada ulasan restoran Indonesia sudah terbukti — Firdaus dkk. (2024)
> dan Nofandi dkk. (2023). Kontribusinya ada pada rekayasa sistem: arsitektur
> lima lapis dengan kontrak data yang terdokumentasi dan teruji, skor
> prioritas yang dapat ditelusuri sampai komponennya dan dibandingkan dengan
> urutan pakar, serta pengujian perangkat lunak yang terukur sampai ke kinerja
> non-fungsional.

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
