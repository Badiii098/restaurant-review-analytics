# Antarmuka Web (Lapisan 5)

Antarmuka berbentuk **klien-server**: API FastAPI (lapis 5a, `src/rra/api`,
`src/rra/services`) dan klien React + TypeScript (lapis 5b, `frontend/`).
Hasil build klien disajikan oleh FastAPI di `/`, jadi satu perintah cukup:

```bash
npm --prefix frontend install && npm --prefix frontend run build   # sekali
python -m rra.cli serve                                            # http://127.0.0.1:8000
```

## Halaman = tahap diagram penelitian

| Rute | Tahap | Bukti yang ditampilkan | Endpoint |
|---|---|---|---|
| `/` | Ringkasan | alur penelitian, statistik utama, keputusan H1–H3 | `hasil`, `data`, `hipotesis` |
| `/data` | Pengumpulan data | kandidat, sampel purposive 8 restoran, target, sebaran ulasan dan rating | `data` |
| `/anotasi` | Anotasi data | progres terhadap 500 ulasan, κ aspek dan sentimen | `anotasi` |
| `/kebutuhan` | Analisis kebutuhan | matriks FR/KNF → kasus uji → status lulus | `kebutuhan` |
| `/desain` | Desain cepat | lima lapis, tabel kontrak, bobot | `desain` |
| `/iterasi` | Prototipe & iterasi | Macro-F1 iterasi 1 vs 2, F1 per aspek, catatan perbaikan | `iterasi` |
| `/hasil` | Hasil & prioritas | peringkat 0–100, frasa keluhan, rekomendasi, sensitivitas, hitung ulang | `hasil/terakhir`, `sensitivitas`, `POST analisis` |
| `/pengujian` | Pengujian | jumlah uji, kasus per tingkat, KNF-01 per ulangan vs batas 60 s | `pengujian` |
| `/pakar` | Validasi pakar | ρ per restoran vs 0,60, median, p Wilcoxon, kesesuaian peringkat 1 | `pakar` |
| `/kesimpulan` | Analisis & kesimpulan | H0/H1, statistik uji, rekomendasi bila H0 tidak ditolak | `hipotesis` |

## Prinsip

- **Tidak ada angka karangan.** Bila sumber bukti belum ada, halaman
  menampilkan kotak "belum tersedia" berisi perintah pembuatnya.
- **Satu tempat menghitung.** Skor, κ, uji statistik dihitung di lapis 4;
  klien hanya memformat (skala 0–100, format angka id-ID).
- **Data contoh ditandai.** Bila `dataset_meta.json` menyatakan
  `data_contoh: true`, halaman menampilkan peringatan agar angka tidak dikutip.
- **Tanpa jaringan.** Seluruh aset dibundel; font memakai fon sistem.
- **Aksesibilitas dan tema.** Mode terang/gelap mengikuti sistem operasi;
  grafik memakai palet tervalidasi buta warna (biru `#2a78d6`, oranye `#eb6834`),
  label teks langsung, dan tooltip. Tata letak berlaku hingga lebar ponsel.

## Tanggung jawab kode

| Berkas | Tanggung jawab |
| --- | --- |
| `src/rra/services/tahap.py` | Membaca bukti tiap tahap; satu-satunya tempat API menyentuh berkas/basis data |
| `src/rra/api/app.py` | Rute `/api/v1`, kunci analisis (409 bila bersamaan), penyajian klien |
| `src/rra/api/schemas.py` | Model respons dari kontrak (`AspectPriority`) |
| `frontend/src/api.ts` | Klien bertipe untuk semua endpoint |
| `frontend/src/pages/*` | Satu berkas per halaman/tahap |
| `frontend/src/components/Grafik.tsx` | Grafik batang SVG (satu/dua seri, garis acuan, tooltip) |
| `frontend/src/styles/tokens.css` | Token warna terang/gelap; satu-satunya tempat warna ditulis |

Antarmuka Streamlit iterasi pertama diarsipkan di `scripts/arsip/streamlit/`.
