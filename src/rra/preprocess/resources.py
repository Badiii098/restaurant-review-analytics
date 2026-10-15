"""Sumber daya bahasa Indonesia untuk praproses teks.

Kamus di sini sengaja diletakkan pada berkas terpisah agar dapat
diperbarui tanpa menyentuh logika praproses, dan agar setiap penambahan
kosakata dapat dicatat sebagai perubahan yang dapat ditelusuri.
"""

from __future__ import annotations

# --------------------------------------------------------------------------- #
# Kata umum yang tidak bermakna bagi klasifikasi aspek
# --------------------------------------------------------------------------- #
STOPWORDS: frozenset[str] = frozenset(
    """
    ada adalah adanya adapun agak agar akan akankah akhir akhiri akhirnya aku
    alias alih ampuh an anda antar antara antarpulau anya apabila apa apalagi
    apapun ara arah aras artinya asal asalkan atas atau ataupun awalnya awas
    bagaimana bagaimanakah bagaimanapun bagi bahkan bahwa bahwasanya baik
    bakal bakalan banyak beberapa begini beginian begitu belakang benar berada
    berakhir berakhirlah berapa berapakah berarti berasal berawal berbeda
    berharap berhenti berikan beritahu berjalan berkata berkehendak beberapa
    bila bilamana bilang bikin bisa bisakah boleh buat bukan bukankah bukanlah
    bung cara cukup dalam dan dapat dari daripada demi demikian dengannya
    dengan denganku dengannya dengn depan di dia dialah diam diantaranya dini
    dll dlu dosen dua dulu setelah oleh untuk pada ke dari yang se sebuah
    sebagai sebab karena itu ini tersebut yaitu ialah anda kamu saya kita kami
    mereka nya lah kah pun sih dong deh ya iya gitu gini juga saja aja masih
    hanya cuma kalau klo kalo udah sudah belum akan terus lalu kemudian serta
    atau maupun jadi maka kalau begitu sini situ sana mari ayo coba
    """.split()
)

# --------------------------------------------------------------------------- #
# Normalisasi kata tidak baku / singkatan
# --------------------------------------------------------------------------- #
SLANG_MAP: dict[str, str] = {
    # umum
    "yg": "yang", "dgn": "dengan", "utk": "untuk", "krn": "karena",
    "karna": "karena", "dr": "dari", "dlm": "dalam", "pake": "pakai",
    "pakai": "pakai", "jd": "jadi", "jg": "juga", "tp": "tapi",
    "tapi": "tetapi", "blm": "belum", "udh": "sudah", "udah": "sudah",
    "dah": "sudah", "gmna": "bagaimana", "gmn": "bagaimana",
    "gimana": "bagaimana", "emg": "memang", "memang": "memang",
    "bgt": "banget", "bgtt": "banget", "bngt": "banget", "sekali": "sangat",
    "bener": "benar", "bener2": "benar", "betul": "benar",
    "gak": "tidak", "ga": "tidak", "g": "tidak", "tdk": "tidak",
    "engga": "tidak", "enggak": "tidak", "nggak": "tidak", "ngga": "tidak",
    "kagak": "tidak", "gk": "tidak", "td": "tidak", "gpp": "tidak apa-apa",
    # kuliner
    "makanan": "makanan", "makannan": "makanan", "makanannya": "makanan",
    "masakannya": "makanan", "masakan": "makanan", "menu": "menu",
    "porsi": "porsi", "prsi": "porsi", "harga": "harga", "hrg": "harga",
    "harganya": "harga", "mahal": "mahal", "murce": "murah", "murah": "murah",
    "pelayanan": "pelayanan", "pelayanannya": "pelayanan",
    "pelayan": "pelayan", "plyn": "pelayanan", "service": "pelayanan",
    "tempat": "tempat", "tmpt": "tempat", "suasana": "suasana",
    "ruangan": "ruangan", "parkir": "parkir", "parkiran": "parkir",
    "toilet": "toilet", "wc": "toilet", "wifi": "wifi", "wi-fi": "wifi",
    # sifat
    "enak": "enak", "enakk": "enak", "mantap": "enak", "mantul": "enak",
    "lezat": "enak", "nikmat": "enak", "gurih": "enak", "hambar": "hambar",
    "asin": "asin", "basi": "basi", "keras": "keras", "lembek": "lembek",
    "lambat": "lambat", "lama": "lama", "lamaa": "lama", "lamaaa": "lama",
    "nunggu": "menunggu", "tunggu": "menunggu", "ngantri": "mengantre",
    "antri": "mengantre", "ramah": "ramah", "cuek": "cuek", "jutek": "cuek",
    "kotor": "kotor", "bersih": "bersih", "bau": "bau", "apek": "bau",
    "panas": "panas", "gerah": "panas", "berisik": "berisik",
    "ramai": "ramai", "nyaman": "nyaman", "sempit": "sempit",
    "rekomended": "direkomendasikan", "rekomen": "direkomendasikan",
    "worth": "sepadan", "sebanding": "sepadan",
}

