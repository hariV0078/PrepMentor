from __future__ import annotations

import asyncio
import logging
from app.core.config import Settings
from app.services.audio_utils import pcm16_to_float32


logger = logging.getLogger(__name__)


class STTService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._model = None

    async def warmup(self) -> None:
        if self._model is not None:
            return
        try:
            from faster_whisper import WhisperModel

            # Use CUDA explicitly, GTX 1650 fully supports float16
            # We use int8_float16 quantization to guarantee it fits entirely in 4GB VRAM
            self._model = WhisperModel(self.settings.whisper_model, device="cuda", compute_type="int8_float16")
            logger.info("Loaded Faster-Whisper model: %s on CUDA (int8)", self.settings.whisper_model)
        except Exception as exc:
            logger.warning("Faster-Whisper unavailable, transcription fallback enabled: %s", exc)
            self._model = None

    async def transcribe(self, pcm_bytes: bytes) -> str:
        if not pcm_bytes:
            return ""

        if self._model is None:
            await self.warmup()

        if self._model is None:
            return ""

        # Convert PCM16 bytes to float32 numpy array and pass directly to
        # faster-whisper — no temp file, no Windows file-lock issues.
        audio = pcm16_to_float32(pcm_bytes)
        loop = asyncio.get_event_loop()

        def run_transcription():
            segments, _ = self._model.transcribe(
                audio,
                language="en",
                vad_filter=False,
                beam_size=1,
            )
            return " ".join(segment.text.strip() for segment in segments if segment.text.strip())

        return await loop.run_in_executor(None, run_transcription)
