
type AIStatus = 'Disconnected' | 'Connecting' | 'Listening' | 'Speaking';

interface VisualizerProps {
    status: AIStatus;
}

export function Visualizer({ status }: VisualizerProps) {
    // No local state needed for waveform heights anymore


    return (
        <div className="flex-1 flex flex-col items-center justify-center gap-12 pt-8 pb-32 relative w-full h-full">
            {/* Top Status Text (Reference: "AI IS SPEAKING...", "Analyzing Strategy") */}
            <div className="flex flex-col items-center gap-3 relative z-20">
                <div className="flex items-center gap-2">
                    <div className={`size-2.5 rounded-full ${status === 'Listening' ? 'bg-white' : status === 'Speaking' ? 'bg-white' : 'bg-slate-500'} ${status !== 'Disconnected' ? 'animate-pulse shadow-[0_0_8px_rgba(255,255,255,0.8)]' : ''}`}></div>
                    <span className={`text-xs font-bold uppercase tracking-widest ${status === 'Listening' ? 'text-white' : status === 'Speaking' ? 'text-white' : 'text-slate-500'}`}>
                        {status === 'Disconnected' ? 'SYSTEM OFFLINE' :
                            status === 'Listening' ? 'LISTENING TO USER...' :
                                status === 'Speaking' ? 'AI IS SPEAKING...' :
                                    'CONNECTING...'}
                    </span>
                </div>

                <h2 className="text-5xl font-extrabold text-white tracking-tight">
                    {status === 'Disconnected' ? 'Not Ready' :
                        status === 'Listening' ? 'System Ready' :
                            status === 'Speaking' ? 'Analyzing Strategy' :
                                'Establishing Uplink'}
                </h2>

                <p className="text-sm font-medium text-slate-400">
                    {status === 'Disconnected' ? 'Start a session to connect' :
                        status === 'Speaking' ? 'Response latency: ~240ms' :
                            'Awaiting Input'}
                </p>
            </div>

            {/* Central Visualizer Area */}
            <div className="relative flex-1 flex items-center justify-center w-full max-h-[450px] z-0">
                <div className="relative group cursor-pointer flex justify-center items-center w-full h-[400px]">
                    {/* The dynamic AI Ring / Plasma Sphere */}
                    <div
                        className={`ai-ring size-72 ${status === 'Listening' ? '' :
                            status === 'Connecting' ? 'thinking' :
                                status === 'Speaking' ? 'speaking' : ''
                            } ${status === 'Disconnected' ? 'opacity-30 grayscale' : ''}`}
                    >
                        {/* The internal core that fades in during 'speaking' state */}
                        <div className="plasma-core"></div>
                    </div>
                </div>
            </div>

            {/* Quote Excerpt below Visualizer */}
            <div className="w-full max-w-2xl px-12 text-center relative z-20">
                <p className="text-xl leading-relaxed text-slate-200 font-display">
                    {status === 'Speaking'
                        ? `"Expanding on the architectural requirements, I recommend implementing a `
                        : "Ready to assist you with "}
                    <span className="text-white font-bold drop-shadow-md">
                        {status === 'Speaking' ? 'distributed vector database' : 'complex strategy'}
                    </span>
                    {status === 'Speaking'
                        ? ` to ensure real-time retrieval performance at this scale."`
                        : " analysis and real-time inference."}
                </p>
            </div>
        </div>
    );
}
