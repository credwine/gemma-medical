"""Gemma Medical -- Fully Automated One-Click Installer.

Installs EVERYTHING automatically. No user input needed except
one optional prompt for startup. Downloads and installs Ollama,
pulls Gemma 4, installs all Python deps, creates launchers.

Usage:
    python install.py           # Full automated install
    python install.py --silent  # No prompts at all
"""

import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request


OLLAMA_WINDOWS_URL = "https://ollama.com/download/OllamaSetup.exe"
OLLAMA_MAC_URL = "https://ollama.com/download/Ollama-darwin.zip"
OLLAMA_LINUX_CMD = "curl -fsSL https://ollama.com/install.sh | sh"

SILENT = "--silent" in sys.argv


def print_banner():
    print()
    print("=" * 60)
    print("  GEMMA MEDICAL INSTALLER")
    print("  Privacy-First Hospital Management System")
    print("  Powered by Gemma 4 -- 100% Local AI")
    print("  Fully Automated -- Sit Back and Relax")
    print("=" * 60)
    print()


def check_python():
    """Step 1: Verify Python version."""
    v = sys.version_info
    print(f"[1/6] Python {v.major}.{v.minor}.{v.micro}")
    if v.major < 3 or (v.major == 3 and v.minor < 10):
        print("      Python 3.10+ required. Please upgrade.")
        print("      https://www.python.org/downloads/")
        sys.exit(1)
    print("      OK")


def install_ollama():
    """Step 2: Download and install Ollama automatically if not present."""
    print("[2/6] Checking Ollama...")

    if shutil.which("ollama"):
        print("      Ollama already installed")
        return True

    system = platform.system()
    print("      Ollama not found -- installing automatically...")

    try:
        if system == "Windows":
            installer_path = os.path.join(tempfile.gettempdir(), "OllamaSetup.exe")
            print("      Downloading Ollama installer...")
            urllib.request.urlretrieve(OLLAMA_WINDOWS_URL, installer_path)
            print(f"      Downloaded to {installer_path}")

            print("      Running Ollama installer (this may take a minute)...")
            subprocess.run([installer_path, "/VERYSILENT", "/NORESTART"], check=True)
            print("      Ollama installed successfully")

            # Ollama may need a moment to register in PATH
            ollama_paths = [
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Ollama", "ollama.exe"),
                os.path.join(os.environ.get("PROGRAMFILES", ""), "Ollama", "ollama.exe"),
                shutil.which("ollama"),
            ]
            for p in ollama_paths:
                if p and os.path.exists(p):
                    os.environ["PATH"] = os.path.dirname(p) + os.pathsep + os.environ["PATH"]
                    print(f"      Found at: {p}")
                    break

            return True

        elif system == "Darwin":
            print("      Downloading Ollama for macOS...")
            zip_path = os.path.join(tempfile.gettempdir(), "Ollama-darwin.zip")
            urllib.request.urlretrieve(OLLAMA_MAC_URL, zip_path)
            subprocess.run(["unzip", "-o", zip_path, "-d", "/Applications"], check=True)
            print("      Ollama installed to /Applications")
            return True

        elif system == "Linux":
            print("      Installing Ollama via official script...")
            subprocess.run(["bash", "-c", OLLAMA_LINUX_CMD], check=True)
            print("      Ollama installed")
            return True

    except Exception as e:
        print(f"      Auto-install failed: {e}")
        print()
        print("      Please install Ollama manually:")
        print("      https://ollama.com/download")
        print()
        if SILENT:
            return False
        resp = input("      Continue without Ollama? (y/n): ").strip().lower()
        return resp == "y"

    return False


