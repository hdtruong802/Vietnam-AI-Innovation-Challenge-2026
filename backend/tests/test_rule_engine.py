from __future__ import annotations

from datetime import date, timedelta

from app.adapters.dev_fixture import FIXTURE_PACKS
from app.models.common import FindingSeverity
from app.models.procedure import ValidationRule, ValidationRuleType
from app.services.rule_engine import RuleEngine
from app.services.rag.pack_builder import build_birth_registration_pack


def test_rule_engine_runs_date_and_conditional_rules_without_eval() -> None:
    pack = FIXTURE_PACKS["dang-ky-khai-sinh"].model_copy(deep=True)
    pack.validation_rules.extend(
        [
            ValidationRule(
                rule_id="TEST-DATE",
                type=ValidationRuleType.DATE_NOT_FUTURE,
                field_id="date_value",
                severity=FindingSeverity.ERROR,
                message="Ngày không hợp lệ.",
                source_ref_ids=["fixture-not-legal"],
            ),
            ValidationRule(
                rule_id="TEST-CONDITIONAL",
                type=ValidationRuleType.CONDITIONAL_REQUIRED,
                field_id="extra_value",
                severity=FindingSeverity.ERROR,
                message="Thiếu giá trị điều kiện.",
                params={"when": {"field_id": "needs_extra", "equals": True}},
                source_ref_ids=["fixture-not-legal"],
            ),
        ]
    )

    findings = RuleEngine().validate(
        pack,
        {
            "fixture_child_name": "Demo User",
            "date_value": (date.today() + timedelta(days=1)).isoformat(),
            "needs_extra": True,
        },
    )

    assert {finding.rule_id for finding in findings} == {
        "TEST-DATE",
        "TEST-CONDITIONAL",
    }


def test_birth_precheck_rejects_invalid_names_and_future_birth_date() -> None:
    pack = build_birth_registration_pack()

    findings = RuleEngine().validate(
        pack,
        {
            "ho_ten_tre": "fwe",
            "ngay_sinh_tre": (date.today() + timedelta(days=1)).isoformat(),
            "ho_ten_cha": "sdefwef",
            "ho_ten_me": "ewe",
        },
    )

    assert {finding.field_id for finding in findings} == {
        "ho_ten_tre",
        "ngay_sinh_tre",
        "ho_ten_cha",
        "ho_ten_me",
    }
    assert any(finding.rule_id.endswith("DATE-NOT-FUTURE-2") for finding in findings)
