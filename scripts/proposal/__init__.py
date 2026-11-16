"""Perkakas pembangkit naskah proposal: fakta data, tabel, gambar, dan berkas .docx.

Ketergantungan tambahan: ``python-docx`` (requirements.txt) dan Graphviz
(perintah ``dot``) untuk diagram.

Urutan pakai dari akar repositori::

    python -m scripts.proposal.buat_gambar --out ".../1.PROPOSAL/GAMBAR"
    python -m scripts.proposal.buat_tabel  --out ".../1.PROPOSAL/GAMBAR"
    python -m scripts.proposal.buat_naskah --templat ".../3a.Template Skripsi (1).docx" \\
        --gambar ".../1.PROPOSAL/GAMBAR" --out ".../1.PROPOSAL/DRAF"
"""
