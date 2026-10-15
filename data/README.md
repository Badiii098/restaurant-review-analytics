# Struktur data

| Direktori | Isi | Dikelola oleh |
|---|---|---|
| `raw/` | ulasan mentah: `reviews.csv` dengan kolom `review_id, text, rating, date, restaurant` | `scripts/import_reviews.py` (data nyata) atau `rra sample-data` (data contoh) |
| `reference/` | data berlabel: `labels.csv`; berkas kerja anotasi `anotator_1.csv`, `anotator_2.csv`; `pertentangan.csv`; `gold_phrases.json` | anotasi manual + `scripts/merge_labels.py` |
| `processed/` | `rra.sqlite` — hasil tiap jalan beserta komponen skor prioritas | `python -m rra.cli run` |

## Format `raw/reviews.csv`

| Kolom | Wajib | Keterangan |
|---|---|---|
| `review_id` | ya | identitas unik ulasan; untuk Google Maps gunakan awalan `GM` + sidik jari isi teks |
| `text` | ya | teks ulasan **apa adanya**, jangan diperbaiki ejaannya |
| `rating` | sebaiknya | bintang 1–5; dipakai menghitung keparahan. Bila kosong, keparahan memakai nilai bawaan 0,5 |
| `date` | tidak | tanggal ulasan (ISO `YYYY-MM-DD`) |
| `restaurant` | tidak | nama tempat, berguna bila menganalisis lebih dari satu restoran |

## Format `reference/labels.csv`

| Kolom | Isi |
|---|---|
| `review_id` | harus ada pada `raw/reviews.csv` |
| `text` | salinan teks ulasan (mempermudah pemeriksaan) |
| `aspect` | `makanan`, `pelayanan`, `harga`, `suasana`, atau `fasilitas` |
| `sentiment` | `positif`, `negatif`, atau `netral` |

Satu ulasan boleh muncul beberapa kali — satu baris per aspek. Tata cara
pelabelan ada di `docs/ANOTASI.md`.

## Isi basis data `processed/rra.sqlite`

| Tabel | Isi |
|---|---|
| `runs` | satu baris per jalan: komponen model, waktu tiap tahap, konfigurasi yang dipakai |
| `priorities` | peringkat prioritas beserta **volume, keparahan, keragaman, bobot** — bahan audit KR-2 |
| `predictions` | aspek, sentimen, dan tingkat keyakinan per ulasan |

Konfigurasi disimpan bersama setiap hasil, sehingga suatu angka dapat
direproduksi persis walau nilai bawaannya kemudian diubah.

## Catatan mengenai data mentah

Ulasan yang dikumpulkan berisi tulisan orang lain. Sebelum dipublikasikan:

- jangan menampilkan nama penulis ulasan;
- ringkas atau buramkan rincian yang dapat menunjuk seseorang;
- cantumkan sumber data dan tanggal pengambilan pada naskah skripsi;
- patuhi Syarat Layanan penyedia data — pengambilan otomatis dari Google Maps
  perlu diperhatikan ketentuannya, dan cara paling aman adalah ekspor resmi
  atau penyalinan manual dengan pencantuman sumber.
