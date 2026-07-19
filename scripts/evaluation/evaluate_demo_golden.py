"""Evaluate the three demo MVP procedure flows against an offline golden set."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPOSITORY_ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from app.adapters.demo_pack import load_demo_packs  # noqa: E402
from app.config import Settings  # noqa: E402
from app.main import create_app  # noqa: E402


DEFAULT_GOLDEN = (
    REPOSITORY_ROOT / "tests" / "evaluation" / "fixtures" / "demo_intake_golden.jsonl"
)
EXPECTED_SUITES = {
    "dang-ky-khai-sinh",
    "dang-ky-thuong-tru",
    "dang-ky-ho-kinh-doanh",
}
REQUIRED_CATEGORIES = {
    "happy_path",
    "no_accent",
    "typo",
    "ambiguous",
    "near_intent",
    "out_of_scope",
    "greeting",
}


@dataclass(frozen=True)
class GoldenCase:
    case_id: str
    suite: str
    category: str
    query: str
    expected_procedure_id: str | None


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    suite: str
    category: str
    expected_procedure_id: str | None
    actual_procedure_id: str | None
    expected_trust_state: str
    actual_trust_state: str | None
    route_correct: bool
    false_route: bool
    missed_route: bool
    wrong_route: bool
    fail_closed_error: bool
    demo_mode_error: bool
    false_verified_surfaces: tuple[str, ...]
    http_errors: tuple[str, ...]


@dataclass(frozen=True)
class EvaluationReport:
    results: tuple[CaseResult, ...]

    @property
    def case_count(self) -> int:
        return len(self.results)

    @property
    def route_correct_count(self) -> int:
        return sum(result.route_correct for result in self.results)

    @property
    def routing_accuracy(self) -> float:
        return self.route_correct_count / self.case_count if self.case_count else 0.0

    @property
    def false_route_count(self) -> int:
        return sum(result.false_route for result in self.results)

    @property
    def missed_route_count(self) -> int:
        return sum(result.missed_route for result in self.results)

    @property
    def wrong_route_count(self) -> int:
        return sum(result.wrong_route for result in self.results)

    @property
    def false_verified_count(self) -> int:
        return sum(len(result.false_verified_surfaces) for result in self.results)

    @property
    def fail_closed_error_count(self) -> int:
        return sum(result.fail_closed_error for result in self.results)

    @property
    def demo_mode_error_count(self) -> int:
        return sum(result.demo_mode_error for result in self.results)

    @property
    def http_error_count(self) -> int:
        return sum(len(result.http_errors) for result in self.results)

    def passed(self, minimum_routing_accuracy: float, max_false_verified: int) -> bool:
        return (
            self.case_count >= 60
            and self.routing_accuracy >= minimum_routing_accuracy
            and self.false_verified_count <= max_false_verified
            and self.fail_closed_error_count == 0
            and self.demo_mode_error_count == 0
            and self.http_error_count == 0
        )

    def grouped_accuracy(self, field: str) -> dict[str, dict[str, int | float]]:
        grouped: dict[str, list[CaseResult]] = defaultdict(list)
        for result in self.results:
            grouped[str(getattr(result, field))].append(result)
        return {
            key: {
                "total": len(values),
                "correct": sum(value.route_correct for value in values),
                "accuracy": sum(value.route_correct for value in values) / len(values),
            }
            for key, values in sorted(grouped.items())
        }

    def as_dict(self) -> dict[str, Any]:
        return {
            "case_count": self.case_count,
            "route_correct_count": self.route_correct_count,
            "routing_accuracy": self.routing_accuracy,
            "false_route_count": self.false_route_count,
            "missed_route_count": self.missed_route_count,
            "wrong_route_count": self.wrong_route_count,
            "false_verified_count": self.false_verified_count,
            "fail_closed_error_count": self.fail_closed_error_count,
            "demo_mode_error_count": self.demo_mode_error_count,
            "http_error_count": self.http_error_count,
            "by_suite": self.grouped_accuracy("suite"),
            "by_category": self.grouped_accuracy("category"),
            "failed_cases": [
                asdict(result)
                for result in self.results
                if not result.route_correct
                or result.false_verified_surfaces
                or result.fail_closed_error
                or result.demo_mode_error
                or result.http_errors
            ],
        }


def load_golden_cases(path: Path) -> tuple[GoldenCase, ...]:
    cases: list[GoldenCase] = []
    required_fields = {
        "case_id",
        "suite",
        "category",
        "query",
        "expected_procedure_id",
    }
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            raw = json.loads(line)
            if set(raw) != required_fields:
                raise ValueError(f"line {line_number}: golden fields do not match schema")
            case = GoldenCase(**raw)
            if not case.case_id or not case.query.strip():
                raise ValueError(f"line {line_number}: case_id and query are required")
            if case.suite not in EXPECTED_SUITES:
                raise ValueError(f"line {line_number}: unknown suite {case.suite}")
            if case.category not in REQUIRED_CATEGORIES:
                raise ValueError(f"line {line_number}: unknown category {case.category}")
            if case.expected_procedure_id not in {None, case.suite}:
                raise ValueError(
                    f"line {line_number}: expected procedure must be null or match suite"
                )
            cases.append(case)
    return tuple(cases)


def validate_phase6_corpus(cases: Iterable[GoldenCase]) -> None:
    materialized = tuple(cases)
    case_ids = [case.case_id for case in materialized]
    if len(materialized) != 60:
        raise ValueError(f"Phase 6 corpus must contain exactly 60 cases, got {len(materialized)}")
    if len(set(case_ids)) != len(case_ids):
        raise ValueError("Phase 6 corpus contains duplicate case_id values")
    suite_counts = Counter(case.suite for case in materialized)
    if suite_counts != Counter({suite: 20 for suite in EXPECTED_SUITES}):
        raise ValueError(f"Each MVP suite must contain 20 cases, got {dict(suite_counts)}")
    for suite in EXPECTED_SUITES:
        categories = {case.category for case in materialized if case.suite == suite}
        missing = REQUIRED_CATEGORIES - categories
        if missing:
            raise ValueError(f"Suite {suite} is missing categories: {sorted(missing)}")


def build_offline_client() -> TestClient:
    settings = Settings(
        app_env="test",
        procedure_data_mode="demo_pack",
        rag_mode="disabled",
        llm_mode="disabled",
        legacy_rag_enabled=False,
        rate_limit_enabled=False,
        ai_api_key="",
        openai_api_key="",
    )
    return TestClient(create_app(settings=settings))


def _answers_for(procedure_id: str) -> dict[str, str]:
    pack = load_demo_packs()[procedure_id]
    return {
        question.id: question.options[0] if question.options else "Thông tin demo"
        for question in pack.intake_questions
    }


def _is_false_verified(payload: dict[str, Any]) -> bool:
    return (
        payload.get("trust_state") == "verified_guidance"
        or payload.get("last_verified_at") is not None
    )


def _expected_intake_trust(case: GoldenCase) -> str:
    if case.expected_procedure_id is not None or case.category in {
        "ambiguous",
        "greeting",
    }:
        return "need_more_information"
    return "official_review_required"


def evaluate_cases(client: TestClient, cases: Iterable[GoldenCase]) -> EvaluationReport:
    results: list[CaseResult] = []
    for case in cases:
        intake_response = client.post(
            "/v1/intake/turn",
            json={
                "session_id": f"golden-{case.case_id}",
                "message": case.query,
                "session_context": {},
            },
        )
        http_errors: list[str] = []
        surfaces: list[tuple[str, dict[str, Any]]] = []
        if intake_response.status_code != 200:
            http_errors.append(f"intake:{intake_response.status_code}")
            intake: dict[str, Any] = {}
        else:
            intake = intake_response.json()
            surfaces.append(("intake", intake))

        actual = intake.get("detected_procedure_id")
        if actual in EXPECTED_SUITES:
            checklist_response = client.post(
                f"/v1/procedures/{actual}/checklist",
                json={"clarification_answers": _answers_for(actual)},
            )
            if checklist_response.status_code == 200:
                surfaces.append(("checklist", checklist_response.json()))
            else:
                http_errors.append(f"checklist:{checklist_response.status_code}")

            validation_response = client.post(
                "/v1/applications/validate",
                json={"procedure_id": actual, "form_data": {}},
            )
            if validation_response.status_code == 200:
                surfaces.append(("validation", validation_response.json()))
            else:
                http_errors.append(f"validation:{validation_response.status_code}")

        route_correct = actual == case.expected_procedure_id
        false_route = case.expected_procedure_id is None and actual is not None
        missed_route = case.expected_procedure_id is not None and actual is None
        wrong_route = (
            case.expected_procedure_id is not None
            and actual is not None
            and actual != case.expected_procedure_id
        )
        expected_trust_state = _expected_intake_trust(case)
        actual_trust_state = intake.get("trust_state")
        fail_closed_error = actual_trust_state != expected_trust_state
        demo_mode_error = (
            actual == case.expected_procedure_id
            and case.expected_procedure_id is not None
            and any(payload.get("demo_mode") is not True for _, payload in surfaces)
        )
        false_verified_surfaces = tuple(
            name for name, payload in surfaces if _is_false_verified(payload)
        )
        results.append(
            CaseResult(
                case_id=case.case_id,
                suite=case.suite,
                category=case.category,
                expected_procedure_id=case.expected_procedure_id,
                actual_procedure_id=actual,
                expected_trust_state=expected_trust_state,
                actual_trust_state=actual_trust_state,
                route_correct=route_correct,
                false_route=false_route,
                missed_route=missed_route,
                wrong_route=wrong_route,
                fail_closed_error=fail_closed_error,
                demo_mode_error=demo_mode_error,
                false_verified_surfaces=false_verified_surfaces,
                http_errors=tuple(http_errors),
            )
        )
    return EvaluationReport(tuple(results))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--golden", type=Path, default=DEFAULT_GOLDEN)
    parser.add_argument("--minimum-routing-accuracy", type=float, default=1.0)
    parser.add_argument("--max-false-verified", type=int, default=0)
    parser.add_argument("--json", action="store_true", help="Print the full JSON report")
    arguments = parser.parse_args(argv)
    if not 0 <= arguments.minimum_routing_accuracy <= 1:
        parser.error("--minimum-routing-accuracy must be between 0 and 1")
    if arguments.max_false_verified < 0:
        parser.error("--max-false-verified must be non-negative")

    try:
        cases = load_golden_cases(arguments.golden.resolve())
        validate_phase6_corpus(cases)
        report = evaluate_cases(build_offline_client(), cases)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as error:
        print(f"Demo golden evaluation failed: {error}", file=sys.stderr)
        return 1

    encoded = report.as_dict()
    if arguments.json:
        print(json.dumps(encoded, ensure_ascii=False, indent=2))
    else:
        print(
            "Demo golden evaluation: "
            f"cases={report.case_count} correct={report.route_correct_count} "
            f"routing_accuracy={report.routing_accuracy:.4f} "
            f"false_routes={report.false_route_count} "
            f"missed_routes={report.missed_route_count} "
            f"wrong_routes={report.wrong_route_count} "
            f"false_verified={report.false_verified_count} "
            f"fail_closed_errors={report.fail_closed_error_count} "
            f"demo_mode_errors={report.demo_mode_error_count} "
            f"http_errors={report.http_error_count}"
        )
        for result in encoded["failed_cases"]:
            print(
                f"FAIL {result['case_id']}: expected={result['expected_procedure_id']} "
                f"actual={result['actual_procedure_id']} "
                f"expected_trust={result['expected_trust_state']} "
                f"actual_trust={result['actual_trust_state']}"
            )

    return 0 if report.passed(
        arguments.minimum_routing_accuracy,
        arguments.max_false_verified,
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
