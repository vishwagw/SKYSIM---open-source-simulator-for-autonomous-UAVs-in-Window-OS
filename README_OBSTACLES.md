# SKYSIM — Obstacle Feature README

This file documents the new obstacle feature added to the SKYSIM Prototype 2 UI and backend.

## Summary
- A left-side "Obstacle" panel was added to `app.html` to create and manage obstacles in the simulation.
- Obstacles are rendered as cylindrical pillars in the Three.js scene and stored in an `obstacles` array.
- The drone has a simple XZ-plane avoidance behavior (repulsive steering) implemented in `updateDronePhysics`.
- The frontend sends an `obstacles` message to the backend on connect / when obstacles change so the server can log or use them.

## Files changed
- `app.html` — added:
  - A left-side `#obstaclePanel` UI with Add/Clear buttons, a live count, and a list of obstacles.
  - `createObstacle`, `addRandomObstacle`, `clearObstacles`, `sendObstacles`, and `updateObstacleUI` functions.
  - Obstacle avoidance logic (repulsive steering) inside `updateDronePhysics`.
- `backend/server.py` — small addition to log incoming messages of type `"obstacles"`.

## How obstacles work
- Each obstacle is represented in the frontend as an object: `{ mesh, position: THREE.Vector3, radius }`.
- Obstacles are visualized as cylinders placed on the ground (y = height/2).
- The avoidance algorithm (prototype): when the drone is `missionActive`, it computes a repulsive force from nearby obstacles on the XZ plane.
  - A `safeDistance` margin is added to each obstacle's radius to determine the avoidance threshold.
  - A steering vector is applied to the drone's X/Z velocity with clamping to a `maxSpeed`.
- The frontend will send to backend messages like:
  ```json
  { "type": "obstacles", "obstacles": [ { "x": 10.5, "z": -3.2, "r": 2.3 }, ... ] }
  ```

## How to run and test (PowerShell)
1. Start the backend server (or use the desktop launcher which will start it automatically):

```powershell
cd "E:\Central Brain Unit\Drone Autonomy Core\SKYSIM\Prototype 2"
python backend\server.py
```

Or (if you have pywebview and the dependencies installed):

```powershell
python launch_desktop.py
```

2. Open `app.html` in a browser (or let pywebview open it). The Obstacle panel appears on the left.
3. Click "Add Obstacle" multiple times to place random obstacles. The panel shows the count and a small list.
4. Click "Connect Python" to send the obstacle list to the backend (server logs will show it).
5. Click "Start Mission" — when the drone approaches obstacles it will apply avoidance steering.
6. Use "Clear" to remove all obstacles.

## Quick checks
- Verify frontend console (Console toggle) for messages like `➕ Obstacle added` and `Failed to send obstacles` (if backend disconnected).
- Check backend terminal for lines like `Obstacles from ('127.0.0.1', 54321): [{...}]` after connecting.

## Troubleshooting
- WebSocket connection failed? Ensure the backend is running and listening on port `8765`.
- If obstacles don't appear: make sure JavaScript is enabled and that `app.html` is the modified version (browser cache may show an older file).
- If avoidance looks jittery: it's a simple reactive steering algorithm. Consider smoothing velocities or increasing prediction horizon.

## Extending this feature (suggestions)
- Click-to-place mode: let the user click/tap on the ground to place obstacles precisely.
- Drag-to-move obstacles and per-obstacle properties (color, weight, shape).
- Implement persistent save/load for obstacles (JSON file or local storage).
- Replace reactive steering with a lightweight path planner (A*, RRT) for smoother avoidance.
- Visual debug overlays (danger radius, avoidance vector arrows).

## Where to edit
- Edit `app.html` for UI/JS/Three.js behavior.
- Edit `backend/server.py` to consume `obstacles` messages for planning or logging.

---

If you want, I can also commit a small `docs/` folder and add an illustrated screenshot workflow or implement click-to-place placement next. Let me know which improvement you'd like next.
