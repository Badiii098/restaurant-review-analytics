# Rencana Pengujian

Dokumen ini memuat hipotesis, kriteria kelulusan, kebutuhan non-fungsional,
dan cara memperoleh bukti. Isinya sama dengan Bab III naskah proposal; angka
hasilnya menjadi bahan Bab IV.

Fokus pengujian adalah **rekayasa perangkat lunak**: uji unit, integrasi,
sistem, dan non-fungsional. Penelitian memakai satu komponen model
(TF-IDF + SVM linear); tidak ada perbandingan antar-algoritma dan tidak ada
uji penerimaan pengguna.

---

## 1. Hipotesis (satu per rumusan masalah)

| RM | H0 | H1 | Uji | Bukti |
|---|---|---|---|---|
| 1 — rancangan arsitektur, kebutuhan, kontrak | ada kontrak antar-lapis yang gagal validasi atau kebutuhan tanpa kasus uji | 100% kontrak lolos validasi dan 100% kebutuhan terlacak ke ≥ 1 kasus uji | validasi kontrak (`tests/test_contracts.py`) + matriks keterlacakan Bagian 3 | `docs/KONTRAK.md`, keluaran pytest |
| 2 — kelulusan uji dan waktu proses | ada uji kritis gagal, atau rata-rata waktu > 60 detik per 1.000 ulasan | seluruh uji kritis lulus dan rata-rata ≤ 60 detik per 1.000 ulasan | pytest; benchmark 5 ulangan; uji-t satu sampel terhadap 60 detik (α = 0,05) | keluaran pytest, `reports/benchmark.json` |
| 3 — prioritas aspek dan kesesuaian dengan pakar | median ρ Spearman antar-restoran ≤ 0,60 | median ρ > 0,60 | ρ per restoran; Wilcoxon satu sampel satu sisi terhadap 0,60 (α = 0,05); kesesuaian aspek peringkat 1 | `reports/uji_pakar.json` |

Mengapa RM3 diuji pada median antar-restoran, bukan per restoran: dengan lima
aspek, ρ = 1,0 pun belum mencapai p < 0,05 pada uji dua sisi, sehingga
kriteria "ρ ≥ 0,60 dan p < 0,05" per restoran tidak mungkin dipenuhi.

**Bila H0 tidak ditolak.** RM1: perbaiki kontrak atau tambah kasus uji pada
iterasi prototipe berikutnya. RM2: telusuri tahap terlambat dari waktu per
tahap lalu ulangi pengukuran. RM3: laporkan sebagai temuan, tinjau bobot
lewat uji sensitivitas ±10%, definisi komponen, atau cakupan frasa.

## 2. Kriteria keberhasilan rekayasa

| Kode | Kriteria | Ambang | Bukti |
|---|---|---|---|
| KR-1 | **Kontrak antar-lapis tetap** — setiap objek yang berpindah lapis mengikuti kontrak | 100% kasus `test_contracts.py` lulus | `tests/test_contracts.py`, `docs/KONTRAK.md` |
| KR-2 | **Keterlacakan keputusan** — setiap peringkat dapat ditelusuri ke komponen penyusunnya | 100% baris prioritas memuat volume, keparahan, keragaman, bobot, peringkat | tabel `priorities` di `data/processed/rra.sqlite` |
| KR-3 | **Ketahanan masukan** — alur selesai pada data tidak sempurna | alur selesai pada rating kosong, teks duplikat, ulasan tanpa aspek | `tests/test_pipeline.py` |

## 3. Kebutuhan non-fungsional

| Kode | Kebutuhan | Ambang | Cara mengukur |
|---|---|---|---|
| KNF-01 | Waktu analisis 1.000 ulasan | rata-rata ≤ 60 detik (5 ulangan) | `python -m rra.cli benchmark --repeat 5` |
| KNF-02 | Berjalan tanpa jaringan | halaman memuat hasil terakhir dan analisis ulang selesai dengan jaringan dimatikan | skenario manual, basis data lokal SQLite |
| KNF-03 | Latency muat halaman | ≤ 3 detik sampai peringkat tampil (5 ulangan) | stopwatch peramban / alat pengembang |
| KNF-04 | Kompatibilitas peramban | halaman tampil benar di Chrome, Firefox, Edge versi terbaru | uji manual + tangkapan layar |
| KNF-05 | Lingkungan | lulus pytest di Python 3.11 dan 3.12 (CI) serta di perangkat uji yang dicatat spesifikasinya | GitHub Actions + catatan perangkat |

Ambang ditetapkan **sebelum** pengukuran.

## 4. Uji fungsional (unit, integrasi, sistem)

```bash
export PYTHONPATH=src
pytest tests -q
```

| Fungsi | Berkas uji | Tingkat |
|---|---|---|
| Kontrak data antar-lapis | `test_contracts.py` | unit |
| Praproses Bahasa Indonesia | `test_preprocess.py` | unit |
| Komponen model SVM | `test_models.py` | unit |
| Modul keputusan (keparahan, prioritas, frasa, aturan) | `test_decision.py` | unit |
| Uji sensitivitas bobot ±10% | `test_sensitivity.py` | unit |
| Kesesuaian dengan pakar | `test_expert.py` | unit |
| Cakupan sampel 18 restoran | `test_data_scope.py` | unit |
| Evaluasi model (pendukung) | `test_evaluate.py` | integrasi |
| Alur menyeluruh | `test_pipeline.py` | integrasi |
| Antarmuka baris perintah | `test_cli.py` | sistem (kotak hitam, `subprocess`) |
| Komponen dan halaman antarmuka | `test_ui_components.py`, `test_ui_page.py` | sistem |

## 5. Evaluasi model (pendukung, bukan hipotesis)

Macro-F1 aspek dan sentimen dilaporkan dari 10-fold cross-validation (benih
42), dipisah per ulasan agar satu ulasan tidak muncul di data latih dan uji
sekaligus. Angka ini hanya menunjukkan bahwa komponen klasifikasi layak
dipakai; penelitian tidak bertujuan menaikkannya.

## 6. Tabel rekap bukti

| Kode | Berkas bukti | Perintah |
|---|---|---|
| H RM1, KR-1 | keluaran pytest + `docs/KONTRAK.md` | `pytest tests/test_contracts.py -v`; `python scripts/export_contracts.py` |
| H RM2, KNF-01 | `reports/benchmark.json` | `python -m rra.cli benchmark --repeat 5` |
| H RM3 | `reports/uji_pakar.json` | `python scripts/uji_pakar.py --pakar data/reference/urutan_pakar.csv` |
| Sensitivitas | `reports/sensitivitas.json` | `python -m rra.cli sensitivity --out reports/sensitivitas.json` |
| KR-2 | ekspor tabel `priorities` | `sqlite3 data/processed/rra.sqlite "select * from priorities"` |
| KNF-05 | riwayat GitHub Actions | otomatis tiap dorongan |
| Mutu data berlabel | `reports/kappa.json` | `python scripts/compute_kappa.py …` |

## 7. Yang tidak boleh disederhanakan

1. **Cohen's κ** data berlabel — tanpa ini mutu label tidak dapat dipertanggungjawabkan.
2. **Pemisahan data latih/uji per ulasan.**
3. **Kejujuran klaim** — "frasa keluhan dominan", bukan "akar masalah"; angka dari data contoh tidak dilaporkan sebagai hasil.
