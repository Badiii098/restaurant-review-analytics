#!/usr/bin/env python3
"""Bangun berkas BAB I–III (.docx) dari templat skripsi FIK UPNVJ.

Gaya, ukuran halaman, dan penomoran bab diambil dari templat resmi; isi bab
dari naskah_bab1.py, naskah_bab2.py, naskah_bab3.py; tabel dari tabel.py;
gambar dari folder GAMBAR (dibangkitkan buat_gambar.py).

Contoh::

    python -m scripts.proposal.buat_naskah --templat "3a.Template Skripsi.docx" \\
        --gambar ".../GAMBAR" --out ".../DRAF"
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

import importlib
from scripts.proposal.buat_gambar import nama_berkas as nama_gambar
from scripts.proposal.pustaka import PUSTAKA, daftar
from scripts.proposal.tabel import tabel

BAB = {1: "BAB-I", 2: "BAB-II", 3: "BAB-III"}
LEBAR_ISI_CM = 16.0


def _kosongkan(doc: Document) -> None:
    body = doc.element.body
    for el in list(body):
        if el.tag != qn("w:sectPr"):
            body.remove(el)


def _mulai_bab(doc: Document, nomor: int) -> None:
    """Atur penomoran bab: 'BAB I' (romawi, judul di baris berikut), subbab '1.1' arab.

    Penomoran templat dimulai dari 1; untuk BAB II dan III awalnya digeser
    lewat startOverride agar subbab bernomor 2.1 dan 3.1.
    """
    numbering = doc.part.numbering_part.element
    abs_id = None
    for num in numbering.findall(qn("w:num")):
        if num.get(qn("w:numId")) == "1":
            abs_id = num.find(qn("w:abstractNumId")).get(qn("w:val"))
    for absn in numbering.findall(qn("w:abstractNum")):
        if absn.get(qn("w:abstractNumId")) != abs_id:
            continue
        for lvl in absn.findall(qn("w:lvl")):
            il = int(lvl.get(qn("w:ilvl")))
            if il == 0:
                lvl.find(qn("w:numFmt")).set(qn("w:val"), "upperRoman")
                lvl.find(qn("w:lvlText")).set(qn("w:val"), "BAB %1")
                suff = lvl.find(qn("w:suff"))
                if suff is None:
                    suff = OxmlElement("w:suff"); lvl.insert(1, suff)
                suff.set(qn("w:val"), "nothing")
            elif lvl.find(qn("w:isLgl")) is None:
                lvl.insert(1, OxmlElement("w:isLgl"))
    for num in numbering.findall(qn("w:num")):
        if num.get(qn("w:numId")) == "1":
            for lama in num.findall(qn("w:lvlOverride")):
                num.remove(lama)
            ov = OxmlElement("w:lvlOverride"); ov.set(qn("w:ilvl"), "0")
            st = OxmlElement("w:startOverride"); st.set(qn("w:val"), str(nomor))
            ov.append(st); num.append(ov)


def _rapikan_gaya(doc: Document) -> None:
    for nama in ("Heading 1", "Heading 2", "Heading 3"):
        gaya = doc.styles[nama]
        gaya.font.name = "Times New Roman"; gaya.font.size = Pt(12 if nama != "Heading 1" else 14)
        gaya.font.bold = True; gaya.font.color.rgb = RGBColor(0, 0, 0)
        rpr = gaya.element.get_or_add_rPr(); fonts = rpr.find(qn("w:rFonts"))
        if fonts is None:
            fonts = OxmlElement("w:rFonts"); rpr.append(fonts)
        for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            fonts.set(qn(a), "Times New Roman")
        for a in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
            if fonts.get(qn(a)) is not None:
                del fonts.attrib[qn(a)]
        gaya.paragraph_format.space_before = Pt(12); gaya.paragraph_format.space_after = Pt(6)
    cap = doc.styles["Caption"]; cap.font.size = Pt(11); cap.font.italic = False
    cap.font.color.rgb = RGBColor(0, 0, 0); cap.font.name = "Times New Roman"


def _teks(par, teks: str) -> None:
    """Tulis teks; *miring* dan **tebal** sederhana didukung."""
    for bagian in re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*)", teks):
        if not bagian:
            continue
        if bagian.startswith("**"):
            par.add_run(bagian[2:-2]).bold = True
        elif bagian.startswith("*"):
            par.add_run(bagian[1:-1]).italic = True
        else:
            par.add_run(bagian)


def _paragraf(doc, teks: str) -> None:
    p = doc.add_paragraph(style="Normal"); _teks(p, teks)
    pf = p.paragraph_format; pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pf.first_line_indent = Cm(1); pf.space_after = Pt(6)


def _daftar(doc, butir: list[str], penanda: str) -> None:
    for i, teks in enumerate(butir):
        tanda = f"{i + 1}." if penanda == "1" else (f"{chr(97 + i)}." if penanda == "a" else "–")
        p = doc.add_paragraph(style="List Paragraph")
        pf = p.paragraph_format; pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        pf.left_indent = Cm(1.6); pf.first_line_indent = Cm(-0.6); pf.space_after = Pt(3)
        pf.tab_stops.add_tab_stop(Cm(1.6))
        p.add_run(f"{tanda}\t"); _teks(p, teks)


def _caption(doc, teks: str, keep_next: bool) -> None:
    p = doc.add_paragraph(style="Caption"); _teks(p, teks)
    p.paragraph_format.space_before = Pt(6); p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = keep_next


def _sel_teks(sel, teks: str, tebal=False, ukuran=10, tengah=False) -> None:
    sel.text = ""
    p = sel.paragraphs[0]
    p.paragraph_format.space_after = Pt(0); p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.line_spacing = 1.0
    if tengah:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(str(teks)); r.bold = tebal; r.font.size = Pt(ukuran)


def _arsir(sel, warna="F3F3F3") -> None:
    tcpr = sel._tc.get_or_add_tcPr(); shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), warna)
    tcpr.append(shd)


def _ulang_kepala(baris) -> None:
    trpr = baris._tr.get_or_add_trPr(); h = OxmlElement("w:tblHeader"); h.set(qn("w:val"), "true")
    trpr.append(h)


def _tabel(doc, nomor: str) -> None:
    t = tabel()[nomor]
    _caption(doc, f"Tabel {nomor} {t['judul']}", keep_next=True)
    tb = doc.add_table(rows=1, cols=len(t["kolom"]))
    tb.style = doc.styles["Table Grid"]; tb.alignment = WD_TABLE_ALIGNMENT.CENTER
    lebar = [w / sum(t["lebar"]) * LEBAR_ISI_CM for w in t["lebar"]]
    tengah = t.get("tengah_dari")
    for j, judul in enumerate(t["kolom"]):
        sel = tb.rows[0].cells[j]; _sel_teks(sel, judul, tebal=True, tengah=True); _arsir(sel)
    _ulang_kepala(tb.rows[0])
    for i, baris in enumerate(t["baris"]):
        sel_baris = tb.add_row().cells
        akhir = t.get("footer") and i == len(t["baris"]) - 1
        for j, nilai in enumerate(baris):
            _sel_teks(sel_baris[j], nilai, tebal=bool(akhir),
                      tengah=(tengah is not None and j >= tengah) or (len(str(nilai)) <= 6 and j > 0))
    tb.autofit = False
    tblpr = tb._tbl.tblPr
    tblw = tblpr.find(qn("w:tblW"))
    if tblw is None:
        tblw = OxmlElement("w:tblW"); tblpr.append(tblw)
    tblw.set(qn("w:w"), str(int(LEBAR_ISI_CM / 2.54 * 1440))); tblw.set(qn("w:type"), "dxa")
    layout = OxmlElement("w:tblLayout"); layout.set(qn("w:type"), "fixed"); tblpr.append(layout)
    grid = tb._tbl.tblGrid
    for j, kol in enumerate(grid.findall(qn("w:gridCol"))):
        kol.set(qn("w:w"), str(int(lebar[j] / 2.54 * 1440)))
    for baris in tb.rows:
        for j, sel in enumerate(baris.cells):
            sel.width = Cm(lebar[j])
    p = doc.add_paragraph(style="Normal"); r = p.add_run(f"Sumber: {t['sumber']}")
    r.italic = True; r.font.size = Pt(10); p.paragraph_format.space_after = Pt(10)


def _gambar(doc, nomor: str, folder: Path, lebar_cm: float) -> None:
    from scripts.proposal.buat_gambar import GAMBAR
    p = doc.add_paragraph(style="Normal"); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0); p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(folder / nama_gambar(nomor)), width=Cm(lebar_cm))
    _caption(doc, f"Gambar {nomor} {GAMBAR[nomor]}", keep_next=False)


def _rumus(doc, teks: str, nomor: str) -> None:
    p = doc.add_paragraph(style="Normal")
    pf = p.paragraph_format; pf.first_line_indent = Cm(0); pf.space_after = Pt(6)
    pf.tab_stops.add_tab_stop(Cm(8), WD_TAB_ALIGNMENT.CENTER)
    pf.tab_stops.add_tab_stop(Cm(16), WD_TAB_ALIGNMENT.RIGHT)
    p.add_run("\t"); r = p.add_run(teks); r.italic = True; p.add_run(f"\t({nomor})")


def _judul_tanpa_nomor(doc, teks: str) -> None:
    p = doc.add_paragraph(style="Heading 1"); p.add_run(teks)
    ppr = p._p.get_or_add_pPr(); numpr = OxmlElement("w:numPr")
    il = OxmlElement("w:ilvl"); il.set(qn("w:val"), "0"); numpr.append(il)
    ni = OxmlElement("w:numId"); ni.set(qn("w:val"), "0"); numpr.append(ni)
    ppr.insert(0, numpr)
    p.paragraph_format.page_break_before = True


def bangun(nomor: int, templat: Path, folder_gambar: Path, keluar: Path) -> Path:
    nama = BAB[nomor]
    modul = importlib.import_module(f"scripts.proposal.naskah_bab{nomor}")
    doc = Document(str(templat)); _kosongkan(doc); _mulai_bab(doc, nomor); _rapikan_gaya(doc)
    dipakai: set[str] = set()
    for blok in modul.blok():
        jenis = blok[0]
        if jenis == "h1":
            p = doc.add_paragraph(style="Heading 1"); p.add_run().add_break(); p.add_run(blok[1])
            p.paragraph_format.space_after = Pt(18)
        elif jenis in ("h2", "h3"):
            doc.add_paragraph(blok[1], style={"h2": "Heading 2", "h3": "Heading 3"}[jenis])
        elif jenis == "p":
            _paragraf(doc, blok[1])
        elif jenis == "list":
            _daftar(doc, blok[1], blok[2] if len(blok) > 2 else "1")
        elif jenis == "tabel":
            _tabel(doc, blok[1])
        elif jenis == "gambar":
            _gambar(doc, blok[1], folder_gambar, blok[2] if len(blok) > 2 else 15)
        elif jenis == "rumus":
            _rumus(doc, blok[1], blok[2])
        else:
            raise ValueError(jenis)
    for blok in modul.blok():
        if blok[0] == "tabel":
            t = tabel()[blok[1]]
            isi = [" ".join(map(str, r)) for r in t["baris"]] + [t["sumber"]]
        else:
            isi = blok[1:]
        for bagian in isi:
            teks = " ".join(bagian) if isinstance(bagian, list) else str(bagian)
            for kunci, p in PUSTAKA.items():
                if p["sitasi"] in teks or p["sitasi"].replace(" 20", " (20").replace(" 19", " (19") in teks:
                    dipakai.add(kunci)
    _judul_tanpa_nomor(doc, "DAFTAR PUSTAKA")
    for entri in daftar(dipakai):
        p = doc.add_paragraph(style="Normal"); _teks(p, entri)
        pf = p.paragraph_format; pf.left_indent = Cm(1); pf.first_line_indent = Cm(-1)
        pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; pf.space_after = Pt(6)
    target = keluar / f"[DRAF] - {nama}.docx"
    doc.save(str(target))
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--templat", required=True)
    parser.add_argument("--gambar", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--bab", type=int, nargs="*", default=[1, 2, 3])
    args = parser.parse_args()
    for n in args.bab:
        print("Ditulis:", bangun(n, Path(args.templat), Path(args.gambar), Path(args.out)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
