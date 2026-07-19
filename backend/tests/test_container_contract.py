from __future__ import annotations

from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]


def test_backend_image_defaults_to_offline_demo_mode() -> None:
    dockerfile = (BACKEND_ROOT / "Dockerfile").read_text(encoding="utf-8")

    assert "APP_ENV=production" in dockerfile
    assert "PROCEDURE_DATA_MODE=demo_pack" in dockerfile
    assert "RAG_MODE=disabled" in dockerfile
    assert "LLM_MODE=disabled" in dockerfile
    assert "LEGACY_RAG_ENABLED=false" in dockerfile
    assert "USER app" in dockerfile
    assert "HEALTHCHECK" in dockerfile
    assert "os.getenv('PORT', '8080')" in dockerfile
    assert "+ '/health'" in dockerfile


def test_backend_image_only_copies_locked_runtime_inputs() -> None:
    dockerfile = (BACKEND_ROOT / "Dockerfile").read_text(encoding="utf-8")
    dockerignore = (BACKEND_ROOT / ".dockerignore").read_text(encoding="utf-8")

    copy_lines = [line.strip() for line in dockerfile.splitlines() if line.startswith("COPY")]
    assert copy_lines == [
        "COPY requirements.lock.txt ./requirements.lock.txt",
        "COPY --chown=app:app app ./app",
    ]

    for excluded_path in (
        ".env",
        "tests/",
        "artifacts/",
        "data_raw/",
        "dataset_raw/",
        "Data_DVC/",
        "*.safetensors",
    ):
        assert excluded_path in dockerignore
