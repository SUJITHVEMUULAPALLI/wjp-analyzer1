"""Minimal Streamlit interface for the WJP Analyser demo."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Optional, Tuple

try:  # pragma: no cover - exercised at runtime by Streamlit
    import streamlit as st
except ModuleNotFoundError as exc:  # pragma: no cover - handled in tests
    st = None  # type: ignore[assignment]
    _STREAMLIT_IMPORT_ERROR = exc
else:  # pragma: no cover - exercised at runtime by Streamlit
    _STREAMLIT_IMPORT_ERROR = None

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SAMPLE_FILES: Tuple[Tuple[str, Path], ...] = (
    ("Sample DXF", PROJECT_ROOT / "test_file.dxf"),
    ("Sample Designer DXF", PROJECT_ROOT / "designer_test.dxf"),
    ("Sample Image", PROJECT_ROOT / "test_image.png"),
)
GUIDED_STEPS: Tuple[str, ...] = (
    "Upload a DXF or supported raster image.",
    "Review automatically extracted geometry information.",
    "Optionally enable AI-powered suggestions to enhance the layout.",
    "Export the optimised DXF for downstream fabrication steps.",
)
BATCH_GUIDED_HINTS: Tuple[str, ...] = (
    "Drop multiple DXF files at once to build a batch queue.",
    "Preview the summary report before committing the batch run.",
    "Export combined analytics as JSON for automated pipelines.",
)


def _parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--guided", action="store_true", help="Enable guided walkthrough mode.")
    parser.add_argument(
        "--batch-guided",
        action="store_true",
        help="Highlight batch processing assistance features.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to a JSON configuration to preload into the interface.",
    )
    args, _unknown = parser.parse_known_args(list(argv) if argv is not None else None)
    return args


def _load_config(path: Optional[Path]) -> Optional[dict]:
    if not path:
        return None

    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        st.sidebar.warning(f"Configuration file not found: {path}")
    except json.JSONDecodeError as exc:
        st.sidebar.error(f"Invalid JSON configuration: {exc}")
    return None


def _render_sidebar(preloaded_config: Optional[dict]) -> None:
    st.sidebar.header("Project assets")

    for label, file_path in SAMPLE_FILES:
        if file_path.exists():
            st.sidebar.download_button(
                label=f"Download {label}",
                file_name=file_path.name,
                data=file_path.read_bytes(),
            )
        else:
            st.sidebar.info(f"{label} not bundled with this build.")

    st.sidebar.divider()

    st.sidebar.markdown(
        "**Environment status**\n\n"
        "This lightweight preview focuses on the Streamlit interface."
    )

    if preloaded_config:
        st.sidebar.success("Loaded configuration overrides.")
        with st.sidebar.expander("Configuration", expanded=False):
            st.json(preloaded_config)


def _render_guided_steps(title: str, steps: Iterable[str]) -> None:
    st.subheader(title)
    for index, step in enumerate(steps, start=1):
        st.markdown(f"**Step {index}.** {step}")


def _render_upload_section() -> None:
    st.subheader("Upload workspace")
    uploaded = st.file_uploader(
        "Upload DXF or image files",
        type=("dxf", "png", "jpg", "jpeg"),
        accept_multiple_files=True,
    )
    if not uploaded:
        st.info("Use the uploader or the sidebar downloads to explore the interface.")
        return

    for item in uploaded:
        st.write(f"**{item.name}** — {item.size} bytes")
        if item.type.startswith("image/"):
            st.image(item)


def _render_analysis_sections() -> None:
    st.subheader("Analysis overview")
    tab_layout, tab_ai, tab_export = st.tabs(["Layout", "AI suggestions", "Export"])

    with tab_layout:
        st.markdown(
            "Visualise DXF layers, detect shapes, and compute bounding boxes. "
            "This placeholder demonstrates where the geometric analysis results would appear."
        )
        st.metric("Detected layers", 5, help="Example metric for demonstration purposes.")

    with tab_ai:
        st.markdown(
            "AI-powered design suggestions would surface here. The demo highlights "
            "how textual explanations and preview thumbnails could be combined."
        )
        st.image(str(PROJECT_ROOT / "test_design.png"), caption="Conceptual AI design proposal", width=320)

    with tab_export:
        st.markdown(
            "Export refined DXF files, generate PDF reports, and integrate with downstream tooling."
        )
        st.code(
            "python wjp_analyser_unified.py cli export --input your_file.dxf --format dxf",
            language="bash",
        )


def main(args: Optional[argparse.Namespace] = None) -> None:
    if st is None:  # pragma: no cover - exercised when dependency missing
        raise RuntimeError("Streamlit is not installed") from _STREAMLIT_IMPORT_ERROR

    parsed_args = args or _parse_args()

    st.set_page_config(
        page_title="WJP Analyser",
        page_icon="🛠️",
        layout="wide",
    )

    st.title("WJP Analyser - Streamlit Preview")
    st.caption("Unified interface prototype for DXF analytics and AI-assisted design.")

    config_data = _load_config(parsed_args.config)
    _render_sidebar(config_data)

    if parsed_args.guided:
        _render_guided_steps("Guided walkthrough", GUIDED_STEPS)

    if parsed_args.batch_guided:
        _render_guided_steps("Batch processing tips", BATCH_GUIDED_HINTS)

    _render_upload_section()
    _render_analysis_sections()

    st.success("Ready to integrate the full backend pipeline when available.")


if __name__ == "__main__":  # pragma: no cover - manual execution only
    main()
