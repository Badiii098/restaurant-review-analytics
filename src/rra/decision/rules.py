"""Tabel aturan rekomendasi tindakan.

Aturan disusun berdasarkan kerangka DINESERV (Stevens dkk., 1995) dan
dinyatakan sebagai tabel yang dapat dibaca manusia, sehingga pengelola
restoran maupun penguji dapat memeriksa dasar setiap rekomendasi.

Tabel ini sengaja **tidak** dihasilkan oleh model. Rekomendasi tindakan
adalah pengetahuan domain, bukan pola statistik; menyerahkannya kepada
model akan membuat sistem sulit dipertanggungjawabkan.
"""

from __future__ import annotations

from typing import Sequence

#: Untuk setiap aspek: daftar (kata kunci, tindakan) yang diperiksa berurutan.
RULES: dict[str, list[tuple[tuple[str, ...], str]]] = {
    "makanan": [
        (("hambar", "tidak_enak", "kurang"), "Meninjau standar bumbu dan resep pada tiap shift dapur agar rasa konsisten."),
        (("asin", "terlalu_asin"), "Menetapkan takaran baku garam dan melakukan pencicipan sebelum penyajian."),
        (("basi", "bau", "tidak_segar"), "Memeriksa rantai penyimpanan bahan dan menetapkan batas waktu penyajian."),
        (("keras", "lembek", "mentah"), "Meninjau waktu dan suhu pemasakan pada menu yang paling sering dikeluhkan."),
        (("dingin",), "Menyiapkan penghangat sajian dan menetapkan batas waktu antar sebelum diantar ke meja."),
        (("porsi", "kecil", "sedikit"), "Meninjau ulang takaran porsi dan menyesuaikannya dengan harga jual."),
        (("sambal",), "Meninjau resep sambal dan menyediakan varian tingkat kepedasan."),
    ],
    "pelayanan": [
        (("lambat", "lama", "menunggu", "nunggu"), "Meninjau jumlah tenaga kerja pada jam sibuk dan mengevaluasi alur penerimaan pesanan."),
        (("salah", "keliru", "tertukar"), "Menerapkan pemeriksaan ulang pesanan sebelum disajikan dan menambah verifikasi pada sistem pesanan."),
        (("cuek", "tidak_tanggap", "tidak_ramah"), "Menyelenggarakan pelatihan keramahan dan menetapkan standar penyambutan tamu."),
        (("antre", "mengantre"), "Menambah loket atau menerapkan sistem antrean digital pada jam padat."),
    ],
    "harga": [
        (("mahal", "kemahalan", "tidak_sepadan", "tidak_sebanding"), "Meninjau ulang struktur harga dan menyajikan porsi contoh agar nilai terlihat jelas."),
        (("porsi", "kecil"), "Menyesuaikan takaran porsi terhadap harga, atau menawarkan ukuran alternatif."),
        (("biaya", "tagihan", "total"), "Memeriksa transparansi daftar harga dan kejelasan rincian tagihan."),
    ],
    "suasana": [
        (("panas", "gerah", "ac"), "Memeriksa kapasitas pendingin ruangan dan sirkulasi udara pada area utama."),
        (("kotor", "jorok", "berdebu"), "Menyusun jadwal pembersihan rutin dan menambah pemeriksaan kebersihan berkala."),
        (("berisik", "ramai", "bising"), "Meninjau tata letak ruang dan mempertimbangkan peredam suara pada area yang paling ramai."),
        (("bau", "apek", "tidak_sedap"), "Memeriksa sistem pembuangan udara dan menambah pengharum ruangan berkala."),
        (("sempit", "sesak"), "Meninjau ulang tata letak meja untuk memberi jarak antartamu yang memadai."),
    ],
    "fasilitas": [
        (("parkir", "sempit"), "Meninjau penataan area parkir dan menjajaki kerja sama lahan parkir tambahan."),
        (("toilet", "kotor", "bau"), "Menerapkan jadwal pembersihan toilet berkala yang tercatat dan menambah perlengkapan kebersihan."),
        (("wifi", "lambat", "lemot", "tidak_kencang"), "Meningkatkan kapasitas jaringan dan menempatkan titik akses tambahan."),
        (("kursi", "tempat_duduk", "meja", "sempit"), "Meninjau jumlah dan penataan tempat duduk agar lebih lapang."),
        (("colokan", "charger", "tidak_ada"), "Menambah titik colokan listrik pada area yang paling sering digunakan."),
    ],
}

#: Tindakan cadangan bila tidak ada kata kunci yang cocok.
FALLBACK: dict[str, str] = {
    "makanan": "Meninjau mutu sajian pada menu yang paling sering dikeluhkan.",
    "pelayanan": "Meninjau alur pelayanan dan menetapkan standar waktu layanan.",
    "harga": "Meninjau kesesuaian harga terhadap mutu dan porsi yang diberikan.",
    "suasana": "Meninjau kenyamanan ruang pada jam operasional tersibuk.",
    "fasilitas": "Meninjau kelengkapan dan perawatan fasilitas pendukung.",
}


def recommend_action(aspect: str, phrase: str) -> str:
    """Tentukan tindakan perbaikan untuk sebuah aspek dan frasa keluhan."""
    text = f" {phrase.lower()} "
    for keywords, action in RULES.get(aspect, []):
        for keyword in keywords:
            if f" {keyword} " in text or keyword in text:
                return action
    return FALLBACK.get(
        aspect, "Meninjau aspek ini bersama pengelola dan menyusun rencana perbaikan."
    )


def rules_for(aspect: str) -> Sequence[tuple[tuple[str, ...], str]]:
    """Kembalikan seluruh aturan pada satu aspek (untuk ditampilkan/diaudit)."""
    return RULES.get(aspect, [])
