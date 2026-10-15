"""Pembangkit dataset ulasan restoran berbahasa Indonesia.

Modul ini **bukan** pengganti pengumpulan data sesungguhnya. Tujuannya
adalah menyediakan data yang :

1. **Dapat diperbanyak** — hasilnya identik setiap kali dijalankan dengan
   ``seed`` yang sama, sehingga seluruh pengujian sistem terulang
   (kebutuhan non-fungsional KNF-04).
2. **Berstruktur realistis** — memuat bahasa tidak baku, singkatan, emoji,
   penegasan berlebih, dan negasi, sebagaimana ulasan daring yang nyata.
3. **Berlabel** — setiap ulasan disertai aspek dan sentimen sebenarnya,
   sehingga kinerja model dan modul keputusan dapat diukur.

Untuk data penelitian sesungguhnya, gunakan ``rra.io_layer.scraper``
atau impor berkas hasil pengumpulan data sendiri ke ``data/raw/``.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Sequence

from rra.contracts import ASPECTS

# --------------------------------------------------------------------------- #
# Profil tiap aspek.
#
# `mention`  : peluang aspek dibahas dalam satu ulasan
# `neg_rate` : peluang aspek dibahas secara negatif
# `severity` : tingkat keparahan rata-rata ketika negatif (0-1)
#
# Profil ini sengaja dibuat tidak seragam agar modul keputusan punya
# sesuatu yang nyata untuk diperingkatkan. Pada konfigurasi bawaan,
# aspek "pelayanan" seharusnya muncul di peringkat pertama.
# --------------------------------------------------------------------------- #
ASPECT_PROFILE: dict[str, dict[str, float]] = {
    "makanan": {"mention": 0.95, "neg_rate": 0.20, "severity": 0.45},
    "pelayanan": {"mention": 0.78, "neg_rate": 0.46, "severity": 0.68},
    "harga": {"mention": 0.62, "neg_rate": 0.30, "severity": 0.42},
    "suasana": {"mention": 0.58, "neg_rate": 0.34, "severity": 0.50},
    "fasilitas": {"mention": 0.42, "neg_rate": 0.28, "severity": 0.40},
}

# --------------------------------------------------------------------------- #
# Templat kalimat positif
# --------------------------------------------------------------------------- #
POSITIVE_TEMPLATES: dict[str, list[str]] = {
    "makanan": [
        "makanannya enak banget",
        "rasanya mantap dan porsinya pas",
        "ayamnya gurih dan sambalnya nampol",
        "masakannya lezat dan bumbunya meresap",
        "nasi gorengnya enak dan toppingnya melimpah",
        "kuahnya gurih dan cocok buat sarapan",
        "menunya variatif dan rasanya konsisten",
        "porsinya banyak dan rasanya enak",
    ],
    "pelayanan": [
        "pelayanannya ramah dan cepat",
        "karyawannya sigap dan pesanan datang cepat",
        "pelayanannya tanggap dan ramah",
        "kasirnya cepat dan ramah",
        "pelayanannya cepat dan ramah sekali",
        "stafnya ramah dan sigap melayani",
    ],
    "harga": [
        "harganya murah dan sepadan",
        "harga sepadan dengan porsinya",
        "harganya terjangkau untuk kantong mahasiswa",
        "harganya murah dan porsinya banyak",
    ],
    "suasana": [
        "tempatnya nyaman dan bersih",
        "suasananya nyaman dan tempatnya bersih",
        "ruangannya adem dan bersih",
        "tempatnya nyaman dan tidak berisik",
    ],
    "fasilitas": [
        "parkirnya luas",
        "toiletnya bersih",
        "wifinya kencang",
        "parkir luas dan toilet bersih",
        "tempatnya ada colokan dan wifinya kencang",
    ],
}

# --------------------------------------------------------------------------- #
# Templat kalimat negatif
# --------------------------------------------------------------------------- #
NEGATIVE_TEMPLATES: dict[str, list[str]] = {
    "makanan": [
        "makanannya hambar",
        "rasanya kurang dan bumbunya tidak meresap",
        "ayamnya keras dan agak basi",
        "porsinya kecil",
        "kuahnya terlalu asin",
        "sambalnya hambar dan nasi agak keras",
        "masakannya tidak enak dan sudah dingin",
        "rasanya hambar dan mengecewakan",
    ],
    "pelayanan": [
        "pelayanan lambat sekali",
        "pelayanan lambat dan menunggu lama",
        "pelayannya cuek",
        "menunggu pesanan hampir satu jam",
        "pesanan saya salah dan pelayanan lambat",
        "pelayanan lama dan pesanannya keliru",
        "pelayan cuek dan lambat",
        "pelayanan lambat dan tidak tanggap",
    ],
    "harga": [
        "harganya mahal",
        "harga mahal tapi porsinya kecil",
        "harganya agak mahal untuk rasa seperti ini",
        "menurut saya harganya kemahalan",
        "harganya mahal dan tidak sepadan",
    ],
    "suasana": [
        "tempatnya panas dan berisik",
        "ruangannya panas dan acnya kurang",
        "tempatnya kotor dan bau",
        "suasananya berisik sekali",
        "tempatnya panas dan kurang nyaman",
    ],
    "fasilitas": [
        "parkirnya sempit",
        "toiletnya kotor",
        "wifinya lambat",
        "parkir sempit dan toilet kotor",
        "tempat duduknya sempit",
    ],
}

# --------------------------------------------------------------------------- #
# Frasa keluhan yang dianggap relevan oleh pakar (acuan Precision@K)
# --------------------------------------------------------------------------- #
GOLD_PHRASES: dict[str, list[str]] = {
    "makanan": ["makanan hambar", "rasa kurang", "ayam keras", "porsi kecil",
                "kuah asin", "sambal hambar", "makanan dingin"],
    "pelayanan": ["pelayanan lambat", "menunggu lama", "pelayan cuek",
                  "pesanan salah", "pesanan keliru", "pelayanan lama"],
    "harga": ["harga mahal", "harga kemahalan", "harga tidak sepadan",
              "mahal porsi kecil"],
    "suasana": ["tempat panas", "tempat kotor", "suasana berisik",
                "ruangan panas", "ac kurang"],
    "fasilitas": ["parkir sempit", "toilet kotor", "wifi lambat",
                  "tempat duduk sempit"],
}

# Penghubung antar-klausa
CONNECTORS: tuple[str, ...] = ("tapi", "namun", "dan", "sedangkan", ",", "cuma", "sayangnya")

NOISE_SUFFIXES: tuple[str, ...] = ("", "", "", " banget", " sih", " ya", " bgt", ":(",
                                   " :(", " 🙏", " 👍", "😍", "😡", "😭", " ...", "!!!")
SLANG_SUBSTITUTIONS: dict[str, str] = {
    "tidak": "gak", "sudah": "udah", "banget": "bgt", "yang": "yg",
    "dengan": "dgn", "sekali": "bgt", "tempat": "tmpt", "makanan": "makanan",
    "pelayanan": "plyn", "harganya": "hrg", "mahal": "mahal",
}

RESTAURANTS: tuple[str, ...] = (
    "Warung Rasa Nusantara",
    "Kedai Kopi Senja",
    "Ayam Bakar Pak Kumis",
    "Dapur Ibu Sri",
    "Soto Betawi Bang Jali",
    "Kafe Sudut Kota",
)


@dataclass(slots=True)
class GeneratedDataset:
    reviews: list[dict[str, Any]]
    labels: list[dict[str, Any]]
    gold_phrases: dict[str, list[str]]
    seed: int
    period_start: str
    period_end: str

    @property
    def n_reviews(self) -> int:
        return len(self.reviews)


def generate_dataset(
    n_reviews: int = 2000,
    *,
    seed: int = 42,
    period_start: str = "2025-01-01",
    period_end: str = "2025-12-31",
    noise_rate: float = 0.28,
) -> GeneratedDataset:
    """Bangkitan dataset ulasan beserta label aspek dan sentimennya.

    Parameters
    ----------
    n_reviews:
        Jumlah ulasan yang dibangkitkan.
    seed:
        Penetapan pembangkit bilangan acak. Nilai yang sama menghasilkan
        dataset yang identik — syarat keterulangan hasil.
    noise_rate:
        Bagian ulasan yang mendapat perlakuan bahasa tidak baku
        (singkatan, emoji, penegasan berlebih).
    """
    rng = random.Random(seed)
    start = date.fromisoformat(period_start)
    end = date.fromisoformat(period_end)
    span_days = max((end - start).days, 1)

    reviews: list[dict[str, Any]] = []
    labels: list[dict[str, Any]] = []

    for index in range(n_reviews):
        review_id = f"R{index + 1:05d}"
        chosen: list[tuple[str, str]] = []

        for aspect in ASPECTS:
            profile = ASPECT_PROFILE[aspect]
            if rng.random() > profile["mention"]:
                continue
            sentiment = "negatif" if rng.random() < profile["neg_rate"] else "positif"
            chosen.append((aspect, sentiment))

        if not chosen:                       # pastikan minimal satu aspek dibahas
            aspect = rng.choice(ASPECTS)
            chosen.append((aspect, "negatif" if rng.random() < 0.4 else "positif"))

        rng.shuffle(chosen)

        clauses: list[str] = []
        for position, (aspect, sentiment) in enumerate(chosen):
            pool = NEGATIVE_TEMPLATES[aspect] if sentiment == "negatif" else POSITIVE_TEMPLATES[aspect]
            clause = rng.choice(pool)
            if position > 0 and rng.random() < 0.35:
                clause = f"{rng.choice(CONNECTORS)} {clause}"
            clauses.append(clause)

        text = " ".join(clauses)
        if rng.random() < noise_rate:
            text = _add_noise(text, rng)
        text = text.strip()
        text = text[0].upper() + text[1:] if text else text

        n_negative = sum(1 for _, sentiment in chosen if sentiment == "negatif")
        neg_ratio = n_negative / len(chosen)
        severity_draw = sum(
            ASPECT_PROFILE[aspect]["severity"]
            for aspect, sentiment in chosen
            if sentiment == "negatif"
        )
        rating = 5.0 - 3.4 * neg_ratio - 0.9 * (severity_draw / max(n_negative, 1)) + rng.uniform(-0.35, 0.35)
        rating = int(min(5, max(1, round(rating))))

        reviews.append(
            {
                "review_id": review_id,
                "text": text,
                "rating": rating,
                "date": (start + timedelta(days=rng.randint(0, span_days))).isoformat(),
                "restaurant": rng.choice(RESTAURANTS),
            }
        )
        for aspect, sentiment in chosen:
            labels.append(
                {
                    "review_id": review_id,
                    "text": text,
                    "aspect": aspect,
                    "sentiment": sentiment,
                }
            )

    return GeneratedDataset(
        reviews=reviews,
        labels=labels,
        gold_phrases={aspect: list(phrases) for aspect, phrases in GOLD_PHRASES.items()},
        seed=seed,
        period_start=period_start,
        period_end=period_end,
    )


def _add_noise(text: str, rng: random.Random) -> str:
    """Sisipkan ciri bahasa tidak baku pada sebagian ulasan."""
    tokens = text.split()
    mutated = [SLANG_SUBSTITUTIONS.get(token, token) if rng.random() < 0.35 else token for token in tokens]
    text = " ".join(mutated)
    if rng.random() < 0.22:                       # penegasan berlebih
        text = text.replace("banget", "bgt").replace("sekali", "bgt")
        text = text.replace("enak", "enakkk") if "enak" in text else text
    text += rng.choice(NOISE_SUFFIXES)
    return text


# --------------------------------------------------------------------------- #
# Penyimpanan
# --------------------------------------------------------------------------- #

def write_dataset(dataset: GeneratedDataset, root: str | Path) -> dict[str, Path]:
    """Tulis dataset ke berkas-berkas yang dipakai pipeline."""
    import pandas as pd

    root = Path(root)
    raw_dir = root / "data" / "raw"
    reference_dir = root / "data" / "reference"
    raw_dir.mkdir(parents=True, exist_ok=True)
    reference_dir.mkdir(parents=True, exist_ok=True)

    reviews_path = raw_dir / "reviews.csv"
    labels_path = reference_dir / "labels.csv"
    gold_path = reference_dir / "gold_phrases.json"
    meta_path = reference_dir / "dataset_meta.json"

    pd.DataFrame(dataset.reviews).to_csv(reviews_path, index=False)
    pd.DataFrame(dataset.labels).to_csv(labels_path, index=False)

    with open(gold_path, "w", encoding="utf-8") as handle:
        json.dump(dataset.gold_phrases, handle, ensure_ascii=False, indent=2)

    with open(meta_path, "w", encoding="utf-8") as handle:
        json.dump(
            {
                "seed": dataset.seed,
                "n_reviews": dataset.n_reviews,
                "n_labels": len(dataset.labels),
                "period_start": dataset.period_start,
                "period_end": dataset.period_end,
                "aspect_profile": ASPECT_PROFILE,
                "catatan": (
                    "Dataset sintetis untuk pengembangan dan pengujian sistem. "
                    "Untuk penelitian sesungguhnya, ganti dengan data hasil "
                    "pengumpulan dari Google Maps."
                ),
            },
            handle,
            ensure_ascii=False,
            indent=2,
        )

    return {
        "reviews": reviews_path,
        "labels": labels_path,
        "gold_phrases": gold_path,
        "meta": meta_path,
    }


def gold_phrases_for(aspect: str) -> Sequence[str]:
    """Frasa acuan pakar untuk satu aspek."""
    return GOLD_PHRASES.get(aspect, [])
