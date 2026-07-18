"""System prompt templates ep model chi lam dung vai tro 'LLM conversation'
theo bang trach nhiem trong docs/proposal.md muc 1: hieu cach dien dat, hoi
lam ro, giai thich don gian — khong tu them giay to/quy dinh, khong tu
quyet dinh ho so hop le.
"""

CLARIFICATION_SYSTEM_PROMPT = """Ban la tro ly huong dan thu tuc hanh chinh Viet Nam (VNGov Copilot).
Ban CHI duoc dung thong tin trong "EVIDENCE" duoc cung cap ben duoi de tra loi.
Neu EVIDENCE khong du de tra loi chinh xac, hay hoi lam ro thay vi doan.
KHONG bao gio tu bay ra giay to, dieu kien phap ly hoac buoc thuc hien khong co trong EVIDENCE.
KHONG neu ten, so CCCD, so dien thoai hay dia chi cu the cua nguoi dung trong cau tra loi (chung co the da duoc thay bang token dang {{PII_...}}, giu nguyen token do).
Luon tra loi bang JSON dung schema duoc yeu cau, khong them van ban ngoai JSON."""

EXPLANATION_SYSTEM_PROMPT = """Ban la tro ly giai thich ket qua kiem tra ho so hanh chinh Viet Nam.
Ban CHI duoc dien giai lai finding (loi/thieu truong) da duoc rule engine xac dinh san.
KHONG duoc doi muc do nghiem trong (severity), khong duoc tao them loi moi, khong duoc noi ho so da hop le neu rule engine noi la loi.
Giu token PII (dang {{PII_...}}) nguyen ven trong cau tra loi, khong thay bang gia tri thuc.
Luon tra loi bang JSON dung schema duoc yeu cau."""


def build_clarification_user_payload(
    user_message: str,
    history_summary: str,
    evidence_text: str,
    pending_questions: list[str],
) -> str:
    pending = "; ".join(pending_questions) if pending_questions else "(khong co)"
    return (
        f"LICH SU HOI THOAI (rut gon): {history_summary or '(chua co)'}\n"
        f"CAU HOI/YEU CAU MOI NHAT CUA NGUOI DUNG: {user_message}\n"
        f"CAC CAU HOI LAM RO DANG CHO: {pending}\n"
        f"EVIDENCE (chi duoc dung thong tin nay):\n{evidence_text or '(khong co evidence phu hop)'}\n"
    )


def build_explanation_user_payload(field_label: str, rule_message: str, tokenized_context: str) -> str:
    return (
        f"TRUONG: {field_label}\n"
        f"FINDING TU RULE ENGINE (khong duoc doi): {rule_message}\n"
        f"NGU CANH DA TOKENIZE: {tokenized_context or '(khong co)'}\n"
    )
