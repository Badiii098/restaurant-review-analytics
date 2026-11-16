"""Cek kandidat tempat: nama h1 + jumlah ulasan yang tersedia di Google Maps."""
from __future__ import annotations

import csv
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
SUMBER = ROOT / "config" / "resolusi_tempat.csv"

JS = """
() => {
  const h1 = (document.querySelector('h1')?.innerText || '').trim();
  const t = document.body.innerText || '';
  const m = t.match(/\\(([\\d.,]+)\\)/);
  let n = m ? m[1].replace(/[.,]/g, '') : '';
  if (!n) { const m2 = t.match(/([\\d.,]+)\\s+ulasan/); n = m2 ? m2[1].replace(/[.,]/g, '') : ''; }
  const alamat = (t.match(/\\b(Jl\\.|Jalan|Ruko|Komplek|Blok)\\s[^\\n]{8,90}/) || [''])[0];
  return {h1, n, alamat: alamat.trim()};
}
"""

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = b.contexts[0].new_page()
    for r in csv.DictReader(SUMBER.open(encoding="utf-8")):
        if not r["url"]:
            print(f"{r['kode']}  -  (tanpa URL)")
            continue
        page.goto(r["url"], wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)
        d = page.evaluate(JS)
        jumlah = int(d["n"]) if d["n"] else 0
        print(f"{r['kode']} | {d['h1'][:32]:32} | ulasan={jumlah:6d} | {d['alamat'][:46]}")
    page.close()
