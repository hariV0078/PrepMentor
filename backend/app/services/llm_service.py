from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import AsyncGenerator
from app.core.config import Settings


logger = logging.getLogger(__name__)


SYSTEM_PROMPT = (
    "You are a helpful voice assistant. Rules:\n"
    "1. Keep responses under 3 sentences.\n"
    "2. End each sentence with . ! or ?\n"
    "3. Avoid long clauses before punctuation.\n"
    "4. Be conversational and concise."
)


class LLMService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client = None

    async def warmup(self) -> None:
        if self._client is not None:
            return
        if not self.settings.gemini_api_key:
            logger.warning("GEMINI_API_KEY not set; LLM fallback enabled")
            return

        try:
            from google import genai

            self._client = genai.Client(api_key=self.settings.gemini_api_key)
            logger.info("Loaded Gemini model: %s", self.settings.gemini_model)
        except Exception as exc:
            logger.warning("Gemini unavailable, LLM fallback enabled: %s", exc)
            self._client = None

    async def stream_response(self, text: str) -> AsyncGenerator[str, None]:
        if not text.strip():
            return

        if self._client is None:
            await self.warmup()

        if self._client is None:
            fallback = f"I heard: {text}. How can I help further?"
            for token in fallback.split(" "):
                await asyncio.sleep(0)
                yield token + " "
            return

        logger.info("[LLM] Stream start | prompt=%r", text)
        loop = asyncio.get_running_loop()

        def extract_text_from_chunk(chunk: object) -> list[str]:
            chunk_text = getattr(chunk, "text", None)
            if isinstance(chunk_text, str) and chunk_text:
                return [chunk_text]

            extracted: list[str] = []
            candidates = getattr(chunk, "candidates", None) or []
            for candidate in candidates:
                content = getattr(candidate, "content", None)
                parts = getattr(content, "parts", None) or []
                for part in parts:
                    if getattr(part, "thought", False):
                        continue
                    part_text = getattr(part, "text", None)
                    if isinstance(part_text, str) and part_text:
                        extracted.append(part_text)
            return extracted

        def collect_chunks() -> list[str]:
            import importlib

            genai_errors = importlib.import_module("google.genai.errors")
            genai_types = importlib.import_module("google.genai.types")

            generation_config = genai_types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.8,
                max_output_tokens=300,
            )
            retryable_status_codes = {408, 429, 500, 502, 503, 504}
            max_attempts = 2

            for attempt in range(1, max_attempts + 1):
                try:
                    chunks: list[str] = []
                    stream = self._client.models.generate_content_stream(
                        model=self.settings.gemini_model,
                        contents=text,
                        config=generation_config,
                    )
                    for chunk in stream:
                        texts = extract_text_from_chunk(chunk)
                        for part_text in texts:
                            logger.debug("[LLM] Chunk collected | text=%r", part_text)
                            chunks.append(part_text)
                    return chunks
                except genai_errors.APIError as exc:
                    status_code = getattr(exc, "status_code", None)
                    if status_code is None:
                        status_code = getattr(exc, "code", None)

                    if status_code in retryable_status_codes and attempt < max_attempts:
                        backoff_seconds = 0.4 * attempt
                        logger.warning(
                            "[LLM] Retryable Gemini error | status=%s | attempt=%d/%d",
                            status_code,
                            attempt,
                            max_attempts,
                        )
                        time.sleep(backoff_seconds)
                        continue

                    logger.warning("[LLM] Gemini API error | status=%s | error=%s", status_code, exc)
                    return []
                except Exception as exc:
                    logger.warning("[LLM] Gemini stream failed: %s", exc)
                    return []

            return []

        chunks = await loop.run_in_executor(None, collect_chunks)
        logger.debug("[LLM] Stream exhausted | total_chunks=%d", len(chunks))

        if not chunks:
            logger.warning("[LLM] Empty provider stream; using lightweight fallback")
            fallback = "Sorry, I missed that. Could you repeat it?"
            for token in fallback.split(" "):
                await asyncio.sleep(0)
                yield token + " "
            return

        for chunk_text in chunks:
            logger.debug("[LLM] Chunk yielded | text=%r", chunk_text)
            yield chunk_text
