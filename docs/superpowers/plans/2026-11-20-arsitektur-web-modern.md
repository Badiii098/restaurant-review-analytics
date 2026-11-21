# Arsitektur Web Modern — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mengganti lapis penyajian Streamlit dengan API FastAPI + SPA React yang menampilkan setiap tahap diagram penelitian beserta buktinya, lalu menulis ulang Bab III agar selaras.

**Architecture:** Inti L1–L4 di `src/rra` tetap. Ditambah modul bukti (`agreement`, `requirements`, `iterations`, `hypotheses`, `junit`), layanan per tahap (`rra.services`), dan aplikasi HTTP (`rra.api`). Klien di `frontend/` dibangun menjadi berkas statis yang disajikan FastAPI di `/`.

**Tech Stack:** Python 3.11+, FastAPI, uvicorn, Pydantic v2, pytest, Playwright (Python); React 18, TypeScript, Vite, React Router, TanStack Query, Recharts, Vitest.

**Spec:** `docs/superpowers/specs/2026-11-20-arsitektur-web-modern-design.md`

## Global Constraints

- Pakem pada spec §2 tidak berubah: bobot 0,4/0,4/0,2; 5 aspek; 3 sentimen; TF-IDF + SVM; ambang ρ 0,60; α 0,05; KNF-01 ≤ 60 dtk per 1.000 ulasan.
- Tanpa CDN atau font daring; semua aset dibundel (KNF-02).
- Endpoint yang sumbernya belum ada mengembalikan `{"status": "belum_tersedia", "langkah": "<perintah>"}`, tidak memalsukan angka.
- Commit: `tipe(scope): pesan` (bahasa Indonesia), atomik, dan `PYTHONPATH=src pytest tests -q` lulus sebelum tiap commit.
- Teks UI dan pesan galat dalam bahasa Indonesia.
- `frontend/dist` dan `frontend/node_modules` masuk `.gitignore`.

## Review Focus

1. Basis data belum punya hasil (instalasi baru): semua halaman tampil dengan status "belum tersedia" dan perintah pembuatnya, tanpa galat 500. Diuji di Task 6 (`test_api_tanpa_hasil`).
2. `restaurants.csv` tanpa kolom `sampel` dan tanpa data mentah: `/data` tetap menjawab, `sampel_ditetapkan: false`. Diuji di Task 2.
3. Kategori yang seluruh restorannya kalah urutan: pemilihan tetap mengembalikan 8 bila kandidat ≥ 8, dan batas per kategori tidak menghasilkan kurang dari 8 selama masih ada kandidat lain. Diuji di Task 2.
4. `POST /api/v1/analisis` dipanggil dua kali bersamaan: panggilan kedua ditolak dengan 409, bukan menjalankan dua pelatihan sekaligus. Diuji di Task 6.
5. `serve` dijalankan sebelum frontend di-build: `/` mengembalikan halaman teks yang memuat `npm --prefix frontend run build`, sementara API tetap jalan. Diuji di Task 6.

---

### Task 1: Kappa menjadi modul inti

**Files:**
- Create: `src/rra/analysis/agreement.py`
- Modify: `scripts/compute_kappa.py` (impor dari modul; perilaku CLI sama), `requirements.txt` (+`fastapi>=0.115`, `uvicorn>=0.30`, `httpx>=0.27`)
- Test: `tests/test_agreement.py`

**Interfaces:**
- Produces: `cohen_kappa(first: pd.Series, second: pd.Series) -> float`, `interpret(value: float) -> str`, `compare(first_path: Path, second_path: Path, level: Literal["aspek","sentimen"]) -> dict`, `ringkas_kappa(first_path, second_path) -> dict` (`{"aspek": compare(...), "sentimen": compare(...), "n_ulasan": int}`).

- [ ] Uji `test_kappa_sempurna` (dua seri identik → 1.0), `test_kappa_kebetulan` (`["a","a","b","b"]` vs `["a","b","a","b"]` → 0.0), `test_compare_aspek_dari_berkas` (dua CSV kecil di `tmp_path`; `n_ulasan` = jumlah review_id bersama), `test_skrip_dan_modul_sama` (`scripts/compute_kappa.compare is rra.analysis.agreement.compare`).
- [ ] Jalankan, pastikan gagal; pindahkan fungsi tanpa mengubah isi; jalankan, pastikan lulus.
- [ ] Commit `refactor(analysis): pindahkan perhitungan kappa ke modul inti`.

### Task 2: Pemilihan 8 restoran secara purposive

