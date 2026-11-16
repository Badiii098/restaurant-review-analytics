# Kontrak Data Antar-Lapis

Dibangkitkan dari `src/rra/contracts.py` oleh `scripts/export_contracts.py`. Jangan diedit tangan.

- Aspek: makanan, pelayanan, harga, suasana, fasilitas
- Sentimen: positif, negatif, netral

## RawReview

Satu ulasan sebagaimana diambil dari sumbernya, belum diolah.

| Bidang | Tipe | Bawaan |
|---|---|---|
| `review_id` | `str` | wajib |
| `text` | `str` | wajib |
| `rating` | `float \| None` | None |
| `date` | `str \| None` | None |
| `restaurant` | `str \| None` | None |

## CleanReview

Ulasan setelah praproses. Menyimpan teks asli agar dapat ditelusuri.

| Bidang | Tipe | Bawaan |
|---|---|---|
| `review_id` | `str` | wajib |
| `text_raw` | `str` | wajib |
| `text_clean` | `str` | wajib |
| `rating` | `float \| None` | None |
| `date` | `str \| None` | None |
| `restaurant` | `str \| None` | None |
| `clauses` | `tuple[str, ...]` | () |

## TrainingExample

Contoh berlabel untuk melatih komponen model.

| Bidang | Tipe | Bawaan |
|---|---|---|
| `review_id` | `str` | wajib |
| `text` | `str` | wajib |
| `aspects` | `tuple[str, ...]` | wajib |
| `sentiments` | `dict[str, str]` | dict() |

## AspectSentiment

Satu pasangan (aspek, sentimen) beserta tingkat keyakinan model.

| Bidang | Tipe | Bawaan |
|---|---|---|
| `aspect` | `str` | wajib |
| `sentiment` | `str` | wajib |
| `confidence` | `float` | 0.0 |

## Prediction

Hasil klasifikasi satu ulasan.

| Bidang | Tipe | Bawaan |
|---|---|---|
| `review_id` | `str` | wajib |
| `items` | `list[AspectSentiment]` | list() |

## ComplaintPhrase

Frasa keluhan dominan pada satu aspek.

| Bidang | Tipe | Bawaan |
|---|---|---|
| `aspect` | `str` | wajib |
| `phrase` | `str` | wajib |
| `frequency` | `int` | wajib |
| `tfidf_weight` | `float` | wajib |
| `score` | `float` | wajib |
| `example_review_ids` | `tuple[str, ...]` | () |

## AspectPriority

Skor prioritas satu aspek beserta komponen pembentuknya.

| Bidang | Tipe | Bawaan |
|---|---|---|
| `aspect` | `str` | wajib |
| `label` | `str` | wajib |
| `rank` | `int` | wajib |
| `priority` | `float` | wajib |
| `volume` | `float` | wajib |
| `severity` | `float` | wajib |
| `diversity` | `float` | wajib |
| `n_negative` | `int` | wajib |
| `n_total` | `int` | wajib |

## Recommendation

Rekomendasi tindakan yang bersesuaian dengan aspek dan frasa keluhan.

| Bidang | Tipe | Bawaan |
|---|---|---|
| `aspect` | `str` | wajib |
| `phrase` | `str` | wajib |
| `action` | `str` | wajib |
| `evidence_review_ids` | `tuple[str, ...]` | () |

## AnalysisResult

Bungkusan lengkap keluaran satu kali analisis.

| Bidang | Tipe | Bawaan |
|---|---|---|
| `model_name` | `str` | '' |
| `n_reviews` | `int` | 0 |
| `priorities` | `list[AspectPriority]` | list() |
| `phrases` | `dict[str, list[ComplaintPhrase]]` | dict() |
| `recommendations` | `list[Recommendation]` | list() |
