import React, { useState, useEffect } from 'react';
import { Save, X, Cloud, Cpu, Mic, Image as ImageIcon, Video, Type, Key, ChevronDown } from 'lucide-react';

const ProviderSelect = ({ value, options, onChange, label, icon: Icon }) => (
    <div className="space-y-2">
        <label className="text-xs text-zinc-400 flex items-center gap-2">
            <Icon size={12} /> {label}
        </label>
        <div className="relative">
            <select
                value={value}
                onChange={(e) => onChange(e.target.value)}
                className="w-full bg-surface/50 border border-white/10 rounded-lg px-3 py-2.5 text-sm text-zinc-300 focus:outline-none focus:border-primary/50 appearance-none cursor-pointer"
            >
                {options.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
            </select>
            <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 pointer-events-none" />
        </div>
    </div>
);

const Settings = ({ isOpen, onClose }) => {
    const [config, setConfig] = useState({
        // Per-model providers
        providers: {
            text: 'openrouter',    // 'openrouter' | 'google'
            image: 'google',       // 'google' | 'replicate'
            video: 'runway'        // 'runway' | 'replicate' | 'google'
        },
        // API Keys
        keys: {
            google_key: '',
            replicate_key: '',
            runway_key: '',
            openrouter_key: ''
        },
        // Model names
        models: {
            text: 'gemini-2.5-flash',
            image: 'imagen-3',
            video: 'gen4_turbo'
        }
    });

    // Load from localStorage
    useEffect(() => {
        const saved = localStorage.getItem('mourne_config_v4');
        if (saved) {
            setConfig(JSON.parse(saved));
        }
    }, []);

    const handleSave = async () => {
        localStorage.setItem('mourne_config_v4', JSON.stringify(config));

        // Send to backend
        try {
            await fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text_provider: config.providers.text,
                    image_provider: config.providers.image,
                    video_provider: config.providers.video,
                    google_key: config.keys.google_key,
                    replicate_key: config.keys.replicate_key,
                    runway_key: config.keys.runway_key,
                    openrouter_key: config.keys.openrouter_key,
                    text_model: config.models.text,
                    image_model: config.models.image,
                    video_model: config.models.video
                })
            });
        } catch (e) {
            console.error('Failed to sync config with backend:', e);
        }

        onClose();
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/90 backdrop-blur-md animate-reveal">
            <div className="bg-[#121214] border border-amber-50/10 rounded-2xl w-full max-w-2xl shadow-2xl overflow-hidden ring-1 ring-white/5 flex flex-col max-h-[90vh] relative animate-blurIn">

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
                            <p className="text-[10px] text-zinc-500 font-mono">Per-Model Provider Configuration</p>
                        </div>
                    </div>
                    <button onClick={onClose} className="text-zinc-500 hover:text-white transition-colors"><X size={20} /></button>
                </div>

                {/* Scrollable Body */}
                <div className="flex-1 overflow-y-auto p-8 space-y-8 relative z-10">

                    {/* 1. Per-Model Provider Selection */}
                    <section className="space-y-4">
                        <h4 className="text-xs font-bold text-zinc-500 uppercase tracking-wider flex items-center gap-2">
                            <Cloud size={14} /> Provider Routing
                        </h4>
                        <p className="text-[10px] text-zinc-600 leading-relaxed mb-4">
                            Select a cloud provider for each model type. Different providers offer different capabilities and pricing.
                        </p>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <ProviderSelect
                                label="Text / Reasoning"
                                icon={Type}
                                value={config.providers.text}
                                onChange={(v) => setConfig({ ...config, providers: { ...config.providers, text: v } })}
                                options={[
                                    { value: 'openrouter', label: 'OpenRouter' },
                                    { value: 'google', label: 'Google Gemini' }
                                ]}
                            />
                            <ProviderSelect
                                label="Image Generation"
                                icon={ImageIcon}
                                value={config.providers.image}
                                onChange={(v) => setConfig({ ...config, providers: { ...config.providers, image: v } })}
                                options={[
                                    { value: 'google', label: 'Google Imagen' },
                                    { value: 'replicate', label: 'Replicate' }
                                ]}
                            />
                            <ProviderSelect
                                label="Video Synthesis"
                                icon={Video}
                                value={config.providers.video}
                                onChange={(v) => setConfig({ ...config, providers: { ...config.providers, video: v } })}
                                options={[
                                    { value: 'runway', label: 'Runway ML' },
                                    { value: 'replicate', label: 'Replicate' },
                                    { value: 'google', label: 'Google Veo' }
                                ]}
                            />
                        </div>
                    </section>

                    {/* 2. API Keys */}
                    <section className="space-y-4">
                        <h4 className="text-xs font-bold text-zinc-500 uppercase tracking-wider flex items-center gap-2">
                            <Key size={14} /> API Keys
                        </h4>
                        <p className="text-[10px] text-zinc-600 leading-relaxed">
                            Only the keys required by your selected providers are shown below. If you only use Google services, you only need the Google API key.
                        </p>

                        <div className="space-y-4">
                            {/* OpenRouter Key */}
                            {config.providers.text === 'openrouter' && (
                                <div className="bg-surface/20 p-4 rounded-xl border border-cyan-500/10 space-y-2">
                                    <label className="text-xs text-zinc-400 flex items-center gap-2">
                                        <Key size={12} /> OpenRouter API Key
                                    </label>
                                    <input
                                        type="password"
                                        className="w-full bg-black/40 border border-white/5 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none focus:border-cyan-500/30 font-mono tracking-tight transition-colors"
                                        placeholder="sk-or-..."
                                        value={config.keys.openrouter_key}
                                        onChange={(e) => setConfig({
                                            ...config,
                                            keys: { ...config.keys, openrouter_key: e.target.value }
                                        })}
                                    />
                                </div>
                            )}

                            {/* Google Key */}
                            {(config.providers.text === 'google' || config.providers.image === 'google' || config.providers.video === 'google') && (
                                <div className="bg-surface/20 p-4 rounded-xl border border-blue-500/10 space-y-2">
                                    <label className="text-xs text-zinc-400 flex items-center gap-2">
                                        <Key size={12} /> Google AI / Gemini API Key
                                    </label>
                                    <input
                                        type="password"
                                        className="w-full bg-black/40 border border-white/5 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none focus:border-blue-500/30 font-mono tracking-tight transition-colors"
                                        placeholder="AIza..."
                                        value={config.keys.google_key}
                                        onChange={(e) => setConfig({
                                            ...config,
                                            keys: { ...config.keys, google_key: e.target.value }
                                        })}
                                    />
                                </div>
                            )}

                            {/* Replicate Key */}
                            {(config.providers.image === 'replicate' || config.providers.video === 'replicate') && (
                                <div className="bg-surface/20 p-4 rounded-xl border border-purple-500/10 space-y-2">
                                    <label className="text-xs text-zinc-400 flex items-center gap-2">
                                        <Key size={12} /> Replicate API Token
                                    </label>
                                    <input
                                        type="password"
                                        className="w-full bg-black/40 border border-white/5 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none focus:border-purple-500/30 font-mono tracking-tight transition-colors"
                                        placeholder="r8_..."
                                        value={config.keys.replicate_key}
                                        onChange={(e) => setConfig({
                                            ...config,
                                            keys: { ...config.keys, replicate_key: e.target.value }
                                        })}
                                    />
                                </div>
                            )}

                            {/* Runway Key */}
                            {config.providers.video === 'runway' && (
                                <div className="bg-surface/20 p-4 rounded-xl border border-emerald-500/10 space-y-2">
                                    <label className="text-xs text-zinc-400 flex items-center gap-2">
                                        <Key size={12} /> Runway ML API Key
                                    </label>
                                    <input
                                        type="password"
                                        className="w-full bg-black/40 border border-white/5 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none focus:border-emerald-500/30 font-mono tracking-tight transition-colors"
                                        placeholder="key_..."
                                        value={config.keys.runway_key}
                                        onChange={(e) => setConfig({
                                            ...config,
                                            keys: { ...config.keys, runway_key: e.target.value }
                                        })}
                                    />
                                </div>
                            )}
                        </div>
                    </section>

                    {/* 3. Model Names */}
                    <section className="space-y-4">
                        <h4 className="text-xs font-bold text-zinc-500 uppercase tracking-wider flex items-center gap-2">
                            <Cpu size={14} /> Model Selection
                        </h4>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            {/* Text Model */}
                            <div className="space-y-2">
                                <label className="text-xs text-zinc-400 flex items-center gap-2">
                                    <Type size={12} /> Text Model
                                </label>
                                <input
                                    type="text"
                                    className="w-full bg-surface/50 border border-white/10 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none focus:border-cyan-500/50 font-mono"
                                    placeholder={config.providers.text === 'google' ? 'gemini-2.5-flash' : 'anthropic/claude-3.5-sonnet'}
                                    value={config.models.text}
                                    onChange={(e) => setConfig({ ...config, models: { ...config.models, text: e.target.value } })}
                                />
                            </div>

                            {/* Image Model */}
                            <div className="space-y-2">
                                <label className="text-xs text-zinc-400 flex items-center gap-2">
                                    <ImageIcon size={12} /> Image Model
                                </label>
                                <input
                                    type="text"
                                    className="w-full bg-surface/50 border border-white/10 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none focus:border-pink-500/50 font-mono"
                                    placeholder={config.providers.image === 'google' ? 'imagen-3' : 'stability-ai/sdxl'}
                                    value={config.models.image}
                                    onChange={(e) => setConfig({ ...config, models: { ...config.models, image: e.target.value } })}
                                />
                            </div>

                            {/* Video Model */}
                            <div className="space-y-2">
                                <label className="text-xs text-zinc-400 flex items-center gap-2">
                                    <Video size={12} /> Video Model
                                </label>
                                <input
                                    type="text"
                                    className="w-full bg-surface/50 border border-white/10 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none focus:border-emerald-500/50 font-mono"
                                    placeholder={config.providers.video === 'runway' ? 'gen4_turbo' : config.providers.video === 'google' ? 'veo-3.1' : 'stable-video-diffusion'}
                                    value={config.models.video}
                                    onChange={(e) => setConfig({ ...config, models: { ...config.models, video: e.target.value } })}
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