**Files:**
- Modify: `config/default.yaml` (blok `sampling: {n_restoran: 8, rentang_tahun: [2021, 2026], maks_per_kategori: 2, batas_target: 625}`), `src/rra/io_layer/scope.py`, `scripts/proposal/fakta.py`, `tests/test_data_scope.py`
- Create: `scripts/pilih_restoran.py`

**Interfaces:**
- Produces:
  - `pilih_sampel(kandidat: list[dict], jumlah_dalam_rentang: Mapping[str,int], n: int, maks_per_kategori: int) -> list[dict]`: urut menurun menurut jumlah (seri: kode menaik), ambil sambil menghormati batas kategori; bila hasil < n karena batas, isi dari sisa urutan.
  - `target_per_restoran(tersedia: int, batas: int) -> int` = `min(tersedia, batas)`.
  - `load_sample(path: Path) -> list[dict]`: baris dengan `sampel == "1"`; `[]` bila kolom tidak ada.
  - `hitung_ulasan_dalam_rentang(maps_dir: Path, rentang: tuple[int,int]) -> dict[str,int]` (membaca `<kode>_hasil.jsonl`, bidang `tanggal`).
  - `pilih_restoran.py --tulis` menambah/mengisi kolom `sampel` dan `target_ulasan` di CSV; tanpa `--tulis` hanya mencetak.
- [ ] Uji: `test_pilih_delapan_urut_jumlah`, `test_batas_dua_per_kategori`, `test_isi_ulang_bila_batas_menyisakan_kurang`, `test_seri_diurut_kode`, `test_target_dibatasi_625`, `test_load_sample_tanpa_kolom_kosong`, `test_aktif_sesuai_konfigurasi` (pengganti U-09: jumlah aktif == 18 dan tidak ada restoran yang dikeluarkan ada di daftar aktif; bila kolom `sampel` ada, jumlahnya == `sampling.n_restoran`).
- [ ] Implementasi; `fakta.py` memakai `load_sample` bila tidak kosong, dan bila kosong memakai `pilih_sampel` atas data yang ada; `n_restoran` diambil dari konfigurasi.
- [ ] Lulus → commit `feat(data): pemilihan sampel delapan restoran secara purposive`.

### Task 3: Katalog kebutuhan dan keterlacakan

**Files:**
- Create: `config/kebutuhan.yaml`, `src/rra/requirements.py`, `tests/test_traceability.py`, `reports/manual/README.md`
- Modify: `tests/conftest.py` (daftarkan marker `req`), seluruh berkas uji yang ada (tambah `@pytest.mark.req(...)` sesuai pemetaan Tabel 3.4 di `scripts/proposal/tabel.py`), `scripts/proposal/tabel.py` (Tabel 3.2 dibaca dari katalog)

**Interfaces:**
- `kebutuhan.yaml`: `kebutuhan: [{kode, jenis: FR|KNF, uraian, kriteria, kasus: [kode_kasus]}]`, `kasus: [{kode, nama, tingkat: unit|integrasi|sistem|nonfungsional, jenis: otomatis|manual, kritis: bool}]`. Isi FR-01..08 dan KNF-01..05 disalin persis dari `tabel.py`. `kritis = true` untuk semua kasus yang dirujuk FR.
- Produces: `Katalog` (dataclass: `kebutuhan`, `kasus`), `muat_katalog(path: Path) -> Katalog`, `kasus_tanpa_bukti(katalog, marker_terkumpul: set[str], bukti_manual: set[str]) -> list[str]`, `persen_terlacak(katalog) -> float`.
- [ ] Uji `test_setiap_kebutuhan_punya_kasus`, `test_setiap_kasus_otomatis_punya_uji` (mengumpulkan marker lewat `pytest --collect-only` dalam proses: `pytest.main(["--collect-only","-q", "-p", "no:cacheprovider"], plugins=[collector])`), `test_kasus_manual_punya_berkas_bukti_atau_templat`.
- [ ] Implementasi dan beri marker; lulus → commit `feat(kebutuhan): katalog FR/KNF dan uji keterlacakan`.

### Task 4: Catatan iterasi prototipe

**Files:**
- Create: `src/rra/iterations.py`, `tests/test_iterations.py`
- Modify: `src/rra/cli.py` (`evaluate --iterasi N --catatan TEKS`), `src/rra/io_layer/sample_data.py` (tulis `dataset_meta.json` dengan `"data_contoh": true` bila belum)

