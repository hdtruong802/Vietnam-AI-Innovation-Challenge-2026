# Review reports

`impeccable-audit.mjs` writes one reviewable Markdown report per Task Record in this directory:

```text
<task-id>-impeccable.md
```

Commit a report only when it is useful handoff evidence for the scoped UI task. The matching raw JSON under `.impeccable/audits/` is ignored because it is machine output and may be noisy. Do not put secrets, customer data or private URLs in either artifact.
