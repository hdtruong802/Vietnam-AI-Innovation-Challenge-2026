---
name: VNGov AI Copilot
description: Hệ thống trợ lý hướng dẫn và tiền kiểm hồ sơ hành chính công — Copilot Workspace Mode dùng bảng màu civic ấm (đỏ trầm & vàng đồng), Portal Mode giữ bảng màu đỏ/vàng riêng đã có (D-012)
colors:
  vg-canvas: "#FBF8F2"
  vg-surface: "#FFFDF9"
  vg-border: "#E8D9CB"
  vg-text: "#25201C"
  vg-accent: "#B52B23"     # Civic crimson — hành động chính, nav active
  vg-gold: "#D8942F"       # Phụ, không cạnh tranh với accent
  vg-success: "#23865F"
  vg-warning: "#B46E15"
  vg-error: "#C63D36"
typography:
  body:
    fontFamily: "Geist Sans, Inter, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.6
rounded:
  compact: "8px"
  panel: "12px"
  surface: "16px"
spacing:
  sm: "8px"
  md: "16px"
  lg: "24px"
components:
  button-primary:
    backgroundColor: "{colors.vg-accent}"
    textColor: "#FFFFFF"
    rounded: "{rounded.compact}"
    padding: "10px 20px"
  panel:
    backgroundColor: "{colors.vg-surface}"
    rounded: "{rounded.panel}"
    padding: "20px"
---

# Design System: VNGov AI Copilot

## 1. Overview

**Creative North Star: "Civic, warm, calm, task-oriented"**

VNGov spans two registers that belong to one civic product family but are styled independently:

- **Portal Mode** — the simulated Cổng Dịch vụ công Quốc gia landing page (`frontend/src/app/components/landing/**`). Uses its own accepted red/gold token set (`--color-gov-*`, D-012), scoped to `.portal-home`. **Not touched by this document's Copilot Workspace section.**
- **Copilot Workspace Mode** — the AI procedure assistant (`frontend/src/features/procedure-case/**`). Uses the `--vg-*` token set defined below, scoped to `.copilot-workspace`.

Both share a civic design language — warm paper surfaces, restrained crimson/gold accents, borders over shadows, no gradients or glassmorphism — without sharing CSS variables. Neither mode repoints the other's tokens; there is no global `:root`/`@theme` civic palette.

> **Provenance note:** this document previously described a Deep-Navy/Brand-Orange (`#0D1B3D`/`#F97316`) palette for the Copilot workspace, matching what `frontend/src/app/globals.css` implemented at the time. That content was never backed by an Accepted Decision Log entry — it was implementation drift that this document mirrored rather than governed. This revision replaces it with the warm civic (`--vg-*`) palette below as the authoritative spec for Copilot Workspace Mode.

## 2. Colors — Copilot Workspace Mode

Token source: `.copilot-workspace` scope in `frontend/src/app/globals.css`. Light-theme only (no dark-mode variant is defined for `--vg-*` in this hackathon scope).

| Token | Value | Use |
| --- | --- | --- |
| `--vg-canvas` | `#FBF8F2` | Page/workspace background |
| `--vg-surface` | `#FFFDF9` | Cards, panels, header |
| `--vg-surface-subtle` | `#F7F1E9` | Nested subtle surfaces (tab bar, quiet blocks) |
| `--vg-border` / `--vg-border-strong` | `#E8D9CB` / `#D5C1AF` | Panel borders, dividers |
| `--vg-text` / `--vg-text-secondary` / `--vg-text-muted` | `#25201C` / `#655B53` / `#8A817A` | Text hierarchy |
| `--vg-accent` / `--vg-accent-hover` / `--vg-accent-soft` | `#B52B23` / `#962018` / `#FCEDEA` | Primary action, active nav/tab underline |
| `--vg-gold` / `--vg-gold-soft` | `#D8942F` / `#FFF1DB` | Secondary accent only — never a competing CTA color |
| `--vg-success` / `--vg-success-soft` | `#23865F` / `#EAF6F0` | Connected/passed states only |
| `--vg-warning` / `--vg-warning-soft` | `#B46E15` / `#FFF4DF` | Non-blocking degrade (e.g. AI unavailable) |
| `--vg-error` / `--vg-error-soft` | `#C63D36` / `#FCECEA` | Blocking errors and connection failures only |

### Color rules

- Warm paper canvas/surfaces (`--vg-canvas`/`--vg-surface`), never a blue-gray canvas, in the Copilot workspace.
- `--vg-accent` (civic crimson) is the only primary-action / active-navigation color.
- `--vg-gold` is secondary decoration/emphasis; it must never appear as a competing CTA next to `--vg-accent`.
- `--vg-success` only for connected/passed states; `--vg-error` only for blocking errors and connection failures — not general validation warnings (use `--vg-warning`).
- Navy may remain only in the VNGov wordmark mark; it must not dominate workspace navigation, tabs, or panels.
- No pale/orange-with-white-text disabled buttons. Disabled buttons: neutral gray background, readable muted text, `cursor-not-allowed`, reason available via adjacent help text — not opacity alone.
- No gradients, glassmorphism, glow, AI-orb, or sparkle decoration in the workspace.
- Prefer borders + spacing over shadow. Shadow only for overlays, drawers, dropdowns, or a focused floating element — not for ordinary panels.
- Avoid nested "card soup" — one primary panel per concern, not cards inside cards.

## 3. Shape

```text
Compact inputs/controls (buttons, inputs, tab underlines): 8px
Standard panels (cards, banners): 12px
Large workspace surfaces (empty states, major containers): 14–16px
Status pills: fully rounded only when semantically a pill (e.g. connection badge)
```

## 4. Typography

Font family: the existing Vietnamese-capable sans-serif stack (`Geist Sans`/`Inter`/system-ui) for all Copilot UI. No serif headings in the workspace (serif remains available for Portal/marketing use only).

```text
Page/header product name: 18–22px, semibold
Pane heading: 16–18px, semibold
Section heading: 14–16px, semibold
Body: 14–16px, regular
Metadata: 12–13px
Button: 14–15px, medium/semibold
```

Avoid all-caps except small metadata eyebrows. Internal review-gate IDs (U1/U2/U3) must never appear in citizen-facing text — they remain in code, state, tests, and analytics only.

## 5. Panels and empty states

- Panels: `--vg-surface` background, `--vg-border` border, 12–16px radius, no strong shadow, a clear heading.
- Empty/locked states (e.g. "Tờ khai chưa được mở" before U2, "Chức năng sẽ khả dụng sau khi hoàn tất tờ khai" for pre-check) must: state what is unavailable, explain what unlocks it, and avoid promotional filler or a fake enabled-looking CTA.
- Progressive disclosure: never render the form before U2 confirmation; never render an active pre-check control before the form pane is mounted. Future steps get an explanatory empty state, not a disabled-but-visually-active panel.
- One primary decision/action per state (e.g. confirm/reject at U1, confirm at U2, run/acknowledge at U3) — no competing CTAs in the same panel.

## 6. Responsive

- No horizontal page scroll at 1440/1366/1280/1024/768/390px. Each pane manages its own vertical overflow.
- Left composer stays sticky at the bottom of the left pane.
- Below the two/three-column breakpoint, the progress rail collapses to a compact horizontal/collapsible header; panes stack without resetting transcript, checklist, or form state.
