from __future__ import annotations

import logging
import numpy as np
from app.core.config import Settings


logger = logging.getLogger(__name__)


class VADService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._silero = None
        self._load_model()

    def _load_model(self) -> None:
        try:
            from silero_vad import load_silero_vad

            self._silero = load_silero_vad()
            logger.info("Loaded Silero VAD model")
        except Exception as exc:
            logger.warning("Silero VAD unavailable, fallback energy VAD enabled: %s", exc)
            self._silero = None

    def is_speech(self, frame: np.ndarray) -> bool:
        if frame.size == 0:
            return False

        if self._silero is not None:
            try:
                import torch

                with torch.no_grad():
                    score = float(self._silero(torch.from_numpy(frame), self.settings.sample_rate).item())
                return score >= self.settings.vad_threshold
            except Exception:
                pass

        energy = float(np.mean(np.abs(frame)))
        return energy >= 0.01
