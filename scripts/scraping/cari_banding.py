"""Daftar kandidat + jumlah ulasan untuk beberapa kueri (diagnosa resolusi)."""
from __future__ import annotations

import sys

from playwright.sync_api import sync_playwright

JS = """
() => {
  const out = [], seen = new Set();
  for (const a of document.querySelectorAll('a[href*="/maps/place/"]')) {
    if (!a.href || seen.has(a.href)) continue;
    seen.add(a.href);
    const card = a.closest('div[role="feed"] > div') || a.parentElement;
    const txt = (card ? card.innerText : (a.getAttribute('aria-label') || '')).replace(/\\n+/g, ' | ');
    out.push({nama: (a.getAttribute('aria-label') || '').trim(), teks: txt.slice(0, 120), url: a.href});
    if (out.length >= 5) break;
  }
  return out;
}
"""

kueri = sys.argv[1:]
with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = b.contexts[0].new_page()
    for q in kueri:
        page.goto("https://www.google.com/maps/search/" + q.replace(" ", "%20"),
                  wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)
        print(f"\n== {q}")
        for k in page.evaluate(JS) or []:
            print(f"   - {k['nama'][:40]:40} | {k['teks'][:80]}")
    page.close()
