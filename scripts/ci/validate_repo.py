#!/usr/bin/env python3
"""Git-aware validation for the repository bootstrap.

The default mode validates every tracked file plus each untracked file that Git
does not ignore.  Preflight modes inspect the staged index or the post-image of
a Git range, so they never print a matched secret value from a working tree.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Sequence
from urllib.parse import unquote


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
REQUIRED_PATHS = (
    "AGENTS.md",
    "CLAUDE.md",
    ".cursor/rules/00-team-protocol.mdc",
    ".agents/context-packs/TEMPLATE.md",
    ".agents/playbooks/claim-task.md",
    ".agents/playbooks/demo-readiness.md",
    ".agents/playbooks/impeccable-audit.md",
    ".agents/playbooks/implement-handoff.md",
    ".agents/playbooks/prepare-context.md",
    ".agents/playbooks/review-merge.md",
    ".agents/playbooks/start-worktree.md",
    ".github/LABELS.md",
    ".github/BRANCH_RULES.md",
    ".github/repository-settings.json",
    ".github/workflows/repository-guard.yml",
    ".impeccable/config.json",
    "docs/DESIGN.md",
    "docs/PRODUCT.md",
    "docs/design/README.md",
    "docs/design/reviews/README.md",
    "docs/ai/ARCHITECTURE.md",
    "docs/ai/DECISIONS.md",
    "docs/ai/DEMO.md",
    "docs/ai/DEPLOYMENT.md",
    "docs/ai/PROJECT_CONTEXT.md",
    "docs/ai/SECRETS_AND_DATA.md",
    "docs/ai/TEAM.md",
    "docs/ai/TEAM_PROTOCOL.md",
    "scripts/ci/validate_repo.py",
    "scripts/design/impeccable-audit.mjs",
    "scripts/github/sync-repo-settings.ps1",
)
TEXT_EXTENSIONS = {
    ".cmd",
    ".css",
    ".html",
    ".json",
    ".js",
    ".mjs",
    ".jsx",
    ".md",
    ".mdc",
    ".ps1",
    ".py",
    ".scss",
    ".sh",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}
TEXT_FILENAMES = {".editorconfig", ".env.example", ".gitattributes", ".gitignore", "Dockerfile", "Makefile"}
FORBIDDEN_FILENAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    "credentials.json",
    "id_ed25519",
    "id_rsa",
    "service-account.json",
}
FORBIDDEN_SUFFIXES = {".key", ".p12", ".pem", ".pfx"}
FORBIDDEN_IMPECCABLE_NATIVE_PATHS = (
    ".codex/hooks.json",
    ".cursor/hooks.json",
    ".agents/skills/impeccable",
    ".agents/skills/impeccable.md",
    ".claude/skills/impeccable",
    ".claude/skills/impeccable.md",
)
MARKDOWN_LINK = re.compile(r"(?<!\!)\[[^\]]*\]\((?P<target>[^)\s]+)(?:\s+[^)]*)?\)")
PRIVATE_KEY = re.compile(r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----")
GITHUB_TOKEN = re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")
OPENAI_TOKEN = re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b")
ANTHROPIC_TOKEN = re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b")
SECRET_PATTERNS = (
    (PRIVATE_KEY, "private key"),
    (GITHUB_TOKEN, "GitHub token"),
    (OPENAI_TOKEN, "API token"),
    (ANTHROPIC_TOKEN, "API token"),
)
CONTEXT_ARTIFACT_FRAGMENTS = {
    "AGENTS.md": (
        "## Prompt Intake Gate",
        "Goal",
        "Success Criteria",
        "Constraints",
        "Stopping Conditions",
        "Không bắt đầu task",
    ),
    "docs/ai/TEAM_PROTOCOL.md": (
        "Prompt Intake Gate",
        "## Mục tiêu, success criteria, constraints và stopping conditions",
        "- Constraints:",
    ),
    ".agents/context-packs/TEMPLATE.md": (
        "## Identity",
        "## Mục tiêu và ranh giới",
        "## Scope đã claim",
        "## Context được chọn lọc",
        "## Dependencies và resource claim",
        "## Kiểm chứng và handoff",
        "- Constraints:",
    ),
    ".agents/playbooks/claim-task.md": (
        "Prompt Intake Gate",
        "Success Criteria",
        "Constraints",
        "Stopping Conditions",
    ),
    ".agents/playbooks/prepare-context.md": (
        "mode `explore`",
        "Context Pack",
        "Prompt Intake Gate",
        "Constraints",
    ),
    ".agents/playbooks/start-worktree.md": (
        "git worktree add",
        ".env.example",
    ),
    ".agents/playbooks/impeccable-audit.md": (
        "CLI audit",
        "advisory",
        "native skill",
    ),
}


class GuardError(RuntimeError):
    """An environment or Git-selection error that can be shown safely."""


def display(relative_path: Path) -> str:
    return relative_path.as_posix()


def is_text_file(relative_path: Path) -> bool:
    return relative_path.suffix.lower() in TEXT_EXTENSIONS or relative_path.name in TEXT_FILENAMES


def is_external_link(target: str) -> bool:
    return target.startswith(("#", "data:", "http:", "https:", "mailto:"))


def run_git(root: Path, arguments: Sequence[str], operation: str) -> bytes:
    """Run Git without relaying output that could include file contents."""
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), *arguments],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except OSError as error:
        raise GuardError(f"Unable to run Git while {operation}.") from error

    if completed.returncode != 0:
        raise GuardError(f"Git failed while {operation}.")
    return completed.stdout


def ensure_git_repository(root: Path) -> None:
    result = run_git(root, ["rev-parse", "--is-inside-work-tree"], "checking the repository")
    if result.strip() != b"true":
        raise GuardError("Repository guard must run inside a Git work tree.")


def decode_git_path(raw_path: bytes) -> Path:
    relative_path = Path(os.fsdecode(raw_path))
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise GuardError("Git returned a path outside the repository.")
    return relative_path


def nul_delimited_paths(output: bytes) -> list[Path]:
    paths: list[Path] = []
    seen: set[Path] = set()
    for raw_path in output.split(b"\0"):
        if not raw_path:
            continue
        relative_path = decode_git_path(raw_path)
        if relative_path not in seen:
            paths.append(relative_path)
            seen.add(relative_path)
    return paths


def default_scope_paths(root: Path) -> list[Path]:
    """Return tracked plus untracked, nonignored paths from the working tree."""
    output = run_git(
        root,
        ["ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        "selecting tracked and untracked files",
    )
    return nul_delimited_paths(output)


def staged_scope_paths(root: Path) -> list[Path]:
    output = run_git(
        root,
        ["diff", "--cached", "--name-only", "-z", "--diff-filter=ACMRT", "-M"],
        "selecting staged files",
    )
    return nul_delimited_paths(output)


def parse_range(value: str) -> tuple[str, str]:
    parts = value.split("...")
    if len(parts) != 2 or not all(parts) or any(part.startswith("-") for part in parts):
        raise GuardError("--range must use the form <base...head>.")
    return parts[0], parts[1]


def resolve_commit(root: Path, revision: str) -> str:
    output = run_git(root, ["rev-parse", "--verify", f"{revision}^{{commit}}"], "resolving a range revision")
    return output.decode("ascii", errors="strict").strip()


def range_scope_paths(root: Path, value: str) -> tuple[list[Path], str]:
    base, head = parse_range(value)
    base_commit = resolve_commit(root, base)
    head_commit = resolve_commit(root, head)
    output = run_git(
        root,
        ["diff", "--name-only", "-z", "--diff-filter=ACMRT", "-M", f"{base_commit}...{head_commit}"],
        "selecting range files",
    )
    return nul_delimited_paths(output), head_commit


def read_workspace_file(root: Path, relative_path: Path) -> bytes | None:
    path = root / relative_path
    if not path.exists() or not path.is_file() or path.is_symlink():
        return None
    try:
        return path.read_bytes()
    except OSError as error:
        raise GuardError(f"Unable to read {display(relative_path)}.") from error


def read_index_file(root: Path, relative_path: Path) -> bytes:
    return run_git(root, ["show", f":{relative_path.as_posix()}"], "reading a staged file")


def read_revision_file(root: Path, commit: str, relative_path: Path) -> bytes:
    return run_git(root, ["show", f"{commit}:{relative_path.as_posix()}"], "reading a range file")


def validate_required_paths(root: Path, errors: list[str]) -> None:
    for relative_path in REQUIRED_PATHS:
        if not (root / relative_path).is_file():
            errors.append(f"Missing required artifact: {relative_path}")


def validate_context_artifacts(root: Path, errors: list[str]) -> None:
    for relative_path, fragments in CONTEXT_ARTIFACT_FRAGMENTS.items():
        path = root / relative_path
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        except UnicodeDecodeError:
            errors.append(f"Context artifact is not valid UTF-8: {relative_path}")
            continue

        for fragment in fragments:
            if fragment not in text:
                errors.append(f"Context artifact is missing required guidance: {relative_path} ({fragment})")


def validate_repository_settings(root: Path, errors: list[str]) -> None:
    path = root / ".github/repository-settings.json"
    try:
        settings = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"Invalid repository settings JSON: {error}")
        return

    if settings.get("schemaVersion") != 1:
        errors.append("repository-settings.json must use schemaVersion 1.")
    if not isinstance(settings.get("repository"), str) or "/" not in settings["repository"]:
        errors.append("repository-settings.json must contain an owner/repository value.")
    if settings.get("ci", {}).get("checkName") != "repository-guard":
        errors.append("repository-settings.json must name the repository-guard CI check.")

    labels = settings.get("labels")
    if not isinstance(labels, list) or not labels:
        errors.append("repository-settings.json must define at least one label.")
    else:
        names = [label.get("name") for label in labels if isinstance(label, dict)]
        if len(names) != len(labels) or len(set(names)) != len(names):
            errors.append("repository-settings.json labels must have unique names.")
        for label in labels:
            if not isinstance(label, dict) or not re.fullmatch(r"[0-9A-Fa-f]{6}", str(label.get("color", ""))):
                errors.append("Every repository label must have a six-character hex color.")
                break
            if len(str(label.get("description", ""))) > 100:
                errors.append("GitHub label descriptions must be 100 characters or fewer.")
                break

    protections = settings.get("branchProtection", {})
    for branch, expected_reviews in (("main", 1), ("dev", 0)):
        policy = protections.get(branch)
        if not isinstance(policy, dict):
            errors.append(f"repository-settings.json is missing branchProtection.{branch}.")
            continue
        if policy.get("requiredApprovingReviewCount") != expected_reviews:
            errors.append(f"branchProtection.{branch} must require {expected_reviews} approval(s).")


def validate_impeccable_policy(root: Path, errors: list[str]) -> None:
    for relative_path in FORBIDDEN_IMPECCABLE_NATIVE_PATHS:
        if (root / relative_path).exists():
            errors.append(f"Impeccable native integration is not allowed: {relative_path}")

    path = root / ".impeccable/config.json"
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"Invalid Impeccable config JSON: {error}")
        return

    detector = config.get("detector")
    if not isinstance(detector, dict):
        errors.append(".impeccable/config.json must define a detector object.")
        return
    for key in ("ignoreRules", "ignoreFiles", "ignoreValues"):
        if not isinstance(detector.get(key), list):
            errors.append(f".impeccable/config.json detector.{key} must be an array.")
    design_system = detector.get("designSystem")
    if not isinstance(design_system, dict) or not isinstance(design_system.get("enabled"), bool):
        errors.append(".impeccable/config.json detector.designSystem.enabled must be a boolean.")
    if "hook" in config or "hook" in detector:
        errors.append(".impeccable/config.json must not configure a native hook.")


def validate_markdown_links(root: Path, relative_path: Path, text: str, errors: list[str]) -> None:
    for match in MARKDOWN_LINK.finditer(text):
        target = unquote(match.group("target").strip("<>"))
        if is_external_link(target):
            continue
        local_target = target.split("#", maxsplit=1)[0]
        if not local_target:
            continue
        resolved = (root / relative_path).parent / local_target
        if not resolved.exists():
            errors.append(f"Broken local link in {display(relative_path)}: {target}")


def validate_path_policy(relative_path: Path, errors: list[str]) -> None:
    name = relative_path.name.lower()
    if name in FORBIDDEN_FILENAMES or relative_path.suffix.lower() in FORBIDDEN_SUFFIXES:
        errors.append(f"Sensitive local file must not be present in repository scope: {display(relative_path)}")


def validate_file_content(
    root: Path,
    relative_path: Path,
    content: bytes,
    errors: list[str],
    *,
    validate_links: bool,
) -> None:
    validate_path_policy(relative_path, errors)
    if not is_text_file(relative_path):
        return

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        errors.append(f"Text file is not valid UTF-8: {display(relative_path)}")
        return

    if relative_path.suffix.lower() not in {".md", ".mdc"}:
        for line_number, line in enumerate(text.splitlines(), start=1):
            if line.rstrip(" \t") != line:
                errors.append(f"Trailing whitespace in {display(relative_path)}:{line_number}")

    if validate_links and relative_path.suffix.lower() in {".md", ".mdc"}:
        validate_markdown_links(root, relative_path, text, errors)

    if relative_path.name != ".env.example":
        for pattern, label in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"Possible {label} in {display(relative_path)}")


def validate_default_scope(root: Path, errors: list[str]) -> None:
    for relative_path in default_scope_paths(root):
        content = read_workspace_file(root, relative_path)
        if content is None:
            validate_path_policy(relative_path, errors)
            continue
        validate_file_content(root, relative_path, content, errors, validate_links=True)


def validate_staged_scope(root: Path, errors: list[str]) -> None:
    for relative_path in staged_scope_paths(root):
        validate_file_content(root, relative_path, read_index_file(root, relative_path), errors, validate_links=False)


def validate_range_scope(root: Path, value: str, errors: list[str]) -> None:
    paths, head_commit = range_scope_paths(root, value)
    for relative_path in paths:
        content = read_revision_file(root, head_commit, relative_path)
        validate_file_content(root, relative_path, content, errors, validate_links=False)


def validate_workflow_contract(root: Path, errors: list[str]) -> None:
    path = root / ".github/workflows/repository-guard.yml"
    try:
        workflow = path.read_text(encoding="utf-8")
    except OSError as error:
        errors.append(f"Unable to read repository guard workflow: {error}")
        return

    required_fragments = (
        "name: Repository guard",
        "repository-guard:",
        "contents: read",
        "python -m unittest discover -s tests/ci",
        "actions/setup-node@v4",
        "node --test tests/design/*.mjs",
        "python scripts/ci/validate_repo.py",
        "pull_request:",
        "workflow_dispatch:",
    )
    for fragment in required_fragments:
        if fragment not in workflow:
            errors.append(f"Repository guard workflow is missing: {fragment}")


def validate_default(root: Path) -> list[str]:
    errors: list[str] = []
    validate_required_paths(root, errors)
    validate_context_artifacts(root, errors)
    validate_repository_settings(root, errors)
    validate_impeccable_policy(root, errors)
    validate_default_scope(root, errors)
    validate_workflow_contract(root, errors)
    return errors


def validate_staged(root: Path) -> list[str]:
    errors: list[str] = []
    validate_staged_scope(root, errors)
    return errors


def validate_range(root: Path, value: str) -> list[str]:
    errors: list[str] = []
    validate_range_scope(root, value, errors)
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help=argparse.SUPPRESS)
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--staged", action="store_true", help="scan staged additions and modifications")
    scope.add_argument("--range", dest="git_range", metavar="BASE...HEAD", help="scan the post-image of a Git range")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    root = args.root.resolve()
    if not root.is_dir():
        print("Repository guard failed:", file=sys.stderr)
        print("- --root must name an existing directory.", file=sys.stderr)
        return 1

    try:
        ensure_git_repository(root)
        if args.staged:
            errors = validate_staged(root)
            scope_name = "staged preflight"
        elif args.git_range:
            errors = validate_range(root, args.git_range)
            scope_name = "range preflight"
        else:
            errors = validate_default(root)
            scope_name = "default repository scope"
    except GuardError as error:
        print("Repository guard failed:", file=sys.stderr)
        print(f"- {error}", file=sys.stderr)
        return 1

    if errors:
        print("Repository guard failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Repository guard passed: {scope_name} is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
