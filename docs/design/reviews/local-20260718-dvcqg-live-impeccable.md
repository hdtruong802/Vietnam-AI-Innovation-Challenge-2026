# Impeccable advisory audit

- **Task Record:** `local-20260718-dvcqg-live`
- **Source:** `http://localhost:3000/`
- **Detector:** `impeccable@3.2.1 detect --json`
- **Scope:** `type,layout`
- **Mode:** local advisory; detector exit `0` and `2` do not block handoff by themselves.
- **Findings:** 8

## Findings

| Severity | Rule | File | Line | Summary |
| --- | --- | --- | ---: | --- |
| warning | low-contrast | http:/localhost:3000 | 0 | Text does not meet WCAG AA contrast requirements (4.5:1 for body, 3:1 for large text). Increase the contrast between text and background. |
| warning | tiny-text | http:/localhost:3000 | 0 | Body text below 12px is hard to read, especially on high-DPI screens. Use at least 14px for body content, 16px is ideal. |
| warning | tiny-text | http:/localhost:3000 | 0 | Body text below 12px is hard to read, especially on high-DPI screens. Use at least 14px for body content, 16px is ideal. |
| warning | tiny-text | http:/localhost:3000 | 0 | Body text below 12px is hard to read, especially on high-DPI screens. Use at least 14px for body content, 16px is ideal. |
| warning | tiny-text | http:/localhost:3000 | 0 | Body text below 12px is hard to read, especially on high-DPI screens. Use at least 14px for body content, 16px is ideal. |
| warning | tiny-text | http:/localhost:3000 | 0 | Body text below 12px is hard to read, especially on high-DPI screens. Use at least 14px for body content, 16px is ideal. |
| warning | tiny-text | http:/localhost:3000 | 0 | Body text below 12px is hard to read, especially on high-DPI screens. Use at least 14px for body content, 16px is ideal. |
| warning | overused-font | http:/localhost:3000 | 0 | Inter, Roboto, Fraunces, Geist, Plus Jakarta Sans, and Space Grotesk are used on so many sites they no longer feel distinctive. Each new wave of AI-generated UIs converges on the same handful of faces. Choose a face that gives your interfac |

## Review notes

- Compare findings with the Task Record, PRODUCT.md and DESIGN.md; fix only the claimed scope.
- Record a narrow, peer-approved waiver in `.impeccable/config.json` only when the finding is intentionally retained.
- Raw detector JSON is stored in ignored `.impeccable/audits/`; do not include secrets, customer data or private URLs in either artifact.
