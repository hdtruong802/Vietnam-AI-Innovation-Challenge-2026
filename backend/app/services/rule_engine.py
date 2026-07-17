from __future__ import annotations

import re
from datetime import date
from typing import Any

from app.models.common import FindingSeverity
from app.models.procedure import ProcedurePack, ValidationRule, ValidationRuleType
from app.models.validation import Finding


class RuleEngine:
    """Small allowlisted deterministic validator for data-owned ProcedurePack rules."""

    def validate(self, pack: ProcedurePack, form_data: dict[str, Any]) -> list[Finding]:
        findings: list[Finding] = []
        for rule in pack.validation_rules:
            if self._violates(rule, form_data):
                findings.append(
                    Finding(
                        field_id=rule.field_id,
                        severity=rule.severity,
                        rule_id=rule.rule_id,
                        message=rule.message,
                        fix_hint=rule.fix_hint,
                        source_ref_ids=rule.source_ref_ids,
                    )
                )
        return findings

    def _violates(self, rule: ValidationRule, form_data: dict[str, Any]) -> bool:
        value = form_data.get(rule.field_id)

        if rule.type == ValidationRuleType.REQUIRED:
            return self._is_empty(value)

        if rule.type == ValidationRuleType.TYPE:
            return not self._matches_type(value, rule.params.get("expected"))

        if rule.type == ValidationRuleType.STRING_PATTERN:
            if self._is_empty(value):
                return False
            pattern = rule.params.get("pattern")
            return (
                not isinstance(value, str)
                or not isinstance(pattern, str)
                or re.fullmatch(pattern, value) is None
            )

        if rule.type == ValidationRuleType.DATE_FORMAT:
            if self._is_empty(value):
                return False
            return self._parse_date(value) is None

        if rule.type == ValidationRuleType.DATE_NOT_FUTURE:
            if self._is_empty(value):
                return False
            parsed = self._parse_date(value)
            return parsed is None or parsed > date.today()

        if rule.type == ValidationRuleType.CONDITIONAL_REQUIRED:
            condition = rule.params.get("when")
            if not isinstance(condition, dict):
                return True
            condition_field = condition.get("field_id")
            if not isinstance(condition_field, str):
                return True
            return form_data.get(condition_field) == condition.get("equals") and self._is_empty(
                value
            )

        if rule.type == ValidationRuleType.FIELD_COMPARE:
            other_field = rule.params.get("other_field")
            operator = rule.params.get("operator")
            if not isinstance(other_field, str) or operator not in {
                "eq",
                "ne",
                "lt",
                "lte",
                "gt",
                "gte",
            }:
                return True
            other_value = form_data.get(other_field)
            if self._is_empty(value) or self._is_empty(other_value):
                return False
            try:
                return not self._compare(value, other_value, operator)
            except TypeError:
                return True

        return True

    @staticmethod
    def _is_empty(value: Any) -> bool:
        return value is None or (isinstance(value, str) and not value.strip())

    @staticmethod
    def _matches_type(value: Any, expected: Any) -> bool:
        if value is None:
            return True
        expected_types: dict[str, type[Any]] = {
            "string": str,
            "number": (int, float),
            "boolean": bool,
        }
        expected_type = expected_types.get(expected)
        return expected_type is not None and isinstance(value, expected_type)

    @staticmethod
    def _parse_date(value: Any) -> date | None:
        if not isinstance(value, str):
            return None
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None

    @staticmethod
    def _compare(value: Any, other_value: Any, operator: str) -> bool:
        operators = {
            "eq": lambda left, right: left == right,
            "ne": lambda left, right: left != right,
            "lt": lambda left, right: left < right,
            "lte": lambda left, right: left <= right,
            "gt": lambda left, right: left > right,
            "gte": lambda left, right: left >= right,
        }
        return operators[operator](value, other_value)

    @staticmethod
    def has_errors(findings: list[Finding]) -> bool:
        return any(finding.severity == FindingSeverity.ERROR for finding in findings)
