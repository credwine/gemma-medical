"""Quick-start script for Gemma Medical.

Usage:
    python run.py          # Start the server
    python run.py --setup  # Pull Gemma 4 model via Ollama first
"""

import subprocess
import sys
import httpx


def check_ollama():
    """Check if Ollama is running."""
    try:
        r = httpx.get("http://localhost:11434/api/tags", timeout=5)
        return r.status_code == 200
    except (httpx.ConnectError, httpx.HTTPError):
        return False


def pull_model(model="gemma4:e4b"):
    """Pull the Gemma 4 model via Ollama."""
    print(f"Pulling {model}... This may take a few minutes on first run.")
    subprocess.run(["ollama", "pull", model], check=True)
    print(f"{model} is ready.")


def main():
    if "--setup" in sys.argv:
        if not check_ollama():
            print("Ollama is not running. Please start Ollama first:")
            print("  https://ollama.com/download")
            sys.exit(1)
        pull_model()
        return

    if not check_ollama():
        print("WARNING: Ollama is not running. Gemma Medical needs Ollama + Gemma 4 for AI features.")
        print("Start Ollama, then run: python run.py --setup")
        print()

    print("Starting Gemma Medical on http://localhost:8000")
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "backend.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload",
    ])


if __name__ == "__main__":
    main()
