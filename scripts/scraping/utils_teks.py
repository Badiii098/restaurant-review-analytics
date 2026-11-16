#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utilitas bersama: parsing rating, parsing tanggal relatif Google Maps, normalisasi teks.

Semua fungsi di sini dipakai oleh src/scrape_maps.py (saat akuisisi) dan
src/preprocess.py (saat pembersihan), agar aturan parsing hanya ditulis sekali.
"""
from __future__ import annotations

import re
import unicodedata
from datetime import date, timedelta

BULAN_ID = {
    "jan": 1, "januari": 1, "feb": 2, "februari": 2, "mar": 3, "maret": 3,
    "apr": 4, "april": 4, "mei": 5, "may": 5, "jun": 6, "juni": 6,
    "jul": 7, "juli": 7, "agu": 8, "agt": 8, "agustus": 8, "aug": 8,
    "sep": 9, "sept": 9, "september": 9, "okt": 10, "oktober": 10, "oct": 10,
    "nov": 11, "november": 11, "des": 12, "desember": 12, "dec": 12,
}

SATUAN_HARI = {
    "detik": 0, "second": 0, "seconds": 0,
    "menit": 0, "minute": 0, "minutes": 0,
    "jam": 0, "hour": 0, "hours": 0,
    "hari": 1, "day": 1, "days": 1,
    "minggu": 7, "week": 7, "weeks": 7,
    "bulan": 30, "month": 30, "months": 30,
    "tahun": 365, "year": 365, "years": 365,
}


def parse_rating(label: str) -> float | None:
    """Ubah label aria ('Bintang 4', '4 stars', '4,0 bintang') menjadi float."""
    if not label:
        return None
    m = re.search(r"(\d+[.,]?\d*)", label)
    if not m:
        return None
    return float(m.group(1).replace(",", "."))


def parse_date(raw: str, today: date | None = None) -> tuple[date | None, str]:
    """Parse tanggal ulasan Google Maps.

    Mengembalikan (tanggal, presisi) dengan presisi salah satu:
      'exact'    -> tanggal lengkap terbaca (mis. '12 Okt 2021')
      'relative' -> diturunkan dari teks relatif ('2 tahun lalu'), tanggal perkiraan
      'none'     -> tidak dapat diparse

    Tanggal relatif dihitung mundur dari `today` (default: hari ini) sehingga
    selalu diberi tanda perkiraan pada kolom presisi.
    """
    if not raw:
        return None, "none"
    today = today or date.today()
    s = raw.strip().lower()

    # "Diperbarui 3 minggu lalu" / "Edited 2 months ago"
    s = re.sub(r"^(diperbarui|diedit|updated|edited)\s*", "", s).strip()

    # 1) Tanggal absolut: "12 okt 2021", "12 oktober 2021", "Oct 12, 2021"
    m = re.search(r"(\d{1,2})\s+([a-z]+)\s+(\d{4})", s)
    if m:
        bln = BULAN_ID.get(m.group(2)[:9])
        if bln:
            try:
                return date(int(m.group(3)), bln, int(m.group(1))), "exact"
            except ValueError:
                pass
    m = re.search(r"([a-z]+)\s+(\d{1,2}),?\s+(\d{4})", s)
    if m:
        bln = BULAN_ID.get(m.group(1)[:9])
        if bln:
            try:
                return date(int(m.group(3)), bln, int(m.group(2))), "exact"
            except ValueError:
                pass
    # Bulan + tahun saja ("Oktober 2021")
    m = re.search(r"([a-z]+)\s+(\d{4})", s)
    if m and BULAN_ID.get(m.group(1)[:9]):
        return date(int(m.group(2)), BULAN_ID[m.group(1)[:9]], 15), "relative"

    # 2) Kata khusus
    if "baru saja" in s or "just now" in s:
        return today, "relative"
    if "kemarin" in s or s.startswith("yesterday"):
        return today - timedelta(days=1), "relative"

    # 3) Relatif berpola angka: "3 minggu lalu", "sebulan lalu", "2 years ago"
    m = re.search(r"(\d+)\s*([a-z]+)", s)
    if m:
        unit = SATUAN_HARI.get(m.group(2))
        if unit is not None:
            return today - timedelta(days=unit * int(m.group(1))), "relative"
    # "sebulan lalu", "setahun lalu", "seminggu lalu"
    for kata, hari in (("sebulan", 30), ("setahun", 365), ("seminggu", 7), ("sehari", 1)):
        if kata in s:
            return today - timedelta(days=hari), "relative"
    for kata, hari in (("a month", 30), ("a year", 365), ("a week", 7), ("an hour", 0)):
        if kata in s:
            return today - timedelta(days=hari), "relative"

    return None, "none"


def normalize_text(text: str) -> str:
    """Normalisasi ringan untuk keperluan deduplikasi & pencocokan.

    Catatan: fungsi ini TIDAK dipakai untuk membersihkan teks yang disimpan;
    teks asli tetap disimpan apa adanya pada kolom `text` (penting untuk anotasi).
    """
    if not text:
        return ""
    t = unicodedata.normalize("NFKC", text).lower()
    t = re.sub(r"http\S+|www\.\S+", " ", t)
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def is_noise(text: str, min_chars: int = 15, min_words: int = 3) -> tuple[bool, str]:
    """Tandai ulasan berpotensi noise (tidak dihapus, hanya diberi flag)."""
    t = (text or "").strip()
    if not t:
        return True, "tanpa_teks"
    if len(t) < min_chars:
        return True, "terlalu_pendek"
    if len(t.split()) < min_words:
        return True, "kurang_dari_%d_kata" % min_words
    if re.fullmatch(r"[\W\d_]+", t):
        return True, "hanya_simbol"
    return False, ""
