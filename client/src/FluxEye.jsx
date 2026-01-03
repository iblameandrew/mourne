import React from 'react';

export const FluxEye = ({
    className = "",
    animate = false,
    thinking = false,
    pulsar = false
}) => {
    // Dynamic duration for the spin based on state
    const getDuration = () => {
        if (pulsar) return '0.5s';
        if (thinking) return '0.4s';
        if (animate) return '0.8s';
        return '1.5s'; // Noticeable idle spin
    };

    const ringStyle = {
        transition: 'all 2s cubic-bezier(0.4, 0, 0.2, 1)',
        // Multi-color spectral gradient
        background: 'conic-gradient(from 0deg, #8b5cf6, #06b6d4, #3b82f6, #8b5cf6, #d946ef, #ec4899, #8b5cf6)',
        animationDuration: getDuration(),
        filter: pulsar ? 'brightness(1.5) blur(2px)' : 'blur(4px)',
        opacity: (thinking || animate || pulsar) ? 1 : 0.8,
        boxShadow: (thinking || animate || pulsar) ? '0 0 40px rgba(255,255,255,0.1)' : 'none'
    };

    return (
        <div className={`relative w-16 h-16 flex items-center justify-center select-none shrink-0 ${className}`}>
            {/* Outer high-fidelity lens body */}
            <div className={`absolute inset-0 bg-[#0a0a0a] rounded-full border border-white/10 flex items-center justify-center transition-all duration-1000 ${(animate || thinking || pulsar) ? 'shadow-[0_0_80px_rgba(255,255,255,0.05)] animate-softGlow' : 'shadow-[0_0_20px_rgba(0,0,0,0.8)]'}`}>
                <div className="absolute inset-[3%] rounded-full border border-white/5 bg-[conic-gradient(from_0deg,_#1a1a1a,_#000,_#1a1a1a)]" />
            </div>
            {/* The vibrant Spectral Ring (The spinning part) */}
            <div
                className="absolute inset-[10%] rounded-full animate-sparkle-rotate mix-blend-screen"
                style={ringStyle}
            />
            {/* Inner Machined Lens Area */}
            <div className="absolute inset-[24%] bg-[#050505] rounded-full flex items-center justify-center shadow-[inset_0_4px_20px_rgba(0,0,0,0.9)] overflow-hidden border border-white/10">
                {/* Central Machined Pupil */}
                <div className={`w-[60%] h-[60%] rounded-full bg-[conic-gradient(from_0deg,_#222,_#050505,_#333,_#050505,_#222)] relative flex items-center justify-center border border-white/5 shadow-2xl transition-all duration-1000 ${pulsar ? 'brightness-150 scale-105 shadow-[0_0_30px_rgba(239,68,68,0.3)]' : ''}`}>
                    <div className="w-[12%] h-[12%] bg-black rounded-full border border-white/20 shadow-[0_0_10px_rgba(255,255,255,0.1)]" />
                </div>
                {/* Sublte glass refraction */}
                <div className="absolute inset-0 bg-gradient-to-tr from-blue-500/10 via-transparent to-pink-500/10 mix-blend-screen opacity-50" />
            </div>
            {/* Optical Glint */}
            <div className={`absolute inset-[15%] rounded-full bg-gradient-to-br from-cyan-400/20 to-transparent pointer-events-none transition-all duration-1000 ${pulsar ? 'from-cyan-400/40' : ''}`} />
        </div>
    );
};

export default FluxEye;
