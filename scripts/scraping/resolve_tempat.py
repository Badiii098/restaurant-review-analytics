"""Resolusi nama restoran -> URL tempat Google Maps (sekali, hasilnya disimpan).

Latar belakang: pencarian nama restoran bisa mendarat di halaman daftar hasil dan
mengambil tempat yang salah (mis. "Ayam Goreng Fatmawati" -> "Martabak Bang Joss"),
sehingga ulasan beberapa tempat tercampur. Skrip ini menyematkan URL tempat yang
tepat ke `config/restaurants.csv` supaya scraping berikutnya deterministik.

Keluaran:
  * config/resolusi_tempat.csv  (kode, nama_config, nama_maps, alamat, skor, url)
  * dengan --terapkan            -> kolom `url` di config/restaurants.csv diisi

Contoh:
  .venv/bin/python scripts/scraping/resolve_tempat.py --cdp http://127.0.0.1:9222 \
      --profile "$HOME/.config/brave-debug" --terapkan
"""
from __future__ import annotations

import argparse
import csv
import difflib
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import quote

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config" / "restaurants.csv"
HASIL = ROOT / "config" / "resolusi_tempat.csv"

JS_KANDIDAT = """
() => {
  const out = [], seen = new Set();
  for (const a of document.querySelectorAll('a[href*="/maps/place/"]')) {
    if (!a.href || seen.has(a.href)) continue;
    seen.add(a.href);
    const nama = (a.getAttribute('aria-label') || a.textContent || '').trim();
    if (nama) out.push({nama, url: a.href});
    if (out.length >= 8) break;
  }
  return out;
}
"""

JS_ALAMAT = """
() => {
  const t = document.body.innerText || '';
  const m = t.match(/\\b(Jl\\.|Jalan|Ruko|Komplek|Blok)\\s[^\\n]{8,90}/);
  return m ? m[0].trim() : '';
}
"""


def normal(teks: str) -> str:
    teks = unicodedata.normalize("NFKD", (teks or "").lower())
    teks = re.sub(r"[^a-z0-9 ]+", " ", teks)
    return re.sub(r"\s+", " ", teks).strip()


def skor(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, normal(a), normal(b)).ratio()


def cari(page, kueri: str) -> list[dict]:
    page.goto("https://www.google.com/maps/search/" + quote(kueri),
              wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(3200)
    kandidat = page.evaluate(JS_KANDIDAT) or []
    for k in kandidat:                      # bersihkan akhiran "·Link yang dibagikan"
        k["nama"] = re.split(r"\s*[·|]\s*", k["nama"])[0].strip()
    # Maps kadang langsung menampilkan satu tempat (panel/halaman), bukan daftar hasil
    judul = page.evaluate("() => (document.querySelector('h1')?.innerText || '').trim()")
    if judul and normal(judul) not in {"hasil", "results"}:
        kandidat.insert(0, {"nama": judul, "url": page.url})
    return kandidat


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cdp", default="http://127.0.0.1:9222")
    ap.add_argument("--terapkan", action="store_true", help="tulis URL terbaik ke restaurants.csv")
    ap.add_argument("--hanya", default="", help="batasi kode, mis. r05,r11")
    args = ap.parse_args()

    baris = list(csv.DictReader(CONFIG.open(encoding="utf-8")))
    pilih = {k.strip() for k in args.hanya.split(",") if k.strip()}
    keluaran = []

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(args.cdp)
        page = browser.contexts[0].new_page()

        for row in baris:
            kode, nama, kota = row["kode"], row["nama"], row["kota"]
            if pilih and kode not in pilih:
                continue
            percobaan = [
                row.get("query") or f"{nama} {kota}",
                f"{nama} {kota}",
                nama,
            ]
            terbaik = None
            for kueri in dict.fromkeys(percobaan):
                kandidat = cari(page, kueri)
                for kand in kandidat:
                    s = skor(nama, kand["nama"])
                    if terbaik is None or s > terbaik["skor"]:
                        terbaik = {"kode": kode, "nama_config": nama, "kueri": kueri,
                                   "nama_maps": kand["nama"], "url": kand["url"], "skor": round(s, 3)}
                if terbaik and terbaik["skor"] >= 0.80:
                    break

            if terbaik is None:
                terbaik = {"kode": kode, "nama_config": nama, "kueri": percobaan[0],
                           "nama_maps": "", "url": "", "skor": 0.0}

            # alamat diambil dari halaman tempat terpilih (opsional, informatif)
            if terbaik["url"]:
                page.goto(terbaik["url"], wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(2500)
                terbaik["alamat"] = (page.evaluate(JS_ALAMAT) or "")[:80]
            else:
                terbaik["alamat"] = ""

            keluaran.append(terbaik)
            tanda = "OK  " if terbaik["skor"] >= 0.80 else ("CEK " if terbaik["skor"] >= 0.55 else "GAGAL")
            print(f"{tanda} {kode} {nama[:26]:26} -> {terbaik['nama_maps'][:30]:30} "
                  f"skor={terbaik['skor']:.2f}", flush=True)

        page.close()

    kolom = ["kode", "nama_config", "nama_maps", "alamat", "skor", "kueri", "url"]
    gabung = {}
    if HASIL.exists():                      # pertahankan hasil resolusi sebelumnya
        for r in csv.DictReader(HASIL.open(encoding="utf-8")):
            gabung[r["kode"]] = r
    for r in keluaran:
        gabung[r["kode"]] = {k: r.get(k, "") for k in kolom}
    with HASIL.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=kolom)
        w.writeheader()
        for kode in sorted(gabung):
            w.writerow(gabung[kode])
    print(f"\nTersimpan: {HASIL.relative_to(ROOT)} ({len(keluaran)} baris)")

    if args.terapkan:
        peta = {r["kode"]: r["url"] for r in keluaran if r["url"]}
        for row in baris:
            if row["kode"] in peta:
                row["url"] = peta[row["kode"]]
        with CONFIG.open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(baris[0].keys()))
            w.writeheader()
            w.writerows(baris)
        print(f"URL disematkan ke {CONFIG.relative_to(ROOT)} ({len(peta)} restoran)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
