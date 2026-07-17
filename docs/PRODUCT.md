# Product design context

> Đây là adapter thiết kế tối thiểu cho Impeccable. Nguồn sự thật về sản phẩm, MVP, scope và quyết định vẫn là [Project Context](ai/PROJECT_CONTEXT.md). Cập nhật tài liệu đó trước, rồi đồng bộ phần liên quan ở đây trước một task UI có shared tokens/components.

## Register and platform

- **Product register:** `TBD` — chốt giọng điệu (ví dụ: calm, editorial, playful, utilitarian) từ Product Brief, không suy đoán.
- **Platform:** `TBD` — web/mobile/desktop, breakpoint và input method chỉ được điền sau khi chọn stack.
- **Locale and content:** `TBD` — ưu tiên nội dung demo thật, không đưa dữ liệu nhạy cảm vào context hoặc screenshot audit.

## Users and job to be done

- **Primary user:** `TBD`
- **User goal / critical journey:** `TBD`
- **Demo-critical state:** `TBD`
- **Failure or empty state:** `TBD`

## Positioning

- **Value proposition:** `TBD`
- **What should feel distinct:** `TBD`
- **What must remain simple or familiar:** `TBD`
- **Non-goals for visual design:** `TBD`

## Accessibility baseline

- Meet keyboard, focus-visible, semantic structure and readable text requirements for the chosen platform.
- Confirm color contrast, reduced-motion behavior and touch/target sizes after tokens and components are chosen.
- Do not treat an Impeccable finding or waiver as an accessibility exception; record known limitations in the Task Record and demo fallback.

## Update contract

1. A product/demo peer updates `docs/ai/PROJECT_CONTEXT.md` when the problem, audience, MVP or non-goal changes.
2. The owner of a scoped UI task updates the affected fields here and in [DESIGN.md](DESIGN.md), citing its Task Record/Decision where relevant.
3. A shared visual change needs a Task Record, `risk:shared` review and a Decision Log entry as defined in the team protocol.

Until the `TBD` fields are confirmed, this file provides boundaries only. It does not authorize a visual direction, platform assumption or new dependency.
