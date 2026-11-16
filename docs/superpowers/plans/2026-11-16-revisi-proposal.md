# Revisi Proposal + Project (Model Tunggal) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Menyelaraskan kode project, BAB I–III (.docx), serta gambar/tabel pendukung dengan feedback dosen: 3 RM, SVM tunggal tanpa swap test, Jabodetabek 18 restoran.

**Architecture:** Kode diubah di branch `revisi/model-tunggal` (commit kecil, pytest tiap commit). Gambar/tabel dibuat oleh skrip yang membaca data nyata dan config. Naskah dibangun dengan python-docx di container, dirender ke PDF untuk diperiksa, lalu disalin ke folder DRAF.

**Tech Stack:** Python 3.11+, scikit-learn, scipy, matplotlib, pytest, python-docx, LibreOffice (render cek).

**Spec:** `docs/superpowers/specs/2026-11-16-revisi-proposal-design.md`

## Global Constraints
- Aspek = 5: makanan, pelayanan, harga, suasana, fasilitas. Sentimen = positif, negatif, netral.
- Model tunggal `svm`; nama `nb` tidak boleh tersisa di src/, app/, tests/, config/, ci.yml.
- Restoran aktif = 18 (keluar: r06, r11, r14, r16, r18, r24); target per restoran 280; target total 5.000; total data 6.874.
- Bobot prioritas 0,4/0,4/0,2; skala tampil 0–100 = skor × 100.
- RM3: median ρ Spearman per restoran > 0,60, Wilcoxon satu sisi, α 0,05.
- Naskah: Times New Roman 12, spasi 1,5, justify; judul bab 14 tebal tengah; caption tabel di atas, gambar di bawah.
- Sitasi di luar folder REFERENSI ditandai "[PDF belum ada di folder REFERENSI]".
- Tidak ada angka hasil sintetis di naskah.
- Commit: `tipe(scope): pesan` + baris atribusi Co-Authored-By/Claude-Session.

## Review Focus
1. Run lama di `rra.sqlite` bermodel `nb` → halaman tetap tampil, label model tetap terbaca (uji di Task 2).
2. `--set model.name=nb` atau artefak `model_nb.joblib` → galat jelas "Model 'nb' tidak terdaftar", bukan traceback (uji di Task 1).
3. Restoran di bawah target → dilaporkan sebagai kekurangan, tidak menggagalkan alur (uji di Task 3).
4. Urutan pakar seri/identik antar-aspek atau ρ tak terdefinisi → dikeluarkan dari agregasi dan dicatat (uji di Task 5).
5. Bobot hasil perturbasi ±10% → dinormalisasi ulang ke jumlah 1 (uji di Task 4).

---

### Task 0: Persiapan repo
- [ ] Minta izin hapus untuk folder repo (git butuh untuk lock file).
- [ ] `git add -A && git commit -m "chore: simpan pekerjaan sebelum revisi"` (isi apa adanya).
- [ ] `git switch -c revisi/model-tunggal`; baseline `PYTHONPATH=src pytest -q` → catat jumlah lulus.
- [ ] Commit spec + plan: `docs(superpowers): rancangan dan rencana revisi proposal`.

### Task 1: Hapus komponen Naive Bayes
**Files:** Delete `src/rra/models/nb_model.py`, `config/model_nb.yaml`, `tests/test_modularity.py`, `artifacts/model_nb.joblib`. Modify `src/rra/models/registry.py` (BUILTIN_MODULES), `src/rra/cli.py` (hapus `--compare`, contoh `nb`; perintah `models` tetap), `src/rra/evaluate.py` (hapus uji berpasangan antar-model bila ada), `scripts/evaluate_models.py`, `.github/workflows/ci.yml` (langkah NB, `--compare`), `tests/test_models.py`, `tests/test_cli.py`, `tests/test_evaluate.py` (pakai `svm`), `tests/test_pipeline.py:110` (`model_name="svm"`).
**Interfaces:** Produces `available_models() -> {"svm": "Support Vector Machine (linear)"}`.
- [ ] Tes gagal: `test_models.py::test_only_svm_registered` → `assert set(available_models()) == {"svm"}`; `test_cli.py::test_unknown_model_gives_clear_error` → `run --set model.name=nb` returncode ≠ 0 dan stderr memuat `tidak terdaftar` tanpa `Traceback`.
- [ ] Jalankan → FAIL.
- [ ] Ubah berkas di atas; CLI menangkap `KeyError` dari `get_model_class` dan mencetak pesannya ke stderr, kode keluar 2.
- [ ] `pytest -q` → PASS; `grep -rn "\bnb\b\|naive" src app tests config .github` → kosong (kecuali komentar riwayat yang dihapus juga).
- [ ] Commit bertahap: `refactor(models): hapus komponen naive bayes`, `test(modularity): hapus uji swap model`, `ci: hapus langkah naive bayes`.

