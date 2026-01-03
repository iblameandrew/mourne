import React, { useState } from 'react';
import { Settings as SettingsIcon } from 'lucide-react';
import Settings from './Settings';

const Layout = ({ children }) => {
    const [isSettingsOpen, setSettingsOpen] = useState(false);

    return (
        <div className="relative min-h-screen bg-background text-zinc-200 overflow-hidden font-sans selection:bg-primary/30">
            {/* 1. Global Gradients (The Atmosphere) */}
            <div className="fixed inset-0 z-0 pointer-events-none">
                {/* Top Left Blue Nebula */}
                <div className="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] bg-blue-900/20 rounded-full blur-[120px]" />
                {/* Bottom Right Red Nebula */}
                <div className="absolute -bottom-[20%] -right-[10%] w-[50%] h-[50%] bg-red-900/10 rounded-full blur-[120px]" />
                {/* Center Violet Glow */}
                <div className="absolute top-[40%] left-[40%] w-[20%] h-[20%] bg-primary/5 rounded-full blur-[100px] animate-pulse" />
            </div>

            {/* 2. Content Frame */}
            <div className="relative z-10 flex flex-col h-screen p-4 gap-4">
                {/* Application Header */}
                <header className="flex items-center justify-between px-6 py-3 bg-surface/30 backdrop-blur-md border border-white/5 rounded-2xl shrink-0 animate-reveal">
                    <div className="flex items-center gap-3">
                        <span className="font-light tracking-[0.2em] text-lg text-white uppercase ml-2 select-none">MOURNE</span>
                    </div>
                    <div className="flex items-center gap-4 text-xs font-mono text-zinc-500">
                        <button
                            onClick={() => setSettingsOpen(true)}
                            className="hover:text-white transition-colors"
                            title="System Configuration"
                        >
                            <SettingsIcon size={16} />
                        </button>
                        <span>v0.2.0-web</span>
                        <span className="w-2 h-2 rounded-full bg-green-500/50 animate-pulse" title="System Online"></span>
                    </div>
                </header>

                {/* Main Workspace */}
                <main className="flex-1 flex gap-4 min-h-0 animate-reveal delay-100 opacity-0">
                    {children}
                </main>
            </div>

            {/* Settings Modal */}
            <Settings isOpen={isSettingsOpen} onClose={() => setSettingsOpen(false)} />
        </div>
    );
};

export default Layout;
