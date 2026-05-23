from pathlib import Path

from poweragen.evaluate import run_evaluation, run_evaluation_suite


def test_mvp_pipeline_generates_valid_editable_pptx(tmp_path: Path) -> None:
    report = run_evaluation(
        template_path=Path("test/courseplan_test.pptx"),
        run_dir=tmp_path / "eval",
        slide_count=8,
    )
    assert report["status"] == "pass"


def test_mvp_suite_accepts_second_template_family(tmp_path: Path) -> None:
    report = run_evaluation_suite(
        templates=[
            Path("test/courseplan_test.pptx"),
            Path("test/presentation_test.pptx"),
        ],
        run_dir=tmp_path / "suite",
        slide_count=8,
    )
    assert report["status"] == "pass"
