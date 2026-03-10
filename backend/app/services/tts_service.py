from __future__ import annotations

import asyncio
import logging
import math
import numpy as np
from app.core.config import Settings
from app.services.audio_utils import float32_to_pcm16_bytes, pcm16_bytes_to_wav_bytes


logger = logging.getLogger(__name__)


class TTSService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._kokoro = None

    async def warmup(self) -> None:
        if self._kokoro is not None:
            return
        try:
            from kokoro_onnx import Kokoro
            import httpx
            import os

            model_dir = os.path.join(os.path.dirname(__file__), "..", "..", "models")
            os.makedirs(model_dir, exist_ok=True)
            
            onnx_path = os.path.join(model_dir, "kokoro-v0_19.onnx")
            voices_path = os.path.join(model_dir, "voices.bin")

            if not os.path.exists(onnx_path) or not os.path.exists(voices_path):
                logger.info("Downloading Kokoro models... This may take a minute.")
                
                async def download_file(url: str, dest: str):
                    # We must follow redirects because GitHub releases redirect to AWS S3 binaries
                    async with httpx.AsyncClient(follow_redirects=True, timeout=120.0) as client:
                        async with client.stream("GET", url) as r:
                            r.raise_for_status()
                            with open(dest, "wb") as f:
                                async for chunk in r.aiter_bytes(chunk_size=8192):
                                    f.write(chunk)

                if not os.path.exists(onnx_path):
                    logger.info("Downloading kokoro-v0_19.onnx...")
                    await download_file("https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/kokoro-v0_19.onnx", onnx_path)
                
                if not os.path.exists(voices_path):
                    logger.info("Downloading voices.bin...")
                    await download_file("https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/voices.bin", voices_path)

            self._kokoro = Kokoro(onnx_path, voices_path)
            logger.info("Loaded Kokoro TTS (ONNX) backend")
        except Exception as exc:
            logger.warning("Kokoro TTS unavailable, synthetic fallback enabled: %s", exc)
            self._kokoro = None

    async def synthesize(self, text: str) -> bytes:
        if not text.strip():
            return b""

        if self._kokoro is None:
            await self.warmup()

        if self._kokoro is None:
            return await self._fallback_sine_wave(text)

        try:
            loop = asyncio.get_running_loop()
            
            # kokoro_onnx returns (audio_samples, sample_rate)
            # We want to resample if needed, but kokoro is usually 24kHz.
            # We'll just generate the PCM audio.
            samples, sr = await loop.run_in_executor(
                None, 
                lambda: self._kokoro.create(text, voice="af_bella", speed=1.1, lang="en-us")
            )
            
            # Convert float32 array (-1.0 to 1.0) to 16-bit PCM bytes
            pcm16 = float32_to_pcm16_bytes(samples.astype(np.float32))
            
            # We need to wrap it in a proper WAV container
            # The client expects either raw PCM or WAV. Our frontend looks for arraybuffer.
            # Using pcm16_bytes_to_wav_bytes handles the wrapper
            return pcm16_bytes_to_wav_bytes(pcm16, sample_rate=sr)
            
        except Exception as exc:
            logger.warning("Kokoro synthesis failed, using fallback audio: %s", exc)

        return await self._fallback_sine_wave(text)

    async def _fallback_sine_wave(self, text: str) -> bytes:
        duration_s = min(max(len(text) * 0.03, 0.25), 1.8)
        sr = self.settings.sample_rate
        sample_count = int(duration_s * sr)
        t = np.linspace(0.0, duration_s, sample_count, endpoint=False)
        waveform = 0.06 * np.sin(2 * math.pi * 220.0 * t)
        pcm = float32_to_pcm16_bytes(waveform.astype(np.float32))
        return pcm16_bytes_to_wav_bytes(pcm, sample_rate=sr)
