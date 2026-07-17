#!/usr/bin/env node
/**
 * Run a portable, advisory Impeccable audit without adding a project dependency.
 *
 * The detector writes raw JSON to an ignored directory and a compact Markdown
 * report that can be referenced from a Task Record. The wrapper intentionally
 * does not invoke native skills, hooks, MCP, a shell, or a browser extension.
 */

import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { mkdir, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const PACKAGE_SPEC = "impeccable@3.2.1";
const PROJECT_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const TASK_ID_PATTERN = /^[A-Za-z0-9][A-Za-z0-9._-]*$/;
const SCOPE_PATTERN = /^[a-z][a-z-]*(?:,[a-z][a-z-]*)*$/;

const USAGE = `Usage:
  node scripts/design/impeccable-audit.mjs --task <task-id> --target <ui-path> [--scope type,layout]
  node scripts/design/impeccable-audit.mjs --task <task-id> --url <local-url> [--scope type,layout]

Runs impeccable@3.2.1 in local advisory mode and writes:
  docs/design/reviews/<task-id>-impeccable.md
  .impeccable/audits/<task-id>-impeccable.json (ignored)`;

export class AuditError extends Error {}

function takeValue(argv, index, option) {
  const value = argv[index + 1];
  if (!value || value.startsWith("--")) {
    throw new AuditError(`${option} requires a value.`);
  }
  return value;
}

export function parseArgs(argv) {
  const options = { task: undefined, target: undefined, url: undefined, scope: undefined, help: false };

  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === "--help" || argument === "-h") {
      options.help = true;
      continue;
    }
    if (argument === "--task" || argument === "--target" || argument === "--url" || argument === "--scope") {
      const key = argument.slice(2);
      options[key] = takeValue(argv, index, argument);
      index += 1;
      continue;
    }
    throw new AuditError(`Unknown argument: ${argument}`);
  }

  if (options.help) {
    return options;
  }
  if (!options.task || !TASK_ID_PATTERN.test(options.task)) {
    throw new AuditError("--task must use only letters, numbers, dots, underscores, or hyphens.");
  }
  if (Boolean(options.target) === Boolean(options.url)) {
    throw new AuditError("Provide exactly one of --target or --url.");
  }
  if (options.scope && !SCOPE_PATTERN.test(options.scope)) {
    throw new AuditError("--scope must be a comma-separated list such as type,layout.");
  }
  return options;
}

function isInside(root, candidate) {
  const relative = path.relative(root, candidate);
  return !relative.startsWith(`..${path.sep}`) && relative !== ".." && !path.isAbsolute(relative);
}

export function resolveTarget(root, target) {
  const resolved = path.resolve(root, target);
  if (!isInside(root, resolved)) {
    throw new AuditError("--target must be inside this repository.");
  }
  if (!existsSync(resolved)) {
    throw new AuditError("--target does not exist.");
  }
  return resolved;
}

export function validateLocalUrl(value) {
  let url;
  try {
    url = new URL(value);
  } catch {
    throw new AuditError("--url must be a valid local http(s) URL.");
  }

  const localHosts = new Set(["localhost", "127.0.0.1", "::1", "[::1]"]);
  if (!localHosts.has(url.hostname.toLowerCase()) || !["http:", "https:"].includes(url.protocol)) {
    throw new AuditError("--url must use http(s) on localhost, 127.0.0.1, or ::1.");
  }
  if (url.username || url.password || url.search || url.hash) {
    throw new AuditError("--url must not include credentials, a query string, or a fragment.");
  }
  return url.toString();
}

function findNpxCli() {
  const candidates = [
    path.join(path.dirname(process.execPath), "node_modules", "npm", "bin", "npx-cli.js"),
  ];
  if (process.env.npm_execpath) {
    candidates.push(path.join(path.dirname(process.env.npm_execpath), "npx-cli.js"));
  }
  return candidates.find((candidate) => existsSync(candidate));
}

export function resolveNpxInvocation() {
  const npxCli = findNpxCli();
  if (npxCli) {
    return { command: process.execPath, prefixArgs: [npxCli] };
  }
  if (process.platform !== "win32") {
    return { command: "npx", prefixArgs: [] };
  }
  throw new AuditError("Unable to locate the Node-bundled npx CLI.");
}

export function runProcess(command, args, options) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      cwd: options.cwd,
      shell: false,
      windowsHide: true,
      stdio: ["ignore", "pipe", "pipe"],
    });
    const stdout = [];
    const stderr = [];

    child.stdout.on("data", (chunk) => stdout.push(chunk));
    child.stderr.on("data", (chunk) => stderr.push(chunk));
    child.once("error", reject);
    child.once("close", (code, signal) => {
      resolve({
        code: typeof code === "number" ? code : 1,
        signal,
        stdout: Buffer.concat(stdout).toString("utf8"),
        stderr: Buffer.concat(stderr).toString("utf8"),
      });
    });
  });
}

export function extractFindings(parsed) {
  if (Array.isArray(parsed)) {
    return parsed;
  }
  if (parsed && Array.isArray(parsed.findings)) {
    return parsed.findings;
  }
  throw new AuditError("Detector JSON must contain a findings array.");
}

