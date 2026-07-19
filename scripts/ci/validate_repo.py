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
DATA_DIRECTORY = Path("data")
REQUIRED_PATHS = (
    "AGENTS.md",
    "CLAUDE.md",
    ".cursor/rules/00-team-protocol.mdc",
    ".agents/context-packs/TEMPLATE.md",
    ".agents/context-packs/README.md",
    ".agents/playbooks/claim-task.md",
    ".agents/playbooks/demo-readiness.md",
    ".agents/playbooks/impeccable-audit.md",
    ".agents/playbooks/implement-handoff.md",
    ".agents/playbooks/prepare-context.md",
    ".agents/playbooks/review-merge.md",
    ".agents/playbooks/start-worktree.md",
    ".githooks/commit-msg",
    ".githooks/post-commit",
    ".githooks/pre-commit",
    ".githooks/pre-merge-commit",
    ".githooks/prepare-commit-msg",
    ".github/LABELS.md",
    ".github/BRANCH_RULES.md",
    ".github/repository-settings.json",
    ".github/workflows/repository-guard.yml",
    ".github/workflows/promote-candidate.yml",
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
    "evidence/ai-log/README.md",
    "evidence/ai-log/policy.json",
    "evidence/ai-log/schemas/commit-evidence.schema.json",
    "evidence/ai-log/schemas/prompt-event.schema.json",
    "scripts/ai_log/ai_log.py",
    "scripts/ci/validate_repo.py",
    "scripts/ci/changed_scope.py",
    "scripts/ci/validate_data.py",
    "scripts/ci/release_manifest.py",
    "scripts/design/impeccable-audit.mjs",
    "scripts/github/sync-repo-settings.ps1",
    "team_docs/phancong.md",
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
        "AI-Log",
    ),
    ".agents/context-packs/TEMPLATE.md": (
        "## Identity",
        "## Mục tiêu và ranh giới",
        "## Scope đã claim",
        "## Context được chọn lọc",
        "## Dependencies và resource claim",
        "## Kiểm chứng và handoff",
        "- Constraints:",
        "AI-Log",
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
    "evidence/ai-log/README.md": (
        "onboard",
        "doctor --strict",
        ".ai-log/hooks",
        "không tự push",
    ),
}

