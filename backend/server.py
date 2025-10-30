#!/usr/bin/env python3
"""
Simple WebSocket backend for the SKYSIM prototype.
Sends periodic command messages to connected frontend(s) and logs incoming telemetry/status messages.
"""
import asyncio
import json
import random
import websockets

COMMANDS = [
    {"action": "patrol", "data": "Executing search pattern"},
    {"action": "avoid", "data": "Obstacle detected, adjusting path"},
    {"action": "navigate", "data": "Moving to waypoint"},
    {"action": "hover", "data": "Maintaining position"}
]


async def handler(websocket, path=None):
    peer = websocket.remote_address
    print(f"Client connected: {peer}")

    async def sender():
        while True:
            await asyncio.sleep(2)
            cmd = random.choice(COMMANDS)
            message = {"type": "command", "action": cmd["action"], "data": cmd["data"]}
            try:
                await websocket.send(json.dumps(message))
            except Exception as e:
                print("Send error:", e)
                break

    send_task = asyncio.create_task(sender())

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
            except Exception:
                print("Received non-JSON message:", message)
                continue

            # Simple logging; in a real backend you might validate and respond
            msg_type = data.get("type")
            if msg_type == "telemetry":
                pos = data.get("position")
                batt = data.get("battery")
                mission = data.get("missionActive")
                print(f"Telemetry from {peer}: pos={pos} batt={batt} mission={mission}")
            elif msg_type == "status":
                print(f"Status from {peer}: {data}")
            elif msg_type == "nl_command" or msg_type == "nl_text":
                # Acknowledge natural-language input back to frontend
                original = data.get("original") or data.get("text")
                command = data.get("command")
                ack = {
                    "type": "ack",
                    "message": f"Received NL input: {original}",
                    "command": command
                }
                try:
                    await websocket.send(json.dumps(ack))
                except Exception as e:
                    print("Ack send error:", e)
                print(f"NL input from {peer}: {original} -> {command}")
            elif msg_type == "obstacles":
                print(f"Obstacles from {peer}: {data.get('obstacles')}")
            else:
                print(f"Message from {peer}: {data}")

    except websockets.exceptions.ConnectionClosed:
        print(f"Client disconnected: {peer}")
    finally:
        send_task.cancel()


async def main():
    print("Starting backend WebSocket server on ws://0.0.0.0:8765")
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped by user")
