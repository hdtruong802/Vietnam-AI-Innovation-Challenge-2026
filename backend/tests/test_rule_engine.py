from __future__ import annotations

from datetime import date, timedelta

from app.adapters.dev_fixture import FIXTURE_PACKS
from app.models.common import FindingSeverity
from app.models.procedure import ValidationRule, ValidationRuleType
from app.services.rule_engine import RuleEngine


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

    assert {finding.rule_id for finding in findings} == {"TEST-DATE", "TEST-CONDITIONAL"}
