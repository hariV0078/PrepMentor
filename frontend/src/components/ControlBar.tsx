import { useState } from 'react';

interface ControlBarProps {
    isMicActive: boolean;
    onToggleMic: () => void;
    onEndCall: () => void;
}

export function ControlBar({ isMicActive, onToggleMic, onEndCall }: ControlBarProps) {
    const [volume, setVolume] = useState(75);
    const [isAutoStop, setIsAutoStop] = useState(true);

    return (
        <footer className="fixed bottom-10 left-1/2 -translate-x-1/2 z-40 px-6 py-4 glass-panel bg-white/5 backdrop-blur-xl border border-white/10 rounded-full flex items-center gap-8 shadow-2xl">
            <div className="flex items-center gap-2 px-2">
                <button className="size-10 flex items-center justify-center rounded-full text-slate-400 hover:text-white transition-all">
                    <span className="material-symbols-outlined">{volume === 0 ? 'volume_off' : 'volume_up'}</span>
                </button>
                <div className="w-24 flex items-center">
                    <input
                        type="range"
                        min="0" max="100"
                        value={volume}
                        onChange={(e) => setVolume(Number(e.target.value))}
                        className="w-full h-1.5 bg-white/10 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-white"
                        style={{ background: `linear-gradient(to right, #FFFFFF ${volume}%, rgba(255,255,255,0.1) ${volume}%)` }}
                    />
                </div>
            </div>
            <div className="h-8 w-px bg-white/10"></div>
            <div className="flex items-center gap-6">
                <button className="size-10 flex items-center justify-center rounded-full text-slate-400 hover:text-white transition-all interactive-btn">
                    <span className="material-symbols-outlined">keyboard</span>
                </button>
                {/* Main Mic Toggle */}
                <button
                    onClick={onToggleMic}
                    className={`size-16 rounded-full flex items-center justify-center shadow-[0_0_30px_rgba(255,255,255,0.4)] action-btn-hover interactive-btn
            ${isMicActive ? 'bg-white text-black' : 'bg-white/5 text-slate-400 border border-white/10'}`}
                >
                    <span className="material-symbols-outlined text-3xl">{isMicActive ? 'mic' : 'mic_off'}</span>
                </button>
                <button
                    onClick={onEndCall}
                    className="size-10 flex items-center justify-center rounded-full text-red-500 hover:text-red-400 hover:bg-red-500/10 transition-all interactive-btn"
                >
                    <span className="material-symbols-outlined">close</span>
                </button>
            </div>
            <div className="h-8 w-px bg-white/10"></div>
            <div className="flex items-center gap-2 pr-2">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">Auto-Stop</span>
                <button
                    onClick={() => setIsAutoStop(!isAutoStop)}
                    className={`w-10 h-5 rounded-full relative transition-colors ${isAutoStop ? 'bg-white/40' : 'bg-white/10'}`}
                >
                    <div className={`absolute top-1 size-3 rounded-full transition-all ${isAutoStop ? 'right-1 bg-white' : 'left-1 bg-slate-400'}`}></div>
                </button>
            </div>
        </footer>
    );
}