def start_ollama():
    """Step 3: Make sure Ollama service is running."""
    print("[3/6] Starting Ollama service...")

    # Check if already running
    try:
        import httpx
        r = httpx.get("http://localhost:11434/api/tags", timeout=3)
        if r.status_code == 200:
            print("      Ollama is running")
            return True
    except Exception:
        pass

    system = platform.system()
    try:
        if system == "Windows":
            ollama_exe = shutil.which("ollama")
            if not ollama_exe:
                for p in [
                    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Ollama", "ollama.exe"),
                    os.path.join(os.environ.get("PROGRAMFILES", ""), "Ollama", "ollama.exe"),
                ]:
                    if os.path.exists(p):
                        ollama_exe = p
                        break

            if ollama_exe:
                subprocess.Popen(
                    [ollama_exe, "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                time.sleep(3)
                print("      Ollama started")
                return True
        else:
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(3)
            print("      Ollama started")
            return True
    except Exception as e:
        print(f"      Could not start Ollama: {e}")
        print("      Start Ollama manually, then run install.py again")

    return False


def install_deps():
    """Step 4: Install all Python dependencies."""
    print("[4/6] Installing Python dependencies...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "-r", "requirements.txt",
        "--quiet",
    ])
    print("      All dependencies installed")


def pull_gemma():
    """Step 5: Pull the Gemma 4 model."""
    print("[5/6] Pulling Gemma 4 model (~9.6 GB, one-time download)...")
    print("      This may take several minutes on first install.")
    try:
        subprocess.check_call(["ollama", "pull", "gemma4:e4b"])
        print("      Gemma 4 E4B ready")
        return True
    except FileNotFoundError:
        print("      Skipped (Ollama not in PATH)")
        return False
    except subprocess.CalledProcessError:
        print("      Failed. Make sure Ollama is running, then run:")
        print("      ollama pull gemma4:e4b")
        return False


def create_shortcuts():
    """Step 6: Create launcher scripts for each platform."""
    print("[6/6] Creating launchers...")
    system = platform.system()
    app_dir = os.path.abspath(".")
    python = sys.executable

    if system == "Windows":
        # All-in-one launcher
        with open("Gemma Medical.bat", "w") as f:
            f.write('@echo off\n')
            f.write(f'cd /d "{app_dir}"\n')
            f.write('echo.\n')
            f.write('echo ============================================================\n')
            f.write('echo   GEMMA MEDICAL -- Privacy-First Hospital Management System\n')
            f.write('echo ============================================================\n')
            f.write('echo.\n')
            f.write('echo Starting Gemma Medical...\n')
            f.write('echo Browser will open automatically at http://localhost:8000\n')
            f.write('echo.\n')
            f.write(f'"{python}" gemma_medical_app.py\n')
            f.write('pause\n')
        print('      Created: "Gemma Medical.bat" (all-in-one launcher)')

        # Standalone server launcher
        with open("Start Server.bat", "w") as f:
            f.write(f'@echo off\ncd /d "{app_dir}"\n')
            f.write('echo Starting Gemma Medical server...\n')
            f.write(f'"{python}" run.py\npause\n')
        print("      Created: Start Server.bat")

        # Auto-start on login (optional)
        if SILENT:
            add_startup = False
        else:
            print()
            resp = input("      Start Gemma Medical automatically on login? (y/n): ").strip().lower()
            add_startup = resp == "y"

        if add_startup:
            try:
                startup_dir = os.path.join(
                    os.environ.get("APPDATA", ""),
                    "Microsoft", "Windows", "Start Menu", "Programs", "Startup",
                )
                shortcut_path = os.path.join(startup_dir, "Gemma Medical.bat")
                with open(shortcut_path, "w") as f:
                    f.write('@echo off\n')
                    f.write(f'cd /d "{app_dir}"\n')
                    f.write(f'start /min "" "{python}" gemma_medical_app.py\n')
                print("      Gemma Medical added to Windows startup")
            except Exception as e:
                print(f"      Could not add to startup: {e}")

    else:
        # Linux / macOS launchers
        for name, cmd in [
            ("gemma-medical.sh", (
                f'#!/bin/bash\ncd "$(dirname "$0")"\n'
                f'echo "Starting Gemma Medical..."\n'
                f'echo "Browser will open at http://localhost:8000"\n'
                f'{python} gemma_medical_app.py'
            )),
            ("start-server.sh", (
                f'#!/bin/bash\ncd "$(dirname "$0")"\n{python} run.py'
            )),
        ]:
            with open(name, "w") as f:
                f.write(cmd + "\n")
            os.chmod(name, 0o755)
        print("      Created: gemma-medical.sh, start-server.sh")


def print_summary():
    print()
    print("=" * 60)
    print("  INSTALLATION COMPLETE")
    print("=" * 60)
    print()
    if platform.system() == "Windows":
        print('  Double-click "Gemma Medical.bat" to start everything.')
    else:
        print("  Run ./gemma-medical.sh to start everything.")
    print()
    print("  What happens:")
    print("  - Ollama starts automatically (if not already running)")
    print("  - Gemma Medical opens at http://localhost:8000")
    print("  - Your browser opens automatically")
    print()
    print("  All AI runs locally. No patient data ever leaves your device.")
    print()


def main():
    print_banner()
    check_python()
    install_ollama()
    start_ollama()
    install_deps()
    pull_gemma()
    create_shortcuts()
    print_summary()


if __name__ == "__main__":
    main()
