from __future__ import annotations

import logging
from asyncio import QueueEmpty
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.audio_utils import pcm16_to_float32
import asyncio
from app.state import AppState


logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/audio")
async def audio_websocket(websocket: WebSocket) -> None:
    await websocket.accept()
    app_state: AppState = websocket.app.state.backend_state
    settings = app_state.settings

    audio_buffer = bytearray()
    silence_frames = 0
    speech_detected = False
    current_task: asyncio.Task | None = None

    outgoing_queue: asyncio.Queue[tuple[str, str | bytes] | None] = asyncio.Queue()

    async def sender_worker() -> None:
        while True:
            msg = await outgoing_queue.get()
            if msg is None:
                break
            msg_type, data = msg
            try:
                if msg_type == "text":
                    await websocket.send_text(data) # type: ignore
                elif msg_type == "audio":
                    await websocket.send_bytes(data) # type: ignore
            except RuntimeError as e:
                if 'Cannot call "send" once a close message has been sent' in str(e):
                    logger.debug("Client disconnected while sending %s.", msg_type)
                    break
                else:
                    logger.exception("WebSocket send error")
            except Exception as e:
                logger.exception("WebSocket send exception")

    sender_task = asyncio.create_task(sender_worker())

    async def send_audio(audio_bytes: bytes) -> None:
        if audio_bytes:
            outgoing_queue.put_nowait(("audio", audio_bytes))

    async def send_text(message: str) -> None:
        outgoing_queue.put_nowait(("text", message))

    def drop_stale_ai_output() -> None:
        kept: list[tuple[str, str | bytes] | None] = []
        dropped = 0

        while True:
            try:
                msg = outgoing_queue.get_nowait()
            except QueueEmpty:
                break

            if msg is None:
                kept.append(msg)
                continue

            msg_type, payload = msg
            if msg_type == "audio":
                dropped += 1
                continue

            if msg_type == "text" and isinstance(payload, str) and payload.startswith("AI:"):
                dropped += 1
                continue

            kept.append(msg)

        for msg in kept:
            outgoing_queue.put_nowait(msg)

        if dropped:
            logger.info("Dropped %d stale AI queue messages after interruption.", dropped)

    async def run_pipeline(pcm_data: bytes) -> None:
        nonlocal current_task
        try:
            await app_state.pipeline_service.process_turn(pcm_data, send_audio=send_audio, send_text=send_text)
        except asyncio.CancelledError:
            logger.info("Pipeline task cancelled (AI interrupted).")
            # Drop stale queued AI output and tell frontend to stop playback now.
            drop_stale_ai_output()
            outgoing_queue.put_nowait(("text", "CMD:interrupt"))
            outgoing_queue.put_nowait(("text", "CMD:stream_end"))
        except Exception as e:
            logger.exception("Pipeline error: %s", e)
        finally:
            if current_task == asyncio.current_task():
                current_task = None

    try:
        while True:
            message = await websocket.receive()
            if message["type"] == "websocket.disconnect":
                logger.info("Client disconnected from /ws/audio")
                break
            
            if "bytes" in message:
                chunk = message["bytes"]
            elif "text" in message:
                text_data = message["text"]
                if text_data == "CMD:transcribe_now":
                    logger.info("Frontend explicitly requested transcription.")
                    if audio_buffer:
                        if current_task and not current_task.done():
                            current_task.cancel()
                        current_task = asyncio.create_task(run_pipeline(bytes(audio_buffer)))
                        audio_buffer.clear()
                        silence_frames = 0
                else:
                    logger.debug("Received unexpected text message: %s", text_data)
                continue
            else:
                continue

            audio_buffer.extend(chunk)

            frame = pcm16_to_float32(chunk)
            if app_state.vad_service.is_speech(frame):
                silence_frames = 0
                if not speech_detected:
                    # New speech segment started - interrupt AI if it's talking
                    if current_task and not current_task.done():
                        logger.info("Interrupting AI due to new user speech.")
                        current_task.cancel()
                speech_detected = True
            else:
                silence_frames += 1

            max_bytes = settings.sample_rate * 2 * settings.max_buffer_seconds
            if len(audio_buffer) >= max_bytes:
                if speech_detected:
                    if current_task and not current_task.done():
                        current_task.cancel()
                    current_task = asyncio.create_task(run_pipeline(bytes(audio_buffer)))
                audio_buffer.clear()
                silence_frames = 0
                speech_detected = False
                continue

            if silence_frames >= settings.silence_frames_threshold and audio_buffer:
                if speech_detected:
                    if current_task and not current_task.done():
                        current_task.cancel()
                    current_task = asyncio.create_task(run_pipeline(bytes(audio_buffer)))
                audio_buffer.clear()
                silence_frames = 0
                speech_detected = False

    except WebSocketDisconnect:
        logger.info("Client disconnected from /ws/audio")
    except Exception as exc:
        logger.exception("WebSocket processing failed: %s", exc)
        try:
            outgoing_queue.put_nowait(("text", "ERROR:processing_failed"))
        except Exception:
            pass
    finally:
        outgoing_queue.put_nowait(None)
        if current_task and not current_task.done():
            current_task.cancel()
