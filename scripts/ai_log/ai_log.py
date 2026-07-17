#!/usr/bin/env python3
"""Provider-neutral, prompt-only AI evidence linked to Git commits.

Only explicit local sources registered with ``bind`` are read. Raw sessions,
assistant responses, tool traffic and source paths are never written to Git.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence


SCHEMA_VERSION = 1
ADAPTER_VERSION = "1"
SUPPORTED_TOOLS = ("codex", "claude", "cursor", "antigravity")
HOOK_NAMES = ("pre-commit", "pre-merge-commit", "prepare-commit-msg", "commit-msg", "post-commit")
LOCAL_HOOKS_PATH = ".ai-log/hooks"
MEMBER_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{1,63}$")
PROMPT_ID_PATTERN = re.compile(r"^prompt-[0-9a-f]{24}$")
LOG_ID_PATTERN = re.compile(r"^log-[0-9a-f]{24}$")
TRAILER_PATTERN = re.compile(r"^(AI-Log|AI-Tools|AI-Capture):\s*(.*?)\s*$", re.MULTILINE)
MAX_JSON_BYTES = 10 * 1024 * 1024
PREFIX_CONTEXT_BYTES = 256 * 1024

PRIVATE_KEY = re.compile(
    r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----.*?-----END (?:[A-Z ]+ )?PRIVATE KEY-----",
    re.DOTALL,
)
GITHUB_TOKEN = re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")
API_TOKEN = re.compile(r"\b(?:sk-(?:proj-)?|sk-ant-)[A-Za-z0-9_-]{20,}\b")
WINDOWS_HOME = re.compile(r"(?i)\b[A-Z]:\\Users\\[^\\\s]+")
UNIX_HOME = re.compile(r"/(?:home|Users)/[^/\s]+")
EMAIL = re.compile(r"(?<![\w.+-])[\w.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![\w.-])")
PHONE_OR_ID = re.compile(r"(?<!\d)(?:\+?84\s?)?\d{10,12}(?!\d)")


class AiLogError(RuntimeError):
    """A safe operational error without raw session content."""


@dataclass(frozen=True)
class Candidate:
    tool: str
    text: str
    occurred_at: str
    model: str | None
    workspace: str | None
    session_identity: str
    event_identity: str
    task_record: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def load_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default
    except (OSError, json.JSONDecodeError) as error:
        raise AiLogError(f"Invalid local AI Log state: {path.name}") from error


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def run_git(root: Path, arguments: Sequence[str], *, check: bool = True) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), *arguments],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError as error:
        raise AiLogError("Unable to run Git.") from error
    if check and completed.returncode != 0:
        raise AiLogError("Git command failed while managing AI Log evidence.")
    return completed.stdout.strip()


def find_repo_root(explicit: Path | None = None) -> Path:
    start = (explicit or Path.cwd()).resolve()
    output = run_git(start, ["rev-parse", "--show-toplevel"])
    root = Path(output).resolve()
    if not root.is_dir():
        raise AiLogError("AI Log must run inside a Git worktree.")
    return root


def state_dir(root: Path) -> Path:
    return root / ".ai-log"


def config_path(root: Path) -> Path:
    return state_dir(root) / "config.json"


def pending_path(root: Path) -> Path:
    return state_dir(root) / "pending.json"


def manual_path(root: Path) -> Path:
    return state_dir(root) / "manual-pending.json"


def exclusions_path(root: Path) -> Path:
    return state_dir(root) / "exclusions.json"


def hook_templates_dir(root: Path) -> Path:
    return root / ".githooks"


def local_hooks_dir(root: Path) -> Path:
    return state_dir(root) / "hooks"


def load_config(root: Path) -> dict[str, Any]:
    config = load_json(config_path(root))
    if not isinstance(config, dict):
        raise AiLogError("Run `ai_log.py setup` before collecting prompts.")
    if config.get("schema_version") != SCHEMA_VERSION:
        raise AiLogError("Unsupported local AI Log config version.")
    return config


def canonical_path(value: str | Path) -> str:
    return os.path.normcase(os.path.realpath(os.fspath(value)))


def file_hash(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as error:
        raise AiLogError(f"Unable to read AI Log hook template: {path.name}") from error


def install_local_hooks(root: Path) -> dict[str, str]:
    """Refresh ignored executable wrappers from tracked, reviewable templates."""

    templates = hook_templates_dir(root)
    destination = local_hooks_dir(root)
    destination.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, str] = {}
    for name in HOOK_NAMES:
        source = templates / name
        if not source.is_file():
            raise AiLogError(f"Tracked AI Log hook template is missing: .githooks/{name}")
        target = destination / name
        try:
            target.write_bytes(source.read_bytes())
            target.chmod(target.stat().st_mode | 0o111)
        except OSError as error:
            raise AiLogError(f"Unable to install local AI Log hook: {name}") from error
        manifest[name] = file_hash(source)
    return manifest


def workspace_matches(candidate: str | None, root: Path) -> bool:
    if not candidate:
        return False
    try:
        return canonical_path(candidate) == canonical_path(root)
    except (OSError, ValueError):
        return False


def current_branch(root: Path) -> str:
    branch = run_git(root, ["branch", "--show-current"], check=False)
    return branch or "detached-head"


def current_head(root: Path) -> str | None:
    value = run_git(root, ["rev-parse", "HEAD"], check=False)
    return value if re.fullmatch(r"[0-9a-f]{40,64}", value) else None


def workspace_fingerprint(root: Path) -> str:
    remote = run_git(root, ["config", "--get", "remote.origin.url"], check=False)
    if remote:
        return stable_hash("remote:" + remote.strip().lower())
    roots = run_git(root, ["rev-list", "--max-parents=0", "HEAD"], check=False).splitlines()
    identity = roots[-1] if roots else root.name
    return stable_hash("repository:" + identity)


def normalize_timestamp(value: Any) -> str:
    if isinstance(value, (int, float)):
        seconds = float(value)
        if seconds > 10_000_000_000:
            seconds /= 1000
        return datetime.fromtimestamp(seconds, timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, str) and value.strip():
        text = value.strip()
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        except ValueError:
            pass
    return utc_now()


def timestamp_not_before(value: str, lower_bound: str) -> bool:
    try:
        event = datetime.fromisoformat(value.replace("Z", "+00:00"))
        bound = datetime.fromisoformat(lower_bound.replace("Z", "+00:00"))
        return event >= bound
    except ValueError:
        return True


def nested(mapping: Any, *keys: str) -> Any:
    current = mapping
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def text_from_content(value: Any) -> str | None:
    if isinstance(value, str):
        return value.strip() or None
    if isinstance(value, list):
        parts: list[str] = []
        for item in value:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and str(item.get("type", "")).lower() in {
                "text",
                "input_text",
                "user_text",
            }:
                text = item.get("text") or item.get("content")
                if isinstance(text, str):
                    parts.append(text)
        result = "\n".join(part.strip() for part in parts if part.strip()).strip()
        return result or None
    return None


def context_update(tool: str, item: dict[str, Any], context: dict[str, Any]) -> None:
    payload = item.get("payload") if isinstance(item.get("payload"), dict) else {}
    if item.get("type") == "session_meta":
        context["workspace"] = payload.get("cwd") or payload.get("workspace") or context.get("workspace")
        context["session"] = payload.get("id") or payload.get("session_id") or context.get("session")
    for key in ("cwd", "workspace", "workspaceRoot", "projectPath", "project_path"):
        value = item.get(key)
        if isinstance(value, str) and value:
            context["workspace"] = value
    session = item.get("sessionId") or item.get("session_id")
    if isinstance(session, str) and session:
        context["session"] = session
    model = item.get("model") or payload.get("model")
    if isinstance(model, str) and model:
        context["model"] = model


def extract_candidate(
    tool: str,
    item: dict[str, Any],
    context: dict[str, Any],
    source_identity: str,
    task_record: str,
) -> Candidate | None:
    context_update(tool, item, context)
    payload = item.get("payload") if isinstance(item.get("payload"), dict) else {}
    event_type = str(item.get("type") or item.get("event") or "").lower()
    text: str | None = None

    if tool == "codex":
        if event_type == "event_msg" and str(payload.get("type", "")).lower() == "user_message":
            text = text_from_content(payload.get("message"))
    elif tool == "claude":
        message = item.get("message") if isinstance(item.get("message"), dict) else {}
        if event_type == "user" and str(message.get("role", "user")).lower() == "user":
            text = text_from_content(message.get("content"))
    elif tool in {"cursor", "antigravity"}:
        role = str(item.get("role") or nested(item, "message", "role") or "").lower()
        allowed_types = {"userprompt", "user_prompt", "user-message", "user_message", "user"}
        if event_type in allowed_types and role in {"", "user", "human"}:
            text = text_from_content(
                item.get("prompt")
                or item.get("text")
                or nested(item, "message", "content")
                or item.get("content")
            )

    if not text:
        return None
    timestamp = normalize_timestamp(item.get("timestamp") or item.get("createdAt") or item.get("time"))
    session = str(context.get("session") or source_identity)
    model = item.get("model") or payload.get("model") or context.get("model")
    event_identity = str(item.get("id") or item.get("uuid") or stable_hash(timestamp + "\n" + text))
    return Candidate(
        tool=tool,
        text=text,
        occurred_at=timestamp,
        model=str(model) if isinstance(model, str) and model else None,
        workspace=str(context.get("workspace")) if context.get("workspace") else None,
        session_identity=session,
        event_identity=event_identity,
        task_record=task_record,
    )


def source_files(source: Path) -> list[Path]:
    if source.is_file():
        return [source]
    if not source.is_dir():
        return []
    files = [*source.rglob("*.jsonl"), *source.rglob("*.json")]
    return sorted({path.resolve() for path in files if path.is_file()})


def source_key(path: Path) -> str:
    return stable_hash(canonical_path(path))


def update_context_from_prefix(path: Path, tool: str, context: dict[str, Any]) -> None:
    try:
        with path.open("rb") as handle:
            prefix = handle.read(PREFIX_CONTEXT_BYTES)
    except OSError:
        return
    for raw_line in prefix.splitlines():
        try:
            value = json.loads(raw_line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        if isinstance(value, dict):
            context_update(tool, value, context)


def iter_json_items(value: Any) -> Iterator[dict[str, Any]]:
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                yield item
    elif isinstance(value, dict):
        events = value.get("events")
        if isinstance(events, list):
            yield from (item for item in events if isinstance(item, dict))
        else:
            yield value


def read_source_file(
    path: Path,
    tool: str,
    checkpoint: dict[str, Any],
    task_record: str,
    bound_at: str,
) -> tuple[list[Candidate], dict[str, Any], list[str]]:
    candidates: list[Candidate] = []
    warnings: list[str] = []
    context: dict[str, Any] = {}
    identity = source_key(path)

    if path.suffix.lower() == ".jsonl":
        size = path.stat().st_size
        offset = int(checkpoint.get("offset", 0))
        if offset < 0 or offset > size:
            offset = 0
            warnings.append("source_rotated")
        if offset:
            update_context_from_prefix(path, tool, context)
        try:
            with path.open("rb") as handle:
                handle.seek(offset)
                for raw_line in handle:
                    try:
                        value = json.loads(raw_line.decode("utf-8"))
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        warnings.append("invalid_json_event")
                        continue
                    if not isinstance(value, dict):
                        continue
                    candidate = extract_candidate(tool, value, context, identity, task_record)
                    if candidate and timestamp_not_before(candidate.occurred_at, bound_at):
                        candidates.append(candidate)
        except OSError:
            warnings.append("source_unreadable")
        return candidates, {"offset": size}, sorted(set(warnings))

    if path.suffix.lower() == ".json":
        stat = path.stat()
        signature = f"{stat.st_size}:{stat.st_mtime_ns}"
        if checkpoint.get("signature") == signature:
            return [], checkpoint, []
        if stat.st_size > MAX_JSON_BYTES:
            return [], {"signature": signature}, ["json_source_too_large"]
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            return [], {"signature": signature}, ["invalid_json_source"]
        for item in iter_json_items(value):
            candidate = extract_candidate(tool, item, context, identity, task_record)
            if candidate and timestamp_not_before(candidate.occurred_at, bound_at):
                candidates.append(candidate)
        return candidates, {"signature": signature}, []

    return [], checkpoint, ["unsupported_source_format"]


def sanitize_prompt(text: str, max_characters: int) -> tuple[str, list[str], list[str]]:
    sanitized = text.replace("\x00", "").replace("\r\n", "\n").strip()
    categories: list[str] = []
    warnings: list[str] = []
    substitutions = (
        (PRIVATE_KEY, "<REDACTED_PRIVATE_KEY>", "private_key"),
        (GITHUB_TOKEN, "<REDACTED_GITHUB_TOKEN>", "github_token"),
        (API_TOKEN, "<REDACTED_API_TOKEN>", "api_token"),
        (WINDOWS_HOME, "<USER_HOME>", "absolute_user_path"),
        (UNIX_HOME, "<USER_HOME>", "absolute_user_path"),
        (EMAIL, "<REDACTED_EMAIL>", "email"),
        (PHONE_OR_ID, "<REDACTED_IDENTIFIER>", "phone_or_identifier"),
    )
    for pattern, replacement, category in substitutions:
        sanitized, count = pattern.subn(replacement, sanitized)
        if count:
            categories.append(category)
    if len(sanitized) > max_characters:
        sanitized = "<OMITTED_PROMPT_EXCEEDS_POLICY_LIMIT>"
        categories.append("oversized_prompt")
        warnings.append("oversized_prompt_omitted")
    if categories:
        warnings.append("sensitive_content_redacted")
    if not sanitized:
        sanitized = "<OMITTED_EMPTY_AFTER_SANITIZATION>"
        warnings.append("empty_after_sanitization")
    return sanitized, sorted(set(categories)), sorted(set(warnings))


def prompt_identifier(member: str, candidate: Candidate) -> str:
    material = "\n".join(
        (member, candidate.tool, candidate.session_identity, candidate.event_identity, candidate.text)
    )
    return "prompt-" + stable_hash(material)[:24]


def prompt_record(
    root: Path,
    config: dict[str, Any],
    candidate: Candidate,
    *,
    adapter: str | None = None,
) -> tuple[dict[str, Any], list[str]]:
    member = str(config["member_id"])
    prompt_id = prompt_identifier(member, candidate)
    sanitized, categories, warnings = sanitize_prompt(
        candidate.text, int(config.get("max_prompt_characters", 100000))
    )
    for local_root in {str(root), str(root).replace("\\", "/")}:
        if local_root and local_root in sanitized:
            sanitized = sanitized.replace(local_root, "<REPO_ROOT>")
            categories.append("absolute_repo_path")
            warnings.append("sensitive_content_redacted")
    categories = sorted(set(categories))
    warnings = sorted(set(warnings))
    preview = re.sub(r"\s+", " ", sanitized).strip()[:277]
    if len(re.sub(r"\s+", " ", sanitized).strip()) > 277:
        preview += "..."
    record = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "prompt_event",
        "prompt_id": prompt_id,
        "occurred_at": candidate.occurred_at,
        "captured_at": utc_now(),
        "member_id": member,
        "tool": candidate.tool,
        "event": "UserPrompt",
        "prompt": sanitized,
        "prompt_preview": preview,
        "model": candidate.model,
        "task_record": candidate.task_record,
        "branch": current_branch(root),
        "workspace_fingerprint": workspace_fingerprint(root),
        "source": {
            "session_hash": stable_hash(candidate.session_identity),
            "adapter": adapter or candidate.tool,
            "adapter_version": ADAPTER_VERSION,
        },
        "sanitization": {"redacted": bool(categories), "categories": categories},
        "capture_warnings": warnings,
    }
    return record, warnings


def prompt_record_path(root: Path, member: str, record: dict[str, Any]) -> Path:
    month = str(record["occurred_at"])[:7]
    if not re.fullmatch(r"\d{4}-\d{2}", month):
        month = utc_now()[:7]
    return root / "evidence" / "ai-log" / "members" / member / "prompts" / month / f"{record['prompt_id']}.json"


def write_immutable_record(path: Path, record: dict[str, Any]) -> None:
    if path.exists():
        existing = load_json(path)
        if existing != record:
            # captured_at is allowed to differ when the same source event is seen again.
            comparable_existing = dict(existing) if isinstance(existing, dict) else existing
            comparable_record = dict(record)
            if isinstance(comparable_existing, dict):
                comparable_existing.pop("captured_at", None)
            comparable_record.pop("captured_at", None)
            if comparable_existing != comparable_record:
                raise AiLogError("Immutable AI Log record collision.")
        return
    write_json(path, record)


def relative(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def initial_checkpoints(source: Path, mode: str) -> dict[str, Any]:
    checkpoints: dict[str, Any] = {}
    for path in source_files(source):
        key = source_key(path)
        if mode == "beginning":
            checkpoints[key] = {"offset": 0} if path.suffix.lower() == ".jsonl" else {}
        elif path.suffix.lower() == ".jsonl":
            checkpoints[key] = {"offset": path.stat().st_size}
        else:
            stat = path.stat()
            checkpoints[key] = {"signature": f"{stat.st_size}:{stat.st_mtime_ns}"}
    return checkpoints


def collect_binding(
    root: Path,
    binding: dict[str, Any],
) -> tuple[list[Candidate], dict[str, Any], list[str]]:
    source = Path(str(binding["source"]))
    candidates: list[Candidate] = []
    warnings: list[str] = []
    next_checkpoints = dict(binding.get("checkpoints", {}))
    files = source_files(source)
    if not files:
        return [], next_checkpoints, ["bound_source_missing_or_unsupported"]
    for path in files:
        key = source_key(path)
        file_candidates, checkpoint, file_warnings = read_source_file(
            path,
            str(binding["tool"]),
            dict(binding.get("checkpoints", {}).get(key, {})),
            str(binding.get("task_record") or "unassigned"),
            str(binding.get("bound_at") or utc_now()),
        )
        next_checkpoints[key] = checkpoint
        warnings.extend(file_warnings)
        for candidate in file_candidates:
            if candidate.workspace is None:
                warnings.append("workspace_metadata_missing")
                continue
            if workspace_matches(candidate.workspace, root):
                candidates.append(candidate)
    return candidates, next_checkpoints, sorted(set(warnings))


def stage_paths(root: Path, paths: Iterable[Path]) -> None:
    relatives = sorted({relative(root, path) for path in paths if path.exists()})
    if relatives:
        run_git(root, ["add", "--", *relatives])


def load_exclusions(root: Path) -> set[str]:
    value = load_json(exclusions_path(root), {})
    if not isinstance(value, dict):
        return set()
    return {key for key in value if PROMPT_ID_PATTERN.fullmatch(key)}


def create_pending(root: Path, *, stage: bool, operation: str = "commit") -> dict[str, Any]:
    config = load_config(root)
    existing = load_json(pending_path(root))
    head = current_head(root)
    if isinstance(existing, dict) and existing.get("parent_commit") == head:
        if stage:
            stage_paths(root, [root / path for path in existing.get("evidence_paths", [])])
        return existing

    exclusions = load_exclusions(root)
    prompt_records: list[dict[str, Any]] = []
    evidence_paths: list[Path] = []
    warnings: list[str] = []
    next_checkpoints: dict[str, Any] = {}

    manual = load_json(manual_path(root), [])
    has_manual = isinstance(manual, list) and any(
        isinstance(item, dict) and item.get("record_type") == "prompt_event" for item in manual
    )
    bindings = config.get("bindings", [])
    manual_tools = config.get("manual_tools", [])
    if not bindings and not has_manual:
        warnings.append("manual_prompt_required" if manual_tools else "no_bound_sources")
    for binding in bindings:
        if not isinstance(binding, dict):
            warnings.append("invalid_binding")
            continue
        candidates, checkpoints, binding_warnings = collect_binding(root, binding)
        next_checkpoints[str(binding.get("binding_id"))] = checkpoints
        warnings.extend(binding_warnings)
        for candidate in candidates:
            prompt_id = prompt_identifier(str(config["member_id"]), candidate)
            if prompt_id in exclusions:
                continue
            record, record_warnings = prompt_record(root, config, candidate)
            prompt_records.append(record)
            warnings.extend(record_warnings)

    if isinstance(manual, list):
        for item in manual:
            if isinstance(item, dict) and item.get("record_type") == "prompt_event":
                prompt_records.append(item)
                warnings.extend(item.get("capture_warnings", []))

    unique_records = {str(record["prompt_id"]): record for record in prompt_records}
    for record in unique_records.values():
        path = prompt_record_path(root, str(config["member_id"]), record)
        write_immutable_record(path, record)
        evidence_paths.append(path)

    task_records = sorted(
        {
            str(record.get("task_record") or "unassigned")
            for record in unique_records.values()
        }
        or {str(config.get("active_task") or "unassigned")}
    )
    if "unassigned" in task_records:
        warnings.append("task_record_unassigned")
    tools = sorted({str(record["tool"]) for record in unique_records.values()})
    warnings = sorted(set(str(value) for value in warnings if value))
    if operation in {"merge", "revert"}:
        capture_status = "git_operation"
    elif warnings:
        capture_status = "warning"
    elif any(record.get("source", {}).get("adapter") == "manual" for record in unique_records.values()):
        capture_status = "manual"
    elif unique_records:
        capture_status = "complete"
    else:
        capture_status = "no_new_prompt"

    log_id = "log-" + uuid.uuid4().hex[:24]
    commit_record = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "commit_evidence",
        "ai_log_id": log_id,
        "created_at": utc_now(),
        "member_id": str(config["member_id"]),
        "branch": current_branch(root),
        "parent_commit": head,
        "task_records": task_records,
        "prompt_ids": sorted(unique_records),
        "tools": tools,
        "capture_status": capture_status,
        "warnings": warnings,
        "operation": operation,
        "replaces_ai_log": None,
    }
    commit_path = root / "evidence" / "ai-log" / "members" / str(config["member_id"]) / "commits" / f"{log_id}.json"
    write_json(commit_path, commit_record)
    evidence_paths.append(commit_path)
    pending = {
        "schema_version": SCHEMA_VERSION,
        "ai_log_id": log_id,
        "parent_commit": head,
        "evidence_paths": [relative(root, path) for path in evidence_paths],
        "commit_record_path": relative(root, commit_path),
        "next_checkpoints": next_checkpoints,
    }
    write_json(pending_path(root), pending)
    if stage:
        stage_paths(root, evidence_paths)
    return pending


def update_pending_operation(root: Path, operation: str, replaces: str | None = None) -> dict[str, Any]:
    pending = load_json(pending_path(root))
    if not isinstance(pending, dict):
        pending = create_pending(root, stage=True, operation=operation)
    record_path = root / str(pending["commit_record_path"])
    record = load_json(record_path)
    if not isinstance(record, dict):
        raise AiLogError("Pending commit evidence is missing.")
    record["operation"] = operation
    if operation in {"merge", "revert"}:
        record["capture_status"] = "git_operation"
    record["replaces_ai_log"] = replaces
    write_json(record_path, record)
    stage_paths(root, [record_path])
    return pending


def inspect_source_metadata(source: Path, tool: str, root: Path) -> tuple[list[str], list[str]]:
    """Check parser/workspace metadata without extracting or printing prompt text."""

    warnings: list[str] = []
    errors: list[str] = []
    files = source_files(source)
    if not files:
        return warnings, ["bound source has no supported JSON/JSONL files"]
    matched_workspace = False
    mismatched_workspace = False
    parsed_event = False
    for path in files:
        context: dict[str, Any] = {}
        try:
            if path.suffix.lower() == ".jsonl":
                with path.open("rb") as handle:
                    raw_items = handle.read(PREFIX_CONTEXT_BYTES).splitlines()
                values: Iterable[Any] = (
                    json.loads(raw.decode("utf-8")) for raw in raw_items if raw.strip()
                )
            elif path.suffix.lower() == ".json":
                if path.stat().st_size > MAX_JSON_BYTES:
                    warnings.append("JSON source exceeds the supported readiness-inspection size")
                    continue
                values = iter_json_items(json.loads(path.read_text(encoding="utf-8")))
            else:
                continue
            for value in values:
                if not isinstance(value, dict):
                    continue
                parsed_event = True
                context_update(tool, value, context)
                workspace = context.get("workspace")
                if isinstance(workspace, str) and workspace:
                    if workspace_matches(workspace, root):
                        matched_workspace = True
                    else:
                        mismatched_workspace = True
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            warnings.append("source contains unreadable or invalid JSON data")
    if not parsed_event:
        errors.append("source parser did not recognize any JSON event")
    if not matched_workspace:
        errors.append("source does not expose workspace metadata matching this repository")
    if mismatched_workspace:
        warnings.append("source also contains events for another workspace")
    return sorted(set(warnings)), sorted(set(errors))


def setup_command(root: Path, args: argparse.Namespace) -> int:
    if not MEMBER_PATTERN.fullmatch(args.member):
        raise AiLogError("Member ID must use lowercase letters, digits and hyphens.")
    current_hooks = run_git(root, ["config", "--get", "core.hooksPath"], check=False)
    if current_hooks and current_hooks not in {".githooks", LOCAL_HOOKS_PATH} and not args.force:
        raise AiLogError("core.hooksPath is already set; rerun setup with --force only after reviewing it.")
    existing = load_json(config_path(root), {})
    if (
        isinstance(existing, dict)
        and existing.get("member_id")
        and existing.get("member_id") != args.member
        and not args.force
    ):
        raise AiLogError("This clone is already assigned to another member; use --force only after review.")
    bindings = existing.get("bindings", []) if isinstance(existing, dict) else []
    manual_tools = existing.get("manual_tools", []) if isinstance(existing, dict) else []
    hook_manifest = install_local_hooks(root)
    config = {
        "schema_version": SCHEMA_VERSION,
        "member_id": args.member,
        "active_task": args.task or (existing.get("active_task") if isinstance(existing, dict) else None) or "unassigned",
        "max_prompt_characters": 100000,
        "bindings": bindings,
        "manual_tools": sorted({str(tool) for tool in manual_tools if tool in SUPPORTED_TOOLS}),
        "hook_manifest": hook_manifest,
    }
    write_json(config_path(root), config)
    run_git(root, ["config", "core.hooksPath", LOCAL_HOOKS_PATH])
    print(f"AI Log configured for {args.member}; ignored local hooks were refreshed for this clone.")
    return 0


def bind_command(root: Path, args: argparse.Namespace) -> int:
    config = load_config(root)
    source = Path(args.source).expanduser().resolve()
    if not source.exists():
        raise AiLogError("Bound source does not exist.")
    task_record = args.task or config.get("active_task") or "unassigned"
    binding_id = "binding-" + stable_hash(args.tool + "\n" + canonical_path(source))[:20]
    previous = next(
        (
            item
            for item in config.get("bindings", [])
            if isinstance(item, dict) and item.get("binding_id") == binding_id
        ),
        None,
    )
    binding = {
        "binding_id": binding_id,
        "tool": args.tool,
        "source": str(source),
        "task_record": str(task_record),
        "bound_at": previous.get("bound_at") if previous else utc_now(),
        "checkpoints": previous.get("checkpoints", {}) if previous else initial_checkpoints(source, args.from_mode),
    }
    bindings = [
        item
        for item in config.get("bindings", [])
        if not isinstance(item, dict) or item.get("binding_id") != binding_id
    ]
    bindings.append(binding)
    config["bindings"] = bindings
    config["manual_tools"] = [tool for tool in config.get("manual_tools", []) if tool != args.tool]
    config["active_task"] = str(task_record)
    write_json(config_path(root), config)
    action = "Refreshed" if previous else "Bound"
    print(f"{action} {args.tool} source {binding_id}; raw path remains in ignored local state only.")
    return 0


def doctor_command(root: Path, args: argparse.Namespace) -> int:
    config = load_config(root)
    warnings: list[str] = []
    errors: list[str] = []
    member = str(config.get("member_id") or "")
    task = str(config.get("active_task") or "")
    if not MEMBER_PATTERN.fullmatch(member):
        errors.append("member configuration is missing or invalid")
    if not task or task == "unassigned":
        errors.append("active Task Record is unassigned")

    expected_manifest: dict[str, str] = {}
    for name in HOOK_NAMES:
        template = hook_templates_dir(root) / name
        installed = local_hooks_dir(root) / name
        if not template.is_file() or not installed.is_file():
            errors.append(f"hook {name} is missing")
            continue
        expected = file_hash(template)
        expected_manifest[name] = expected
        if file_hash(installed) != expected:
            errors.append(f"hook {name} is stale; rerun onboard")
        if os.name != "nt" and not os.access(installed, os.X_OK):
            errors.append(f"hook {name} is not executable")
    if config.get("hook_manifest") != expected_manifest:
        errors.append("hook manifest is stale; rerun onboard")
    if run_git(root, ["config", "--get", "core.hooksPath"], check=False) != LOCAL_HOOKS_PATH:
        errors.append(f"core.hooksPath must be {LOCAL_HOOKS_PATH}")

    bindings = config.get("bindings", [])
    manual_tools = config.get("manual_tools", [])
    if not bindings and not manual_tools:
        errors.append("no explicit source binding or manual tool is configured")
    for binding in bindings:
        if not isinstance(binding, dict) or binding.get("tool") not in SUPPORTED_TOOLS:
            errors.append("a source binding is malformed")
            continue
        source = Path(str(binding.get("source") or ""))
        if not source.exists():
            errors.append(f"{binding.get('tool')} source is missing")
            continue
        source_warnings, source_errors = inspect_source_metadata(source, str(binding["tool"]), root)
        warnings.extend(f"{binding['tool']}: {message}" for message in source_warnings)
        errors.extend(f"{binding['tool']}: {message}" for message in source_errors)
    for tool in manual_tools:
        if tool not in SUPPORTED_TOOLS:
            errors.append("manual tool configuration is malformed")

    print(f"AI Log doctor: member={member or 'missing'} task={task or 'missing'}")
    print(f"Bindings: {len(bindings)}; manual tools: {len(manual_tools)}; hooks: {len(expected_manifest)}/{len(HOOK_NAMES)}")
    for message in warnings:
        print(f"WARNING: {message}")
    for message in errors:
        print(f"ERROR: {message}")
    if errors or (args.strict and warnings):
        return 1
    print("AI Log readiness: PASS")
    return 0


def onboard_command(root: Path, args: argparse.Namespace) -> int:
    setup_command(
        root,
        argparse.Namespace(member=args.member, task=args.task, force=args.force),
    )
    if args.manual:
        config = load_config(root)
        config["manual_tools"] = sorted({*config.get("manual_tools", []), args.tool})
        config["active_task"] = args.task
        write_json(config_path(root), config)
        print(f"Configured {args.tool} for prompt intake through `record --stdin`.")
    else:
        bind_command(
            root,
            argparse.Namespace(
                tool=args.tool,
                source=args.source,
                task=args.task,
                from_mode=args.from_mode,
            ),
        )
    return doctor_command(root, argparse.Namespace(strict=True))


def set_task_command(root: Path, args: argparse.Namespace) -> int:
    config = load_config(root)
    config["active_task"] = args.task
    write_json(config_path(root), config)
    print(f"Active Task Record: {args.task}")
    return 0


def status_command(root: Path, _args: argparse.Namespace) -> int:
    config = load_config(root)
    print(f"Member: {config['member_id']}")
    print(f"Task Record: {config.get('active_task', 'unassigned')}")
    print(f"Hooks: {run_git(root, ['config', '--get', 'core.hooksPath'], check=False) or 'not configured'}")
    exclusions = load_exclusions(root)
    total = 0
    for binding in config.get("bindings", []):
        candidates, _, warnings = collect_binding(root, binding)
        visible = []
        for candidate in candidates:
            prompt_id = prompt_identifier(str(config["member_id"]), candidate)
            if prompt_id not in exclusions:
                safe_text, _, _ = sanitize_prompt(
                    candidate.text, int(config.get("max_prompt_characters", 100000))
                )
                for local_root in {str(root), str(root).replace("\\", "/")}:
                    safe_text = safe_text.replace(local_root, "<REPO_ROOT>")
                visible.append((prompt_id, re.sub(r"\s+", " ", safe_text)[:120]))
        total += len(visible)
        print(
            f"- {binding['binding_id']} tool={binding['tool']} task={binding.get('task_record', 'unassigned')} "
            f"candidates={len(visible)} warnings={','.join(warnings) or 'none'}"
        )
        for prompt_id, preview in visible:
            print(f"  {prompt_id}: {preview}")
    print(f"New prompt candidates: {total}")
    return 0


def collect_command(root: Path, _args: argparse.Namespace) -> int:
    pending = create_pending(root, stage=False)
    record = load_json(root / str(pending["commit_record_path"]), {})
    print(
        f"Prepared {pending['ai_log_id']}: {len(record.get('prompt_ids', []))} prompt(s), "
        f"status={record.get('capture_status', 'warning')}."
    )
    return 0


def exclude_command(root: Path, args: argparse.Namespace) -> int:
    if not PROMPT_ID_PATTERN.fullmatch(args.prompt_id):
        raise AiLogError("Invalid prompt ID.")
    exclusions = load_json(exclusions_path(root), {})
    if not isinstance(exclusions, dict):
        exclusions = {}
    exclusions[args.prompt_id] = {"reason": args.reason, "excluded_at": utc_now()}
    write_json(exclusions_path(root), exclusions)
    print(f"Excluded {args.prompt_id} from future capture in this local state.")
    return 0


def manual_record_command(root: Path, args: argparse.Namespace) -> int:
    config = load_config(root)
    if not args.stdin:
        raise AiLogError("Manual prompt input is accepted only through --stdin.")
    text = sys.stdin.read()
    if not text.strip():
        raise AiLogError("No prompt was provided on stdin.")
    nonce = uuid.uuid4().hex
    candidate = Candidate(
        tool=args.tool,
        text=text,
        occurred_at=utc_now(),
        model=args.model,
        workspace=str(root),
        session_identity="manual:" + nonce,
        event_identity=nonce,
        task_record=args.task or str(config.get("active_task") or "unassigned"),
    )
    record, _ = prompt_record(root, config, candidate, adapter="manual")
    pending = load_json(manual_path(root), [])
    if not isinstance(pending, list):
        pending = []
    pending.append(record)
    write_json(manual_path(root), pending)
    print(f"Recorded manual prompt candidate {record['prompt_id']}; it will be staged by the next commit hook.")
    return 0


def parse_trailers(message: str) -> dict[str, str]:
    return {key: value for key, value in TRAILER_PATTERN.findall(message)}


def find_commit_record(root: Path, log_id: str) -> Path | None:
    matches = list((root / "evidence" / "ai-log" / "members").glob(f"*/commits/{log_id}.json"))
    return matches[0] if len(matches) == 1 else None


def prepare_commit_message(root: Path, message_path: Path, source: str | None, source_sha: str | None) -> int:
    # `pre-commit` has already created and staged the immutable evidence. Git may
    # hold the index lock while this hook runs, so invoking `git add` here can
    # abort an otherwise valid commit on Windows and other platforms.
    pending = load_json(pending_path(root))
    if not isinstance(pending, dict) or pending.get("parent_commit") != current_head(root):
        raise AiLogError("AI Log pre-commit evidence is missing; commit without bypassing pre-commit.")
    message = message_path.read_text(encoding="utf-8")
    record = load_json(root / str(pending["commit_record_path"]), {})
    filtered_lines = [line for line in message.rstrip().splitlines() if not re.match(r"^AI-(?:Log|Tools|Capture):", line)]
    while filtered_lines and not filtered_lines[-1].strip():
        filtered_lines.pop()
    tools = ",".join(record.get("tools", [])) or "none"
    trailers = [
        f"AI-Log: {record['ai_log_id']}",
        f"AI-Tools: {tools}",
        f"AI-Capture: {record['capture_status']}",
    ]
    message_path.write_text("\n".join(filtered_lines + ["", *trailers]) + "\n", encoding="utf-8")
    return 0


def validate_commit_message(root: Path, message_path: Path) -> int:
    trailers = parse_trailers(message_path.read_text(encoding="utf-8"))
    log_id = trailers.get("AI-Log", "")
    if not LOG_ID_PATTERN.fullmatch(log_id):
        print("AI Log error: commit message is missing a valid AI-Log trailer.", file=sys.stderr)
        return 1
    path = find_commit_record(root, log_id)
    if path is None:
        print("AI Log error: commit trailer does not resolve to one evidence record.", file=sys.stderr)
        return 1
    record = load_json(path, {})
    if record.get("ai_log_id") != log_id or trailers.get("AI-Capture") != record.get("capture_status"):
        print("AI Log error: commit trailers and evidence record disagree.", file=sys.stderr)
        return 1
    return 0


def finalize_commit(root: Path) -> int:
    pending = load_json(pending_path(root))
    if not isinstance(pending, dict):
        return 0
    config = load_config(root)
    next_checkpoints = pending.get("next_checkpoints", {})
    for binding in config.get("bindings", []):
        binding_id = str(binding.get("binding_id"))
        if binding_id in next_checkpoints:
            binding["checkpoints"] = next_checkpoints[binding_id]
    write_json(config_path(root), config)
    pending_path(root).unlink(missing_ok=True)
    manual_path(root).unlink(missing_ok=True)
    return 0


def hook_command(root: Path, args: argparse.Namespace) -> int:
    if args.hook_name == "pre-commit":
        pending = create_pending(root, stage=True, operation=args.operation)
        record = load_json(root / str(pending["commit_record_path"]), {})
        if record.get("capture_status") == "warning":
            print(
                "AI Log warning: prompt capture is incomplete; a warning record was staged and commit may continue.",
                file=sys.stderr,
            )
        return 0
    if args.hook_name == "prepare-commit-msg":
        if not args.hook_args:
            raise AiLogError("prepare-commit-msg requires the commit message path.")
        return prepare_commit_message(
            root,
            Path(args.hook_args[0]),
            args.hook_args[1] if len(args.hook_args) > 1 else None,
            args.hook_args[2] if len(args.hook_args) > 2 else None,
        )
    if args.hook_name == "commit-msg":
        if not args.hook_args:
            raise AiLogError("commit-msg requires the commit message path.")
        return validate_commit_message(root, Path(args.hook_args[0]))
    if args.hook_name == "post-commit":
        return finalize_commit(root)
    raise AiLogError("Unsupported AI Log hook.")


def git_log_records(root: Path, git_range: str | None) -> list[dict[str, str]]:
    arguments = ["log"]
    if git_range:
        arguments.append(git_range)
    else:
        arguments.append("--all")
    arguments.append("--format=%H%x1f%aI%x1f%B%x1e")
    output = run_git(root, arguments, check=False)
    records: list[dict[str, str]] = []
    for chunk in output.split("\x1e"):
        chunk = chunk.strip("\r\n")
        if not chunk:
            continue
        parts = chunk.split("\x1f", 2)
        if len(parts) != 3:
            continue
        commit, committed_at, message = parts
        records.append({"commit": commit, "committed_at": committed_at, "message": message})
    return records


def build_index_command(root: Path, args: argparse.Namespace) -> int:
    prompt_records: dict[str, dict[str, Any]] = {}
    for path in (root / "evidence" / "ai-log" / "members").glob("*/prompts/*/*.json"):
        record = load_json(path, {})
        if isinstance(record, dict) and PROMPT_ID_PATTERN.fullmatch(str(record.get("prompt_id", ""))):
            prompt_records[str(record["prompt_id"])] = record
    commit_records: dict[str, dict[str, Any]] = {}
    for path in (root / "evidence" / "ai-log" / "members").glob("*/commits/*.json"):
        record = load_json(path, {})
        if isinstance(record, dict) and LOG_ID_PATTERN.fullmatch(str(record.get("ai_log_id", ""))):
            commit_records[str(record["ai_log_id"])] = record

    entries: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    for commit in git_log_records(root, args.git_range):
        trailers = parse_trailers(commit["message"])
        log_id = trailers.get("AI-Log")
        record = commit_records.get(str(log_id))
        if not record:
            continue
        if not record.get("prompt_ids"):
            gaps.append(
                {
                    "commit": commit["commit"],
                    "ai_log_id": log_id,
                    "capture_status": record.get("capture_status"),
                    "warnings": record.get("warnings", []),
                }
            )
        for prompt_id in record.get("prompt_ids", []):
            prompt = prompt_records.get(prompt_id)
            if not prompt:
                continue
            entries.append(
                {
                    "time": prompt.get("occurred_at"),
                    "tool": prompt.get("tool"),
                    "event": prompt.get("event"),
                    "prompt": prompt.get("prompt"),
                    "prompt_preview": prompt.get("prompt_preview"),
                    "model": prompt.get("model"),
                    "member": prompt.get("member_id"),
                    "branch": record.get("branch"),
                    "commit": commit["commit"],
                    "task_record": prompt.get("task_record"),
                    "ai_log_id": log_id,
                    "capture_status": record.get("capture_status"),
                }
            )
    index = {"schema_version": 1, "generated_at": utc_now(), "entries": entries, "gaps": gaps}
    output = Path(args.output) if args.output else state_dir(root) / "index.json"
    if not output.is_absolute():
        output = root / output
    write_json(output, index)
    print(f"AI Log index written to {output}; it remains local unless explicitly moved into tracked scope.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, help=argparse.SUPPRESS)
    commands = parser.add_subparsers(dest="command", required=True)

    setup = commands.add_parser("setup", help="configure local member state and shared Git hooks")
    setup.add_argument("--member", required=True)
    setup.add_argument("--task")
    setup.add_argument("--force", action="store_true")

    onboard = commands.add_parser("onboard", help="configure one member, source/manual mode and local hooks")
    onboard.add_argument("--member", required=True)
    onboard.add_argument("--task", required=True)
    onboard.add_argument("--tool", required=True, choices=SUPPORTED_TOOLS)
    source_mode = onboard.add_mutually_exclusive_group(required=True)
    source_mode.add_argument("--source")
    source_mode.add_argument("--manual", action="store_true")
    onboard.add_argument("--from", dest="from_mode", choices=("now", "beginning"), default="now")
    onboard.add_argument("--force", action="store_true")

    bind = commands.add_parser("bind", help="bind one explicit coding-agent source")
    bind.add_argument("--tool", required=True, choices=SUPPORTED_TOOLS)
    bind.add_argument("--source", required=True)
    bind.add_argument("--task")
    bind.add_argument("--from", dest="from_mode", choices=("now", "beginning"), default="now")

    task = commands.add_parser("set-task", help="set the active Task Record for new manual entries")
    task.add_argument("--task", required=True)
    doctor = commands.add_parser("doctor", help="check local AI Log readiness without printing prompts")
    doctor.add_argument("--strict", action="store_true")
    commands.add_parser("status", help="show local bindings and new prompt candidates")
    commands.add_parser("collect", help="prepare prompt and commit evidence without staging it")

    exclude = commands.add_parser("exclude", help="exclude a local prompt candidate")
    exclude.add_argument("--prompt-id", required=True)
    exclude.add_argument("--reason", required=True)

    record = commands.add_parser("record", help="record a manual prompt fallback")
    record.add_argument("--tool", required=True, choices=SUPPORTED_TOOLS)
    record.add_argument("--stdin", action="store_true")
    record.add_argument("--task")
    record.add_argument("--model")

    index = commands.add_parser("build-index", help="build a local dashboard-ready JSON index")
    index.add_argument("--range", dest="git_range")
    index.add_argument("--output")

    hook = commands.add_parser("hook", help=argparse.SUPPRESS)
    hook.add_argument("hook_name", choices=("pre-commit", "prepare-commit-msg", "commit-msg", "post-commit"))
    hook.add_argument("--operation", choices=("commit", "merge", "revert", "amend"), default="commit")
    hook.add_argument("hook_args", nargs="*")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        root = find_repo_root(args.root)
        handlers = {
            "onboard": onboard_command,
            "setup": setup_command,
            "bind": bind_command,
            "set-task": set_task_command,
            "doctor": doctor_command,
            "status": status_command,
            "collect": collect_command,
            "exclude": exclude_command,
            "record": manual_record_command,
            "build-index": build_index_command,
            "hook": hook_command,
        }
        return handlers[args.command](root, args)
    except AiLogError as error:
        print(f"AI Log error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
