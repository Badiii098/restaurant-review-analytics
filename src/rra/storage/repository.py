"""Penyimpanan hasil analisis ke basis data SQLite.

Lapisan penyimpanan menyimpan bukan hanya hasil akhir, melainkan juga
bahan pembentuknya — komponen skor, bobot, dan nilai keparahan tiap
ulasan. Inilah yang membuat sistem dapat diaudit: pertanyaan "mengapa
aspek ini berada di peringkat pertama?" dapat dijawab dari basis data.
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from rra.contracts import RawReview
from rra.decision.module import DecisionOutput

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    run_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at    TEXT NOT NULL,
    model_name    TEXT NOT NULL,
    n_reviews     INTEGER NOT NULL,
    weights_json  TEXT NOT NULL,
    timings_json  TEXT NOT NULL,
    config_json   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS priorities (
    run_id        INTEGER NOT NULL,
    rank          INTEGER NOT NULL,
    aspect        TEXT NOT NULL,
    label         TEXT NOT NULL,
    priority      REAL NOT NULL,
    volume        REAL NOT NULL,
    severity      REAL NOT NULL,
    diversity     REAL NOT NULL,
    n_negative    INTEGER NOT NULL,
    n_total       INTEGER NOT NULL,
    PRIMARY KEY (run_id, aspect),
    FOREIGN KEY (run_id) REFERENCES runs (run_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS phrases (
    run_id            INTEGER NOT NULL,
    aspect            TEXT NOT NULL,
    rank              INTEGER NOT NULL,
    phrase            TEXT NOT NULL,
    frequency         INTEGER NOT NULL,
    tfidf_weight      REAL NOT NULL,
    score             REAL NOT NULL,
    example_review_ids TEXT NOT NULL,
    PRIMARY KEY (run_id, aspect, rank),
    FOREIGN KEY (run_id) REFERENCES runs (run_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS recommendations (
    run_id      INTEGER NOT NULL,
    aspect      TEXT NOT NULL,
    phrase      TEXT NOT NULL,
    action      TEXT NOT NULL,
    evidence    TEXT NOT NULL,
    FOREIGN KEY (run_id) REFERENCES runs (run_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS predictions (
    run_id      INTEGER NOT NULL,
    review_id   TEXT NOT NULL,
    aspect      TEXT NOT NULL,
    sentiment   TEXT NOT NULL,
    confidence  REAL NOT NULL,
    PRIMARY KEY (run_id, review_id, aspect),
    FOREIGN KEY (run_id) REFERENCES runs (run_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS review_severity (
    run_id      INTEGER NOT NULL,
    review_id   TEXT NOT NULL,
    rating      REAL,
    severity    REAL NOT NULL,
    PRIMARY KEY (run_id, review_id),
    FOREIGN KEY (run_id) REFERENCES runs (run_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_priorities_rank ON priorities (run_id, rank);
CREATE INDEX IF NOT EXISTS idx_phrases_aspect ON phrases (run_id, aspect, rank);
"""


