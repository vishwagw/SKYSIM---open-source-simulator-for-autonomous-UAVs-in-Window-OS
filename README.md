SKYSIM Prototype 2 — Python WebSocket backend

This workspace contains a simple frontend `app.html` (Three.js) and a minimal Python WebSocket backend in `backend/server.py`.

What the backend does
- Listens on ws://0.0.0.0:8765
- Sends a simple `command` JSON every 2 seconds to connected clients
- Logs incoming `telemetry` or other messages from the frontend

Quick start (Windows PowerShell)

1. Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r backend\requirements.txt
```

3. Run the backend server:

```powershell
python backend\server.py
```

Desktop launcher (pywebview)
---------------------------

You can run the app as a native desktop application using pywebview. The repository includes a small launcher script `launch_desktop.py` that will attempt to start the backend server (if needed) and open a window with the existing `app.html`.

1. Install dependencies (includes pywebview):

```powershell
pip install -r backend\requirements.txt
```

2. Run the desktop launcher:

```powershell
python launch_desktop.py
```

Notes:
- The launcher looks for `app.html` in the repository root and connects the frontend to the backend at `ws://localhost:8765`.
- If a backend is already running on port 8765 the launcher will not start another one.
- On Windows the pywebview debug mode is enabled by default for convenience so devtools may be available.

4. Open `app.html` in your browser (double-click or serve via a simple HTTP server). Click "Connect Python" in the UI to connect the frontend to the backend.

Notes
- The current frontend expects the backend at `ws://localhost:8765`.
- The websocket protocol is simple JSON messages with a `type` field. Examples:
  - Backend -> Frontend: {"type":"command","action":"patrol","data":"..."}
  - Frontend -> Backend: {"type":"telemetry","position":{...},"battery":...}

Security / production
- This server is a simple prototype for local testing. Do not expose it to the internet without proper authentication and transport security (use TLS / WSS).

Natural Language Controls
-------------------------

This simulator supports a simple natural-language input in the frontend to control the drone. The input is intentionally lightweight and keyword-based for now. It parses common phrases and converts them into simulator commands. The frontend applies the parsed command locally and also forwards it to the backend as a JSON message (type `nl_command`).

Supported phrases (examples):

- Take off: "take off", "takeoff", "launch" — optionally with altitude: "take off to 15" or "launch to 12.5"
- Land: "land", "landing"
- Hover / hold: "hover", "hold position", "hold"
- Move / Go to coordinates:
  - "go to x 10 z -5"  (explicit x/z)
  - "go to 10 -5"      (X then Z)
- Patrol / Search: "patrol", "search"
- Navigate (fallback): "navigate", "go to"

How it maps to simulator commands

- takeoff -> { type: 'command', action: 'takeoff', altitude?: number }
- land -> { type: 'command', action: 'land' }
- hover -> { type: 'command', action: 'hover' }
- move -> { type: 'command', action: 'move', target: { x, z } }
- patrol/navigate -> { type: 'command', action: 'patrol' | 'navigate' }

Testing the NL controls locally
-------------------------------

1. Start the Python backend (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
python backend\server.py
```

2. Open `app.html` in your browser (double-click or serve via a simple static server). Click the "Connect Python" button.

3. Use the Natural Language input in the top controls to send commands. Examples to try:

- "take off to 20"  — drone should ascend toward ~20m and mission becomes active.
- "go to x 5 z -8"  — drone should start moving toward X=5, Z=-8.
- "hover"           — drone velocity dampens and holds position.
- "land"            — drone should descend smoothly and stop when landed.

4. Observe the frontend console panel for parsed messages and the backend terminal for logged telemetry messages.

Notes and next improvements
---------------------------
- The NL parser is intentionally simple. If you want more natural phrasing ("ascend", "climb 5 meters", relative moves, or cardinal directions), I can extend the parser to support units and relative coordinates.
- The backend currently only logs received NL commands; we can make it acknowledge or respond with higher-level mission logic (e.g., only send commands when missionActive=true).
- For production or more sophisticated interaction, consider integrating a proper NLP service or a lightweight intent parser (e.g., Rasa, spaCy, or a small rule-based intent matcher).
