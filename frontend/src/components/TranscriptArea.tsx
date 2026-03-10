
export interface ChatMessage {
    id: string;
    role: 'user' | 'assistant';
    text: string;
}

interface TranscriptAreaProps {
    messages: ChatMessage[];
    isSpeaking: boolean;
}

export function TranscriptArea({ messages, isSpeaking }: TranscriptAreaProps) {
    return (
        <aside className="w-full flex flex-col h-full z-20 relative">
            <div className="p-8 pb-4 flex items-center justify-between">
                <h3 className="text-white font-bold text-lg">
                    Live Transcript
                </h3>
                <div className="flex items-center gap-1.5 px-3 py-1 bg-white/10 border border-white/20 rounded-full">
                    <div className="size-2 rounded-full bg-white animate-pulse shadow-[0_0_8px_rgba(255,255,255,0.5)]"></div>
                    <span className="text-[10px] font-bold uppercase tracking-widest text-white">Recording</span>
                </div>
            </div>
            <div className="flex-1 overflow-y-auto px-8 pb-8 space-y-8 scrollbar-thin scrollbar-thumb-white/20 scrollbar-track-transparent mt-4">

                {messages.map((msg) => (
                    <div key={msg.id} className="w-full">
                        <p className="text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-3 ml-1">
                            {msg.role === 'assistant' ? 'Assistant' : 'User'}
                        </p>
                        {msg.role === 'assistant' ? (
                            <div className="glass-panel p-5 rounded-2xl border-white/5 relative group">
                                <p className="text-slate-200 leading-relaxed text-[15px] font-display">{msg.text}</p>
                            </div>
                        ) : (
                            <p className="text-slate-400 leading-relaxed text-[15px] font-display px-1">{msg.text}</p>
                        )}
                    </div>
                ))}

                {/* Streaming / Loading Indicator */}
                {isSpeaking && (
                    <div className="w-full">
                        <div className="flex items-center gap-4 mb-3">
                            <p className="text-[10px] font-bold uppercase tracking-widest text-white ml-1">Current Response</p>
                            <div className="h-px flex-1 bg-white/20"></div>
                        </div>
                        <div className="glass-panel p-5 rounded-2xl border-white/20 relative group shadow-[0_0_30px_rgba(255,255,255,0.1)] bg-white/5">
                            <div className="animate-pulse flex flex-col gap-3">
                                <div className="h-2 w-3/4 bg-white/40 rounded mb-1"></div>
                                <div className="h-2 w-full bg-white/20 rounded"></div>
                                <div className="h-2 w-1/2 bg-white/20 rounded"></div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </aside>
    );
}