### Task 2: UI model tunggal
**Files:** `app/streamlit_app.py` (hapus selectbox model & peringatan keselarasan; `NAMA_MODEL` tetap memuat `"nb": "Naive Bayes (arsip)"` hanya untuk label run lama), `app/components.py`, `tests/test_ui_components.py`, `tests/test_ui_page.py`.
**Interfaces:** `format_skor(priority: float) -> str` di `app/components.py` → `"81,5"` untuk 0.8151 (skala 0–100, satu desimal, koma).
- [ ] Tes gagal: `test_format_skor` (0.8151 → "81,5"; 0 → "0,0"; 1 → "100,0"); `test_page_renders_archived_nb_run` (repo sementara berisi run `model_name="nb"` → halaman tampil tanpa galat).
- [ ] Implementasi; tabel peringkat memakai `format_skor`.
- [ ] `pytest -q` → PASS. Commit `refactor(ui): hapus pemilih model dan tampilkan skor 0-100`.

### Task 3: Cakupan data Jabodetabek 18 restoran
**Files:** `config/restaurants.csv` (`aktif=0` untuk 6 restoran, `target_ulasan=280` untuk 18 aktif), `config/default.yaml` (placeholder wilayah → `Jabodetabek`, `target_reviews: 5000`), `docs/AKUISISI_DATA.md` (rencana sampel, rasional n=280: galat baku maks ±5,9% pada 95%), `docs/ANOTASI.md` tetap 5 aspek, Create `tests/test_data_scope.py`.
**Interfaces:** Create `src/rra/data/scope.py`: `load_active_restaurants(path: Path) -> list[dict]`, `shortfall(active: list[dict], counts: dict[str,int]) -> list[dict]` (kode, target, terkumpul, kurang ≥ 0).
- [ ] Tes gagal: 18 aktif; kode keluar = {r06,r11,r14,r16,r18,r24}; Σ target = 5.040 ≥ 5.000; `shortfall` dengan r10=228 → kurang 52, r01=400 → kurang 0.
- [ ] Implementasi + ubah berkas config/docs. `pytest -q` → PASS.
- [ ] Commit `feat(data): batasi cakupan ke 18 restoran jabodetabek`, `docs(data): perbarui rencana sampel`.

### Task 4: Uji sensitivitas bobot ±10%
**Files:** Create `src/rra/decision/sensitivity.py`, `tests/test_sensitivity.py`; Modify `src/rra/cli.py` (subperintah `sensitivity`).
**Interfaces:** `weight_sensitivity(stats: Mapping[str, AspectStat], base: Mapping[str,float] | None = None, delta: float = 0.10) -> list[dict]` → satu baris per (komponen, arah ±): `{"komponen","arah","bobot","peringkat","peringkat_1_sama": bool, "tau_kendall": float}`.
- [ ] Tes gagal: 6 baris; bobot tiap baris berjumlah 1 (±1e-6); data dengan pelayanan dominan → `peringkat_1_sama` True di semua baris.
- [ ] Implementasi memakai `PriorityEngine`; τ dari `scipy.stats.kendalltau`.
- [ ] PASS. Commit `feat(decision): tambah uji sensitivitas bobot`.

### Task 5: Analisis kesesuaian pakar (RM3)
**Files:** Create `src/rra/analysis/__init__.py`, `src/rra/analysis/expert.py`, `scripts/uji_pakar.py`, `tests/test_expert.py`, templat `data/reference/urutan_pakar_template.csv` (kolom `kode_restoran, aspek, peringkat_pakar`).
**Interfaces:** `spearman_per_restaurant(system: dict[str, list[str]], expert: dict[str, list[str]]) -> dict[str, float | None]`; `test_median_rho(rhos: Iterable[float], threshold: float = 0.60, alpha: float = 0.05) -> dict` → `{"n","median","statistik","p","tolak_h0": bool}`; `top1_agreement(system, expert) -> float`.
- [ ] Tes gagal: urutan identik → ρ = 1,0; terbalik → −1,0; urutan pakar semua seri → `None` dan tidak masuk `test_median_rho`; 10 ρ = 0,9 → `tolak_h0` True; 10 ρ = 0,3 → False; `top1_agreement` 3 dari 4 → 0,75.
- [ ] Implementasi (`scipy.stats.spearmanr`, `wilcoxon(x - threshold, alternative="greater")`). Skrip membaca CSV pakar + tabel `priorities` run terakhir, menulis `reports/uji_pakar.json`.
- [ ] PASS. Commit `feat(analysis): tambah uji kesesuaian peringkat pakar`.

