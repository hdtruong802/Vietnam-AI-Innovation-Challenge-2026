import assert from "node:assert/strict";
import { existsSync } from "node:fs";
import { mkdtemp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import { AuditError, parseArgs, runAudit, validateLocalUrl } from "../../scripts/design/impeccable-audit.mjs";

const invocation = { command: "npx", prefixArgs: [] };

async function temporaryRepository() {
  const root = await mkdtemp(path.join(os.tmpdir(), "impeccable-audit-"));
  await mkdir(path.join(root, "ui"), { recursive: true });
  await writeFile(path.join(root, "ui", "Card.jsx"), "export const Card = () => null;\n", "utf8");
  return root;
}

async function withRepository(action) {
  const root = await temporaryRepository();
  try {
    await action(root);
  } finally {
    await rm(root, { recursive: true, force: true });
  }
}

test("exit 0 with no findings writes an advisory report and raw JSON", async () => {
  await withRepository(async (root) => {
    const result = await runAudit(
      { task: "local-20260717-clean-ui", target: "ui" },
      {
        root,
        npxInvocation: invocation,
        runCommand: async (_command, args) => {
          assert.deepEqual(args.slice(0, 5), ["--yes", "impeccable@3.2.1", "detect", "--json", path.join(root, "ui")]);
          assert.equal(args.includes("--scope"), false);
          assert.equal(args.includes("type,layout"), false);
          return { code: 0, stdout: "[]", stderr: "" };
        },
      },
    );

    const report = await readFile(result.reportPath, "utf8");
    const raw = await readFile(result.rawPath, "utf8");
    assert.equal(result.findingCount, 0);
    assert.match(report, /No findings reported\./);
    assert.equal(raw, "[]\n");
  });
});

test("exit 2 preserves a finding as advisory evidence with rule, severity, file and line", async () => {
  await withRepository(async (root) => {
    const result = await runAudit(
      { task: "local-20260717-finding-ui", target: "ui", scope: "type,layout" },
      {
        root,
        npxInvocation: invocation,
        runCommand: async (_command, args) => {
          assert.equal(args.includes("--scope"), false);
          assert.equal(args.includes("type,layout"), false);
          return {
            code: 2,
            stdout: JSON.stringify([
              {
                antipattern: "tiny-text",
                severity: "warning",
                file: path.join(root, "ui", "Card.jsx"),
                line: 12,
                description: "Text uses a pipe | and a line break\nthat must be escaped.",
              },
            ]),
            stderr: "findings are expected",
          };
        },
      },
    );

    const report = await readFile(result.reportPath, "utf8");
    assert.equal(result.detectorExitCode, 2);
    assert.equal(result.findingCount, 1);
    assert.match(report, /\*\*Scope:\*\* `type,layout`/);
    assert.match(report, /\| warning \| tiny-text \| ui\/Card\.jsx \| 12 \|/);
    assert.match(report, /pipe \\| and a line break that must be escaped/);
  });
});

test("malformed detector JSON fails without writing a report", async () => {
  await withRepository(async (root) => {
    await assert.rejects(
      runAudit(
        { task: "local-20260717-invalid-json", target: "ui" },
        { root, npxInvocation: invocation, runCommand: async () => ({ code: 0, stdout: "not-json", stderr: "" }) },
      ),
      (error) => error instanceof AuditError && error.message === "Detector did not produce valid JSON.",
    );
    assert.equal(existsSync(path.join(root, "docs", "design", "reviews", "local-20260717-invalid-json-impeccable.md")), false);
  });
});

test("unexpected detector exit fails without relaying command stderr", async () => {
  await withRepository(async (root) => {
    await assert.rejects(
      runAudit(
        { task: "local-20260717-exec-error", target: "ui" },
        {
          root,
          npxInvocation: invocation,
          runCommand: async () => ({ code: 1, stdout: "", stderr: "token=must-not-be-relayed" }),
        },
      ),
      (error) => error instanceof AuditError && error.message === "Detector did not complete successfully (exit 1).",
    );
  });
});

test("argument and local URL validation keep the audit scoped", () => {
  assert.throws(() => parseArgs(["--task", "bad task", "--target", "ui"]), AuditError);
  assert.throws(() => parseArgs(["--task", "local-1", "--target", "ui", "--url", "http://localhost:3000"]), AuditError);
  assert.throws(() => validateLocalUrl("https://example.com"), AuditError);
  assert.throws(() => validateLocalUrl("http://localhost:3000/?token=value"), AuditError);
  assert.equal(validateLocalUrl("http://localhost:3000"), "http://localhost:3000/");
});
