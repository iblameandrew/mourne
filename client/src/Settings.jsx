import React, { useState, useEffect } from 'react';
import { Save, X, Cloud, Cpu, Mic, Image as ImageIcon, Video, Type, Key } from 'lucide-react';

const Settings = ({ isOpen, onClose }) => {
    const [config, setConfig] = useState({
        cloud_provider: 'google', // 'google' | 'replicate'
        keys: {
            google_key: '',
            replicate_key: '',
            openrouter_key: ''
        },
        routes: {
            text_model: 'gemini-1.5-pro',
            speech_model: 'gemini-2.5-flash-preview-tts',
            image_model: 'imagen-3',
            video_model: 'veo-2'
        },
        // Only relevant when replicate is chosen
        openrouter_text_model: '' // Optional: e.g. 'anthropic/claude-3.5-sonnet'
    });

    // Load from localStorage
    useEffect(() => {
        const saved = localStorage.getItem('mourne_config_v3');
        if (saved) {
            setConfig(JSON.parse(saved));
        }
    }, []);

    const handleSave = () => {
        localStorage.setItem('mourne_config_v3', JSON.stringify(config));
        onClose();
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/90 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="bg-[#121214] border border-amber-50/10 rounded-2xl w-full max-w-2xl shadow-2xl overflow-hidden ring-1 ring-white/5 flex flex-col max-h-[90vh] relative">

                {/* Atmospheric Gradients */}
                <div className="absolute top-0 left-0 w-64 h-64 bg-blue-600/5 blur-[80px] rounded-full pointer-events-none mix-blend-screen" />
                <div className="absolute bottom-0 right-0 w-64 h-64 bg-red-600/5 blur-[80px] rounded-full pointer-events-none mix-blend-screen" />

                {/* Header */}
                <div className="h-16 border-b border-amber-50/5 flex justify-between items-center px-6 bg-surface/30 shrink-0 relative z-10">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-white/5 border border-amber-50/10 flex items-center justify-center text-zinc-300">
                            <Cpu size={18} />
                        </div>
                        <div>
                            <h3 className="font-bold text-sm text-zinc-200 uppercase tracking-wider">System Architecture</h3>
                            <p className="text-[10px] text-zinc-500 font-mono">Configure Cloud Providers</p>
                        </div>
                    </div>
                    <button onClick={onClose} className="text-zinc-500 hover:text-white transition-colors"><X size={20} /></button>
                </div>

                {/* Scrollable Body */}
                <div className="flex-1 overflow-y-auto p-8 space-y-8 relative z-10">

                    {/* 1. Cloud Provider Selection */}
                    <section className="space-y-4">
                        <h4 className="text-xs font-bold text-zinc-500 uppercase tracking-wider flex items-center gap-2">
                            <Cloud size={14} /> Cloud Provider
                        </h4>
                        <div className="flex gap-4">
                            {['google', 'replicate'].map(provider => (
                                <button
                                    key={provider}
                                    onClick={() => setConfig({ ...config, cloud_provider: provider })}
                                    className={`px-5 py-3 rounded-xl text-sm font-bold uppercase tracking-wider border transition-all ${config.cloud_provider === provider
                                        ? 'bg-amber-50/10 text-amber-50 border-amber-50/20 shadow-[0_0_20px_-5px_rgba(255,255,255,0.1)]'
                                        : 'bg-transparent text-zinc-500 border-white/5 hover:border-white/10 hover:bg-white/5'
                                        }`}
                                >
                                    {provider}
                                </button>
                            ))}
                        </div>
                    </section>

                    {/* 2. API Keys */}
                    <section className="space-y-4">
                        <h4 className="text-xs font-bold text-zinc-500 uppercase tracking-wider flex items-center gap-2">
                            <Key size={14} /> API Keys
                        </h4>

                        {/* Google Key */}
                        {config.cloud_provider === 'google' && (
                            <div className="bg-surface/20 p-4 rounded-xl border border-amber-50/5 space-y-2">
                                <label className="text-xs text-zinc-400 flex items-center gap-2">
                                    <Key size={12} /> Google AI / Gemini API Key
                                </label>
                                <input
                                    type="password"
                                    className="w-full bg-black/40 border border-white/5 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none focus:border-amber-50/30 font-mono tracking-tight transition-colors"
                                    placeholder="AIza..."
                                    value={config.keys.google_key}
                                    onChange={(e) => setConfig({
                                        ...config,
                                        keys: { ...config.keys, google_key: e.target.value }
                                    })}
                                />
                            </div>
                        )}

                        {/* Replicate Key + Optional OpenRouter */}
                        {config.cloud_provider === 'replicate' && (
                            <div className="space-y-4">
                                <div className="bg-surface/20 p-4 rounded-xl border border-amber-50/5 space-y-2">
                                    <label className="text-xs text-zinc-400 flex items-center gap-2">
                                        <Key size={12} /> Replicate API Token
                                    </label>
                                    <input
                                        type="password"
                                        className="w-full bg-black/40 border border-white/5 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none focus:border-amber-50/30 font-mono tracking-tight transition-colors"
                                        placeholder="r8_..."
                                        value={config.keys.replicate_key}
                                        onChange={(e) => setConfig({
                                            ...config,
                                            keys: { ...config.keys, replicate_key: e.target.value }
                                        })}
                                    />
                                </div>

                                {/* Optional: OpenRouter for Text */}
                                <div className="bg-surface/20 p-4 rounded-xl border border-primary/10 space-y-3">
                                    <div className="flex items-center justify-between">
                                        <label className="text-xs text-zinc-400 flex items-center gap-2">
                                            <Type size={12} /> OpenRouter Text Model <span className="text-[10px] text-zinc-600 bg-white/5 px-1.5 rounded">OPTIONAL</span>
                                        </label>
                                    </div>
                                    <p className="text-[10px] text-zinc-600 leading-relaxed">
                                        Use an OpenRouter model for text/reasoning instead of Replicate.
                                    </p>
                                    <input
                                        type="password"
                                        className="w-full bg-black/40 border border-white/5 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none focus:border-primary/30 font-mono tracking-tight transition-colors"
                                        placeholder="OpenRouter API Key (sk-or-...)"
                                        value={config.keys.openrouter_key}
                                        onChange={(e) => setConfig({
                                            ...config,
                                            keys: { ...config.keys, openrouter_key: e.target.value }
                                        })}
                                    />
                                    <input
                                        type="text"
                                        className="w-full bg-black/40 border border-white/5 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none focus:border-primary/30 font-mono tracking-tight transition-colors"
                                        placeholder="Model (e.g. anthropic/claude-3.5-sonnet)"
                                        value={config.openrouter_text_model}
                                        onChange={(e) => setConfig({
                                            ...config,
                                            openrouter_text_model: e.target.value
                                        })}
                                    />
                                </div>
                            </div>
                        )}
                    </section>

                    {/* 3. Model Routing */}
                    <section className="space-y-4">
                        <h4 className="text-xs font-bold text-zinc-500 uppercase tracking-wider flex items-center gap-2">
                            <Cpu size={14} /> Model Routing
                        </h4>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {/* Text Model */}
                            <div className="space-y-2">
                                <label className="text-xs text-zinc-400 flex items-center gap-2">
                                    <Type size={12} /> Text / Reasoning
                                </label>
                                <input
                                    type="text"
                                    className="w-full bg-surface/50 border border-white/10 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none focus:border-cyan-500/50 font-mono"
                                    placeholder={config.cloud_provider === 'google' ? 'gemini-1.5-pro' : 'meta/llama-2-70b-chat'}
                                    value={config.routes.text_model}
                                    onChange={(e) => setConfig({ ...config, routes: { ...config.routes, text_model: e.target.value } })}
                                />
                            </div>

                            {/* Speech Model */}
                            <div className="space-y-2">
                                <label className="text-xs text-zinc-400 flex items-center gap-2">
                                    <Mic size={12} /> Speech Synthesis
                                </label>
                                <input
                                    type="text"
                                    className="w-full bg-surface/50 border border-white/10 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none focus:border-violet-500/50 font-mono"
                                    placeholder={config.cloud_provider === 'google' ? 'gemini-2.5-flash-preview-tts' : 'cjwbw/bark'}
                                    value={config.routes.speech_model}
                                    onChange={(e) => setConfig({ ...config, routes: { ...config.routes, speech_model: e.target.value } })}
                                />
                            </div>

                            {/* Image Model */}
                            <div className="space-y-2">
                                <label className="text-xs text-zinc-400 flex items-center gap-2">
                                    <ImageIcon size={12} /> Image Generation
                                </label>
                                <input
                                    type="text"
                                    className="w-full bg-surface/50 border border-white/10 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none focus:border-pink-500/50 font-mono"
                                    placeholder={config.cloud_provider === 'google' ? 'imagen-3' : 'stability-ai/sdxl'}
                                    value={config.routes.image_model}
                                    onChange={(e) => setConfig({ ...config, routes: { ...config.routes, image_model: e.target.value } })}
                                />
                            </div>

                            {/* Video Model */}
                            <div className="space-y-2">
                                <label className="text-xs text-zinc-400 flex items-center gap-2">
                                    <Video size={12} /> Video Synthesis
                                </label>
                                <input
                                    type="text"
                                    className="w-full bg-surface/50 border border-white/10 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none focus:border-emerald-500/50 font-mono"
                                    placeholder={config.cloud_provider === 'google' ? 'veo-2' : 'stability-ai/stable-video-diffusion'}
                                    value={config.routes.video_model}
                                    onChange={(e) => setConfig({ ...config, routes: { ...config.routes, video_model: e.target.value } })}
                                />
                            </div>
                        </div>
                    </section>
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-amber-50/5 bg-surface/20 flex justify-end gap-3 shrink-0 relative z-10">
                    <button onClick={onClose} className="px-6 py-2 rounded-lg hover:bg-white/5 text-zinc-400 text-sm font-medium transition-colors">Cancel</button>
                    <button onClick={handleSave} className="px-6 py-2 rounded-lg bg-white/5 border border-amber-50/20 hover:bg-amber-50/10 text-amber-50 text-sm font-medium flex items-center gap-2 shadow-[0_0_15px_-5px_rgba(251,191,36,0.1)] transition-all hover:scale-[1.02]">
                        <Save size={16} /> Save Config
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Settings;
