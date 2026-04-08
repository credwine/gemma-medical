"""Gemma Medical -- Single Entry Point for PyInstaller Packaging.

Starts the FastAPI server on port 8000, opens the browser automatically,
and handles graceful shutdown on Ctrl+C.

Usage:
    python gemma_medical_app.py
"""

import multiprocessing
import signal
import sys
import threading
import time
import webbrowser

import uvicorn


SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000
STARTUP_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"


def open_browser():
    """Wait for the server to start, then open the browser."""
    time.sleep(2)
    print(f"Opening browser at {STARTUP_URL}")
    webbrowser.open(STARTUP_URL)


def main():
    multiprocessing.freeze_support()

    print()
    print("=" * 60)
    print("  GEMMA MEDICAL")
    print("  Privacy-First Hospital Management System")
    print("  Powered by Gemma 4 -- 100% Local AI")
    print("=" * 60)
    print()
    print(f"  Server: {STARTUP_URL}")
    print("  Press Ctrl+C to stop")
    print()

    # Open browser in a background thread
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

    # Graceful shutdown on Ctrl+C
    def handle_signal(sig, frame):
        print()
        print("Shutting down Gemma Medical...")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # Start uvicorn server
    uvicorn.run(
        "backend.main:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        log_level="info",
    )


if __name__ == "__main__":
    main()
