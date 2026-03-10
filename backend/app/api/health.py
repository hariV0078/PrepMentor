from fastapi import APIRouter, Request


router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def readiness_check(request: Request) -> dict:
    backend_state = getattr(request.app.state, "backend_state", None)
    if backend_state is None:
        return {
            "status": "not_ready",
            "reason": "backend_state_unavailable",
        }

    stt_loaded = backend_state.stt_service._model is not None
    llm_loaded = backend_state.llm_service._client is not None
    tts_loaded = backend_state.tts_service._kokoro is not None

    services = {
        "vad": True,
        "stt": stt_loaded,
        "llm": llm_loaded,
        "tts": tts_loaded,
    }

    llm_required = bool((backend_state.settings.gemini_api_key or "").strip())
    if llm_required and not llm_loaded:
        return {
            "status": "not_ready",
            "reason": "llm_unavailable_with_api_key",
            "preload_models": backend_state.settings.preload_models,
            "services": services,
            "notes": {
                "stt": "lazy-loaded when PRELOAD_MODELS=false",
                "llm": "GEMINI_API_KEY is set but Gemini client failed to initialize",
                "tts": "fallback audio synthesis enabled when Kokoro backend is unavailable",
            },
        }

    return {
        "status": "ready",
        "preload_models": backend_state.settings.preload_models,
        "services": services,
        "notes": {
            "stt": "lazy-loaded when PRELOAD_MODELS=false",
            "llm": "fallback response enabled when GEMINI_API_KEY is missing",
            "tts": "fallback audio synthesis enabled when Kokoro backend is unavailable",
        },
    }
