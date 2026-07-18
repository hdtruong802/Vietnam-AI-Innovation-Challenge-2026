from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "ci" / "changed_scope.py"
SPEC = importlib.util.spec_from_file_location("changed_scope", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load changed scope module.")
scope = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = scope
SPEC.loader.exec_module(scope)


class ChangedScopeTests(unittest.TestCase):
    def test_classify_only_selects_affected_application_and_policy_jobs(self) -> None:
        result = scope.classify(
            [
                "frontend/src/app/page.tsx",
                "backend/app/main.py",
                "data/1.000005.txt",
                "evidence/ai-log/policy.json",
                "scripts/ci/validate_repo.py",
            ]
        )

        self.assertEqual(
            result,
            {
                "frontend": True,
                "backend": True,
                "data": True,
                "design": False,
                "ai_log": True,
                "guard": True,
            },
        )

    def test_docs_only_diff_does_not_select_application_jobs(self) -> None:
        result = scope.classify(["docs/ai/TEAM_PROTOCOL.md", "README.md"])

        self.assertTrue(all(value is False for value in result.values()))


if __name__ == "__main__":
    unittest.main()
