<p align="center">
  <img src="frontend/icon-128.png" alt="GetLanded Logo" width="128" height="128">
</p>

<h1 align="center">GetLanded — PrepMentor (AI Career Assistant & Voice Pipeline)</h1>

<p align="center">
  <strong>Your intelligent co-pilot for every job application with Real-Time Voice-to-Voice capabilities</strong>
</p>

<p align="center">
  <a href="#overview">Overview</a> •
  <a href="#features">Features</a> •
  <a href="#tech-stack">Tech Stack</a> •
  <a href="#project-structure">Project Structure</a> •
  <a href="#setup-instructions">Setup Instructions</a> •
  <a href="#support">Support</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/react-19.1-61dafb?style=flat-square&logo=react" alt="React 19">
  <img src="https://img.shields.io/badge/typescript-5.9-3178c6?style=flat-square&logo=typescript" alt="TypeScript">
  <img src="https://img.shields.io/badge/fastapi-10.9-009688?style=flat-square&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/vite-7.1-646cff?style=flat-square&logo=vite" alt="Vite 7">
</p>

---

## 🎯 Overview

**GetLanded PrepMentor** is a powerful career application engineered to revolutionize your job search experience. Integrating a real-time voice conversation system where users speak naturally and receive AI-generated voice responses with minimal delay, it acts as a comprehensive AI career assistant that prepares you for job interviews and applications with ultra-low latency conversational AI.

---

## ✨ Features

### 🎙️ Real-Time Voice-to-Voice Pipeline
- **Ultra-Low Latency:** 1.2s - 2.0s end-to-end response time using a streaming sentence-level pipeline.
- **Smart Turn-taking:** Natural conversation flow with Voice Activity Detection (VAD).
- **Architecture:** Full-Duplex WebSockets for continuous audio streams.

### 🧠 AI-Powered Career Capabilities
- **Resume Matching & Insights:** Analyzes your resume against job requirements in real-time to provide actionable feedback.
- **AI Cover Letter Generator:** Powered by Google Gemini AI for natural, professional writing tailored to each job.
- **Visa Sponsorship Verification:** Instantly checks if a company sponsors work visas like H-1B, OPT, etc.
- **AI Autofill for Applications:** Intelligently fills out application forms using parsed details from your resume.
- **Smart Job Scraping:** Automatically extracts job details from platforms like LinkedIn and Indeed.

---

## 🧰 Tech Stack

| Component | Stack |
|-----------|-------|
| **Backend** | FastAPI, Python, Silero VAD, Faster-Whisper (STT), Gemini Flash (LLM), Kokoro-82M (TTS) |
| **Frontend** | React, Next.js, Vite, TypeScript, TailwindCSS |

---

## 🏗️ Project Structure

- `backend/`: Contains the FastAPI application and audio processing services.
- `frontend/`: Contains the React/Next.js/Vite client interface.

---

## 📦 Setup Instructions

### Backend Setup
1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # macOS / Linux
   ```
3. Install the dependencies based on `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the development server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup
1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:
1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

---

## 📄 License

This project is proprietary software owned by **GetLanded**. All rights reserved.

For licensing inquiries, please contact: [support@getlanded.io](mailto:support@getlanded.io)

---

## 📞 Support

- **Website**: [https://getlanded.io](https://getlanded.io)
- **Documentation**: [https://docs.getlanded.io](https://docs.getlanded.io)
- **Email**: [support@getlanded.io](mailto:support@getlanded.io)

---

<p align="center">
  Made with ❤️ by the <strong>GetLanded</strong> Team
</p>

<p align="center">
  <sub>© 2024-2026 GetLanded. All rights reserved.</sub>
</p>
