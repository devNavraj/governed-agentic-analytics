"""Phase 0 smoke test: proves the toolchain (uv + pytest) is wired up."""

from pathlib import Path


def test_repo_layout_exists() -> None:
    root = Path(__file__).resolve().parents[1]
    for pkg in ("ingestion", "agent", "orchestration", "eval", "infra"):
        assert (root / pkg).is_dir(), f"missing top-level package: {pkg}"


def test_env_example_present() -> None:
    root = Path(__file__).resolve().parents[1]
    assert (root / ".env.example").is_file()
