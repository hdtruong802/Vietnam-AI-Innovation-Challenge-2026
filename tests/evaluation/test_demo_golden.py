from __future__ import annotations

from collections import Counter

from scripts.evaluation.evaluate_demo_golden import (
    DEFAULT_GOLDEN,
    REQUIRED_CATEGORIES,
    CaseResult,
    EvaluationReport,
    build_offline_client,
    evaluate_cases,
    load_golden_cases,
    validate_phase6_corpus,
)


def _result(
    case_id: str,
    *,
    route_correct: bool = True,
    false_verified_surfaces: tuple[str, ...] = (),
) -> CaseResult:
    return CaseResult(
        case_id=case_id,
        suite="dang-ky-khai-sinh",
        category="happy_path",
        expected_procedure_id="dang-ky-khai-sinh",
        actual_procedure_id=(
            "dang-ky-khai-sinh" if route_correct else None
        ),
        expected_trust_state="need_more_information",
        actual_trust_state="need_more_information",
        route_correct=route_correct,
        false_route=False,
        missed_route=not route_correct,
        wrong_route=False,
        fail_closed_error=False,
        demo_mode_error=False,
        false_verified_surfaces=false_verified_surfaces,
        http_errors=(),
    )


def test_phase6_corpus_has_60_balanced_unique_cases() -> None:
    cases = load_golden_cases(DEFAULT_GOLDEN)

    validate_phase6_corpus(cases)
    assert len(cases) == 60
    assert len({case.case_id for case in cases}) == 60
    assert Counter(case.suite for case in cases) == {
        "dang-ky-khai-sinh": 20,
        "dang-ky-thuong-tru": 20,
        "dang-ky-ho-kinh-doanh": 20,
    }


def test_every_suite_covers_all_required_categories() -> None:
    cases = load_golden_cases(DEFAULT_GOLDEN)

    for suite in {case.suite for case in cases}:
        categories = {case.category for case in cases if case.suite == suite}
        assert categories == REQUIRED_CATEGORIES


def test_offline_suite_passes_phase6_release_gate() -> None:
    cases = load_golden_cases(DEFAULT_GOLDEN)

    report = evaluate_cases(build_offline_client(), cases)

    assert report.case_count == 60
    assert report.route_correct_count == 60
    assert report.routing_accuracy == 1.0
    assert report.false_route_count == 0
    assert report.missed_route_count == 0
    assert report.wrong_route_count == 0
    assert report.false_verified_count == 0
    assert report.fail_closed_error_count == 0
    assert report.demo_mode_error_count == 0
    assert report.http_error_count == 0
    assert report.passed(1.0, 0) is True


def test_gate_rejects_any_false_verified_surface() -> None:
    results = [_result(f"case-{index}") for index in range(59)]
    results.append(
        _result("case-false-verified", false_verified_surfaces=("intake",))
    )
    report = EvaluationReport(tuple(results))

    assert report.routing_accuracy == 1.0
    assert report.false_verified_count == 1
    assert report.passed(1.0, 0) is False


def test_gate_rejects_routing_accuracy_below_threshold() -> None:
    results = [_result(f"case-{index}") for index in range(59)]
    results.append(_result("case-missed", route_correct=False))
    report = EvaluationReport(tuple(results))

    assert report.routing_accuracy < 1.0
    assert report.false_verified_count == 0
    assert report.passed(1.0, 0) is False