# --------------------------------------------------------------------------- #
# Emoji -> kata (membawa muatan sentimen yang harus dipertahankan)
# --------------------------------------------------------------------------- #
EMOJI_MAP: dict[str, str] = {
    "😍": "senang", "🥰": "senang", "😋": "enak", "🤤": "enak",
    "👍": "bagus", "👌": "bagus", "🔥": "bagus", "⭐": "bagus",
    "🙏": "terima kasih", "😂": "lucu", "🤣": "lucu", "😊": "senang",
    "😐": "biasa", "🤔": "ragu", "😕": "kecewa", "🙁": "kecewa",
    "😞": "kecewa", "😢": "kecewa", "😡": "marah", "🤬": "marah",
    "👎": "buruk", "💩": "buruk", "🤢": "jijik", "🤮": "jijik",
    "😴": "lama", "⏰": "lama", "🐌": "lambat", "🥵": "panas",
    "🥶": "dingin", "💰": "mahal", "💸": "mahal", "💵": "murah",
    "🚗": "parkir", "🅿️": "parkir", "🚻": "toilet", "📶": "wifi",
}

# --------------------------------------------------------------------------- #
# Kata negasi dan penanda penegasan
# --------------------------------------------------------------------------- #
NEGATION_WORDS: frozenset[str] = frozenset(
    {"tidak", "bukan", "belum", "jangan", "tanpa", "kurang", "gagal", "nggak", "tak"}
)

INTENSIFIER_WORDS: frozenset[str] = frozenset(
    {"sangat", "banget", "amat", "terlalu", "sekali", "paling", "super", "begitu"}
)

# --------------------------------------------------------------------------- #
# Kata penghubung antarklausa
# --------------------------------------------------------------------------- #
# Dipakai untuk dua hal: (a) menghentikan cakupan negasi agar tidak melintasi
# batas klausa, dan (b) memecah ulasan menjadi klausa saat mengekstraksi frasa
# keluhan per aspek. Karena tanda baca dibuang pada tahap pembersihan, kata
# penghubung inilah satu-satunya penanda batas klausa yang tersisa.
CLAUSE_CONNECTORS: frozenset[str] = frozenset(
    {
        "dan", "tapi", "tetapi", "namun", "cuma", "serta", "sedangkan",
        "sementara", "padahal", "walaupun", "meski", "meskipun", "kalau",
    }
)

# --------------------------------------------------------------------------- #
# Pemetaan kata penanda -> aspek (dipakai generator data & pemeriksaan cepat)
# --------------------------------------------------------------------------- #
ASPECT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "makanan": (
        "makanan", "masakan", "rasa", "porsi", "enak", "hambar", "asin", "basi",
        "nasi", "ayam", "sambal", "kuah", "menu", "gurih", "lezat", "pahit",
        "mentah", "keras", "lembek", "bumbu", "topping", "sayur", "daging",
    ),
    "pelayanan": (
        "pelayanan", "pelayan", "kasir", "menunggu", "menunggu lama", "lambat",
        "ramah", "cuek", "antre", "pesanan", "salah pesan", "tanggap", "kasih",
        "pesan", "datang", "dilayani", "kotak", "pesananku",
    ),
    "harga": (
        "harga", "mahal", "murah", "sepadan", "biaya", "bayar", "struk",
        "total", "tagihan", "irit", "kemahalan", "porsi harga", "nilai",
    ),
    "suasana": (
        "suasana", "tempat", "ruangan", "nyaman", "panas", "gerah", "berisik",
        "ramai", "bersih", "kotor", "musik", "dekorasi", "pencahayaan",
        "dingin", "ac", "bau", "sempit", "luas", "pewangi",
    ),
    "fasilitas": (
        "parkir", "parkiran", "toilet", "wifi", "musala", "mushola", "colokan",
        "tempat duduk", "kursi", "meja", "bayar qris", "qris", "card",
        "sendok", "tisu", "lift", "escalator", "tempat parkir",
    ),
}

# --------------------------------------------------------------------------- #
# Kata benda penanda aspek
# --------------------------------------------------------------------------- #
# Berbeda dari ASPECT_KEYWORDS, daftar ini **hanya** memuat kata yang menamai
# objek atau bagian layanan, bukan kata sifat penilainya. Pembedaan ini penting:
# ASPECT_KEYWORDS memuat kata seperti "hambar", "mahal", "lambat", dan "kotor"
# yang justru merupakan kata keluhan paling informatif. Bila kata-kata itu ikut
# dibuang sebagai "penanda aspek", daftar frasa keluhan kehilangan justru isi
# yang paling berguna bagi pengelola restoran.
#
# Dipakai untuk menyaring frasa satu kata yang tidak informatif — frasa
# "harga" pada aspek harga hanya mengulang nama aspeknya sendiri.
ASPECT_NOUNS: tuple[str, ...] = (
    # makanan
    "makanan", "masakan", "menu", "nasi", "ayam", "sambal", "kuah", "bumbu",
    "topping", "sayur", "daging", "rasa", "porsi", "hidangan", "sajian",
    # pelayanan
    "pelayanan", "pelayan", "kasir", "pesanan", "pesan", "antre", "antrian",
    "kotak", "staf", "karyawan",
    # harga
    "harga", "biaya", "tagihan", "struk", "total", "bayar", "nilai", "tarif",
    # suasana
    "suasana", "tempat", "ruangan", "ruang", "kursi", "meja", "musik",
    "dekorasi", "pencahayaan", "ac", "pewangi",
    # fasilitas
    "fasilitas", "parkir", "parkiran", "toilet", "wifi", "musala", "mushola",
    "colokan", "charger", "sendok", "tisu", "lift", "escalator",
)