function cell(value) {
  return String(value ?? "—")
    .replaceAll("|", "\\|")
    .replaceAll("\r", " ")
    .replaceAll("\n", " ")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, 240) || "—";
}

function relativeFile(root, value) {
  if (typeof value !== "string" || !value) {
    return "—";
  }
  const resolved = path.resolve(root, value);
  return isInside(root, resolved) ? path.relative(root, resolved).split(path.sep).join("/") : value;
}

function findingFields(root, finding) {
  const severity = finding.severity ?? "unknown";
  const rule = finding.antipattern ?? finding.rule ?? finding.id ?? finding.name ?? "unknown";
  const file = relativeFile(root, finding.file ?? finding.path);
  const line = Number.isInteger(finding.line) ? finding.line : finding.line ?? "—";
  const summary = finding.description ?? finding.message ?? finding.name ?? "No description supplied.";
  return { severity, rule, file, line, summary };
}

export function buildReport({ task, source, scope, findings, root }) {
  const rows = findings.map((finding) => findingFields(root, finding));
  const lines = [
    "# Impeccable advisory audit",
    "",
    `- **Task Record:** \`${task}\``,
    `- **Source:** \`${source}\``,
    `- **Detector:** \`${PACKAGE_SPEC} detect --json\``,
    `- **Scope:** ${scope ? `\`${scope}\`` : "all detector scopes"}`,
    "- **Mode:** local advisory; detector exit `0` and `2` do not block handoff by themselves.",
    `- **Findings:** ${rows.length}`,
    "",
    "## Findings",
    "",
  ];

  if (rows.length === 0) {
    lines.push("No findings reported.");
  } else {
    lines.push("| Severity | Rule | File | Line | Summary |");
    lines.push("| --- | --- | --- | ---: | --- |");
    for (const row of rows) {
      lines.push(`| ${cell(row.severity)} | ${cell(row.rule)} | ${cell(row.file)} | ${cell(row.line)} | ${cell(row.summary)} |`);
    }
  }

  lines.push(
    "",
    "## Review notes",
    "",
    "- Compare findings with the Task Record, PRODUCT.md and DESIGN.md; fix only the claimed scope.",
    "- Record a narrow, peer-approved waiver in `.impeccable/config.json` only when the finding is intentionally retained.",
    "- Raw detector JSON is stored in ignored `.impeccable/audits/`; do not include secrets, customer data or private URLs in either artifact.",
    "",
  );
  return lines.join("\n");
}

export async function runAudit(options, dependencies = {}) {
  const root = path.resolve(dependencies.root ?? PROJECT_ROOT);
  const runCommand = dependencies.runCommand ?? runProcess;
  const invocation = dependencies.npxInvocation ?? resolveNpxInvocation();
  const sourcePath = options.target ? resolveTarget(root, options.target) : undefined;
  const source = sourcePath ? path.relative(root, sourcePath).split(path.sep).join("/") || "." : validateLocalUrl(options.url);
  const detectorArgs = [
    ...invocation.prefixArgs,
    "--yes",
    PACKAGE_SPEC,
    "detect",
    "--json",
    sourcePath ?? source,
  ];
  const result = await runCommand(invocation.command, detectorArgs, { cwd: root });

  if (![0, 2].includes(result.code) || result.signal) {
    throw new AuditError(`Detector did not complete successfully (exit ${result.code}).`);
  }

  let parsed;
  try {
    parsed = JSON.parse(result.stdout);
  } catch {
    throw new AuditError("Detector did not produce valid JSON.");
  }
  const findings = extractFindings(parsed);
  const report = buildReport({ task: options.task, source, scope: options.scope, findings, root });
  const reportPath = path.join(root, "docs", "design", "reviews", `${options.task}-impeccable.md`);
  const rawPath = path.join(root, ".impeccable", "audits", `${options.task}-impeccable.json`);

  await Promise.all([
    mkdir(path.dirname(reportPath), { recursive: true }),
    mkdir(path.dirname(rawPath), { recursive: true }),
  ]);
  await Promise.all([
    writeFile(reportPath, report, "utf8"),
    writeFile(rawPath, `${JSON.stringify(parsed, null, 2)}\n`, "utf8"),
  ]);

  return { findingCount: findings.length, reportPath, rawPath, detectorExitCode: result.code };
}

export async function main(argv = process.argv.slice(2), dependencies = {}) {
  try {
    const options = parseArgs(argv);
    if (options.help) {
      console.log(USAGE);
      return 0;
    }
    const result = await runAudit(options, dependencies);
    console.log(`Impeccable advisory audit completed: ${result.findingCount} finding(s).`);
    console.log(`Report: ${path.relative(dependencies.root ?? PROJECT_ROOT, result.reportPath)}`);
    return 0;
  } catch (error) {
    const message = error instanceof AuditError ? error.message : "Unable to run the advisory audit.";
    console.error(`Impeccable advisory audit failed: ${message}`);
    return 1;
  }
}

const isEntrypoint = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isEntrypoint) {
  process.exitCode = await main();
}
