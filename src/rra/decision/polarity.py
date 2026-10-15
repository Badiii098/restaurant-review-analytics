"""Leksikon polaritas domain restoran dan penyaring klausa keluhan.

**Mengapa leksikon, bukan model.** Penentuan sentimen pada tingkat ulasan
sudah dikerjakan komponen model. Namun satu ulasan dapat memuat beberapa
klausa dengan polaritas berlawanan — "pesanannya datang cepat tapi
pelayannya cuek". Bila seluruh klausa dipakai, kata "cepat" ikut terhitung
sebagai keluhan dan merusak ketepatan daftar frasa.

Karena itu diperlukan penilaian polaritas pada tingkat klausa. Penilaian
ini sengaja memakai leksikon yang dinyatakan terbuka, bukan model kedua,
karena tiga alasan:

1. **Dapat diaudit.** Setiap kata yang menentukan sebuah klausa disebut
   keluhan dapat diperiksa pada berkas ini.
2. **Tidak menambah beban pelatihan.** Leksikon tidak perlu data berlabel.
3. **Tidak mengaburkan asal keputusan.** Komponen model tetap satu-satunya
   pihak yang menentukan aspek dan sentimen; leksikon hanya menyaring
   klausa mana yang layak dianalisis lebih lanjut.

Keterbatasan yang disadari: leksikon tidak mengenali sarkasme dan tidak
menangani kata yang tidak tercantum. Keterbatasan ini dicatat pada Bab IV
dan tidak disembunyikan.
"""

from __future__ import annotations

#: Kata bermuatan positif pada domain layanan restoran.
POSITIVE_WORDS: frozenset[str] = frozenset(
    {
        "enak", "lezat", "gurih", "segar", "hangat", "matang", "pas", "konsisten",
        "variatif", "melimpah", "banyak", "murah", "terjangkau", "sepadan",
        "sesuai", "sebanding", "irit", "nilai",
        "ramah", "cepat", "sigap", "tanggap", "melayani", "sopan", "profesional",
        "nyaman", "adem", "bersih", "wangi", "luas", "lapang", "rapi", "tenang",
        "kencang", "lancar", "lengkap", "mudah", "strategis",
        "puas", "suka", "bagus", "baik", "memuaskan", "mantap", "nampol",
        "rekomendasi", "cocok", "sesuai standar",
    }
)

#: Kata bermuatan negatif pada domain layanan restoran.
NEGATIVE_WORDS: frozenset[str] = frozenset(
    {
        "hambar", "asin", "basi", "keras", "lembek", "mentah", "dingin", "pahit",
        "bland", "kering", "alot", "anyir", "sedikit", "kurang",
        "mahal", "kemahalan", "overprice", "mengecewakan", "tidak_sepadan",
        "lambat", "lama", "menunggu", "nunggu", "cuek", "acuh", "kasar", "ketus",
        "salah", "keliru", "tertukar", "lupa", "berantakan", "antre", "mengantre",
        "kotor", "jorok", "berdebu", "lengket", "kumal", "apek", "bau", "berisik",
        "bising", "panas", "gerah", "pengap", "sempit", "sesak", "sumpek",
        "jauh", "macet", "penuh", "rusak", "mati", "error", "tidak_ada",
        "tidak", "bukan", "tanpa", "belum", "gagal",
    }
)

#: Penanda negasi yang dipakai pembersih teks sebagai awalan.
NEGATION_PREFIX = "tidak_"


def clause_polarity(clause: str) -> int:
    """Hitung polaritas satu klausa sebagai selisih jumlah kata bermuatan.

    Nilai positif berarti klausa cenderung memuji, negatif berarti
    mengeluh, dan nol berarti tidak memihak.

    Aturan yang diberlakukan:

    * Kata dengan awalan negasi (``tidak_enak``) dihitung terbalik.
    * Kata bermuatan yang tidak dikenal tetap dihitung sebagai keluhan
      bila berawalan negasi, karena frasa seperti ``tidak_melayani``
      memang menyatakan keluhan.
    """
    score = 0
    for token in clause.split():
        if token.startswith(NEGATION_PREFIX):
            base = token[len(NEGATION_PREFIX) :]
            if base in POSITIVE_WORDS:
                score -= 1
            elif base in NEGATIVE_WORDS:
                score += 1
            else:
                score -= 1
            continue
        if token in POSITIVE_WORDS:
            score += 1
        elif token in NEGATIVE_WORDS:
            score -= 1
    return score


def is_complaint_clause(clause: str) -> bool:
    """Benar bila klausa condong mengeluh (polaritas negatif)."""
    return clause_polarity(clause) < 0
