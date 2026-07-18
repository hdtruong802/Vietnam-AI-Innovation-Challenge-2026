import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.getenv("APP_ENV", "development")
ALLOWED_ORIGINS = ["*"]  # In production, specify allowed origins

# --- AI / LLM Gateway (provider-neutral, xem docs/proposal.md muc 5 va D-006) ---
# De trong AI_API_KEY khi demo offline: LLMGateway se fallback deterministic,
# khong goi model va khong bia noi dung quy pham.
AI_PROVIDER = os.getenv("AI_PROVIDER", "")
AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini")
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_BASE_URL = os.getenv("AI_BASE_URL") or None
AI_TIMEOUT_SECONDS = float(os.getenv("AI_TIMEOUT_SECONDS", "8"))

# --- RAG / Knowledge (in-process, xem D-006) ---
BACKEND_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_ROOT.parent
RAG_SOURCE_DIR = Path(os.getenv("RAG_SOURCE_DIR", str(REPO_ROOT / "data" / "Data_DVC")))
RAG_SOURCE_FREEZE_DATE = os.getenv("RAG_SOURCE_FREEZE_DATE", "2026-07-17")
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))
RAG_MIN_CONFIDENCE = float(os.getenv("RAG_MIN_CONFIDENCE", "0.12"))

# --- Guardrail / PII Guard (session-scoped, in-memory, xem D-006) ---
PII_TOKEN_TTL_SECONDS = int(os.getenv("PII_TOKEN_TTL_SECONDS", "1800"))
