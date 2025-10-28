#!/usr/bin/env python3
"""One-click launcher for the Waterjet DXF Analyzer project."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional

import os
import sys

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

REPO_ROOT = Path(__file__).resolve().parent
REQUIREMENTS = REPO_ROOT / "requirements.txt"
def install_dependencies(skip: bool, upgrade: bool) -> None:
    """Install project requirements unless explicitly skipped."""
    if skip:
        print("[skip] Skipping dependency installation as requested.")
        return
    if not REQUIREMENTS.exists():
        print(f"[warn] requirements.txt not found at {REQUIREMENTS}, skipping install.")
        return

    cmd = [sys.executable, "-m", "pip", "install"]
    if upgrade:
        cmd.append("--upgrade")
    cmd.extend(["-r", str(REQUIREMENTS)])

    print("[setup] Installing dependencies...")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as exc:  # pragma: no cover - external command
        raise SystemExit(f"Dependency installation failed (exit code {exc.returncode}).") from exc
    print("[setup] Dependencies ready.")


def run_demo(skip_install: bool, upgrade: bool, open_preview: bool) -> None:
    """Placeholder demo runner shown when the original pipeline is unavailable."""
    print("[demo] The full demo pipeline is not bundled with this lightweight build.")
    print("[demo] Launch the UI mode instead to explore the Streamlit preview.")
    if open_preview:
        print("[demo] Preview assets are not generated in this mode.")


def _streamlit_command() -> list[str]:
    base_dir = os.path.dirname(sys.executable)
    if os.name == "nt":
        candidate = os.path.join(base_dir, "streamlit.exe")
    else:
        candidate = os.path.join(base_dir, "streamlit")
    if os.path.exists(candidate):
        return [candidate]
    return [sys.executable, "-m", "streamlit"]


def launch_streamlit_unified(
    host: str,
    port: int,
    no_browser: bool,
    guided: bool = False,
    batch_guided: bool = False,
    config: Optional[Path] = None,
) -> int:
    repo_root = os.path.dirname(__file__)
    script_path = os.path.join(repo_root, "src", "wjp_analyser", "web", "streamlit_app.py")
    if not os.path.exists(script_path):
        print(f"[ui] Streamlit app not found at {script_path}.")
        return 1

    cmd = _streamlit_command() + [
        "run",
        script_path,
        "--server.address", host,
        "--server.port", str(port),
    ]
    if no_browser:
        cmd.extend(["--server.headless", "true"])

    script_flags: list[str] = []
    if guided:
        script_flags.append("--guided")
    if batch_guided:
        script_flags.append("--batch-guided")
    if config is not None:
        script_flags.extend(["--config", str(config)])
    if script_flags:
        cmd.append("--")
        cmd.extend(script_flags)

    env = os.environ.copy()
    env.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "0")
    if guided:
        env["WJP_GUIDED_MODE"] = "true"
    if batch_guided:
        env["WJP_BATCH_GUIDED_MODE"] = "true"

    print(f"[ui] Starting Streamlit UI at http://{host}:{port}/")
    try:
        subprocess.run(cmd, check=True, env=env)
        return 0
    except subprocess.CalledProcessError as exc:
        print(f"[ui] Streamlit exited with status {exc.returncode}")
        return exc.returncode
    except KeyboardInterrupt:
        print("\n[ui] Stopping Streamlit UI...")
        return 0


def launch_web_ui(host: str, port: int, open_browser: bool) -> None:
    """Legacy Flask UI placeholder when the backend is unavailable."""
    url = f"http://{host}:{port}/"
    print("[ui] The Flask-based interface is not bundled with this build.")
    print("[ui] Use --ui-backend streamlit to launch the available preview instead.")
    if open_browser:
        print(f"[ui] Requested browser launch skipped for unavailable endpoint at {url}.")


def run_ui(
    skip_install: bool,
    upgrade: bool,
    host: str,
    port: int,
    no_browser: bool,
    ui_backend: str,
    guided: bool = False,
    batch_guided: bool = False,
    config: Optional[Path] = None,
) -> None:
    install_dependencies(skip_install, upgrade)
    if ui_backend == "flask":
        launch_web_ui(host=host, port=port, open_browser=not no_browser)
    else:
        launch_streamlit_unified(
            host=host,
            port=port,
            no_browser=no_browser,
            guided=guided,
            batch_guided=batch_guided,
            config=config,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bootstrap, install requirements, and either run the UI or the demo pipeline.",
    )
    parser.add_argument(
        "--mode",
        choices=["ui", "demo", "guided", "batch-guided"],
        default="ui",
        help="Which workflow to run (default: ui).",
    )
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="Skip dependency installation.",
    )
    parser.add_argument(
        "--upgrade",
        action="store_true",
        help="Pass --upgrade to pip while installing requirements.",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host/interface for the web UI (ui mode).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8501,
        help="Port for the web UI (ui mode).",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not auto-open the browser when starting the UI.",
    )
    parser.add_argument(
        "--open-preview",
        action="store_true",
        help="Open the generated preview image after the demo pipeline completes.",
    )
    parser.add_argument(
        "--ui-backend",
        choices=["streamlit", "flask"],
        default="streamlit",
        help="Choose UI backend for --mode ui (default: streamlit).",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Optional JSON configuration to preload into the Streamlit UI.",
    )
    parser.add_argument(
        "--guided-ui",
        action="store_true",
        help="Enable guided walkthrough hints when using --mode ui.",
    )
    parser.add_argument(
        "--batch-guided-ui",
        action="store_true",
        help="Highlight batch processing hints when using --mode ui.",
    )
    return parser.parse_args()


def launch_guided_interface(host: str, port: int, no_browser: bool, config: Optional[Path] = None) -> None:
    print(f"[guided] Starting Guided Individual Interface on {host}:{port}")
    launch_streamlit_unified(
        host=host,
        port=port,
        no_browser=no_browser,
        guided=True,
        config=config,
    )


def launch_batch_guided_interface(host: str, port: int, no_browser: bool, config: Optional[Path] = None) -> None:
    print(f"[batch-guided] Starting Guided Batch Interface on {host}:{port}")
    launch_streamlit_unified(
        host=host,
        port=port,
        no_browser=no_browser,
        batch_guided=True,
        config=config,
    )


def launch_all_interfaces(host: str, port: int, no_browser: bool, config: Optional[Path] = None) -> None:
    print("[all-interfaces] Deprecated: launching unified Streamlit app instead.")
    launch_streamlit_unified(host=host, port=port, no_browser=no_browser, config=config)


def main() -> int:
    args = parse_args()

    if args.mode == "demo":
        run_demo(args.skip_install, args.upgrade, args.open_preview)
    elif args.mode == "guided":
        install_dependencies(args.skip_install, args.upgrade)
        launch_guided_interface(args.host, args.port, args.no_browser, config=args.config)
    elif args.mode == "batch-guided":
        install_dependencies(args.skip_install, args.upgrade)
        launch_batch_guided_interface(args.host, args.port, args.no_browser, config=args.config)
    else:
        run_ui(
            args.skip_install,
            args.upgrade,
            args.host,
            args.port,
            args.no_browser,
            ui_backend=args.ui_backend,
            guided=args.guided_ui,
            batch_guided=args.batch_guided_ui,
            config=args.config,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
