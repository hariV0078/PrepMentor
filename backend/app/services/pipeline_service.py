from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from collections.abc import Awaitable, Callable
from app.services.sentence_utils import extract_complete_sentences, sanitize_for_tts
from app.services.stt_service import STTService
from app.services.llm_service import LLMService
from app.services.tts_service import TTSService


logger = logging.getLogger(__name__)


SendAudioCallable = Callable[[bytes], Awaitable[None]]
SendTextCallable = Callable[[str], Awaitable[None]]


@dataclass
class PipelineResult:
    transcript: str


class PipelineService:
    def __init__(self, stt_service: STTService, llm_service: LLMService, tts_service: TTSService, sample_rate: int) -> None:
        self.stt_service = stt_service
        self.llm_service = llm_service
        self.tts_service = tts_service
        self.sample_rate = sample_rate

    async def process_turn(self, pcm_bytes: bytes, send_audio: SendAudioCallable, send_text: SendTextCallable) -> PipelineResult:
        transcript = await self.stt_service.transcribe(pcm_bytes)
        if not transcript:
            return PipelineResult(transcript="")

        logger.info("[PIPELINE] Turn start | transcript=%r", transcript)
        await send_text(f"USER:{transcript}")

        try:
            stream_buffer = ""
            sentence_index = 0

            async for token in self.llm_service.stream_response(transcript):
                stream_buffer += token
                logger.debug("[PIPELINE] Token received | buffer=%r", stream_buffer)
                completed, remainder = extract_complete_sentences(stream_buffer)
                stream_buffer = remainder

                for sentence in completed:
                    sentence_index += 1
                    logger.info("[PIPELINE] Sentence #%d dispatched | text=%r", sentence_index, sentence)
                    await send_text(f"AI:{sentence}")

                    clean_text = sanitize_for_tts(sentence)
                    if clean_text:
                        logger.debug("[PIPELINE] TTS start | sentence=%r", clean_text)
                        await self._synthesize_sentence(clean_text, send_audio)
                        logger.debug("[PIPELINE] TTS done  | sentence=%r", clean_text)

            logger.info("[PIPELINE] LLM stream ended | stream_buffer=%r", stream_buffer)

            if stream_buffer.strip():
                tail = stream_buffer.strip()
                if len(tail.split()) >= 2:
                    # Yield to the event loop so any pending CancelledError fires here
                    # before we queue the partial tail — prevents incomplete sentences
                    # from being sent when the pipeline is cancelled mid-stream.
                    await asyncio.sleep(0)
                    logger.info("[PIPELINE] Tail flushed | text=%r", tail)
                    await send_text(f"AI:{tail}")
                    clean_tail = sanitize_for_tts(tail)
                    if clean_tail:
                        await self._synthesize_sentence(clean_tail, send_audio)
                else:
                    logger.info("[PIPELINE] Tail suppressed (< 2 words) | text=%r", stream_buffer.strip())

            await send_text("CMD:stream_end")
            logger.info("[PIPELINE] Turn complete | sentences=%d", sentence_index)

            return PipelineResult(transcript=transcript)
        except asyncio.CancelledError:
            logger.info("[PIPELINE] Turn cancelled | stream_buffer=%r", stream_buffer)
            raise

    async def _synthesize_sentence(self, sentence: str, send_audio: SendAudioCallable) -> None:
        try:
            audio = await self.tts_service.synthesize(sentence)
            if audio:
                await send_audio(audio)
        except Exception as exc:
            logger.warning("TTS sentence synthesis failed: %s", exc)