### Task 6: Dokumen project
**Files:** Create `scripts/export_contracts.py` → `docs/KONTRAK.md` (satu tabel per dataclass di `contracts.py`: bidang, tipe, default); Modify `docs/PENGUJIAN.md` (KR-1 → validasi kontrak; hapus H2 SVM vs NB, H4/KNF-03 SUS; tambah KNF-01..05; hipotesis = 3 RM spec §4), `docs/NOVELTY_DAN_GAP.md`, `README.md` (hapus K1 swap, K3 SUS, tabel pembanding; 5 aspek; Jabodetabek), `docs/ARSITEKTUR.md`, `docs/ALUR.md` (fase prototype 2 iterasi). `scripts/hitung_sus.py` dipindah ke `scripts/arsip/` dengan catatan di luar lingkup.
- [ ] `python scripts/export_contracts.py` → `docs/KONTRAK.md` memuat setiap nama kelas dataclass di contracts.py (cek dengan grep).
- [ ] `grep -rn "swap\|SUS\|ComplementNB\|enam aspek" README.md docs/*.md` → kosong (kecuali rancangan di docs/superpowers).
- [ ] `pytest -q` → PASS. Commit per berkas utama: `docs(kontrak): …`, `docs(pengujian): …`, `docs(novelty): …`, `chore(sus): arsipkan skrip sus`.

### Task 7: Gambar & tabel pendukung
**Files:** Create `scripts/proposal/buat_gambar.py` (gambar), `scripts/proposal/buat_tabel.py` (tabel CSV + PNG); keluaran ke `--out <folder GAMBAR>`.
Gambar (PNG 300 dpi, nama = nomor di naskah): 1.1 kerangka masalah→gap→kontribusi; 3.1 tahapan penelitian; 3.2 siklus prototype 2 iterasi; 3.3 arsitektur lima lapis; 3.4 alur data & kontrak; 3.5 komponen skor prioritas; 3.6 ulasan per restoran (18, garis target 280); 3.7 sebaran per kota; 3.8 wireframe halaman laporan.
Tabel (CSV + PNG): 1.1 RM–luaran–hipotesis; 1.2 luaran L1–L14; 2.1 penelitian terdahulu; 3.1 rencana sampel 18 restoran; 3.2 kebutuhan FR/KNF; 3.3 hipotesis & prosedur; 3.4 kasus uji ↔ berkas uji; 3.5 skenario non-fungsional; 3.6 alat & bahan; 3.7 jadwal Nov 2026–Mei 2027.
- [ ] Jalankan skrip → 9 PNG gambar + 10 CSV + 10 PNG tabel; buka tiap PNG dan periksa terbaca.
- [ ] Commit `feat(proposal): skrip gambar dan tabel pendukung`.

### Task 8–10: BAB I, BAB II, BAB III (.docx)
Isi mengikuti spec §5; tabel & gambar dari Task 7 ditanam dengan caption bernomor sama. Paragraf draf lama yang masih benar dipakai ulang.
- [ ] Bangun tiap bab dengan python-docx (gaya Normal Times New Roman 12, spasi 1,5, justify; Heading bab 14 tebal tengah).
- [ ] Render ke PDF (`soffice --headless --convert-to pdf`) dan lihat tiap halaman: font, caption, gambar tidak terpotong.
- [ ] Cek isi: `grep` teks bab untuk `swap|SUS|Naive Bayes|6.666|enam aspek|Jakarta Pusat dan Jakarta Selatan` → hanya muncul di penelitian terdahulu (NB) atau tidak sama sekali.
- [ ] Ganti nama draf lama ke `… - lama.docx`, simpan baru sebagai `[DRAF] - BAB-I.docx`, `[DRAF] - BAB-II.docx`, `[DRAF] - BAB-III.docx`.

### Task 11: Verifikasi akhir
- [ ] `pytest -q` di branch → semua lulus; `git log --oneline main..` tampil commit atomik.
- [ ] Silang: angka 18 / 6.874 / 5.000 / 280 / 5 aspek sama di config, docs, BAB I, BAB III, Tabel 3.1.
- [ ] Perbarui kolom Status di sheet Revisi Terpadu sesuai yang selesai.
