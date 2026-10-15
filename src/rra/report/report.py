"""Penyusunan laporan hasil analisis.

Modul ini menghasilkan berkas yang dapat langsung dipakai pada Bab IV:
tabel peringkat prioritas, daftar frasa keluhan dominan, rekomendasi
tindakan, dan ringkasan mutu data — dalam bentuk CSV (untuk diolah
lanjut) dan Markdown (untuk disalin ke naskah).
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

import pandas as pd

from rra.contracts import ASPECT_LABELS, RawReview
from rra.decision.module import DecisionOutput
from rra.pipeline import PipelineOutput


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


class ReportWriter:
    """Menulis laporan analisis ke direktori keluaran."""

    def __init__(self, output_dir: str | Path) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    def write_all(
        self,
        *,
        output: PipelineOutput,
        extra_frames: dict[str, pd.DataFrame] | None = None,
        summary: dict[str, Any] | None = None,
        tag: str | None = None,
    ) -> dict[str, Path]:
        """Tulis seluruh berkas laporan; kembalikan pemetaan nama → jalur."""
        from rra.pipeline import Pipeline  # impor lokal: hindari siklus modul

        stamp = tag or _timestamp()
        written: dict[str, Path] = {}

        pipeline = Pipeline.__new__(Pipeline)  # hanya untuk memakai perakit tabel
        priorities = pipeline.priorities_frame(output)
        phrases = pipeline.phrases_frame(output)
        predictions = pipeline.predictions_frame(output)

        written["priorities_csv"] = self._write_frame(priorities, f"prioritas-{stamp}.csv")
        written["phrases_csv"] = self._write_frame(phrases, f"frasa_keluhan-{stamp}.csv")
        written["predictions_csv"] = self._write_frame(predictions, f"prediksi-{stamp}.csv")

        for name, frame in (extra_frames or {}).items():
            written[f"{name}_csv"] = self._write_frame(frame, f"{name}-{stamp}.csv")

        written["report_md"] = self.write_markdown(
            output=output, summary=summary, tag=stamp
        )
        return written

    # ------------------------------------------------------------------ #
    def _write_frame(self, frame: pd.DataFrame, filename: str) -> Path:
        path = self.output_dir / filename
        frame.to_csv(path, index=False)
        return path

    def write_markdown(
        self,
        *,
        output: PipelineOutput,
        summary: dict[str, Any] | None = None,
        tag: str | None = None,
    ) -> Path:
        stamp = tag or _timestamp()
        path = self.output_dir / f"laporan-{stamp}.md"
        path.write_text(self._render(output, summary or {}), encoding="utf-8")
        return path

    # ------------------------------------------------------------------ #
    def _render(self, output: PipelineOutput, summary: dict[str, Any]) -> str:
        decision = output.decision
        lines: list[str] = []
        lines.append("# Laporan Analisis Ulasan Pelanggan Restoran")
        lines.append("")
        lines.append(f"- Waktu analisis: {datetime.now().strftime('%d %B %Y, %H:%M')}")
        lines.append(f"- Komponen model aktif: **{output.model_name}**")
        lines.append(f"- Jumlah ulasan dianalisis: **{output.n_reviews}**")
        if decision:
            bobot = ", ".join(f"{k}={v}" for k, v in decision.weights.items())
            lines.append(f"- Rumus prioritas: `w1*Volume + w2*Keparahan + w3*Keragaman` ({bobot})")
        lines.append("")

        if decision:
            lines.append("## 1. Peringkat prioritas perbaikan")
            lines.append("")
            lines.append("| Peringkat | Aspek | Skor | Volume | Keparahan | Keragaman | Keluhan | Dibahas |")
            lines.append("|---|---|---|---|---|---|---|---|")
            for item in decision.priorities:
                lines.append(
                    f"| {item.rank} | {item.label} | {item.priority:.4f} | {item.volume:.4f} "
                    f"| {item.severity:.4f} | {item.diversity:.4f} | {item.n_negative} | {item.n_total} |"
                )
            lines.append("")
            lines.append("**Bahan audit peringkat.** Setiap skor dapat diperiksa komponennya:")
            lines.append("")
            for line in decision.audit_lines():
                lines.append(f"- {line}")
            lines.append("")

            lines.append("## 2. Frasa keluhan dominan")
            lines.append("")
            lines.append(
                "Frasa berikut adalah yang paling menonjol, bukan bukti penyebab "
                "persoalan. Setiap frasa dapat ditelusuri ke ulasan asalnya."
            )
            lines.append("")
            for aspect, items in decision.phrases.items():
                lines.append(f"### {ASPECT_LABELS.get(aspect, aspect)}")
                lines.append("")
                lines.append("| # | Frasa | Frekuensi | Bobot TF-IDF | Skor | Contoh ulasan |")
                lines.append("|---|---|---|---|---|---|")
                for position, item in enumerate(items, start=1):
                    contoh = ", ".join(item.example_review_ids)
                    lines.append(
                        f"| {position} | {item.phrase} | {item.frequency} "
                        f"| {item.tfidf_weight:.4f} | {item.score:.4f} | {contoh} |"
                    )
                lines.append("")

            lines.append("## 3. Rekomendasi tindakan")
            lines.append("")
            lines.append("| Aspek | Frasa pemicu | Tindakan yang disarankan |")
            lines.append("|---|---|---|")
            for item in decision.recommendations:
                lines.append(f"| {ASPECT_LABELS.get(item.aspect, item.aspect)} "
                             f"| {item.phrase} | {item.action} |")
            lines.append("")

        if summary:
            lines.append("## 4. Ringkasan kinerja")
            lines.append("")
            lines.append("```json")
            import json as _json

            lines.append(_json.dumps(summary, indent=2, ensure_ascii=False))
            lines.append("```")
            lines.append("")

        lines.append("## 5. Waktu proses per tahap")
        lines.append("")
        lines.append("| Tahap | Detik |")
        lines.append("|---|---|")
        for stage, seconds in output.timings.items():
            lines.append(f"| {stage} | {seconds} |")
        lines.append("")

        return "\n".join(lines)


def coverage_frame(reviews: Sequence[RawReview], decision: DecisionOutput) -> pd.DataFrame:
    """Ringkasan cakupan aspek: berapa ulasan yang membahas tiap aspek."""
    rows = []
    for aspect, stat in decision.stats.items():
        rows.append(
            {
                "aspek": ASPECT_LABELS.get(aspect, aspect),
                "kode_aspek": aspect,
                "jumlah_dibahas": stat.n_total,
                "jumlah_negatif": stat.n_negative,
                "persen_dibahas": round(100.0 * stat.n_total / max(len(reviews), 1), 2),
                "keparahan_rata_rata": stat.mean_severity,
            }
        )
    return pd.DataFrame(rows).sort_values("jumlah_negatif", ascending=False)
