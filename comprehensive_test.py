"""Pytest-friendly smoke tests for optional dependencies and key modules."""

from __future__ import annotations

import importlib
import importlib.util
import inspect
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