AI_LOG_TOOLS = {"codex", "claude", "cursor", "antigravity"}
AI_LOG_CAPTURE_STATUSES = {"complete", "warning", "no_new_prompt", "manual", "git_operation"}
AI_LOG_FORBIDDEN_KEYS = {
    "absolute_path",
    "assistant_response",
    "chain_of_thought",
    "raw_session",
    "session_path",
    "source_path",
    "system_prompt",
    "tool_call",
    "tool_output",
    "transcript",
}
AI_LOG_TRAILER = re.compile(r"^AI-Log:\s*(log-[0-9a-f]{24})\s*$", re.MULTILINE)
GIT_OID = re.compile(r"^[0-9a-f]{40}$")
CONFLICT_MARKER = re.compile(r"^(?:<<<<<<< .+|=======|>>>>>>> .+)$", re.MULTILINE)
AI_LOG_EMAIL = re.compile(r"(?<![\w.+-])[\w.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![\w.-])")
AI_LOG_IDENTIFIER = re.compile(r"(?<!\d)(?:\+?84\s?)?\d{10,12}(?!\d)")
AI_LOG_USER_PATH = re.compile(r"(?i)(?:\b[A-Z]:\\Users\\[^\\\s]+|/(?:home|Users)/[^/\s]+)")
AI_LOG_PROMPT_KEYS = {
    "schema_version",
    "record_type",
    "prompt_id",
    "occurred_at",
    "captured_at",
    "member_id",
    "tool",
    "event",
    "prompt",
    "prompt_preview",
    "model",
    "task_record",
    "branch",
    "workspace_fingerprint",
    "source",
    "sanitization",
    "capture_warnings",
}
AI_LOG_COMMIT_KEYS = {
    "schema_version",
    "record_type",
    "ai_log_id",
    "created_at",
    "member_id",
    "branch",
    "parent_commit",
    "task_records",
    "prompt_ids",
    "tools",
    "capture_status",
    "warnings",
    "operation",
    "replaces_ai_log",
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


def is_data_path(relative_path: Path) -> bool:
    """Return whether a path belongs to the intentionally payload-free data scope."""
    return relative_path == DATA_DIRECTORY or DATA_DIRECTORY in relative_path.parents


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


def ai_log_forbidden_key(value: object) -> str | None:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in AI_LOG_FORBIDDEN_KEYS:
                return str(key)
            nested_key = ai_log_forbidden_key(child)
            if nested_key:
                return nested_key
    elif isinstance(value, list):
        for child in value:
            nested_key = ai_log_forbidden_key(child)
            if nested_key:
                return nested_key
    return None


def validate_ai_log_policy(root: Path, errors: list[str]) -> None:
    policy_path = root / "evidence/ai-log/policy.json"
    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        errors.append(f"Invalid AI Log policy JSON: {error}")
        return

    if policy.get("schemaVersion") != 1 or policy.get("format") != "prompt-only":
        errors.append("AI Log policy must use schemaVersion 1 and prompt-only format.")
    if set(policy.get("supportedTools", [])) != AI_LOG_TOOLS:
        errors.append("AI Log policy must support Codex, Claude, Cursor and Antigravity equally.")
    if policy.get("allowedEvents") != ["UserPrompt"]:
        errors.append("AI Log policy may allow only UserPrompt events.")
    if policy.get("captureFailure") != "warn-and-commit":
        errors.append("AI Log capture failure policy must be warn-and-commit.")
    enforcement = policy.get("historyEnforcement")
    expected_enforcement_keys = {"mode", "enabled", "exemptMergeCommits", "exemptCommitOids"}
    if not isinstance(enforcement, dict) or set(enforcement) != expected_enforcement_keys:
        errors.append("AI Log history enforcement must declare its exact scoped-exception contract.")
    elif (
        enforcement.get("mode") != "policy-presence"
        or enforcement.get("enabled") is not True
        or enforcement.get("exemptMergeCommits") is not True
    ):
        errors.append("AI Log history enforcement must use policy-presence and exempt merge commits.")
    else:
        exemptions = enforcement.get("exemptCommitOids")
        if not isinstance(exemptions, list):
            errors.append("AI Log history exemptions must be a list.")
        else:
            seen_oids: set[str] = set()
            for exemption in exemptions:
                if not isinstance(exemption, dict) or set(exemption) != {"oid", "reason"}:
                    errors.append("Each AI Log history exemption must contain only oid and reason.")
                    continue
                oid = exemption.get("oid")
                reason = exemption.get("reason")
                if not isinstance(oid, str) or not GIT_OID.fullmatch(oid):
                    errors.append("AI Log history exemption oid must be a full lowercase Git SHA.")
                elif oid in seen_oids:
                    errors.append("AI Log history exemption oids must be unique.")
                else:
                    seen_oids.add(oid)
                if not isinstance(reason, str) or not reason.strip():
                    errors.append("AI Log history exemption reason must be non-empty.")

    for relative_path in (
        "evidence/ai-log/schemas/prompt-event.schema.json",
        "evidence/ai-log/schemas/commit-evidence.schema.json",
    ):
        try:
            schema = json.loads((root / relative_path).read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            errors.append(f"Invalid AI Log schema JSON: {relative_path}: {error}")
            continue
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            errors.append(f"AI Log schema must use JSON Schema 2020-12: {relative_path}")


def validate_ai_log_records(root: Path, errors: list[str]) -> None:
    members_root = root / "evidence/ai-log/members"
    if not members_root.is_dir():
        return
    prompt_ids: set[str] = set()
    commit_records: list[tuple[Path, dict[str, object]]] = []
    prompt_pattern = re.compile(
        r"^evidence/ai-log/members/(?P<member>[a-z0-9][a-z0-9-]{1,63})/prompts/"
        r"\d{4}-\d{2}/(?P<id>prompt-[0-9a-f]{24})\.json$"
    )
    commit_pattern = re.compile(
        r"^evidence/ai-log/members/(?P<member>[a-z0-9][a-z0-9-]{1,63})/commits/"
        r"(?P<id>log-[0-9a-f]{24})\.json$"
    )

    for path in members_root.rglob("*.json"):
        relative_path = path.relative_to(root)
        display_path = display(relative_path)
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            errors.append(f"Invalid AI Log record JSON: {display_path}")
            continue
        if not isinstance(record, dict):
            errors.append(f"AI Log record must be a JSON object: {display_path}")
            continue
        forbidden_key = ai_log_forbidden_key(record)
        if forbidden_key:
            errors.append(f"AI Log record contains forbidden session content key in {display_path}: {forbidden_key}")

        if record.get("record_type") == "prompt_event":
            match = prompt_pattern.fullmatch(display_path)
            prompt_id = str(record.get("prompt_id", ""))
            if not match or match.group("id") != prompt_id or match.group("member") != record.get("member_id"):
                errors.append(f"AI Log prompt record path/identity mismatch: {display_path}")
            if record.get("schema_version") != 1 or record.get("event") != "UserPrompt":
                errors.append(f"AI Log may store only schema v1 UserPrompt records: {display_path}")
            if set(record) != AI_LOG_PROMPT_KEYS:
                errors.append(f"AI Log prompt record does not match the prompt-only schema: {display_path}")
            if record.get("tool") not in AI_LOG_TOOLS:
                errors.append(f"AI Log prompt record uses an unsupported tool: {display_path}")
            if not isinstance(record.get("prompt"), str) or not record.get("prompt"):
                errors.append(f"AI Log prompt record must contain sanitized prompt text: {display_path}")
            elif any(pattern.search(record["prompt"]) for pattern in (AI_LOG_EMAIL, AI_LOG_IDENTIFIER, AI_LOG_USER_PATH)):
                errors.append(f"AI Log prompt record contains unredacted sensitive data: {display_path}")
            source = record.get("source")
            if not isinstance(source, dict) or set(source) != {"session_hash", "adapter", "adapter_version"}:
                errors.append(f"AI Log source metadata must be hash-only: {display_path}")
            if prompt_id in prompt_ids:
                errors.append(f"Duplicate AI Log prompt ID: {prompt_id}")
            capture_warnings = record.get("capture_warnings")
            if not isinstance(capture_warnings, list) or any(
                not re.fullmatch(r"[a-z0-9_]+", str(warning)) for warning in capture_warnings
            ):
                errors.append(f"AI Log prompt warnings must be safe machine codes: {display_path}")
            prompt_ids.add(prompt_id)
        elif record.get("record_type") == "commit_evidence":
            match = commit_pattern.fullmatch(display_path)
            log_id = str(record.get("ai_log_id", ""))
            if not match or match.group("id") != log_id or match.group("member") != record.get("member_id"):
                errors.append(f"AI Log commit record path/identity mismatch: {display_path}")
            if record.get("schema_version") != 1 or record.get("capture_status") not in AI_LOG_CAPTURE_STATUSES:
                errors.append(f"Invalid AI Log commit evidence status: {display_path}")
            if set(record) != AI_LOG_COMMIT_KEYS:
                errors.append(f"AI Log commit record does not match the commit-evidence schema: {display_path}")
            tools = record.get("tools")
            if not isinstance(tools, list) or not set(tools).issubset(AI_LOG_TOOLS):
                errors.append(f"Invalid AI Log commit evidence tools: {display_path}")
            warnings = record.get("warnings")
            if not isinstance(warnings, list) or any(
                not re.fullmatch(r"[a-z0-9_]+", str(warning)) for warning in warnings
            ):
                errors.append(f"AI Log commit warnings must be safe machine codes: {display_path}")
            commit_records.append((relative_path, record))
        else:
            errors.append(f"Unknown AI Log record type: {display_path}")

    for relative_path, record in commit_records:
        references = record.get("prompt_ids")
        if not isinstance(references, list):
            errors.append(f"AI Log commit prompt_ids must be an array: {display(relative_path)}")
            continue
        for prompt_id in references:
            if prompt_id not in prompt_ids:
                errors.append(f"AI Log commit references a missing prompt record: {display(relative_path)}")


def validate_ai_log_history(root: Path, value: str, errors: list[str]) -> None:
    base, range_head = parse_range(value)
    resolved_head = resolve_commit(root, range_head)
    exemptions: set[str] = set()
    try:
        head_policy = json.loads(
            read_revision_file(root, resolved_head, Path("evidence/ai-log/policy.json")).decode("utf-8")
        )
        configured_exemptions = head_policy.get("historyEnforcement", {}).get("exemptCommitOids", [])
        if isinstance(configured_exemptions, list):
            exemptions = {
                entry["oid"]
                for entry in configured_exemptions
                if isinstance(entry, dict) and isinstance(entry.get("oid"), str) and GIT_OID.fullmatch(entry["oid"])
            }
    except (GuardError, UnicodeDecodeError, json.JSONDecodeError):
        pass
    commits_output = run_git(
        root,
        ["rev-list", "--reverse", f"{resolve_commit(root, base)}..{resolved_head}"],
        "listing AI Log range commits",
    )
    for raw_commit in commits_output.splitlines():
        commit = raw_commit.decode("ascii", errors="strict")
        if commit in exemptions:
            continue
        try:
            policy = json.loads(
                read_revision_file(root, commit, Path("evidence/ai-log/policy.json")).decode("utf-8")
            )
        except GuardError:
            # A commit without the policy is legacy history.
            continue
        except (UnicodeDecodeError, json.JSONDecodeError):
            errors.append(f"Commit {commit[:12]} has an invalid AI Log policy.")
            continue
        enforcement = policy.get("historyEnforcement")
        if not isinstance(enforcement, dict) or enforcement.get("mode") != "policy-presence":
            errors.append(f"Commit {commit[:12]} has an unsupported AI Log history policy.")
            continue
        if enforcement.get("enabled") is not True:
            continue
        parents = run_git(
            root,
            ["rev-list", "--parents", "-n", "1", commit],
            "reading AI Log commit parents",
        ).decode("ascii", errors="strict").split()
        if len(parents) > 2 and enforcement.get("exemptMergeCommits") is True:
            continue
        message = run_git(root, ["show", "-s", "--format=%B", commit], "reading AI Log commit trailers").decode(
            "utf-8", errors="replace"
        )
        match = AI_LOG_TRAILER.search(message)
        if not match:
            errors.append(f"Commit {commit[:12]} is missing an AI-Log trailer.")
            continue
        log_id = match.group(1)
        tree_paths = run_git(
            root,
            ["ls-tree", "-r", "--name-only", commit, "--", "evidence/ai-log/members"],
            "locating AI Log commit evidence",
        ).decode("utf-8", errors="replace").splitlines()
        matches = [path for path in tree_paths if path.endswith(f"/commits/{log_id}.json")]
        if len(matches) != 1:
            errors.append(f"Commit {commit[:12]} AI-Log trailer does not resolve to exactly one record.")
            continue
        try:
            record = json.loads(read_revision_file(root, commit, Path(matches[0])).decode("utf-8"))
        except (GuardError, UnicodeDecodeError, json.JSONDecodeError):
            errors.append(f"Commit {commit[:12]} has invalid AI Log commit evidence.")
            continue
        if record.get("ai_log_id") != log_id or record.get("capture_status") not in AI_LOG_CAPTURE_STATUSES:
            errors.append(f"Commit {commit[:12]} has inconsistent AI Log evidence.")


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

    for line_number, line in enumerate(text.splitlines(), start=1):
        if CONFLICT_MARKER.match(line):
            errors.append(f"Unresolved Git conflict marker in {display(relative_path)}:{line_number}")

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
        if is_data_path(relative_path):
            continue
        content = read_workspace_file(root, relative_path)
        if content is None:
            validate_path_policy(relative_path, errors)
            continue
        validate_file_content(root, relative_path, content, errors, validate_links=True)


def validate_staged_scope(root: Path, errors: list[str]) -> None:
    for relative_path in staged_scope_paths(root):
        if is_data_path(relative_path):
            continue
        validate_file_content(root, relative_path, read_index_file(root, relative_path), errors, validate_links=False)


def validate_range_scope(root: Path, value: str, errors: list[str]) -> None:
    paths, head_commit = range_scope_paths(root, value)
    for relative_path in paths:
        if is_data_path(relative_path):
            continue
        content = read_revision_file(root, head_commit, relative_path)
        validate_file_content(root, relative_path, content, errors, validate_links=True)


def validate_workflow_contract(root: Path, errors: list[str]) -> None:
    path = root / ".github/workflows/repository-guard.yml"
    try:
        workflow = path.read_text(encoding="utf-8")
    except OSError as error:
        errors.append(f"Unable to read repository guard workflow: {error}")
        return

    required_fragments = (
        "name: Repository guard",
        "scope:",
        "repository-policy:",
        "repository-guard:",
        "contents: read",
        "actions/checkout@v6",
        "actions/setup-node@v6",
        "actions/setup-python@v6",
        "node --test tests/design/*.mjs",
        "python scripts/ci/validate_repo.py",
        "scripts/ci/changed_scope.py",
        "scripts/ci/validate_data.py",
        "release-candidate:",
        "actions/upload-artifact@v7",
        "pull_request:",
        "workflow_dispatch:",
    )
    for fragment in required_fragments:
        if fragment not in workflow:
            errors.append(f"Repository guard workflow is missing: {fragment}")

    promotion_path = root / ".github/workflows/promote-candidate.yml"
    try:
        promotion = promotion_path.read_text(encoding="utf-8")
    except OSError as error:
        errors.append(f"Unable to read promotion workflow: {error}")
        return
    for fragment in (
        "name: Promote release candidate",
        "workflow_dispatch:",
        "source_run_id:",
        "confirmation:",
        "actions/download-artifact@v6",
        "scripts/ci/release_manifest.py verify",
        "actions/upload-artifact@v7",
    ):
        if fragment not in promotion:
            errors.append(f"Promotion workflow is missing: {fragment}")


def validate_default(root: Path) -> list[str]:
    errors: list[str] = []
    validate_required_paths(root, errors)
    validate_context_artifacts(root, errors)
    validate_repository_settings(root, errors)
    validate_impeccable_policy(root, errors)
    validate_ai_log_policy(root, errors)
    validate_ai_log_records(root, errors)
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
    validate_ai_log_history(root, value, errors)
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
