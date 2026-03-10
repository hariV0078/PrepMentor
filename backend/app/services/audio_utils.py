from __future__ import annotations

import io
import wave
import numpy as np


def pcm16_to_float32(audio_bytes: bytes) -> np.ndarray:
    if not audio_bytes:
        return np.array([], dtype=np.float32)
    pcm = np.frombuffer(audio_bytes, dtype=np.int16)
    return (pcm.astype(np.float32) / 32768.0).clip(-1.0, 1.0)


def float32_to_pcm16_bytes(audio: np.ndarray) -> bytes:
    clipped = np.clip(audio, -1.0, 1.0)
    pcm = (clipped * 32767.0).astype(np.int16)
    return pcm.tobytes()


def pcm16_bytes_to_wav_bytes(audio_bytes: bytes, sample_rate: int = 16000, channels: int = 1) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_bytes)
    return buffer.getvalue()
