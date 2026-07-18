"""Standard-library tests for prompt-only, multi-agent AI Log evidence."""

from __future__ import annotations

import argparse
import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "ai_log" / "ai_log.py"
SPEC = importlib.util.spec_from_file_location("ai_log", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load AI Log module.")
ai_log = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ai_log
SPEC.loader.exec_module(ai_log)


class AdapterContractTests(unittest.TestCase):
    def test_all_adapters_extract_only_user_prompt_events(self) -> None:
        workspace = str(Path.cwd())
        cases = {
            "codex": [
                {"type": "session_meta", "payload": {"id": "c1", "cwd": workspace}},
                {"type": "response_item", "payload": {"type": "message", "role": "assistant", "content": "no"}},
                {"type": "event_msg", "timestamp": "2026-07-17T01:00:00Z", "payload": {"type": "user_message", "message": "codex prompt"}},
                {"type": "event_msg", "payload": {"type": "agent_message", "message": "no"}},
            ],
            "claude": [
                {"type": "assistant", "cwd": workspace, "message": {"role": "assistant", "content": "no"}},
                {"type": "user", "cwd": workspace, "sessionId": "cl1", "message": {"role": "user", "content": [{"type": "text", "text": "claude prompt"}]}},
                {"type": "tool", "cwd": workspace, "message": {"role": "user", "content": "no"}},
            ],
            "cursor": [
                {"event": "ToolOutput", "role": "tool", "workspace": workspace, "text": "no"},
                {"event": "UserPrompt", "role": "user", "workspace": workspace, "sessionId": "cu1", "prompt": "cursor prompt"},
            ],
            "antigravity": [
                {"type": "assistant", "role": "assistant", "projectPath": workspace, "text": "no"},
                {"type": "user_message", "role": "human", "projectPath": workspace, "session_id": "a1", "content": "antigravity prompt"},
            ],
        }

        for tool, events in cases.items():
            context: dict[str, object] = {}
            extracted = [
                candidate
                for event in events
                if (candidate := ai_log.extract_candidate(tool, event, context, "source", "local-task"))
            ]
            self.assertEqual(1, len(extracted), tool)
            self.assertEqual(f"{tool} prompt", extracted[0].text)
            self.assertEqual(workspace, extracted[0].workspace)

    def test_sanitizer_redacts_sensitive_values_and_user_paths(self) -> None:
        token = "ghp_" + "a" * 28
        prompt = (
            f"Use {token} for <person@example.test> at C:\\Users\\private-user\\repo "
            "with citizen 012345678901"
        )

        sanitized, categories, warnings = ai_log.sanitize_prompt(prompt, 100000)

        self.assertNotIn(token, sanitized)
        self.assertNotIn("person@example.test", sanitized)
        self.assertNotIn("private-user", sanitized)
        self.assertNotIn("012345678901", sanitized)
        self.assertIn("github_token", categories)
        self.assertIn("sensitive_content_redacted", warnings)


class TemporaryAiLogRepository(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.git("init")
        self.git("config", "user.email", "ai-log@example.test")
        self.git("config", "user.name", "AI Log Test")
        (self.root / ".gitignore").write_text(".ai-log/\nsession.jsonl\n", encoding="utf-8")
        (self.root / "base.txt").write_text("base\n", encoding="utf-8")
        self.git("add", ".gitignore", "base.txt")
        self.git("commit", "-m", "base")
        (self.root / ".githooks").mkdir()
        repository_root = SCRIPT_PATH.parents[2]
        for hook_name in ai_log.HOOK_NAMES:
            shutil.copy2(repository_root / ".githooks" / hook_name, self.root / ".githooks" / hook_name)

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
            encoding="utf-8",
        )
        return completed.stdout.strip()

    def setup_and_bind(self, events: list[dict[str, object]]) -> Path:
        setup_args = argparse.Namespace(member="member-1", task="local-test", force=False)
        ai_log.setup_command(self.root, setup_args)
        source = self.root / "session.jsonl"
        source.write_text("".join(json.dumps(event) + "\n" for event in events), encoding="utf-8")
        bind_args = argparse.Namespace(tool="codex", source=str(source), task="local-test", from_mode="beginning")
        ai_log.bind_command(self.root, bind_args)
        return source

    def install_cli_script(self) -> None:
        target = self.root / "scripts" / "ai_log" / "ai_log.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SCRIPT_PATH, target)

    def test_onboard_is_idempotent_and_doctor_strict(self) -> None:
        source = self.root / "session.jsonl"
        source.write_text(
            json.dumps({"type": "session_meta", "payload": {"id": "one", "cwd": str(self.root)}})
            + "\n",
            encoding="utf-8",
        )
        args = argparse.Namespace(
            member="member-1",
            task="local-onboard",
            tool="codex",
            source=str(source),
            manual=False,
            from_mode="beginning",
            force=False,
        )

        self.assertEqual(0, ai_log.onboard_command(self.root, args))
        first = ai_log.load_config(self.root)
        first_checkpoints = first["bindings"][0]["checkpoints"]
        self.assertEqual(ai_log.LOCAL_HOOKS_PATH, self.git("config", "--get", "core.hooksPath"))
        self.assertEqual(0, ai_log.doctor_command(self.root, argparse.Namespace(strict=True)))

        self.assertEqual(0, ai_log.onboard_command(self.root, args))
        second = ai_log.load_config(self.root)
        self.assertEqual(first_checkpoints, second["bindings"][0]["checkpoints"])
        self.assertEqual(1, len(second["bindings"]))

    def test_hooked_commit_collects_prompt_without_push(self) -> None:
        self.install_cli_script()
        source = self.root / "session.jsonl"
        source.write_text(
            "".join(
                json.dumps(event) + "\n"
                for event in [
                    {"type": "session_meta", "payload": {"id": "hook", "cwd": str(self.root)}},
                    {
                        "type": "event_msg",
                        "timestamp": "2026-07-17T01:00:00Z",
                        "payload": {"type": "user_message", "message": "Implement the current repository task"},
                    },
                ]
            ),
            encoding="utf-8",
        )
        args = argparse.Namespace(
            member="member-1",
            task="local-hook",
            tool="codex",
            source=str(source),
            manual=False,
            from_mode="beginning",
            force=False,
        )
        self.assertEqual(0, ai_log.onboard_command(self.root, args))
        (self.root / "base.txt").write_text("changed\n", encoding="utf-8")
        self.git("add", "base.txt")

        self.git("commit", "-m", "test: commit with AI evidence")

        message = self.git("show", "-s", "--format=%B", "HEAD")
        self.assertRegex(message, r"AI-Log: log-[0-9a-f]{24}")
        self.assertEqual("", self.git("remote"))
        self.assertEqual(1, len(list((self.root / "evidence" / "ai-log" / "members" / "member-1").glob("commits/*.json"))))

    def test_manual_onboard_warns_when_prompt_was_not_recorded(self) -> None:
        args = argparse.Namespace(
            member="member-2",
            task="local-manual-onboard",
            tool="cursor",
            source=None,
            manual=True,
            from_mode="now",
            force=False,
        )
        self.assertEqual(0, ai_log.onboard_command(self.root, args))
        pending = ai_log.create_pending(self.root, stage=False)
        record = ai_log.load_json(self.root / pending["commit_record_path"])
        self.assertEqual("warning", record["capture_status"])
        self.assertIn("manual_prompt_required", record["warnings"])

    def test_doctor_rejects_source_without_matching_workspace(self) -> None:
        source = self.root / "session.jsonl"
        source.write_text(
            json.dumps({"event": "UserPrompt", "workspace": str(self.root / "other"), "prompt": "repo task"})
            + "\n",
            encoding="utf-8",
        )
        args = argparse.Namespace(
            member="member-4",
            task="local-bad-source",
            tool="cursor",
            source=str(source),
            manual=False,
            from_mode="beginning",
            force=False,
        )
        self.assertEqual(1, ai_log.onboard_command(self.root, args))

    def test_two_members_write_separate_evidence_namespaces(self) -> None:
        for member, prompt_text in (("member-1", "First member prompt"), ("member-2", "Second member prompt")):
            setup_args = argparse.Namespace(
                member=member,
                task=f"local-{member}",
                force=member == "member-2",
            )
            ai_log.setup_command(self.root, setup_args)
            record_args = argparse.Namespace(tool="claude", stdin=True, task=None, model=None)
            with mock.patch("sys.stdin", io.StringIO(prompt_text)):
                ai_log.manual_record_command(self.root, record_args)
            ai_log.create_pending(self.root, stage=False)
            ai_log.finalize_commit(self.root)

        member_root = self.root / "evidence" / "ai-log" / "members"
        self.assertEqual(1, len(list((member_root / "member-1").glob("prompts/*/*.json"))))
        self.assertEqual(1, len(list((member_root / "member-2").glob("prompts/*/*.json"))))
        self.assertEqual(1, len(list((member_root / "member-1").glob("commits/*.json"))))
        self.assertEqual(1, len(list((member_root / "member-2").glob("commits/*.json"))))

    def test_collect_commit_trailers_and_dashboard_index(self) -> None:
        events = [
            {"type": "session_meta", "payload": {"id": "session-1", "cwd": str(self.root)}},
            {"type": "event_msg", "payload": {"type": "user_message", "message": "Add the repository guard"}},
            {"type": "event_msg", "payload": {"type": "agent_message", "message": "assistant output must not be stored"}},
        ]
        self.setup_and_bind(events)

        pending = ai_log.create_pending(self.root, stage=True)
        commit_record = ai_log.load_json(self.root / pending["commit_record_path"])
        self.assertEqual("complete", commit_record["capture_status"])
        self.assertEqual(1, len(commit_record["prompt_ids"]))

        prompt_paths = list((self.root / "evidence" / "ai-log" / "members").glob("*/prompts/*/*.json"))
        self.assertEqual(1, len(prompt_paths))
        prompt = ai_log.load_json(prompt_paths[0])
        self.assertEqual("UserPrompt", prompt["event"])
        self.assertEqual("Add the repository guard", prompt["prompt"])
        self.assertNotIn("assistant output", json.dumps(prompt))
        self.assertNotIn(str(self.root), json.dumps(prompt))

        message = self.root / "COMMIT_MESSAGE"
        message.write_text("feat: add guarded prompt evidence\n", encoding="utf-8")
        ai_log.prepare_commit_message(self.root, message, None, None)
        self.assertEqual(0, ai_log.validate_commit_message(self.root, message))
        self.git("config", "--unset", "core.hooksPath")
        self.git("commit", "-F", str(message))
        ai_log.finalize_commit(self.root)

        next_pending = ai_log.create_pending(self.root, stage=False)
        next_record = ai_log.load_json(self.root / next_pending["commit_record_path"])
        self.assertEqual("no_new_prompt", next_record["capture_status"])

        output = self.root / ".ai-log" / "test-index.json"
        args = argparse.Namespace(git_range=None, output=str(output))
        ai_log.build_index_command(self.root, args)
        index = ai_log.load_json(output)
        self.assertEqual(1, len(index["entries"]))
        self.assertEqual(self.git("rev-parse", "HEAD"), index["entries"][0]["commit"])
        self.assertEqual("codex", index["entries"][0]["tool"])

    def test_prepare_commit_message_reuses_staged_evidence_without_restaging(self) -> None:
        events = [
            {"type": "session_meta", "payload": {"id": "session-prepare", "cwd": str(self.root)}},
            {"type": "event_msg", "payload": {"type": "user_message", "message": "Commit the backend task"}},
        ]
        self.setup_and_bind(events)
        ai_log.create_pending(self.root, stage=True)
        message = self.root / "COMMIT_MESSAGE"
        message.write_text("feat: guarded commit\n", encoding="utf-8")

        with mock.patch.object(ai_log, "stage_paths") as stage_paths:
            self.assertEqual(0, ai_log.prepare_commit_message(self.root, message, None, None))

        stage_paths.assert_not_called()
        self.assertEqual(0, ai_log.validate_commit_message(self.root, message))

    def test_missing_workspace_creates_warning_without_committing_prompt(self) -> None:
        events = [
            {"type": "event_msg", "payload": {"type": "user_message", "message": "prompt without workspace"}}
        ]
        self.setup_and_bind(events)

        pending = ai_log.create_pending(self.root, stage=False)
        record = ai_log.load_json(self.root / pending["commit_record_path"])

        self.assertEqual("warning", record["capture_status"])
        self.assertEqual([], record["prompt_ids"])
        self.assertIn("workspace_metadata_missing", record["warnings"])
        self.assertFalse(list((self.root / "evidence" / "ai-log" / "members").glob("*/prompts/*/*.json")))

    def test_invalid_adapter_event_warns_and_git_operation_metadata_is_explicit(self) -> None:
        setup_args = argparse.Namespace(member="member-3", task="local-operation", force=False)
        ai_log.setup_command(self.root, setup_args)
        source = self.root / "session.jsonl"
        source.write_text("{invalid-json}\n", encoding="utf-8")
        bind_args = argparse.Namespace(
            tool="cursor", source=str(source), task="local-operation", from_mode="beginning"
        )
        ai_log.bind_command(self.root, bind_args)

        pending = ai_log.create_pending(self.root, stage=False)
        warning_record = ai_log.load_json(self.root / pending["commit_record_path"])
        self.assertEqual("warning", warning_record["capture_status"])
        self.assertIn("invalid_json_event", warning_record["warnings"])

        replacement = "log-" + "d" * 24
        updated = ai_log.update_pending_operation(self.root, "amend", replacement)
        amend_record = ai_log.load_json(self.root / updated["commit_record_path"])
        self.assertEqual("amend", amend_record["operation"])
        self.assertEqual(replacement, amend_record["replaces_ai_log"])

        ai_log.update_pending_operation(self.root, "merge")
        merge_record = ai_log.load_json(self.root / updated["commit_record_path"])
        self.assertEqual("merge", merge_record["operation"])
        self.assertEqual("git_operation", merge_record["capture_status"])

    def test_manual_stdin_fallback_stores_only_sanitized_prompt(self) -> None:
        setup_args = argparse.Namespace(member="member-2", task="local-manual", force=False)
        ai_log.setup_command(self.root, setup_args)
        args = argparse.Namespace(tool="antigravity", stdin=True, task=None, model=None)
        token = "sk-proj-" + "b" * 28
        with mock.patch("sys.stdin", io.StringIO(f"Implement feature using {token}")):
            ai_log.manual_record_command(self.root, args)

        pending = ai_log.create_pending(self.root, stage=False)
        commit_record = ai_log.load_json(self.root / pending["commit_record_path"])
        prompt_path = next((self.root / "evidence" / "ai-log" / "members").glob("*/prompts/*/*.json"))
        prompt = ai_log.load_json(prompt_path)

        self.assertEqual("warning", commit_record["capture_status"])
        self.assertEqual("manual", prompt["source"]["adapter"])
        self.assertNotIn(token, prompt["prompt"])
        self.assertIn("<REDACTED_API_TOKEN>", prompt["prompt"])


if __name__ == "__main__":
    unittest.main()
