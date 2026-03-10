from __future__ import annotations

from dataclasses import dataclass
from app.core.config import Settings
from app.services.vad_service import VADService
from app.services.stt_service import STTService
from app.services.llm_service import LLMService
from app.services.tts_service import TTSService
from app.services.pipeline_service import PipelineService


@dataclass
class AppState:
    settings: Settings
    vad_service: VADService
    stt_service: STTService
    llm_service: LLMService
    tts_service: TTSService
    pipeline_service: PipelineService


async def build_state(settings: Settings) -> AppState:
    vad_service = VADService(settings)
    stt_service = STTService(settings)
    llm_service = LLMService(settings)
    tts_service = TTSService(settings)

    if settings.preload_models:
        try:
            await stt_service.warmup()
        except BaseException:
            pass
        try:
            await llm_service.warmup()
        except BaseException:
            pass
        try:
            await tts_service.warmup()
        except BaseException:
            pass

    pipeline_service = PipelineService(
        stt_service=stt_service,
        llm_service=llm_service,
        tts_service=tts_service,
        sample_rate=settings.sample_rate,
    )

    return AppState(
        settings=settings,
        vad_service=vad_service,
        stt_service=stt_service,
        llm_service=llm_service,
        tts_service=tts_service,
        pipeline_service=pipeline_service,
    )
