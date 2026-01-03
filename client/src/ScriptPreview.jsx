import React, { useState } from 'react';
import { Code, Play, Edit3, Check, X, AlertCircle } from 'lucide-react';
import FluxOrb from './FluxOrb';

/**
 * ScriptPreview - Displays generated MoviePy script for approval
 */
const ScriptPreview = ({
    script,
    projectId,
    onApprove,
    onEdit,
    isExecuting = false
}) => {
    const [editedScript, setEditedScript] = useState(script);
    const [isEditing, setIsEditing] = useState(false);

    const handleApprove = () => {
        onApprove(isEditing ? editedScript : script);
    };

    if (!script) {
        return (
            <div className="p-6 bg-surface/20 rounded-xl border border-white/5 text-center">
                <AlertCircle size={24} className="text-zinc-600 mx-auto mb-2" />
                <p className="text-sm text-zinc-500">No script generated yet.</p>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full bg-[#0d0d0f] rounded-xl border border-white/5 overflow-hidden animate-reveal">
            {/* Header */}
            <div className="p-4 border-b border-white/5 flex justify-between items-center bg-surface/30">
                <div className="flex items-center gap-3">
                    <Code size={16} className="text-primary animate-float" />
                    <div>
                        <h3 className="text-sm font-bold text-white">Generated Script</h3>
                        <p className="text-[10px] text-zinc-500 font-mono">MoviePy assembly ready for approval</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    {isExecuting && (
                        <span className="flex items-center gap-2 text-xs text-primary">
                            <FluxOrb size="sm" /> Rendering...
                        </span>
                    )}
                </div>
            </div>

            {/* Script Display / Editor */}
            <div className="flex-1 overflow-auto relative">
                {isEditing ? (
                    <textarea
                        value={editedScript}
                        onChange={(e) => setEditedScript(e.target.value)}
                        className="w-full h-full bg-transparent p-4 text-green-400 font-mono text-xs leading-relaxed focus:outline-none resize-none"
                        spellCheck={false}
                    />
                ) : (
                    <pre className="p-4 text-green-400 font-mono text-xs leading-relaxed whitespace-pre-wrap overflow-x-auto">
                        {script}
                    </pre>
                )}
            </div>

            {/* Actions */}
            <div className="p-4 border-t border-white/5 bg-surface/20 flex justify-between items-center gap-3">
                <div className="flex gap-2">
                    {isEditing ? (
                        <>
                            <button
                                onClick={() => setIsEditing(false)}
                                className="px-4 py-2 rounded-lg bg-white/5 text-zinc-400 text-sm hover:bg-white/10 transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={() => {
                                    setIsEditing(false);
                                    if (onEdit) onEdit(editedScript);
                                }}
                                className="px-4 py-2 rounded-lg bg-blue-600/20 text-blue-400 text-sm hover:bg-blue-600/30 transition-colors flex items-center gap-2"
                            >
                                <Check size={14} /> Save Changes
                            </button>
                        </>
                    ) : (
                        <button
                            onClick={() => setIsEditing(true)}
                            className="px-4 py-2 rounded-lg bg-white/5 text-zinc-400 text-sm hover:bg-white/10 transition-colors flex items-center gap-2"
                        >
                            <Edit3 size={14} /> Edit Script
                        </button>
                    )}
                </div>

                <button
                    onClick={handleApprove}
                    disabled={isExecuting}
                    className={`px-6 py-2 rounded-lg text-sm font-bold flex items-center gap-2 transition-all ${isExecuting
                        ? 'bg-zinc-700 text-zinc-400 cursor-not-allowed'
                        : 'bg-green-600 text-white hover:bg-green-500 shadow-[0_0_20px_rgba(34,197,94,0.2)]'
                        }`}
                >
                    <Play size={14} /> Approve & Execute
                </button>
            </div>
        </div>
    );
};

export default ScriptPreview;