**Interfaces:**
- Produces: `simpan_iterasi(laporan: dict, nomor: int, catatan: str, folder: Path, data_contoh: bool, commit: str | None) -> Path` → `folder/iterasi-{nomor}.json` berisi `{nomor, waktu, commit, data_contoh, catatan, ringkasan: laporan["summary"], per_lipatan, per_aspek}`; `muat_iterasi(folder) -> list[dict]` (urut nomor); `bandingkan(a: dict, b: dict) -> dict` (`{"aspek_macro_f1": b-a, "sentimen_macro_f1": b-a}`, 4 desimal).
- [ ] Uji simpan/muat/bandingkan pada `tmp_path`, serta `test_cli_evaluate_iterasi` (sample-data n=200, evaluate --folds 2 --iterasi 1 → berkas ada, `data_contoh` true).
- [ ] Implementasi; lulus → commit `feat(evaluasi): catatan iterasi prototipe dengan macro-f1`.

### Task 5: Ringkasan pengujian dan keputusan hipotesis

**Files:**
- Create: `src/rra/junit.py`, `src/rra/analysis/hypotheses.py`, `tests/test_hypotheses.py`

**Interfaces:**
- `ringkas_junit(path: Path) -> dict`: `{total, lulus, gagal, dilewati, per_kasus: {kode_kasus: "lulus"|"gagal"|"dilewati"}}`. Kode kasus dibaca dari properti `req`/`kasus` yang ditulis conftest lewat `record_property`.
- `uji_h1(katalog, kontrak_lolos: bool, junit: dict) -> dict`, `uji_h2(benchmark: dict, junit: dict, katalog) -> dict` (normalisasi `detik_per_1000 = total_detik × 1000 / n_ulasan` per ulangan; uji-t satu sampel satu sisi `scipy.stats.ttest_1samp(x, 60, alternative="less")`; tolak H0 bila p < 0,05 **dan** semua kasus kritis lulus), `uji_h3(laporan_pakar: dict) -> dict` (memakai `uji_median_rho`). Setiap fungsi mengembalikan `{"rm": int, "h0": str, "h1": str, "statistik": ..., "p": ..., "tolak_h0": bool | None, "status": "selesai"|"belum_tersedia", "rekomendasi": str}`.
- [ ] Uji: H2 dengan benchmark 5 ulangan 10 dtk/1.000 → tolak H0; satu kasus kritis gagal → tidak tolak; H3 dengan ρ `[1,0.9,0.9,0.8,1,0.9,0.7,0.9]` → tolak H0; masukan kosong → `belum_tersedia`.
- [ ] Implementasi (conftest: hook `pytest_runtest_makereport` menulis marker `req` sebagai properti); lulus → commit `feat(analysis): keputusan hipotesis rm1-rm3`.

### Task 6: Lapis layanan dan API

**Files:**
- Create: `src/rra/services/{__init__,tahap}.py`, `src/rra/api/{__init__,app,schemas}.py`, `tests/test_api.py`
- Modify: `src/rra/cli.py` (`serve --host 127.0.0.1 --port 8000`), `scripts/export_contracts.py` (ekspor `docs/openapi.json`)

**Interfaces:**
- `create_app(cfg: Config) -> FastAPI`; router prefix `/api/v1`; endpoint sesuai spec §5.2. Fungsi layanan `tahap.data(cfg)`, `anotasi(cfg)`, `kebutuhan(cfg)`, `desain(cfg)`, `iterasi(cfg)`, `hasil(cfg, run_id: int | None)`, `analisis(cfg) -> int`, `sensitivitas(cfg)`, `pengujian(cfg)`, `pakar(cfg)`, `hipotesis(cfg)`, `status(cfg)`, masing-masing mengembalikan `dict` yang dapat di-JSON-kan.
- `schemas.py`: `TypeAdapter` dari dataclass `contracts.py` untuk `AspectPriority`, `ComplaintPhrase`, `Recommendation`.
- Analisis ulang memakai `threading.Lock`; bila terkunci → 409 `{"detail": "Analisis sedang berjalan"}`.
- `/` dan rute SPA menyajikan `frontend/dist/index.html` (fallback rute klien); bila tidak ada → teks dengan perintah build.
- [ ] Uji (TestClient pada `tmp_path` berisi salinan config + sample-data n=200): tiap endpoint 200; `test_api_tanpa_hasil`; `test_hasil_sama_dengan_repository` (peringkat API == `ResultRepository.load_priorities`); `test_analisis_bersamaan_409`; `test_root_tanpa_build`; `test_openapi_memuat_skema_kontrak`.
- [ ] Implementasi; lulus → commit `feat(api): layanan per tahap dan api fastapi`.

### Task 7: Klien web React

