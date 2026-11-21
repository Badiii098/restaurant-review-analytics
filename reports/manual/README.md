# Bukti pengujian manual

Kasus uji berjenis `manual` pada `config/kebutuhan.yaml` (N-02, N-03 sementara, N-04, N-05)
dicatat sebagai berkas JSON di folder ini, satu berkas per kode kasus, misalnya `N-04.json`:

```json
{
  "kode": "N-04",
  "tanggal": "2027-02-10",
  "pelaksana": "Abdi",
  "lingkungan": "Windows 11, Chrome 131 / Firefox 133 / Edge 131",
  "langkah": "Buka http://127.0.0.1:8000, periksa sepuluh halaman",
  "hasil": "lulus",
  "lampiran": ["tangkapan/N-04-chrome.png"]
}
```

`hasil` bernilai `lulus` atau `gagal`. Dashboard (halaman Pengujian) membaca berkas ini.
Berkas yang belum ada ditampilkan sebagai "belum diuji", bukan sebagai lulus.
