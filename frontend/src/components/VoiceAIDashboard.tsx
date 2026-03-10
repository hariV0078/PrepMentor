import { Visualizer } from './Visualizer';
import { ControlBar } from './ControlBar';
import { TranscriptArea } from './TranscriptArea';
import { useVoiceAgent } from '../hooks/useVoiceAgent';

export function VoiceAIDashboard() {
    const { status, isMicActive, messages, toggleMic, endSession } = useVoiceAgent();

    return (
        <div className="relative flex h-screen w-full bg-[#05080A] text-slate-100 overflow-hidden font-display">
            {/* Left Sidebar (Navigation) */}
            <aside className="w-72 flex flex-col justify-between py-8 px-6 border-r border-white/10 glass-panel !rounded-none z-20">
                <div>
                    <div className="flex items-center gap-3 mb-12">
                        <div className="size-8 rounded-full bg-white flex items-center justify-center shadow-[0_0_15px_rgba(255,255,255,0.4)]">
                            <span className="material-symbols-outlined text-black text-sm">graphic_eq</span>
                        </div>
                        <h1 className="text-xl font-bold tracking-tight">LUX.AI</h1>
                    </div>

                    <nav className="space-y-2">
                        <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-4 pl-3">Navigation</p>
                        <button className="w-full flex items-center gap-4 px-4 py-3 rounded-xl bg-white/5 text-white border border-white/5 transition-all">
                            <span className="material-symbols-outlined text-[20px]">grid_view</span>
                            <span className="text-sm font-semibold text-white">Dashboard</span>
                        </button>
                        <button className="w-full flex items-center gap-4 px-4 py-3 rounded-xl text-slate-400 hover:text-white hover:bg-white/5 transition-all">
                            <span className="material-symbols-outlined text-[20px]">chat_bubble_outline</span>
                            <span className="text-sm font-medium">History</span>
                        </button>
                        <button className="w-full flex items-center gap-4 px-4 py-3 rounded-xl text-slate-400 hover:text-white hover:bg-white/5 transition-all">
                            <span className="material-symbols-outlined text-[20px]">settings</span>
                            <span className="text-sm font-medium">Settings</span>
                        </button>
                    </nav>
                </div>

                <div className="space-y-4">
                    <div className="glass-panel p-4 pb-5 rounded-2xl flex flex-col gap-2 relative overflow-hidden">
                        <p className="text-xs font-bold text-white relative z-10">Pro Plan</p>
                        <p className="text-[10px] text-slate-400 relative z-10">24.5k tokens remaining</p>
                        <div className="w-full h-1 bg-white/10 rounded-full mt-2 relative z-10">
                            <div className="w-3/4 h-full bg-white rounded-full shadow-[0_0_8px_rgba(255,255,255,0.8)]"></div>
                        </div>
                        <div className="absolute inset-0 bg-white/5 blur-xl"></div>
                    </div>
                    <button className="w-full py-3.5 rounded-full bg-white hover:bg-white/90 text-black font-bold flex items-center justify-center gap-2 transition-all shadow-[0_4px_20px_rgba(255,255,255,0.4)] interactive-btn">
                        <span className="material-symbols-outlined text-[20px]">add</span>
                        New Session
                    </button>
                </div>
            </aside>

            {/* Main Center Area */}
            <main className="flex-1 flex flex-col relative overflow-hidden pb-24">
                {/* Top Header - simple navigation links per reference */}
                <header className="flex items-center justify-between px-12 py-8 z-20">
                    <div className="flex gap-8 items-center text-sm font-semibold">
                        <span className="text-white border-b-2 border-white pb-1 cursor-pointer">Assistant</span>
                        <span className="text-slate-400 hover:text-white cursor-pointer transition-colors">Library</span>
                        <span className="text-slate-400 hover:text-white cursor-pointer transition-colors">Analytics</span>
                        <span className="text-slate-400 hover:text-white cursor-pointer transition-colors">API</span>
                    </div>
                    <div className="flex items-center gap-4">
                        <button className="size-10 flex items-center justify-center rounded-full text-slate-400 hover:text-white border border-white/10 hover:bg-white/10 transition-all">
                            <span className="material-symbols-outlined text-[20px]">notifications</span>
                        </button>
                        <button className="size-10 flex items-center justify-center rounded-full text-slate-400 hover:text-white border border-white/10 hover:bg-white/10 transition-all">
                            <span className="material-symbols-outlined text-[20px]">person</span>
                        </button>
                    </div>
                </header>

                {/* Central Visualizer Area */}
                <Visualizer status={status} />
            </main>

            {/* Right Sidebar: Transcript */}
            <div className="w-[380px] border-l border-white/10 glass-panel !rounded-none z-20 pb-24">
                <TranscriptArea
                    messages={messages}
                    isSpeaking={status === 'Speaking'}
                />
            </div>

            {/* Bottom Control Bar */}
            <ControlBar
                isMicActive={isMicActive}
                onToggleMic={toggleMic}
                onEndCall={endSession}
            />

            {/* Background Ambient Blobs */}
            <div className="fixed top-[-10%] left-[20%] size-[800px] bg-slate-400/10 blur-[150px] rounded-full pointer-events-none z-0"></div>
            <div className="fixed top-[-10%] right-[-10%] size-[800px] bg-white/5 blur-[150px] rounded-full pointer-events-none z-0"></div>
        </div>
    );
}
