import React from 'react';
import { motion } from 'framer-motion';

const FluxOrb = ({ size = "md", className = "" }) => {
    const sizeClasses = {
        sm: "w-6 h-6",
        md: "w-12 h-12",
        lg: "w-32 h-32"
    };

    const currentSize = sizeClasses[size] || sizeClasses.md;

    return (
        <div className={`relative flex items-center justify-center ${currentSize} ${className}`}>
            {/* Chromatic Ring (Conic Gradient) */}
            <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                className="absolute inset-0 rounded-full"
                style={{
                    background: "conic-gradient(from 0deg, #ff0080, #7928ca, #00c0ff, #ff0080)",
                    padding: "10%", // Thickness of the ring
                    mask: "linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)",
                    maskComposite: "exclude",
                    WebkitMask: "linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)",
                    WebkitMaskComposite: "xor",
                    filter: "drop-shadow(0 0 8px rgba(121, 40, 202, 0.5))"
                }}
            />

            {/* Inner Glow / Core */}
            <motion.div
                animate={{ scale: [0.9, 1.1, 0.9], opacity: [0.8, 1, 0.8] }}
                transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
                className="absolute inset-[25%] rounded-full bg-black/50 backdrop-blur-md flex items-center justify-center border border-white/10"
            >
                {/* Central Iris */}
                <div className="w-[40%] h-[40%] rounded-full bg-gradient-to-tr from-cyan-400 to-violet-500 blur-[2px]" />
            </motion.div>
        </div>
    );
};

export default FluxOrb;
