"""Standard-library tests for the Git-aware repository guard."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "ci" / "validate_repo.py"
SPEC = importlib.util.spec_from_file_location("validate_repo", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load repository guard module.")
guard = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = guard
SPEC.loader.exec_module(guard)


class TemporaryGitRepository(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.git("init")
        self.git("config", "user.email", "guard@example.test")
        self.git("config", "user.name", "Repository Guard Test")

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def git(self, *arguments: str) -> str:
        completed = subprocess.run(
            ["git", *arguments],
            cwd=self.root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return completed.stdout.strip()

    def write(self, relative_path: str, content: str) -> None:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def create_valid_default_fixture(self) -> None:
        workflow = """name: Repository guard
repository-guard:
  permissions: contents: read
  pull_request:
  workflow_dispatch:
  steps:
    - uses: actions/setup-node@v4
    - run: python -m unittest discover -s tests/ci -p test_*.py
    - run: node --test tests/design/*.mjs
    - run: python scripts/ci/validate_repo.py
"""
        settings = {
            "schemaVersion": 1,
            "repository": "owner/repository",
            "ci": {"checkName": "repository-guard"},
            "labels": [{"name": "type: task", "color": "1D76DB", "description": "Task"}],
            "branchProtection": {
                "main": {"requiredApprovingReviewCount": 1},
                "dev": {"requiredApprovingReviewCount": 0},
            },
        }
        context_artifacts = {
            "AGENTS.md": """## Prompt Intake Gate
Goal
Success Criteria
Constraints
Stopping Conditions
Không bắt đầu task
""",
            "docs/ai/TEAM_PROTOCOL.md": """Prompt Intake Gate
## Mục tiêu, success criteria, constraints và stopping conditions
- Constraints:
""",
            ".agents/context-packs/TEMPLATE.md": """## Identity
## Mục tiêu và ranh giới
## Scope đã claim
## Context được chọn lọc
## Dependencies và resource claim
## Kiểm chứng và handoff
- Constraints:
""",
            ".agents/playbooks/claim-task.md": "# Prompt Intake Gate\nSuccess Criteria\nConstraints\nStopping Conditions\n",
            ".agents/playbooks/prepare-context.md": "# Context Pack\nmode `explore`\nPrompt Intake Gate\nConstraints\n",
            ".agents/playbooks/start-worktree.md": "git worktree add <path>\n.env.example\n",
            ".agents/playbooks/impeccable-audit.md": "# CLI audit\nadvisory\nnative skill\n",
            ".impeccable/config.json": json.dumps(
                {
                    "detector": {
                        "ignoreRules": [],
                        "ignoreFiles": [],
                        "ignoreValues": [],
                        "designSystem": {"enabled": False},
                    }
                }
            ),
        }
        for relative_path in guard.REQUIRED_PATHS:
            if relative_path == ".github/repository-settings.json":
                self.write(relative_path, json.dumps(settings))
            elif relative_path == ".github/workflows/repository-guard.yml":
                self.write(relative_path, workflow)
            elif relative_path in context_artifacts:
                self.write(relative_path, context_artifacts[relative_path])
            else:
                self.write(relative_path, "fixture\n")
        self.write(".gitignore", ".env\n")
        self.git("add", ".")

    def test_default_scope_includes_tracked_and_untracked_but_not_ignored_env(self) -> None:
        self.create_valid_default_fixture()
        self.write("tracked.txt", "tracked\n")
        self.git("add", "tracked.txt")
        self.write("untracked.txt", "untracked\n")
        self.write(".env", "API_KEY=local-only\n")

        paths = {path.as_posix() for path in guard.default_scope_paths(self.root)}

        self.assertIn("tracked.txt", paths)
        self.assertIn("untracked.txt", paths)
        self.assertNotIn(".env", paths)
        self.assertEqual([], guard.validate_default(self.root))

    def test_staged_preflight_reads_index_and_redacts_secret_value(self) -> None:
        token = "ghp_" + "a" * 26 + "123456"
        self.write("secret.txt", f"TOKEN={token}\n")
        self.git("add", "secret.txt")
        self.write("secret.txt", "TOKEN=removed-from-worktree\n")

        errors = guard.validate_staged(self.root)
        output = "\n".join(errors)

        self.assertIn("Possible GitHub token in secret.txt", output)
        self.assertNotIn(token, output)

    def test_staged_preflight_checks_sensitive_paths_and_whitespace(self) -> None:
        self.write(".env", "LOCAL=1\n")
        self.git("add", "-f", ".env")
        self.write("whitespace.txt", "line with trailing space \n")
        self.git("add", "whitespace.txt")

        output = "\n".join(guard.validate_staged(self.root))

        self.assertIn("Sensitive local file must not be present in repository scope: .env", output)
        self.assertIn("Trailing whitespace in whitespace.txt:1", output)

    def test_default_scope_requires_context_pack_contract(self) -> None:
        self.create_valid_default_fixture()
        self.write(".agents/context-packs/TEMPLATE.md", "# Incomplete\n")

        output = "\n".join(guard.validate_default(self.root))

        self.assertIn("Context artifact is missing required guidance: .agents/context-packs/TEMPLATE.md", output)

    def test_default_scope_requires_prompt_intake_gate_and_constraints(self) -> None:
        self.create_valid_default_fixture()
        self.write("AGENTS.md", "# Rules\n")
        self.write(
            ".agents/context-packs/TEMPLATE.md",
            """## Identity
## Mục tiêu và ranh giới
## Scope đã claim
## Context được chọn lọc
## Dependencies và resource claim
## Kiểm chứng và handoff
""",
        )

        output = "\n".join(guard.validate_default(self.root))

        self.assertIn("Context artifact is missing required guidance: AGENTS.md (## Prompt Intake Gate)", output)
        self.assertIn("Context artifact is missing required guidance: .agents/context-packs/TEMPLATE.md (- Constraints:)", output)

    def test_default_scope_rejects_impeccable_native_hook_or_invalid_shared_config(self) -> None:
        self.create_valid_default_fixture()
        self.write(".cursor/hooks.json", "{}\n")
        self.write(".impeccable/config.json", "{}\n")

        output = "\n".join(guard.validate_default(self.root))

        self.assertIn("Impeccable native integration is not allowed: .cursor/hooks.json", output)
        self.assertIn(".impeccable/config.json must define a detector object.", output)

    def test_range_preflight_reads_head_revision_not_worktree(self) -> None:
        self.write("base.txt", "base\n")
        self.git("add", "base.txt")
        self.git("commit", "-m", "base")
        base = self.git("rev-parse", "HEAD")

        token = "sk-proj-" + "a" * 26 + "123456"
        self.write("range.txt", f"TOKEN={token}\n")
        self.git("add", "range.txt")
        self.git("commit", "-m", "range change")
        head = self.git("rev-parse", "HEAD")
        self.write("range.txt", "TOKEN=removed-from-worktree\n")

        errors = guard.validate_range(self.root, f"{base}...{head}")
        output = "\n".join(errors)

        self.assertIn("Possible API token in range.txt", output)
        self.assertNotIn(token, output)

    def test_git_worktree_isolated_and_does_not_copy_ignored_env(self) -> None:
        self.write(".gitignore", ".env\n")
        self.write("source.txt", "source\n")
        self.write(".env", "LOCAL_ONLY=1\n")
        self.git("add", ".gitignore", "source.txt")
        self.git("commit", "-m", "worktree source")
        worktree = self.root.parent / "isolated-worktree"

        self.git("worktree", "add", "--detach", str(worktree), "HEAD")
        try:
            completed = subprocess.run(
                ["git", "-C", str(worktree), "status", "--short", "--branch"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.assertIn("HEAD", completed.stdout)
            self.assertTrue((worktree / "source.txt").is_file())
            self.assertFalse((worktree / ".env").exists())
        finally:
            self.git("worktree", "remove", "--force", str(worktree))


if __name__ == "__main__":
    unittest.main()
