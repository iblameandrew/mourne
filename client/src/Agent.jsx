import React, { useState, useRef, useEffect } from 'react';
import { Send, Scroll, Plus, X, Image as ImageIcon } from 'lucide-react';
import FluxEye from './FluxEye';

const Agent = () => {
    const [input, setInput] = useState("");
    const [messages, setMessages] = useState([
        { sender: 'Agent', text: 'Ready. Upload an audio track to begin orchestration.' }
    ]);
    const [isThinking, setIsThinking] = useState(false);
    const [isScriptModalOpen, setScriptModalOpen] = useState(false);
    const messagesEndRef = useRef(null);
    const fileInputRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(scrollToBottom, [messages, isThinking]);

    const handleFileUpload = (e) => {
        const file = e.target.files[0];
        if (file) {
            setMessages(prev => [...prev, {
                sender: 'User',
                text: `Attached Audio: ${file.name}`
            }]);
            setIsThinking(true);
            // Simulate agent response
            setTimeout(() => {
                setMessages(prev => [...prev, {
                    sender: 'Agent',
                    text: 'Audio received. Analyzing tempo and mood...'
                }]);
                setIsThinking(false);
            }, 800);
        }
    };

    const sendMessage = () => {
        if (!input.trim()) return;
        setMessages(prev => [...prev, { sender: 'User', text: input }]);
        setInput("");
        setIsThinking(true);
        // Simulate thinking
        setTimeout(() => {
            setMessages(prev => [...prev, { sender: 'Agent', text: 'Analyzing input...' }]);
            setIsThinking(false);
        }, 600);
    };

    return (
        <section className="flex-[2] flex flex-col bg-surface/20 backdrop-blur-xl border border-white/5 rounded-3xl overflow-hidden relative">
            {/* Header */}
            <div className="p-6 border-b border-white/5 flex justify-between items-center bg-black/10">
                <h2 className="text-xs font-bold text-zinc-500 uppercase tracking-widest">Agent Director</h2>
                <div className="flex items-center gap-3">
                    <span className="text-[10px] text-zinc-600 font-mono">{isThinking ? 'THINKING...' : 'IDLE'}</span>
                    <FluxEye
                        thinking={isThinking}
                        className="scale-[0.25] -mr-4"
                    />
                </div>
            </div>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`flex flex-col gap-1 ${msg.sender === 'User' ? 'items-end' : 'items-start'}`}>
                        <span className="text-[10px] uppercase font-bold text-zinc-600 ml-1">{msg.sender}</span>
                        <div
                            className={`max-w-[85%] p-4 rounded-2xl text-sm leading-relaxed shadow-sm animate-reveal opacity-0 ${msg.sender === 'User'
                                ? 'bg-primary/10 text-primary border border-primary/20 rounded-tr-sm'
                                : 'bg-white/5 text-zinc-200 border border-white/5 rounded-tl-sm shadow-[0_4px_20px_rgba(0,0,0,0.2)] animate-softGlow'
                                }`}
                        >
                            {msg.text}
                        </div>
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 bg-gradient-to-t from-black/40 to-transparent">
                <div className="relative group bg-surface/50 border border-white/10 rounded-3xl p-1.5 flex items-center gap-2 shadow-2xl transition-colors hover:border-white/20 focus-within:border-primary/50 focus-within:ring-1 focus-within:ring-primary/50">

                    {/* Tools Left */}
                    <div className="flex items-center gap-1 pl-1">
                        <input
                            type="file"
                            ref={fileInputRef}
                            onChange={handleFileUpload}
                            accept="audio/*"
                            className="hidden"
                        />
                        <button
                            onClick={() => fileInputRef.current?.click()}
                            className="h-9 w-9 flex items-center justify-center rounded-full text-zinc-400 hover:bg-white/10 hover:text-white transition-all bg-white/5"
                            title="Attach Audio"
                        >
                            <Plus size={18} />
                        </button>
                        <input
                            type="file"
                            id="styleImageInput"
                            onChange={async (e) => {
                                const file = e.target.files[0];
                                if (file) {
                                    setMessages(prev => [...prev, {
                                        sender: 'User',
                                        text: `Style Reference: ${file.name}`
                                    }]);
                                    setIsThinking(true);
                                    // TODO: Upload to /api/project/{id}/style-reference
                                    setTimeout(() => {
                                        setMessages(prev => [...prev, {
                                            sender: 'Agent',
                                            text: 'Style reference analyzed. Visual style will be applied to all generated media.'
                                        }]);
                                        setIsThinking(false);
                                    }, 1200);
                                }
                            }}
                            accept="image/*"
                            className="hidden"
                        />
                        <button
                            onClick={() => document.getElementById('styleImageInput')?.click()}
                            className="h-9 w-9 flex items-center justify-center rounded-full text-zinc-400 hover:bg-white/10 hover:text-white transition-all"
                            title="Add Style Reference"
                        >
                            <ImageIcon size={16} />
                        </button>
                        <button
                            onClick={() => setScriptModalOpen(true)}
                            className="h-9 w-9 flex items-center justify-center rounded-full text-zinc-400 hover:bg-white/10 hover:text-white transition-all"
                            title="Script Editor"
                        >
                            <Scroll size={16} />
                        </button>
                    </div>

                    {/* Input Field */}
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                        placeholder="Give direction..."
                        className="flex-1 bg-transparent border-none text-white placeholder-zinc-500 focus:outline-none focus:ring-0 text-sm h-10 px-2"
                    />

                    {/* Send Button */}
                    <button
                        onClick={sendMessage}
                        className={`h-9 w-9 flex items-center justify-center rounded-full transition-all duration-300 ${input.trim()
                            ? 'bg-primary text-black shadow-[0_0_15px_rgba(255,251,235,0.4)] hover:scale-105'
                            : 'bg-white/5 text-zinc-500'
                            }`}
                    >
                        <Send size={16} className={input.trim() ? 'translate-x-0.5' : ''} />
                    </button>
                </div>

                <div className="text-center mt-3">
                    <span className="text-[10px] text-zinc-600 uppercase tracking-widest">Mourne Intelligence v1.0</span>
                </div>
            </div>

            {/* Script Modal (Refined) */}
            {isScriptModalOpen && (
                <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/95 backdrop-blur-xl animate-in fade-in duration-200">
                    <div className="w-full h-full flex flex-col bg-[#121214] relative">
                        {/* Header */}
                        <div className="h-16 border-b border-white/5 flex justify-between items-center px-6 bg-surface/30 shrink-0">
                            <div className="flex items-center gap-3">
                                <Scroll size={18} className="text-primary" />
                                <div>
                                    <h3 className="font-bold text-sm text-white uppercase tracking-wider">Script / Narrative Engine</h3>
                                    <p className="text-[10px] text-zinc-500 font-mono">Sequencing text and lyrics</p>
                                </div>
                            </div>
                            <button
                                onClick={() => setScriptModalOpen(false)}
                                className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-white/10 text-zinc-500 hover:text-white transition-colors"
                            >
                                <X size={24} />
                            </button>
                        </div>

                        {/* Editor Area */}
                        <div className="flex-1 bg-[#0b0b0d] relative overflow-hidden">
                            <textarea
                                className="w-full h-full bg-transparent p-6 text-zinc-300 font-mono text-base leading-relaxed focus:outline-none resize-none selection:bg-primary/20 placeholder-zinc-700"
                                placeholder="// Enter your script, lyrics, or narrative concept here..."
                                autoFocus
                            />
                        </div>

                        {/* Footer */}
                        <div className="p-4 border-t border-white/5 bg-surface/20 flex justify-end gap-3 shrink-0">
                            <button
                                onClick={() => setScriptModalOpen(false)}
                                className="px-6 py-3 rounded-lg hover:bg-white/5 text-zinc-400 text-sm font-medium transition-colors"
                            >
                                Close Editor
                            </button>
                            <button
                                onClick={() => setScriptModalOpen(false)}
                                className="px-8 py-3 rounded-lg bg-primary hover:bg-primary/90 text-black text-sm font-bold shadow-[0_0_20px_rgba(255,251,235,0.2)] transition-all hover:scale-[1.02] flex items-center gap-2"
                            >
                                <Scroll size={16} /> Analyze Script
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </section>
    );
};

export default Agent;
