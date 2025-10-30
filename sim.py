#!/usr/bin/env python3
"""
Simple desktop launcher for SKYSIM using pywebview.

This script will:
- Attempt to start the backend WebSocket server (backend/server.py) in a background thread
  unless it detects a server already listening on port 8765.
- Launch a pywebview window that loads the local `app.html` file via the file:// URL.

Run:
    python launch_desktop.py

Install deps (from project root):
    python -m pip install -r backend/requirements.txt

Notes:
- On Windows, pywebview will choose an available GUI backend. For a better developer experience
  you can run with `webview.start(debug=True)` (this script already enables debug mode).
- If you plan to package this app (pyinstaller / briefcase), you can use this script as the
  application entry point.
"""

import os
import sys
import threading
import time
import socket

PORT = 8765
HOST = '127.0.0.1'

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_HTML = os.path.join(PROJECT_ROOT, 'app.html')


def is_port_open(host: str, port: int, timeout: float = 0.8) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def start_backend():
    """Import and run the backend server main coroutine."""
    try:
        # Import here so that the main program can fail early if pywebview is missing
        import asyncio
        # Ensure backend package importable
        sys.path.insert(0, PROJECT_ROOT)
        import backend.server as server
        print('Starting backend server (in-thread).')
        asyncio.run(server.main())
    except Exception as e:
        print('Backend server terminated with exception:', e)


def ensure_backend_running():
    if is_port_open(HOST, PORT):
        print(f"Detected backend already running on {HOST}:{PORT}; not starting new server.")
        return

    t = threading.Thread(target=start_backend, daemon=True)
    t.start()

    # wait a short while for server to appear
    for i in range(30):
        if is_port_open(HOST, PORT):
            print(f'Backend listening on {HOST}:{PORT}')
            return
        time.sleep(0.1)

    print('Warning: backend did not start within timeout; continuing to open UI.')


def main():
    if not os.path.exists(APP_HTML):
        print('ERROR: app.html not found at expected path:', APP_HTML)
        sys.exit(1)

    ensure_backend_running()

    try:
        import webview
    except Exception as e:
        print('pywebview is not installed. Install requirements with:')
        print('  python -m pip install -r backend/requirements.txt')
        raise

    url = 'file://' + APP_HTML.replace('\\', '/')
    window = webview.create_window('SKYSIM Desktop', url, width=1280, height=800, resizable=True)

    # Start webview (debug True shows devtools where supported)
    webview.start(debug=True)


if __name__ == '__main__':
    main()
