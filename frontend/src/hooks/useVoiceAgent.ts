import { useState, useRef, useCallback, useEffect } from 'react';
import type { ChatMessage } from '../components/TranscriptArea';

type AIStatus = 'Disconnected' | 'Connecting' | 'Listening' | 'Speaking';

const WS_URL = 'ws://127.0.0.1:8000/ws/audio';
const SAMPLE_RATE = 16000;

export function useVoiceAgent() {
    const [status, setStatus] = useState<AIStatus>('Disconnected');
    const [isMicActive, setIsMicActive] = useState(false);
    const [messages, setMessages] = useState<ChatMessage[]>([]);

    const wsRef = useRef<WebSocket | null>(null);
    const audioContextRef = useRef<AudioContext | null>(null);
    const mediaStreamRef = useRef<MediaStream | null>(null);
    const processorRef = useRef<ScriptProcessorNode | null>(null);

    // Audio playback queue
    const playQueueRef = useRef<AudioBuffer[]>([]);
    const isPlayingRef = useRef(false);
    const activeSourceRef = useRef<AudioBufferSourceNode | null>(null);
    const lastBargeInAtRef = useRef(0);

    const stopPlayback = useCallback(() => {
        playQueueRef.current = [];

        const activeSource = activeSourceRef.current;
        activeSourceRef.current = null;
        if (activeSource) {
            activeSource.onended = null;
            try { activeSource.stop(); } catch (e) { }
            try { activeSource.disconnect(); } catch (e) { }
        }

        isPlayingRef.current = false;
    }, []);

    const stopRecording = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            // The python backend's VAD triggers on silence, but we push it to transcribe manually
            try { wsRef.current.send("CMD:transcribe_now"); } catch (e) { }
        }

        if (processorRef.current) {
            processorRef.current.disconnect();
            processorRef.current = null;
        }
        if (mediaStreamRef.current) {
            mediaStreamRef.current.getTracks().forEach(t => t.stop());
            mediaStreamRef.current = null;
        }
        setIsMicActive(false);
    }, []);

    const playNextAudio = useCallback(function nextAudio() {
        if (playQueueRef.current.length === 0) {
            isPlayingRef.current = false;
            // Await explicit CMD:stream_end before transitioning
            return;
        }

        isPlayingRef.current = true;
        const buffer = playQueueRef.current.shift();
        const source = audioContextRef.current!.createBufferSource();
        activeSourceRef.current = source;

        source.buffer = buffer!;
        source.connect(audioContextRef.current!.destination);
        source.onended = () => {
            if (activeSourceRef.current === source) {
                activeSourceRef.current = null;
            }
            nextAudio();
        };
        source.start();
    }, []);

    const connectWebSocket = useCallback(() => {
        setStatus('Connecting');
        const ws = new WebSocket(WS_URL);

        ws.binaryType = 'arraybuffer';

        ws.onopen = () => {
            console.log('Connected to Voice Agent');
            setStatus('Listening');
        };

        ws.onmessage = async (event) => {
            if (typeof event.data === 'string') {
                // Received text (transcript or status)
                try {
                    if (event.data === 'ERROR:processing_failed') return;
                    if (event.data === 'CMD:interrupt') {
                        stopPlayback();
                        setStatus('Listening');
                        return;
                    }
                    if (event.data === 'CMD:stream_end') {
                        // Backend confirms stream is exhausted
                        if (!isPlayingRef.current && playQueueRef.current.length === 0) {
                            setStatus('Listening');
                        } else {
                            // Audio still playing, poll until done
                            const checkDone = setInterval(() => {
                                if (!isPlayingRef.current && playQueueRef.current.length === 0) {
                                    setStatus('Listening');
                                    clearInterval(checkDone);
                                }
                            }, 100);
                        }
                        return;
                    }

                    let role: 'user' | 'assistant' = 'assistant';
                    let text = event.data;

                    if (event.data.startsWith('USER:')) {
                        role = 'user';
                        text = event.data.substring(5);
                    } else if (event.data.startsWith('AI:')) {
                        role = 'assistant';
                        text = event.data.substring(3);
                    } else if (event.data.startsWith('TRANSCRIPT:')) {
                        role = 'user';
                        text = event.data.substring(11);
                    }

                    if (!text.trim()) return;

                    setMessages(prev => {
                        const last = prev[prev.length - 1];
                        if (last && last.role === role) {
                            return [
                                ...prev.slice(0, -1),
                                { ...last, text: last.text.trimEnd() + ' ' + text.trimStart() }
                            ];
                        } else {
                            return [...prev, {
                                id: Date.now().toString() + Math.random().toString(),
                                role: role,
                                text: text
                            }];
                        }
                    });
                } catch (e) {
                    console.error("Text parse error", e);
                }
            } else if (event.data instanceof ArrayBuffer) {
                // Received audio bytes
                setStatus('Speaking');
                if (audioContextRef.current) {
                    try {
                        const audioBuffer = await audioContextRef.current.decodeAudioData(event.data);
                        playQueueRef.current.push(audioBuffer);
                        if (!isPlayingRef.current) {
                            playNextAudio();
                        }
                    } catch (e) {
                        console.error("Audio decode error", e);
                    }
                }
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket Error:', error);
            setStatus('Disconnected');
        };

        ws.onclose = () => {
            console.log('WebSocket closed');
            stopPlayback();
            setStatus('Disconnected');
            stopRecording();
        };

        wsRef.current = ws;
    }, [playNextAudio, stopPlayback, stopRecording]);

    const startRecording = useCallback(async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                },
            });
            mediaStreamRef.current = stream;

            const audioCtx = new window.AudioContext({ sampleRate: SAMPLE_RATE });
            audioContextRef.current = audioCtx;

            const source = audioCtx.createMediaStreamSource(stream);
            const processor = audioCtx.createScriptProcessor(512, 1, 1);
            processorRef.current = processor;

            source.connect(processor);
            processor.connect(audioCtx.destination);

            processor.onaudioprocess = (e) => {
                if (wsRef.current?.readyState === WebSocket.OPEN) {
                    const inputData = e.inputBuffer.getChannelData(0);

                    // Convert Float32Array to Int16Array (PCM 16-bit)
                    const pcm16 = new Int16Array(inputData.length);
                    let sumAbs = 0;
                    for (let i = 0; i < inputData.length; i++) {
                        const s = Math.max(-1, Math.min(1, inputData[i]));
                        sumAbs += Math.abs(s);
                        pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
                    }

                    // User barge-in: stop local playback immediately so overlap speech is responsive.
                    const avgAbs = sumAbs / inputData.length;
                    const now = performance.now();
                    if (isPlayingRef.current && avgAbs >= 0.04 && (now - lastBargeInAtRef.current) > 250) {
                        lastBargeInAtRef.current = now;
                        stopPlayback();
                        setStatus('Listening');
                    }

                    wsRef.current.send(pcm16.buffer);
                }
            };

            setIsMicActive(true);
        } catch (err) {
            console.error("Error accessing mic: ", err);
            setIsMicActive(false);
        }
    }, [stopPlayback]);

    const toggleMic = useCallback(() => {
        if (isMicActive) {
            stopRecording();
        } else {
            if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
                connectWebSocket();
            }
            startRecording();
        }
    }, [isMicActive, connectWebSocket, startRecording, stopRecording]);

    const endSession = useCallback(() => {
        stopPlayback();
        stopRecording();
        if (wsRef.current) {
            wsRef.current.close();
        }
        setStatus('Disconnected');
    }, [stopPlayback, stopRecording]);

    // Auto-connect on mount, cleanup on unmount
    useEffect(() => {
        connectWebSocket();

        return () => {
            endSession();
            if (audioContextRef.current) {
                audioContextRef.current.close();
            }
        };
    }, [connectWebSocket, endSession]);

    return {
        status,
        isMicActive,
        messages,
        toggleMic,
        endSession
    };
}
