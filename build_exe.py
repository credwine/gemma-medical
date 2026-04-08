"""Gemma Medical -- PyInstaller Build Script.

Builds a standalone executable at dist/GemmaMedical/GemmaMedical.exe.
Bundles the frontend, backend prompts, and all required Python modules.

Usage:
    python build_exe.py
"""

import os
import subprocess
import sys


def main():
    print()
    print("=" * 60)
    print("  GEMMA MEDICAL -- Building Standalone Executable")
    print("=" * 60)
    print()

    # Ensure PyInstaller is installed
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "pyinstaller", "--quiet",
        ])

    app_dir = os.path.abspath(".")
    frontend_dir = os.path.join(app_dir, "frontend")
    prompts_dir = os.path.join(app_dir, "backend", "prompts")
    backend_dir = os.path.join(app_dir, "backend")

    # Verify required directories exist
    for d, label in [
        (frontend_dir, "frontend/"),
        (prompts_dir, "backend/prompts/"),
        (backend_dir, "backend/"),
    ]:
        if not os.path.isdir(d):
            print(f"ERROR: Required directory not found: {label}")
            sys.exit(1)

    # Build the PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "GemmaMedical",
        "--noconfirm",
        "--clean",
        # Bundle data directories
        "--add-data", f"{frontend_dir}{os.pathsep}frontend",
        "--add-data", f"{prompts_dir}{os.pathsep}backend/prompts",
        "--add-data", f"{backend_dir}{os.pathsep}backend",
        # Hidden imports for uvicorn + fastapi ecosystem
        "--hidden-import", "uvicorn",
        "--hidden-import", "uvicorn.logging",
        "--hidden-import", "uvicorn.loops",
        "--hidden-import", "uvicorn.loops.auto",
        "--hidden-import", "uvicorn.protocols",
        "--hidden-import", "uvicorn.protocols.http",
        "--hidden-import", "uvicorn.protocols.http.auto",
        "--hidden-import", "uvicorn.protocols.websockets",
        "--hidden-import", "uvicorn.protocols.websockets.auto",
        "--hidden-import", "uvicorn.lifespan",
        "--hidden-import", "uvicorn.lifespan.on",
        "--hidden-import", "uvicorn.lifespan.off",
        "--hidden-import", "fastapi",
        "--hidden-import", "starlette",
        "--hidden-import", "starlette.responses",
        "--hidden-import", "starlette.routing",
        "--hidden-import", "starlette.middleware",
        "--hidden-import", "starlette.staticfiles",
        "--hidden-import", "httpx",
        "--hidden-import", "pydantic",
        "--hidden-import", "multipart",
        "--hidden-import", "jinja2",
        "--hidden-import", "aiofiles",
        # Backend modules
        "--hidden-import", "backend",
        "--hidden-import", "backend.main",
        "--hidden-import", "backend.config",
        "--hidden-import", "backend.ollama_client",
        "--hidden-import", "backend.routers",
        "--hidden-import", "backend.routers.assistant",
        "--hidden-import", "backend.routers.clinic",
        "--hidden-import", "backend.routers.drugs",
        "--hidden-import", "backend.routers.maternal",
        "--hidden-import", "backend.routers.medtranslate",
        "--hidden-import", "backend.routers.patients",
        "--hidden-import", "backend.routers.visits",
        "--hidden-import", "backend.routers.medications",
        "--hidden-import", "backend.routers.analytics",
        "--hidden-import", "backend.services",
        # Entry point
        "gemma_medical_app.py",
    ]

    print("Running PyInstaller...")
    print()
    subprocess.check_call(cmd)

    print()
    print("=" * 60)
    print("  BUILD COMPLETE")
    print("=" * 60)
    print()
    print("  Output: dist/GemmaMedical/GemmaMedical.exe")
    print()
    print("  To distribute:")
    print("  1. Zip the entire dist/GemmaMedical/ folder")
    print("  2. Users extract and double-click GemmaMedical.exe")
    print("  3. Ollama must be installed separately on the target machine")
    print("     (or bundle OllamaSetup.exe alongside the zip)")
    print()


if __name__ == "__main__":
    main()
