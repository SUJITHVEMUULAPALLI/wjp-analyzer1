"""Pytest-friendly smoke tests for optional dependencies and key modules."""

from __future__ import annotations

import importlib
import importlib.util
import inspect
import sys
from typing import Iterable, Tuple

import pytest


_OPTIONAL_DEPENDENCIES: Tuple[Tuple[str, str], ...] = (
    ("numpy", "NumPy"),
    ("matplotlib.pyplot", "Matplotlib"),
    ("PIL.Image", "Pillow"),
    ("streamlit", "Streamlit"),
    ("cv2", "OpenCV"),
    ("shapely.geometry", "Shapely"),
    ("ezdxf", "EzDXF"),
    ("pydantic", "Pydantic"),
)


def _importable(module_name: str) -> bool:
    """Return ``True`` when *module_name* can be imported."""

    return importlib.util.find_spec(module_name) is not None


@pytest.mark.parametrize(
    "module_name, display_name",
    _OPTIONAL_DEPENDENCIES,
    ids=[name for _, name in _OPTIONAL_DEPENDENCIES],
)
def test_optional_dependency_importable(module_name: str, display_name: str) -> None:
    """Ensure optional third-party dependencies import when installed.

    These packages are optional for the current repository state. If a
    dependency is unavailable in the execution environment the test is
    marked as skipped so the suite still succeeds.
    """

    if not _importable(module_name):
        pytest.skip(f"{display_name} ({module_name}) is not installed")

    try:
        importlib.import_module(module_name)
    except ImportError as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"{display_name} could not be imported: {exc}")


def test_unified_entry_point_exposes_application_class() -> None:
    """Validate the unified entry point exposes the expected class."""

    module = importlib.import_module("wjp_analyser_unified")
    assert hasattr(module, "WJPUnifiedApp"), "Unified application class missing"

    unified_cls = module.WJPUnifiedApp
    assert inspect.isclass(unified_cls), "WJPUnifiedApp should be a class"

    required_methods: Iterable[str] = (
        "launch_web_ui",
        "_launch_streamlit_ui",
        "_launch_flask_ui",
        "_launch_enhanced_ui",
        "_launch_supervisor_ui",
    )

    for method_name in required_methods:
        assert hasattr(unified_cls, method_name), (
            f"WJPUnifiedApp missing expected method '{method_name}'"
        )


def test_run_one_click_parse_args_handles_new_flags(monkeypatch, tmp_path) -> None:
    """Ensure the one-click launcher exposes the new convenience flags."""

    cfg_path = tmp_path / "config.json"
    argv = [
        "run_one_click.py",
        "--mode",
        "ui",
        "--config",
        str(cfg_path),
        "--guided-ui",
        "--batch-guided-ui",
    ]
    monkeypatch.setattr(sys, "argv", argv)

    from run_one_click import parse_args

    parsed = parse_args()
    assert parsed.config == cfg_path
    assert parsed.guided_ui is True
    assert parsed.batch_guided_ui is True


def test_launch_streamlit_unified_forwards_flags(monkeypatch, tmp_path) -> None:
    """Verify Streamlit launcher propagates CLI flags to the subprocess."""

    import run_one_click

    captured: dict[str, object] = {}

    def fake_run(cmd, check, env):
        captured["cmd"] = cmd
        captured["env"] = env

        class Result:
            returncode = 0

        return Result()

    monkeypatch.setattr(run_one_click, "_streamlit_command", lambda: ["streamlit"])
    monkeypatch.setattr(run_one_click.subprocess, "run", fake_run)

    config_path = tmp_path / "config.json"
    config_path.write_text("{}", encoding="utf-8")

    exit_code = run_one_click.launch_streamlit_unified(
        host="0.0.0.0",
        port=9999,
        no_browser=True,
        guided=True,
        batch_guided=True,
        config=config_path,
    )

    assert exit_code == 0
    cmd = list(captured["cmd"])
    env = dict(captured["env"])

    assert "--server.headless" in cmd
    assert "--" in cmd
    dash_index = cmd.index("--")
    assert cmd[dash_index + 1 : dash_index + 5] == [
        "--guided",
        "--batch-guided",
        "--config",
        str(config_path),
    ]
    assert env.get("WJP_GUIDED_MODE") == "true"
    assert env.get("WJP_BATCH_GUIDED_MODE") == "true"
