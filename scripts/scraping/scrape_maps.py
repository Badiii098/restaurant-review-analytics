#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper ulasan publik Google Maps (Playwright).

Kenapa perlu login sekali?
    Sejak 2026 Google Maps menampilkan maksimum 10 ulasan untuk pengunjung
    yang belum masuk, lalu memasang dinding login ("Login untuk menikmati
    fitur terbaik dari Google Maps") ketika tombol "Lihat ulasan lainnya"
    diklik. Agar bisa menggulir sampai 400 ulasan per restoran, sesi harus
    sudah login. Login dilakukan SEKALI secara manual pada profil
    `.browser-profile/`; sesi tersimpan dan dipakai lagi pada run berikutnya.

Pemakaian
    # 1) login sekali (jendela terbuka; login manual; skrip menunggu)
    python scripts/scraping/scrape_maps.py --login

    # 2) uji 2 restoran x 60 ulasan
    python scripts/scraping/scrape_maps.py --pilot

    # 3) pengambilan penuh sesuai config/restaurants.csv
    python scripts/scraping/scrape_maps.py

    # 4) memakai Brave yang sudah jalan dengan port debug
    brave-browser --remote-debugging-port=9222 --user-data-dir="$HOME/.config/brave-debug" &
    python scripts/scraping/scrape_maps.py --cdp http://127.0.0.1:9222 --limit 3

Keluaran
    data/raw/maps/<kode>_<slug>.jsonl     satu baris = satu ulasan
    data/raw/maps/<kode>_<slug>.meta.json info tempat + status pengambilan
    logs/scraping/run_<stempel>.json      ringkasan satu kali jalan
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import re
import shutil
import subprocess
import sys
import urllib.request
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import TimeoutError as PWTimeout
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils_teks import normalize_text, parse_date, parse_rating  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config" / "restaurants.csv"
RAW_DIR = ROOT / "data" / "raw" / "maps"
LOG_DIR = ROOT / "logs" / "scraping"
PROFILE_DIR = ROOT / ".browser-profile"

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/141.0.0.0 Safari/537.36")


# ---------------------------------------------------------------- utilitas ---
def slugify(text: str, maks: int = 40) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (s or "tempat")[:maks].strip("-")


def jitter(a: float = 1.4, b: float = 3.2) -> None:
    time.sleep(random.uniform(a, b))


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def baca_config(path: Path, only: set[str] | None, limit: int | None) -> list[dict]:
    with path.open(encoding="utf-8-sig") as fh:
        rows = [r for r in csv.DictReader(fh)
                if (r.get("aktif", "1").strip() not in ("0", "false", "False"))]
    if only:
        rows = [r for r in rows if r["kode"] in only]
    if limit:
        rows = rows[:limit]
    return rows


# ------------------------------------------------------------ interaksi UI ---
JS_STATUS_HALAMAN = """
() => ({
  h1: ([...document.querySelectorAll('h1')][0]?.innerText || '').trim().slice(0, 40),
  tab: document.querySelectorAll('[role="tab"]').length,
  hasil: document.querySelectorAll('a[href*="/maps/place/"]').length,
  tombol_ulasan: [...document.querySelectorAll('button')]
      .some(e => /^ulasan untuk|^ulasan/i.test((e.getAttribute('aria-label') || '').trim())),
})
"""

JS_URL_HASIL_PERTAMA = """
() => {
  const a = document.querySelector('a[href*="/maps/place/"]');
  return a ? a.href : null;
}
"""

JS_KLIK_HASIL_PERTAMA = """
() => {
  const a = document.querySelector('a[href*="/maps/place/"]');
  if (!a) return false;
  a.click();
  return true;
}
"""

JS_KLIK_TOMBOL_ULASAN = """
() => {
  const b = [...document.querySelectorAll('button')]
    .find(e => /^ulasan untuk|^ulasan$/i.test((e.getAttribute('aria-label') || '').trim()));
  if (!b) return false;
  b.click();
  return true;
}
"""

JS_KLIK_TAB_ULASAN = """
() => {
  const t = [...document.querySelectorAll('[role="tab"], button')]
    .find(e => /^ulasan/i.test((e.getAttribute('aria-label') || e.innerText || '').trim()));
  if (!t) return false;
  t.click();
  return true;
}
"""

JS_TUTUP_BANNER = """
() => {
  const b = document.querySelector('button[aria-label="Lihat lainnya"]');
  if (b && /tampilan terbatas/i.test(document.body.innerText)) { b.click(); return true; }
  return false;
}
"""

JS_BUKA_DAFTAR_PENUH = """
() => {
  const b = [...document.querySelectorAll('button')]
    .find(e => /lihat ulasan lainnya/i.test((e.innerText || '').trim()));
  if (!b) return false;
  b.scrollIntoView({block: 'center'});
  b.click();
  return true;
}
"""

JS_DIALOG_LOGIN = """
() => /login untuk menikmati fitur terbaik/i.test(document.body.innerText || '')
"""

JS_SORTIR_TERBARU = """
() => {
  const b = [...document.querySelectorAll('button')]
    .find(e => /urutkan ulasan/i.test(e.getAttribute('aria-label') || ''));
  if (!b) return false;
  b.click();
  return true;
}
"""

JS_PILIH_TERBARU = """
() => {
  const opsi = [...document.querySelectorAll('[role="menuitemradio"]')]
    .filter(e => { const r = e.getBoundingClientRect();
                   return r.width > 0 && r.height > 0 &&
                          /^terbaru$/i.test((e.innerText || '').trim()); });
  if (!opsi.length) return false;
  opsi[0].click();
  return true;
}
"""

JS_INFO_TEMPAT = """
() => {
  const judul = document.querySelector('h1');
  const alamat = document.querySelector('button[data-item-id="address"]');
  const rating = document.querySelector('div.F7nice span[aria-hidden="true"]');
  const jumlah = document.querySelector('div.F7nice span[aria-label*="ulasan"]');
  const kategori = document.querySelector('button[jsaction*="category"]');
  return {
    nama: judul ? judul.innerText.trim() : null,
    alamat: alamat ? alamat.innerText
        .replace(/[\uE000-\uF8FF]/g, '')
        .replace(/\\s+/g, ' ')
        .replace(/^Alamat:\\s*/i, '')
        .trim() : null,
    rating: rating ? rating.innerText.trim() : null,
    jumlah_ulasan_teks: jumlah ? jumlah.innerText.trim() : null,
    kategori: kategori ? kategori.innerText.trim() : null,
    url: location.href
  };
}
"""

JS_AMBIL_ULASAN = """
() => {
  return [...document.querySelectorAll('div[data-review-id]')].map(k => {
    const penulis = k.querySelector('.d4r55');
    const ratingEl = k.querySelector('span[role="img"][aria-label]');
    const teksEl = k.querySelector('.wiI7pd') || k.querySelector('.MyEned span');
    const tgl = k.querySelector('span.rsqaWe');
    const suka = k.querySelector('button[aria-label*="Suka"], span[aria-label*="Suka"]');
    const resp = k.querySelector('.CDe7pd .wiI7pd');
    return {
      review_id: k.getAttribute('data-review-id'),
      penulis: penulis ? penulis.innerText.trim() : '',
      rating_label: ratingEl ? ratingEl.getAttribute('aria-label') : '',
      tanggal_teks: tgl ? tgl.innerText.trim() : '',
      teks: teksEl ? teksEl.innerText.replace(/\\n+/g, ' ').trim() : '',
      respons_pemilik: resp ? resp.innerText.replace(/\\n+/g, ' ').trim() : '',
      suka_teks: suka ? (suka.getAttribute('aria-label') || suka.innerText || '').trim() : '',
      local_guide: /\\.Local Guide/i.test(k.innerText) ? 1 : 0
    };
  });
}
"""

JS_SCROLLER = """
() => {
  const c = [...document.querySelectorAll('div')].filter(e => {
    const s = getComputedStyle(e);
    return /(auto|scroll)/.test(s.overflowY) && e.scrollHeight > e.clientHeight + 60;
  }).sort((a, b) => b.scrollHeight - a.scrollHeight)[0];
  if (!c) return null;
  const r = c.getBoundingClientRect();
  return {x: r.x + r.width / 2, y: r.y + r.height / 2,
          sh: c.scrollHeight, ch: c.clientHeight, top: Math.round(c.scrollTop)};
}
"""

JS_GULIR_SEKALI = """
() => {
  const n = document.querySelector('div[data-review-id]');
  if (!n) { window.scrollBy(0, 2200); return -1; }
  let el = n.parentElement;
  while (el && el !== document.body) {
    const s = getComputedStyle(el);
    if (/(auto|scroll)/.test(s.overflowY) && el.scrollHeight > el.clientHeight + 40) break;
    el = el.parentElement;
  }
  if (el && el !== document.body) { el.scrollTop = el.scrollTop + el.clientHeight * 0.9; }
  else { window.scrollBy(0, 2200); }
  return el ? el.scrollTop : 0;
}
"""


# -------------------------------------------------------------- infrastruktur ---
def matikan_brave_lama(profil: str) -> int:
    """Matikan proses Brave yang memakai profil ini (mis. sisa crash tanpa port debug)."""
    import os
    profil = str(Path(profil).expanduser())
    dibunuh = 0
    for pid_dir in Path("/proc").iterdir():
        if not pid_dir.name.isdigit():
            continue
        pid = int(pid_dir.name)
        if pid == os.getpid():
            continue
        try:
            argv = (pid_dir / "cmdline").read_bytes().split(b"\x00")
        except OSError:
            continue
        if not argv or not argv[0]:
            continue
        exe = Path(argv[0].decode("utf-8", "ignore")).name
        if not exe.startswith("brave"):
            continue
        cmd = b" ".join(argv).decode("utf-8", "ignore")
        if profil in cmd:
            try:
                os.kill(pid, 15)
                dibunuh += 1
            except OSError:
                pass
    return dibunuh


def cdp_hidup(port: int) -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=2) as r:
            return r.status == 200
    except Exception:
        return False


