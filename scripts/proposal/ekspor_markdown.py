#!/usr/bin/env python3
"""Ekspor BAB I–III ke Markdown siap-tempel (teks, tabel, rumus, daftar pustaka).

Pengganti berkas .docx bila templat FIK tidak tersedia. Isi sama persis dengan
``buat_naskah.py`` karena membaca ``naskah_bab{1,2,3}.blok()`` dan ``tabel()``.

Contoh::

    python -m scripts.proposal.ekspor_markdown --out docs/proposal
"""

from __future__ import annotations

import argparse
import importlib
from pathlib import Path

from scripts.proposal.buat_gambar import GAMBAR, nama_berkas
from scripts.proposal.pustaka import PUSTAKA, daftar
from scripts.proposal.tabel import tabel

NAMA = {1: "BAB-I", 2: "BAB-II", 3: "BAB-III"}
ROMAWI = {1: "I", 2: "II", 3: "III"}


def _sel(v: object) -> str:
    return str(v).replace("|", "\\|").replace("\n", " ")


def _tabel_md(nomor: str) -> list[str]:
    t = tabel()[nomor]
    baris = [f"**Tabel {nomor}** {t['judul']}", "", "| " + " | ".join(t["kolom"]) + " |",
             "|" + "|".join("---" for _ in t["kolom"]) + "|"]
    baris += ["| " + " | ".join(_sel(v) for v in r) + " |" for r in t["baris"]]
    baris += ["", f"*Sumber: {t['sumber']}*", ""]
    return baris


def _daftar_md(butir: list[str], penanda: str) -> list[str]:
    hasil = []
    for i, teks in enumerate(butir):
        awal = f"{i + 1}." if penanda == "1" else f"{chr(ord('a') + i)})"
        hasil.append(f"{awal} {teks}")
    return hasil + [""]


def bab_markdown(nomor: int) -> tuple[str, set[str]]:
    modul = importlib.import_module(f"scripts.proposal.naskah_bab{nomor}")
    baris: list[str] = []
    teks_semua: list[str] = []
    for blok in modul.blok():
        jenis = blok[0]
        if jenis == "h1":
            baris += [f"# BAB {ROMAWI[nomor]} {blok[1]}", ""]
        elif jenis == "h2":
            baris += [f"## {blok[1]}", ""]
        elif jenis == "h3":
            baris += [f"### {blok[1]}", ""]
        elif jenis == "p":
            baris += [blok[1], ""]; teks_semua.append(blok[1])
        elif jenis == "list":
            baris += _daftar_md(blok[1], blok[2] if len(blok) > 2 else "1"); teks_semua += blok[1]
        elif jenis == "rumus":
            baris += [f"`{blok[1]}`  **({blok[2]})**", ""]
        elif jenis == "gambar":
            baris += [f"> **[Sisipkan: {nama_berkas(blok[1])}]**", f"> *Gambar {blok[1]} {GAMBAR[blok[1]]}*", ""]
        elif jenis == "tabel":
            baris += _tabel_md(blok[1])
            t = tabel()[blok[1]]
            teks_semua += [" ".join(map(str, r)) for r in t["baris"]] + [t["sumber"]]
        else:
            raise ValueError(jenis)
    dipakai = {k for k, p in PUSTAKA.items() if any(p["sitasi"] in t for t in teks_semua)}
    return "\n".join(baris), dipakai


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    semua: set[str] = set()
    for nomor in (1, 2, 3):
        isi, dipakai = bab_markdown(nomor)
        semua |= dipakai
        berkas = out / f"{NAMA[nomor]}.md"
        berkas.write_text(isi + "\n", encoding="utf-8")
        print(f"Ditulis: {berkas}  ({len(dipakai)} sitasi)")
    pustaka = out / "DAFTAR-PUSTAKA.md"
    pustaka.write_text("# DAFTAR PUSTAKA\n\n" + "\n\n".join(daftar(semua)) + "\n", encoding="utf-8")
    print(f"Ditulis: {pustaka}  ({len(semua)} entri)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
