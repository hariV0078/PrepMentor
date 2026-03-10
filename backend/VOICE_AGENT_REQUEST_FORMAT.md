# Voice Agent: Startup + Request Format

## 1) Start the backend

From `backend` folder:

1. Activate venv (PowerShell):
   - `.\.venv\Scripts\Activate.ps1`
2. Ensure env file exists:
   - `Copy-Item .env.example .env`
3. Start server:
   - `python app/main.py`

Server should listen on:
- `http://127.0.0.1:8000`

## 2) Health and readiness checks

- Health:
  - `GET http://127.0.0.1:8000/health`
  - Response: `{ "status": "ok" }`

- Readiness:
  - `GET http://127.0.0.1:8000/ready`
  - Response includes `services` and fallback notes.

## 3) Request format for Postman (WebSocket)

Create a **WebSocket** request in Postman:
- URL: `ws://127.0.0.1:8000/ws/audio`

Send messages as **binary** (not JSON/text):
- Encoding: PCM16 little-endian
- Channels: mono
- Sample rate: 16,000 Hz
- Chunk size: ~20 ms per frame (recommended)

Server responses:
- Text frame: `TRANSCRIPT:<recognized text>`
- Binary frame: synthesized audio bytes (WAV)

## 4) Common connection-refused fixes

1. Use `127.0.0.1`, not `0.0.0.0`, in Postman.
2. Confirm backend is running before connect.
3. Check port 8000 is open locally:
   - `Test-NetConnection 127.0.0.1 -Port 8000`
4. Verify endpoint exactly:
   - `ws://127.0.0.1:8000/ws/audio`
