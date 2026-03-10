# GETLANDED Voice Backend (Python)

## Run locally

1. Create virtual environment and activate it.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Copy env file:
   - `copy .env.example .env`
4. Set `GEMINI_API_KEY` in `.env`.
5. Start server:
   - `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

Note:
- The backend has a built-in fallback TTS generator.
- `kokoro-tts` is not pinned in `requirements.txt` because a stable PyPI package name/version may vary.
- Gemini integration uses `google-genai`.
- When `GEMINI_API_KEY` is missing, the backend serves a lightweight LLM fallback response.
- `GET /ready` returns `not_ready` when `GEMINI_API_KEY` is set but Gemini client initialization fails.

## Endpoints

- `GET /health`
- `GET /ready`
- `WS /ws/audio`

## WebSocket behavior

- Accepts binary PCM16 mono chunks (expected 16kHz).
- Detects end-of-turn via VAD + silence frame threshold.
- Sends transcript text frame (`TRANSCRIPT:<text>`).
- Sends synthesized audio as binary WAV chunks.

## Additional guide

- See `VOICE_AGENT_REQUEST_FORMAT.md` for Postman request format and startup steps.

## Rollback (Gemini SDK)

If Gemini SDK migration causes issues in your environment:

1. Revert the migration changes in:
   - `requirements.txt`
   - `app/services/llm_service.py`
   - `app/core/config.py`
   - `app/api/health.py`
2. Reinstall dependencies:
   - `pip install -r requirements.txt`
3. If using Docker, rebuild and restart:
   - `docker compose build --no-cache voice-backend`
   - `docker compose up -d`
