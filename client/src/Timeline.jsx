import React from 'react';
import { Play } from 'lucide-react';
import { motion } from 'framer-motion';
import FluxOrb from './FluxOrb';

const Timeline = () => {
    return (
        <section className="flex-[3] flex flex-col bg-surface/20 backdrop-blur-xl border border-white/5 rounded-3xl overflow-hidden relative group">
            {/* Aesthetic Corner Gradients */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-blue-900/10 blur-[80px] rounded-full pointer-events-none" />
            <div className="absolute bottom-0 left-0 w-64 h-64 bg-red-900/10 blur-[80px] rounded-full pointer-events-none" />

            {/* Section Header */}
            <div className="p-6 pb-2 relative z-10">
                <h2 className="text-xs font-bold text-zinc-500 uppercase tracking-widest">Timeline / Assets</h2>
            </div>

            {/* Main Content Area */}
            <div className="flex-1 flex flex-col items-center justify-center relative p-10 z-10">

                {/* Ready State */}

            </div>

            {/* Bottom Control Bar Stub */}
            <div className="h-16 border-t border-white/5 bg-black/20 flex items-center px-6 gap-4 relative z-10">
                <div className="h-10 w-10 rounded-full bg-white/5 flex items-center justify-center hover:bg-white/10 cursor-pointer transition-colors">
                    <Play size={16} className="fill-white text-white ml-0.5" />
                </div>
                <div className="h-1 flex-1 bg-white/5 rounded-full overflow-hidden">
                    <div className="h-full w-0 bg-primary shadow-[0_0_10px_2px_rgba(124,77,255,0.5)]" />
                </div>
                <span className="font-mono text-xs text-zinc-600">00:00 / 00:00</span>
            </div>
        </section>
    );
};

export default Timeline;