class ResultRepository:
    """Penyimpanan hasil analisis pada berkas SQLite tunggal."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> Path:
        with closing(self._connect()) as connection, connection:
            connection.executescript(SCHEMA)
        return self.path

    # ------------------------------------------------------------------ #
    def save_run(
        self,
        *,
        model_name: str,
        decision: DecisionOutput,
        severities: dict[str, float],
        reviews: Sequence[RawReview],
        timings: dict[str, Any] | None = None,
        config: dict[str, Any] | None = None,
    ) -> int:
        """Simpan satu kali penjalanan lengkap; kembalikan ``run_id``."""
        self.initialize()
        rating_lookup = {review.review_id: review.rating for review in reviews}
        created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

        with closing(self._connect()) as connection, connection:
            cursor = connection.execute(
                "INSERT INTO runs (created_at, model_name, n_reviews, weights_json,"
                " timings_json, config_json) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    created_at,
                    model_name,
                    decision.n_reviews,
                    json.dumps(decision.weights, ensure_ascii=False),
                    json.dumps(timings or {}, ensure_ascii=False),
                    json.dumps(config or {}, ensure_ascii=False),
                ),
            )
            run_id = int(cursor.lastrowid)

            connection.executemany(
                "INSERT INTO priorities (run_id, rank, aspect, label, priority, volume,"
                " severity, diversity, n_negative, n_total) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    (run_id, item.rank, item.aspect, item.label, item.priority,
                     item.volume, item.severity, item.diversity, item.n_negative, item.n_total)
                    for item in decision.priorities
                ],
            )

            phrase_rows = []
            for aspect, items in decision.phrases.items():
                for position, item in enumerate(items, start=1):
                    phrase_rows.append(
                        (run_id, aspect, position, item.phrase, item.frequency,
                         item.tfidf_weight, item.score,
                         json.dumps(list(item.example_review_ids), ensure_ascii=False))
                    )
            connection.executemany(
                "INSERT INTO phrases (run_id, aspect, rank, phrase, frequency, tfidf_weight,"
                " score, example_review_ids) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                phrase_rows,
            )

            connection.executemany(
                "INSERT INTO recommendations (run_id, aspect, phrase, action, evidence)"
                " VALUES (?, ?, ?, ?, ?)",
                [
                    (run_id, item.aspect, item.phrase, item.action,
                     json.dumps(list(item.evidence_review_ids), ensure_ascii=False))
                    for item in decision.recommendations
                ],
            )

            connection.executemany(
                "INSERT INTO review_severity (run_id, review_id, rating, severity)"
                " VALUES (?, ?, ?, ?)",
                [
                    (run_id, review_id, rating_lookup.get(review_id), severity)
                    for review_id, severity in severities.items()
                ],
            )
        return run_id

    def save_predictions(self, run_id: int, predictions: Sequence[Any]) -> None:
        rows = [
            (run_id, prediction.review_id, item.aspect, item.sentiment, item.confidence)
            for prediction in predictions
            for item in prediction.items
        ]
        with closing(self._connect()) as connection, connection:
            connection.executemany(
                "INSERT OR REPLACE INTO predictions (run_id, review_id, aspect, sentiment,"
                " confidence) VALUES (?, ?, ?, ?, ?)",
                rows,
            )

    # ------------------------------------------------------------------ #
    def latest_run_id(self) -> int | None:
        """Nomor hasil terakhir, atau ``None`` bila belum ada hasil sama sekali.

        Basis data yang baru dibuat belum memiliki tabel apa pun. Keadaan itu
        diperiksa lebih dahulu supaya perintah yang membutuhkan hasil
        sebelumnya dapat memberi pesan yang menuntun pengguna, bukan
        menampilkan galat teknis dari SQLite.
        """
        if not self._has_table("runs"):
            return None
        with closing(self._connect()) as connection, connection:
            row = connection.execute("SELECT MAX(run_id) FROM runs").fetchone()
        return int(row[0]) if row and row[0] is not None else None

    def _has_table(self, table: str) -> bool:
        if not self.path.exists():
            return False
        with closing(self._connect()) as connection, connection:
            row = connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
                (table,),
            ).fetchone()
        return row is not None

    def load_priorities(self, run_id: int | None = None) -> list[dict[str, Any]]:
        run_id = run_id if run_id is not None else self.latest_run_id()
        if run_id is None:
            return []
        with closing(self._connect()) as connection, connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                "SELECT * FROM priorities WHERE run_id = ? ORDER BY rank", (run_id,)
            ).fetchall()
        return [dict(row) for row in rows]

    def load_phrases(self, run_id: int | None = None) -> list[dict[str, Any]]:
        run_id = run_id if run_id is not None else self.latest_run_id()
        if run_id is None:
            return []
        with closing(self._connect()) as connection, connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                "SELECT * FROM phrases WHERE run_id = ? ORDER BY aspect, rank", (run_id,)
            ).fetchall()
        return [dict(row) for row in rows]

    def load_recommendations(self, run_id: int | None = None) -> list[dict[str, Any]]:
        run_id = run_id if run_id is not None else self.latest_run_id()
        if run_id is None:
            return []
        with closing(self._connect()) as connection, connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                "SELECT * FROM recommendations WHERE run_id = ?", (run_id,)
            ).fetchall()
        return [dict(row) for row in rows]

    def load_run(self, run_id: int | None = None) -> dict[str, Any] | None:
        """Keterangan satu hasil: waktu, model, jumlah ulasan, bobot, waktu proses.

        Dipakai antarmuka untuk menampilkan asal-usul angka (provenance)
        tanpa perlu menjalankan ulang pipeline.
        """
        run_id = run_id if run_id is not None else self.latest_run_id()
        if run_id is None or not self._has_table("runs"):
            return None
        with closing(self._connect()) as connection, connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute(
                "SELECT * FROM runs WHERE run_id = ?", (run_id,)
            ).fetchone()
        if row is None:
            return None
        record = dict(row)
        for key, source in (("weights", "weights_json"), ("timings", "timings_json"),
                            ("config", "config_json")):
            try:
                record[key] = json.loads(record.get(source) or "{}")
            except (TypeError, ValueError):
                record[key] = {}
        return record