def pastikan_brave(args) -> bool:
    """Pastikan endpoint CDP hidup; hidupkan Brave (start_new_session) bila mati."""
    if not args.cdp:
        return True
    port = urlparse(args.cdp).port or 9222
    if cdp_hidup(port):
        return True
    exe = args.brave or shutil.which("brave-browser") or shutil.which("brave")
    if not exe:
        print("      (browser) Brave tidak ditemukan, tidak bisa menghidupkan ulang", flush=True)
        return False
    sisa = matikan_brave_lama(args.profile)
    if sisa:
        print(f"      (browser) {sisa} proses Brave lama dimatikan", flush=True)
        time.sleep(3)
    print(f"      (browser) CDP mati — menghidupkan ulang Brave di port {port}", flush=True)
    subprocess.Popen(
        [exe, f"--remote-debugging-port={port}",
         f"--user-data-dir={Path(args.profile).expanduser()}",
         "--no-first-run", "--no-default-browser-check"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True,
    )
    for _ in range(40):
        time.sleep(1)
        if cdp_hidup(port):
            time.sleep(2)
            return True
    print("      (browser) Brave tidak merespons setelah 40 detik", flush=True)
    return False


def buka_browser(pw, args):
    """Kembalikan (context, page, mode)."""
    if args.cdp:
        browser = pw.chromium.connect_over_cdp(args.cdp)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        return ctx, page, f"cdp:{args.cdp}"

    opts = dict(
        user_data_dir=str(Path(args.profile).expanduser()),
        headless=args.headless,
        locale="id-ID",
        viewport={"width": 1400, "height": 950},
        user_agent=UA,
        ignore_default_args=["--enable-automation"],
        args=["--lang=id-ID", "--no-first-run", "--disable-blink-features=AutomationControlled"],
    )
    if args.brave:
        opts["executable_path"] = args.brave
        mode = f"brave:{args.brave}"
    else:
        mode = "chromium"
    # Chromium menolak/menutup diri bila profil masih dikunci proses lama
    for f in Path(opts["user_data_dir"]).glob("Singleton*"):
        try:
            f.unlink()
        except OSError:
            pass
    ctx = pw.chromium.launch_persistent_context(**opts)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    return ctx, page, mode


COOKIE_LOGIN = {"SID", "SAPISID", "__Secure-1PSID", "__Secure-3PSID"}


def sudah_login(ctx, page=None) -> bool:
    """Login dinilai dari cookie sesi Google (andal) + verifikasi halaman."""
    try:
        nama = {c["name"] for c in ctx.cookies("https://www.google.com")}
        if nama & COOKIE_LOGIN:
            return True
    except Exception:
        pass
    if page is None:
        return False
    try:
        return bool(page.evaluate(
            '() => !!document.querySelector(\'a[href*="SignOutOptions"]\')'))
    except Exception:
        return False


def tab_ulasan(page) -> bool:
    """Aktifkan tab Ulasan; tunggu elemennya muncul, lalu coba tombol 'Ulasan untuk ...'."""
    try:
        page.wait_for_selector('[role="tab"], a[href*="/maps/place/"]', timeout=15000)
    except PWTimeout:
        pass
    for _ in range(4):
        try:
            if page.evaluate(JS_KLIK_TAB_ULASAN):
                page.wait_for_timeout(2200)
                return True
            if page.evaluate(JS_KLIK_TOMBOL_ULASAN):
                page.wait_for_timeout(2500)
                return True
        except Exception:
            pass
        page.wait_for_timeout(1200)
    return False


def siapkan_daftar(page) -> dict:
    """Buka daftar ulasan penuh. Kembalikan status langkah."""
    status = {"banner_ditutup": False, "klik_daftar_penuh": False, "perlu_login": False}
    page.wait_for_timeout(1200)
    try:
        status["banner_ditutup"] = bool(page.evaluate(JS_TUTUP_BANNER))
    except Exception:
        pass
    page.wait_for_timeout(800)
    page.wait_for_timeout(600)
    try:
        status["perlu_login"] = bool(page.evaluate(JS_DIALOG_LOGIN))
    except Exception:
        pass
    return status


JS_MENU_TERBUKA = """
() => [...document.querySelectorAll('[role="menu"]')]
        .filter(e => { const r = e.getBoundingClientRect();
                       return r.width > 0 && r.height > 0; }).length
"""


def sortir_terbaru(page, verbose: bool = True) -> bool:
    """Klik 'Urutkan ulasan' -> 'Terbaru'. Diulang sampai menu benar-benar muncul."""
    for attempt in range(1, 4):
        try:
            if not page.evaluate(JS_SORTIR_TERBARU):
                page.wait_for_timeout(1500)
                continue
            page.wait_for_timeout(1300)
            if page.evaluate(JS_MENU_TERBUKA) == 0:
                if verbose:
                    print(f"      (sortir) menu belum muncul, coba lagi ({attempt})", flush=True)
                continue
            if not page.evaluate(JS_PILIH_TERBARU):
                continue
            page.wait_for_timeout(3200)
            try:
                page.keyboard.press("Escape")   # pastikan overlay menu tidak menahan roda mouse
            except Exception:
                pass
            page.wait_for_timeout(600)
            if page.evaluate(JS_MENU_TERBUKA) == 0:
                if verbose:
                    print("      sortir: Terbaru", flush=True)
                return True
        except Exception:
            page.wait_for_timeout(1000)
    if verbose:
        print("      (peringatan) sortir 'Terbaru' gagal; memakai urutan bawaan", flush=True)
    return False


def panen(page) -> list[dict]:
    try:
        return page.evaluate(JS_AMBIL_ULASAN) or []
    except Exception:
        return []


def kumpulkan(page, target: int, max_scroll: int, verbose: bool = True):
    """Gulir panel ulasan dengan roda mouse sampai target/macet.

    Google Maps hanya memuat batch ulasan berikutnya (20 kartu) bila menerima
    event wheel asli di atas panel; menyetel scrollTop / window.scrollBy tidak
    memicu pemuatan.
    """
    kumpulan: dict[str, dict] = {}

    def serap() -> None:
        for item in panen(page):
            rid = item.get("review_id")
            if rid and item.get("teks") and rid not in kumpulan:
                kumpulan[rid] = item

    serap()
    kotak = page.evaluate(JS_SCROLLER)
    if not kotak:
        return list(kumpulan.values()), {"gulir": 0, "macet": True, "sebab": "panel_tidak_ada"}
    page.mouse.move(kotak["x"], kotak["y"])

    macet = 0
    gulir = 0
    while len(kumpulan) < target and gulir < max_scroll:
        gulir += 1
        sebelum = len(kumpulan)
        page.mouse.wheel(0, 1900)
        page.wait_for_timeout(int(random.uniform(1100, 1800)))
        serap()
        if verbose and gulir % 5 == 0:
            print(f"      gulir {gulir}: {len(kumpulan)} ulasan", flush=True)
        if len(kumpulan) == sebelum:
            macet += 1
            if macet >= 6:          # ~10 detik tanpa kartu baru -> anggap habis
                break
        else:
            macet = 0
    return list(kumpulan.values()), {"gulir": gulir, "macet": macet >= 6}


# -------------------------------------------------------------- per restoran ---
def ambil_restoran(page, row: dict, target: int, max_scroll: int) -> dict:
    kode = row["kode"]
    kueri = (row.get("url") or "").strip() or row["query"]
    url = kueri if kueri.startswith("http") else (
        "https://www.google.com/maps/search/?api=1&query="
        + kueri.replace(" ", "%20") + "&hl=id&gl=ID")

    print(f"  [{kode}] buka: {row['nama']}", flush=True)
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(random.randint(2600, 3600))

    for percobaan in range(1, 4):
        status = page.evaluate(JS_STATUS_HALAMAN) or {}
        judul = (status.get("h1") or "").strip().lower()
        di_daftar = bool(status.get("hasil")) or judul in {"hasil", "results"}
        if status.get("tab") and not di_daftar:     # benar-benar di halaman tempat
            break
        if di_daftar:                               # daftar hasil -> buka URL tempat
            url_tempat = page.evaluate(JS_URL_HASIL_PERTAMA)
            if url_tempat:
                print("      (resolver) daftar hasil -> buka URL tempat", flush=True)
                page.goto(url_tempat, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(3800)
                try:
                    page.wait_for_selector('[role="tab"]', timeout=12000)
                except PWTimeout:
                    pass
                continue
        print(f"      (resolver) halaman belum siap, muat ulang ({percobaan})", flush=True)
        page.reload(wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3200)

    info = page.evaluate(JS_INFO_TEMPAT) or {}
    if not info.get("nama"):
        try:
            info["nama"] = (page.evaluate(JS_STATUS_HALAMAN) or {}).get("h1", "")
        except Exception:
            pass
    if not tab_ulasan(page):
        return {"kode": kode, "status": "tab_ulasan_gagal", "jumlah": 0, "data": [], "info": info}

    sortir_terbaru(page)
    siap = siapkan_daftar(page)
    if siap["perlu_login"]:
        data, stat = kumpulkan(page, target=min(target, 10), max_scroll=3, verbose=False)
        return {"kode": kode, "status": "perlu_login", "jumlah": len(data), "data": data,
                "info": info, "stat": stat, "siap": siap}

    data, stat = kumpulkan(page, target=target, max_scroll=max_scroll)
    status = "ok" if len(data) >= target else ("kurang" if data else "kosong")
    return {"kode": kode, "status": status, "jumlah": len(data), "data": data,
            "info": info, "stat": stat, "siap": siap}


def tulis_hasil(kode: str, nama: str, hasil: dict, target: int) -> Path:
    slug = slugify((hasil.get("info") or {}).get("nama") or nama)
    base = RAW_DIR / f"{kode}_hasil"           # kanonik, stabil lintas run
    berkas_lama = sorted(RAW_DIR.glob(f"{kode}_*.jsonl"))
    base.parent.mkdir(parents=True, exist_ok=True)
    ambil_pada = now_iso()
    hari_ini = datetime.now(timezone.utc).date()

    baris = []
    for i, r in enumerate(hasil["data"], 1):
        rating = parse_rating(r.get("rating_label", ""))
        rating = int(rating) if rating is not None else None
        tanggal, presisi = parse_date(r.get("tanggal_teks", ""), hari_ini)
        baris.append({
            "kode_restoran": kode,
            "nama_restoran_config": nama,
            "nama_tempat_maps": (hasil.get("info") or {}).get("nama"),
            "alamat": (hasil.get("info") or {}).get("alamat"),
            "kota": hasil.get("kota"),
            "kategori_config": hasil.get("kategori"),
            "peringkat_ke": i,
            "review_id": r.get("review_id"),
            "penulis": r.get("penulis"),
            "rating": rating,
            "rating_label": r.get("rating_label"),
            "tanggal_teks": r.get("tanggal_teks"),
            "tanggal": tanggal.isoformat() if tanggal else None,
            "tanggal_presisi": presisi,
            "teks": r.get("teks"),
            "teks_normal": normalize_text(r.get("teks") or ""),
            "respons_pemilik": r.get("respons_pemilik"),
            "suka_teks": r.get("suka_teks"),
            "local_guide": r.get("local_guide"),
            "sumber_url": (hasil.get("info") or {}).get("url"),
            "diambil_pada": ambil_pada,
        })

    # gabung dengan hasil run sebelumnya (akumulatif, dedup per review_id)
    lama = []
    for berkas in berkas_lama:
        with berkas.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        lama.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    sudah = {b.get("review_id") for b in lama if b.get("review_id")}
    gabung = lama + [b for b in baris if b.get("review_id") not in sudah]
    for i, b in enumerate(gabung, 1):
        b["peringkat_ke"] = i
    baris = gabung
    hasil["jumlah"] = len(gabung)
    if len(gabung) >= target:
        hasil["status"] = "ok"
    elif len(gabung) and hasil["status"] in {"kosong", "kuran", "kurang"}:
        hasil["status"] = "kurang"

    with base.with_suffix(".jsonl").open("w", encoding="utf-8") as fh:
        for b in baris:
            fh.write(json.dumps(b, ensure_ascii=False) + "\n")

    meta = {
        "kode": kode,
        "nama_config": nama,
        "target": target,
        "terkumpul": len(baris),
        "status": hasil["status"],
        "info_tempat": hasil.get("info") or {},
        "statistik_gulir": hasil.get("stat") or {},
        "siap": hasil.get("siap") or {},
        "diambil_pada": ambil_pada,
    }
    base.with_suffix(".meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return base.with_suffix(".jsonl")


# --------------------------------------------------------------------- main ---
def main() -> int:
    ap = argparse.ArgumentParser(description="Scraper ulasan Google Maps (Playwright)")
    ap.add_argument("--config", default=str(CONFIG))
    ap.add_argument("--target", type=int, default=400, help="ulasan per restoran")
    ap.add_argument("--max-scroll", type=int, default=120)
    ap.add_argument("--limit", type=int, default=None, help="batasi jumlah restoran")
    ap.add_argument("--only", default=None, help="kode restoran, mis. r01,r04")
    ap.add_argument("--pilot", action="store_true", help="2 restoran x 60 ulasan")
    ap.add_argument("--login", action="store_true",
                    help="buka jendela untuk login manual, lalu keluar")
    ap.add_argument("--login-wait", type=int, default=300,
                    help="detik menunggu login selesai (mode --login)")
    ap.add_argument("--profile", default=str(PROFILE_DIR))
    ap.add_argument("--brave", default=None, help="path Brave, mis. /usr/bin/brave-browser")
    ap.add_argument("--cdp", default=None, help="mis. http://127.0.0.1:9222")
    ap.add_argument("--headless", action="store_true")
    ap.add_argument("--jeda", type=float, default=4.0, help="jeda antar restoran (detik)")
    args = ap.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    target = 60 if args.pilot else args.target
    only = {s.strip() for s in args.only.split(",")} if args.only else None
    limit = 2 if args.pilot else args.limit
    rows = baca_config(Path(args.config), only, limit)
    if not rows:
        print("Tidak ada restoran pada config.", file=sys.stderr)
        return 1

    ringkasan = {"mulai": now_iso(), "mode": None, "target_per_restoran": target,
                 "restoran": [], "status": "berjalan"}
    kode_keluar = 0

    with sync_playwright() as pw:
        pastikan_brave(args)
        ctx, page, mode = buka_browser(pw, args)
        ringkasan["mode"] = mode
        print(f"Browser: {mode}", flush=True)

        if args.login:
            page.goto("https://accounts.google.com/ServiceLogin?hl=id"
                      "&continue=https%3A%2F%2Fwww.google.com%2Fmaps%3Fhl%3Did",
                      wait_until="domcontentloaded", timeout=60000)
            print("\n>>> Jendela browser terbuka pada halaman login Google.")
            print(">>> Masukkan email + sandi DI JENDELA ITU (jangan di chat).")
            print(">>> Jendela TIDAK akan tertutup sendiri sampai login terdeteksi.")
            print(f">>> Menunggu maksimum {args.login_wait} detik...\n", flush=True)
            batas = time.time() + args.login_wait
            ok = False
            try:
                while time.time() < batas:
                    if sudah_login(ctx, page):
                        ok = True
                        break
                    page.wait_for_timeout(2500)
            except Exception as exc:  # jendela ditutup pengguna / browser crash
                print(f"Jendela ditutup sebelum login terdeteksi "
                      f"({type(exc).__name__}).", flush=True)
                ok = False
            if ok:
                try:
                    page.goto("https://www.google.com/maps?hl=id&gl=ID",
                              wait_until="domcontentloaded", timeout=45000)
                    page.wait_for_timeout(2500)
                except Exception:
                    pass
                print("Login terdeteksi. Sesi tersimpan pada profil "
                      f"{Path(args.profile).name}/", flush=True)
            else:
                print("Login belum terdeteksi (timeout). Jalankan --login lagi.",
                      flush=True)
            try:
                ctx.close()
            except Exception:
                pass
            return 0 if ok else 2

        if not sudah_login(ctx, page):
            print("PERINGATAN: sesi belum login — Google membatasi 10 ulasan per tempat.",
                  flush=True)

        for i, row in enumerate(rows, 1):
            print(f"\n({i}/{len(rows)}) {row['kode']} — {row['nama']}", flush=True)
            hasil = None
            for percobaan in range(1, 4):
                try:
                    hasil = ambil_restoran(page, row, target=target,
                                           max_scroll=args.max_scroll)
                    break
                except Exception as exc:  # noqa: BLE001
                    jenis = type(exc).__name__
                    print(f"      error ({percobaan}/3): {jenis}: {str(exc)[:80]}", flush=True)
                    if percobaan == 3:
                        hasil = {"kode": row["kode"], "status": f"error:{jenis}",
                                 "jumlah": 0, "data": [], "info": {}}
                        break
                    try:
                        ctx.close()
                    except Exception:
                        pass
                    if not pastikan_brave(args):
                        hasil = {"kode": row["kode"], "status": "error:browser_mati",
                                 "jumlah": 0, "data": [], "info": {}}
                        break
                    time.sleep(random.uniform(3, 6))
                    try:
                        ctx, page, mode = buka_browser(pw, args)
                    except Exception as exc2:
                        print(f"      (browser) gagal sambung ulang: {type(exc2).__name__}",
                              flush=True)
                        hasil = {"kode": row["kode"], "status": "error:browser_mati",
                                 "jumlah": 0, "data": [], "info": {}}
                        break
            hasil["kota"] = row.get("kota")
            hasil["kategori"] = row.get("kategori")
            path = tulis_hasil(row["kode"], row["nama"], hasil, target)
            print(f"      status={hasil['status']} jumlah={hasil['jumlah']} -> {path.name}",
                  flush=True)
            ringkasan["restoran"].append({
                "kode": row["kode"], "nama": row["nama"], "status": hasil["status"],
                "terkumpul": hasil["jumlah"], "target": target, "berkas": path.name,
            })
            if hasil["status"] == "perlu_login":
                kode_keluar = 3
                ringkasan["status"] = "butuh_login"
                print("\nDinding login terdeteksi: Google hanya memberi 10 ulasan untuk "
                      "pengunjung anonim.\nJalankan `--login` sekali, lalu ulangi run ini.",
                      flush=True)
                break
            if i < len(rows):
                jitter(args.jeda, args.jeda + 3)

        try:
            ctx.close()
        except Exception:
            pass

    ringkasan["selesai"] = now_iso()
    ringkasan["total_terkumpul"] = sum(r["terkumpul"] for r in ringkasan["restoran"])
    if ringkasan["status"] == "berjalan":
        ringkasan["status"] = "ok"
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = LOG_DIR / f"run_{stamp}.json"
    out.write_text(json.dumps(ringkasan, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nRingkasan: {out}")
    print(f"Total terkumpul: {ringkasan['total_terkumpul']} ulasan")
    return kode_keluar


if __name__ == "__main__":
    raise SystemExit(main())