**Files:**
- Create: `frontend/` (Vite React-TS): `src/api.ts` (fungsi fetch bertipe per endpoint), `src/layout/Tahapan.tsx` (navigasi samping berupa garis tahap dengan status), `src/pages/{Ringkasan,Data,Anotasi,Kebutuhan,Desain,Iterasi,Hasil,Pengujian,Pakar,Kesimpulan}.tsx`, `src/components/{Kartu,Tabel,BelumTersedia,Grafik}.tsx`, `src/styles/tokens.css` (warna dari `app/theme.py`, mode gelap via `prefers-color-scheme`), uji `src/**/*.test.tsx`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: semua endpoint Task 6. `vite.config.ts` mem-proxy `/api` → `http://127.0.0.1:8000` saat dev.
- [ ] Uji Vitest: `BelumTersedia` merender perintah `langkah`; `Hasil` merender 5 baris peringkat dari data tiruan dengan skor tampil 0–100 (`82,2`, format id-ID); `Tahapan` menampilkan 10 tahap urut diagram.
- [ ] Implementasi; `npm --prefix frontend run build` dan `npm --prefix frontend test -- --run` lulus → commit `feat(web): klien react per tahap penelitian`.

### Task 8: Uji sistem peramban, CI, dan pensiun Streamlit

**Files:**
- Create: `tests/test_e2e_web.py` (Playwright Python; dilewati bila `frontend/dist` tidak ada)
- Move: `app/` → `scripts/arsip/streamlit/`; `tests/test_ui_page.py`, `tests/test_ui_components.py` → `scripts/arsip/streamlit/tests/`
- Modify: `.github/workflows/ci.yml` (job `web`: setup-node 22, `npm ci`, build, vitest; job Python memasang build lalu menjalankan pytest + `--junitxml=reports/pytest.xml`), `requirements.txt` (hapus streamlit)

- [ ] Uji `test_setiap_halaman_tampil` (10 rute, tanpa galat konsol, judul halaman ada) dan `test_knf03_peringkat_tampil_3_detik` (marker `req("KNF-03")`, ukur dari `goto` sampai baris peringkat pertama terlihat; ≤ 3,0 dtk).
- [ ] Lulus → commit terpisah: `test(web): uji sistem peramban dan knf-03`, `chore(ui): arsipkan antarmuka streamlit`, `ci: tambah job klien web`.

### Task 9: Dokumen dan naskah Bab III

**Files:**
- Modify: `scripts/proposal/naskah_bab3.py`, `scripts/proposal/buat_gambar.py` (Gambar 3.1 sesuai diagram; 3.3 arsitektur lima lapis dengan 5a API/5b klien; 3.8 diganti tangkapan layar dashboard), `scripts/proposal/tabel.py` (3.1 kriteria sampling + realisasi dari `fakta`; 3.4 kasus uji baru; 3.6 alat + FastAPI/React/Node/Playwright), `README.md`, `docs/{ARSITEKTUR,ANTARMUKA,PENGUJIAN,ANOTASI,ALUR}.md`
- Create: `docs/superpowers/specs/2026-11-20-konflik-bab-1-2.md` (daftar kalimat Bab I/II yang bertentangan)

- [ ] Urutan subbab 3.1 mengikuti diagram: Identifikasi Masalah → Studi Literatur (2022–2026) → Pengumpulan Data (purposive 8 restoran: kriteria, rumus target `min(tersedia, 625)`) → Anotasi Data (500 ulasan, dua anotator penuh, κ Cohen per aspek dan sentimen) → Perancangan Sistem SDLC Prototipe (a. Analisis kebutuhan, b. Desain cepat: arsitektur klien-server lima lapis + kontrak + OpenAPI, c. Pembangunan prototipe dan pemodelan NLP, d. Evaluasi prototipe: Macro-F1 dan kebutuhan, iterasi 1–2) → Pengujian Perangkat Lunak (definisi uji kritis = kasus FR) → Validasi Pakar (ρ, Wilcoxon, keterbatasan n = 8 dan p minimum 1/256) → Analisis Hasil dan Penarikan Kesimpulan. Subbab 3.2–3.5 (hipotesis, alat, jadwal) dipertahankan, hanya diselaraskan.
- [ ] `python -m scripts.proposal.buat_gambar` dan `buat_tabel` jalan tanpa galat (tanpa templat docx); pytest lulus.
- [ ] Commit per berkas kelompok: `docs(naskah): rombak bab iii mengikuti diagram tahapan`, `docs(proposal): gambar dan tabel bab iii`, `docs: selaraskan readme dan dokumen arsitektur`.
