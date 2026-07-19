from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path


EVAL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = EVAL_ROOT / "validate_procedure_packs.py"
SPEC = importlib.util.spec_from_file_location("eval_pack_validator", SCRIPT)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VALIDATOR
SPEC.loader.exec_module(VALIDATOR)
PACK_FILES = (
    "dang-ky-khai-sinh.json",
    "dang-ky-thuong-tru.json",
    "dang-ky-ho-kinh-doanh.json",
)


def read(root: Path, relative: str) -> dict:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def write(root: Path, relative: str, value: dict) -> None:
    (root / relative).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


class ProcedurePackContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "eval"
        self.root.mkdir()
        shutil.copy(EVAL_ROOT / "approved-source-registry.json", self.root)
        shutil.copy(EVAL_ROOT / "synthetic-candidate-rag-chunks.jsonl", self.root)
        shutil.copytree(EVAL_ROOT / "procedure-packs", self.root / "procedure-packs")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_candidate_passes_structural_validation(self) -> None:
        self.assertEqual([], VALIDATOR.validate(root=EVAL_ROOT, as_of=date(2026, 7, 18)))

    def test_candidate_cannot_pass_release_validation(self) -> None:
        issues = VALIDATOR.validate(release=True, root=EVAL_ROOT, as_of=date(2026, 7, 18))
        self.assertTrue(any(issue.code == "release_blocked" for issue in issues))

    def test_each_pack_is_fail_closed_and_scoped(self) -> None:
        for filename in PACK_FILES:
            pack = read(EVAL_ROOT, f"procedure-packs/{filename}")
            self.assertEqual("needs_review", pack["review_status"])
            self.assertTrue(pack["not_for_production"])
            self.assertTrue(pack["scope"]["included_cases"])
            self.assertTrue(pack["scope"]["excluded_cases"])
            self.assertEqual([], pack["checklist_items"])
            self.assertEqual([], pack["validation_rules"])

    def test_registry_has_exact_canonical_pairs(self) -> None:
        registry = read(EVAL_ROOT, "approved-source-registry.json")
        pairs = {(row["procedure_id"], row["source_id"]) for row in registry["sources"]}
        self.assertEqual({
            ("dang-ky-khai-sinh", "1.001193"),
            ("dang-ky-thuong-tru", "1.004222"),
            ("dang-ky-ho-kinh-doanh", "1.001612"),
        }, pairs)

    def test_unknown_and_cross_pack_citations_are_rejected(self) -> None:
        relative = f"procedure-packs/{PACK_FILES[0]}"
        pack = read(self.root, relative)
        pack["steps"] = [{"id": "STEP-001", "source": {"source_id": "1.004222", "locator": "x"}}]
        write(self.root, relative, pack)
        self.assertTrue(any(issue.code == "citation" for issue in VALIDATOR.validate(root=self.root)))

    def test_duplicate_stable_id_is_rejected(self) -> None:
        relative = f"procedure-packs/{PACK_FILES[0]}"
        pack = read(self.root, relative)
        item = {"id": "DOC-001", "source": {"source_id": "1.001193", "locator": "x"}}
        pack["checklist_items"] = [item, item]
        write(self.root, relative, pack)
        self.assertTrue(any(issue.code == "duplicate_id" for issue in VALIDATOR.validate(root=self.root)))

    def test_intake_and_form_claims_require_citations(self) -> None:
        relative = f"procedure-packs/{PACK_FILES[0]}"
        pack = read(self.root, relative)
        pack["intake_questions"] = [{"id": "Q-001", "text": "Synthetic"}]
        pack["form_schema"]["properties"] = {"field": {"type": "string"}}
        write(self.root, relative, pack)
        rendered = "\n".join(issue.render() for issue in VALIDATOR.validate(root=self.root))
        self.assertIn("intake_questions[0].source", rendered)
        self.assertIn("form_schema.properties.field.source", rendered)

    def test_non_deterministic_rule_is_rejected(self) -> None:
        relative = f"procedure-packs/{PACK_FILES[0]}"
        pack = read(self.root, relative)
        pack["validation_rules"] = [{
            "rule_id": "RULE-001", "type": "llm_verdict",
            "source": {"source_id": "1.001193", "locator": "x"},
        }]
        write(self.root, relative, pack)
        self.assertTrue(any(issue.code == "rule_type" for issue in VALIDATOR.validate(root=self.root)))

    def test_synthetic_chunks_are_watermarked_and_use_canonical_slugs(self) -> None:
        rows = [json.loads(line) for line in (EVAL_ROOT / "synthetic-candidate-rag-chunks.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertTrue(rows)
        self.assertTrue(all(row["review_status"] == "needs_review" for row in rows))
        self.assertTrue(all(row["approval_mode"] == "synthetic_demo" for row in rows))
        self.assertTrue(all(row["not_for_production"] is True for row in rows))
        self.assertTrue(all(row["release_eligible"] is False for row in rows))
        self.assertTrue(all(row["quarantine_reason"] == "missing_human_k1_and_official_evidence" for row in rows))
        self.assertTrue(all(set(row["procedure_ids"]).issubset(VALIDATOR.EXPECTED) for row in rows))

    def test_release_rejects_local_url_and_future_dates(self) -> None:
        registry = read(self.root, "approved-source-registry.json")
        registry.update({"review_status": "approved", "approval_mode": "human_k1", "not_for_production": False, "freeze_date": "2026-07-18"})
        row = registry["sources"][0]
        row.update({"source_url": "local-k1-fixture://1.001193", "effective_from": "2027-01-01", "last_verified_at": "2027-01-01", "reviewed_at": "2027-01-01"})
        write(self.root, "approved-source-registry.json", registry)
        rendered = "\n".join(issue.render() for issue in VALIDATOR.validate(release=True, root=self.root, as_of=date(2026, 7, 18)))
        self.assertIn("official HTTPS .gov.vn URL required", rendered)
        self.assertIn("future-effective source", rendered)
        self.assertIn("future verification date", rendered)

    def test_coverage_report_is_machine_readable(self) -> None:
        report = VALIDATOR.coverage(EVAL_ROOT)
        self.assertEqual("vaic-procedure-pack-coverage-v1", report["schema_version"])
        self.assertEqual(set(VALIDATOR.EXPECTED), set(report["packs"]))
        self.assertTrue(all(row["citation_coverage"] == 0.0 for row in report["packs"].values()))


if __name__ == "__main__":
    unittest.main()
