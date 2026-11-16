"""Pengujian integrasi alur end-to-end dan lapisan penyimpanan/laporan."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from rra.contracts import ASPECTS, RawReview
from rra.pipeline import Pipeline, PipelineError
from rra.report.report import ReportWriter, coverage_frame
from rra.storage.repository import ResultRepository

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def output(dataset_root):
    from rra.config import Config

    cfg = Config.load(root=dataset_root)
    return cfg, Pipeline(cfg).run()


def test_pipeline_completes_all_stages(output) -> None:
    _, result = output
    assert set(result.timings) == {
        "01_muat_data", "02_praproses", "03_muat_label",
        "04_latih_model", "05_klasifikasi", "06_modul_keputusan", "total",
    }
    assert result.n_reviews > 0
    assert result.decision is not None


def test_every_review_gets_a_prediction(output) -> None:
    _, result = output
    assert len(result.predictions) == result.n_reviews
    assert all(prediction.items for prediction in result.predictions)


def test_decision_output_is_complete(output) -> None:
    _, result = output
    decision = result.decision
    assert len(decision.priorities) == len(ASPECTS)
    assert decision.weights
    assert decision.recommendations
    assert decision.audit_lines()
    assert all("Volume" in line for line in decision.audit_lines())


def test_priorities_are_ranked_from_one(output) -> None:
    _, result = output
    ranks = [item.rank for item in result.decision.priorities]
    assert ranks == list(range(1, len(ranks) + 1))


def test_data_quality_summary_is_produced(output) -> None:
    _, result = output
    assert result.data_quality["total"] == result.n_reviews
    assert "panjang_rata_rata" in result.data_quality


def test_frames_are_non_empty(output) -> None:
    cfg, result = output
    pipeline = Pipeline(cfg)
    assert not pipeline.priorities_frame(result).empty
    assert not pipeline.phrases_frame(result).empty
    assert not pipeline.predictions_frame(result).empty


def test_coverage_frame_covers_every_aspect(output) -> None:
    _, result = output
    reviews = [RawReview(review_id="R1", text="a")]
    frame = coverage_frame(reviews, result.decision)
    assert set(frame["kode_aspek"]) == set(ASPECTS)


def test_storage_roundtrip(output, tmp_path) -> None:
    cfg, result = output
    from rra.decision.severity import severity_map

    reviews = Pipeline(cfg).load_reviews()
    repository = ResultRepository(tmp_path / "hasil.sqlite")
    run_id = repository.save_run(
        model_name=result.model_name,
        decision=result.decision,
        severities=severity_map(reviews),
        reviews=reviews,
        timings=result.timings,
    )
    repository.save_predictions(run_id, result.predictions)

    assert repository.latest_run_id() == run_id
    priorities = repository.load_priorities()
    assert len(priorities) == len(ASPECTS)
    assert priorities[0]["rank"] == 1
    assert repository.load_phrases()
    assert repository.load_recommendations()


def test_second_run_gets_a_new_id(output, tmp_path) -> None:
    cfg, result = output
    from rra.decision.severity import severity_map

    reviews = Pipeline(cfg).load_reviews()
    repository = ResultRepository(tmp_path / "dua.sqlite")
    first = repository.save_run(model_name="svm", decision=result.decision,
                               severities=severity_map(reviews), reviews=reviews)
    second = repository.save_run(model_name="svm", decision=result.decision,
                                severities=severity_map(reviews), reviews=reviews)
    assert second > first


def test_report_writer_produces_all_files(output, tmp_path) -> None:
    cfg, result = output
    writer = ReportWriter(tmp_path / "laporan")
    reviews = Pipeline(cfg).load_reviews()
    written = writer.write_all(
        output=result,
        extra_frames={"cakupan": coverage_frame(reviews, result.decision)},
        summary={"model": result.model_name},
        tag="uji",
    )
    for path in written.values():
        assert path.exists() and path.stat().st_size > 0
    markdown = written["report_md"].read_text(encoding="utf-8")
    assert "Peringkat prioritas" in markdown
    assert "Frasa keluhan dominan" in markdown
    assert "Rekomendasi tindakan" in markdown


def test_pipeline_reports_missing_data_clearly(tmp_path) -> None:
    from rra.config import Config

    cfg = Config.load(root=ROOT)
    cfg.root = tmp_path
    with pytest.raises(PipelineError):
        Pipeline(cfg).load_reviews()


def test_pipeline_reports_missing_labels_clearly(tmp_path) -> None:
    """Data ulasan ada, label tidak — pesan galat harus menuntun pengguna."""
    from conftest import make_project
    from rra.config import Config

    root = make_project(tmp_path / "proyek", n_reviews=40, seed=3)
    labels = root / "data" / "reference" / "labels.csv"
    labels.unlink()

    cfg = Config.load(root=root)
    with pytest.raises(PipelineError) as info:
        Pipeline(cfg).load_labels()
    assert "anotasi" in str(info.value).lower() or "label" in str(info.value).lower()
