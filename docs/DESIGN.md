# Design system context

> Đây là adapter thiết kế tối thiểu cho Impeccable. Nó bổ sung, không thay thế [Project Context](ai/PROJECT_CONTEXT.md), [Architecture](ai/ARCHITECTURE.md) hoặc [Product design context](PRODUCT.md). Các giá trị `TBD` không phải token hợp lệ và không được tự suy ra.

## Design principles

- **Visual direction:** `TBD`
- **Information density:** `TBD`
- **Hierarchy and emphasis:** `TBD`
- **Responsive strategy:** `TBD`

## Tokens

| Token family | Source of truth | Status |
| --- | --- | --- |
| Color | `TBD` | Chưa chọn palette/semantic colors. |
| Spacing | `TBD` | Chưa chọn scale. |
| Radius, border and shadow | `TBD` | Chưa chọn surface language. |
| Size and breakpoints | `TBD` | Chưa chọn platform/layout grid. |
| Iconography and assets | `TBD` | Chưa chọn library hoặc asset policy. |

## Typography

- **Font family and fallback:** `TBD`
- **Type scale and line-height:** `TBD`
- **Weight, casing and emphasis rules:** `TBD`
- **Readable minimum sizes:** `TBD`

## Components and states

- **Shared components:** `TBD`
- **Interactive states:** define default, hover, focus-visible, active, disabled, loading, empty and error states when each component is introduced.
- **Ownership:** one Task Record claims a shared component or token migration at a time; record the consumer impact before changing it.

## Layout

- **Page shell and navigation:** `TBD`
- **Grid, alignment and spacing rhythm:** `TBD`
- **Responsive breakpoints and overflow behavior:** `TBD`
- **Content priority on small screens:** `TBD`

## Motion

- **Motion purpose:** `TBD`
- **Duration/easing and interruption rules:** `TBD`
- Respect `prefers-reduced-motion`; motion must not be the only way to convey state or complete the demo.

## Audit readiness

Impeccable design-system checks remain disabled in [.impeccable/config.json](../.impeccable/config.json) while these shared values are `TBD`. After a peer-reviewed task defines actual tokens/components, update this file first and enable those checks through a Task Record. Other Impeccable detector rules can still run in local advisory mode.
