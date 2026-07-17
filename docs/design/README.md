# Design audit workflow

This directory holds portable design-audit context and reports. It is intentionally tool-neutral: Codex, Claude, Cursor and Antigravity use the same documents, wrapper, Task Record and handoff.

## Source of truth and readiness

- [Project Context](../ai/PROJECT_CONTEXT.md) remains the product source of truth.
- [PRODUCT.md](../PRODUCT.md) is the compact product adapter that Impeccable can discover.
- [DESIGN.md](../DESIGN.md) is the design-system adapter. Complete and peer-review it before enabling design-system checks in [.impeccable/config.json](../../.impeccable/config.json).
- Reports are written below [reviews/](reviews/); raw detector JSON is deliberately kept in ignored `.impeccable/audits/`.

## Run an advisory audit

From the repository root, claim the UI scope in a Task Record and run one target at a time:

```powershell
node scripts/design/impeccable-audit.mjs --task local-20260717-example-ui --target path/to/ui
node scripts/design/impeccable-audit.mjs --task local-20260717-example-ui --url http://localhost:3000 --scope type,layout
```

The wrapper pins `impeccable@3.2.1`, runs `detect --json`, and writes `docs/design/reviews/<task-id>-impeccable.md`. `--scope` is a review/category annotation in the report; Impeccable `detect` does not expose a detector scope flag, so it never limits the scan. Detector exit `0` (no finding) and exit `2` (finding) both yield a successful advisory audit; execution failures and malformed JSON fail. The wrapper never uses a shell, never installs a repo dependency, and accepts a path inside this repository or an unauthenticated local `http(s)` URL.

Do not use `/impeccable init`, `/impeccable craft`, `/impeccable live`, `npx impeccable install`, browser extensions, native skills or hooks as part of this workflow. There is no `.agents/skills`, `.codex/hooks.json`, `.cursor/hooks.json`, MCP configuration or provider-specific configuration for Impeccable in this bootstrap.

## Review, waiver and handoff

1. In `review`, read the Markdown report against the Task Record and design context; fix findings that improve the scoped UI.
2. A necessary exception must be narrow, include a reason and receive the peer confirmation required by its Task Record. Create a shared waiver only through the Impeccable CLI, for example `npx --yes impeccable@3.2.1 ignores add-rule <rule> --reason "<reason>"`.
3. Team-approved shared waivers belong in tracked [.impeccable/config.json](../../.impeccable/config.json). Personal/experimental exclusions use `.impeccable/config.local.json`, which is ignored and must not become shared policy.
4. Do not disable a detector family globally merely to silence a report. Record the waiver and any unverified viewport/state in the Task Record handoff.
5. In `verify-demo`, audit the local URL after the dev server is ready, then include report path, waiver(s), evidence and remaining limitations in the handoff.

Impeccable is local and advisory until the team chooses a frontend path, package manager and a separate Decision to add a stable design gate to CI. It does not replace accessibility review, product judgment or manual demo rehearsal.
