# PrepMentor (Real-Time Voice-to-Voice Pipeline MVP)

A real-time voice conversation system where users speak naturally and receive AI-generated voice responses with minimal delay. 

## Features
- **Ultra-Low Latency:** 1.2s - 2.0s end-to-end response time using a streaming sentence-level pipeline.
- **Architecture:** Full-Duplex WebSockets for continuous audio streams.
- **Backend:** FastAPI, Python, Silero VAD, Faster-Whisper (STT), Gemini Flash (LLM), and Kokoro-82M (TTS).
- **Frontend:** React / Next.js.
- **Smart Turn-taking:** Natural conversation flow with Voice Activity Detection.

## Project Structure
- `backend/`: Contains the FastAPI application and audio processing services.
- `frontend/`: Contains the React/Next.js client interface.

## Setup Instructions

### Backend Setup
1. Navigate to the `backend` directory.
2. Create a virtual environment: `python -m venv .venv` and activate it.
3. Install the dependencies based on `requirements.txt`.
4. Run the development server (e.g. `uvicorn main:app --reload`).

### Frontend Setup
1. Navigate to the `frontend` directory.
2. Install npm dependencies: `npm install`.
3. Start the development server: `npm run dev`.
