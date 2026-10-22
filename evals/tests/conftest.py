from pathlib import Path

import pytest

EVALS = Path(__file__).resolve().parents[1]


@pytest.fixture
def fixture_design() -> str:
    return (EVALS / "fixtures/designs/2026-09-17-unified-cache.md").read_text(encoding="utf-8")


@pytest.fixture
def smoke_case() -> Path:
    return EVALS / "cases/reportgen-unified-cache.json"
