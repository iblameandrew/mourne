import React, { useState, useRef } from 'react';
import { Image, Upload, X, Link2, Check, Trash2, Plus } from 'lucide-react';

/**
 * EntityEditor - Allows users to upload custom images and bind them to scenes
 */
const EntityEditor = ({
    scenes = [],
    customAssets = [],
    onUpload,
    onBind,
    onRemove
}) => {
    const [dragOver, setDragOver] = useState(false);
    const [selectedScene, setSelectedScene] = useState(null);
    const fileInputRef = useRef(null);

    const handleDrop = (e) => {
        e.preventDefault();
        setDragOver(false);
        const files = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('image/'));
        if (files.length > 0 && onUpload) {
            files.forEach(file => onUpload(file));
        }
    };

    const handleFileSelect = (e) => {
        const files = Array.from(e.target.files);
        if (files.length > 0 && onUpload) {
            files.forEach(file => onUpload(file));
        }
    };

    const handleBind = (assetId, sceneNumber) => {
        if (onBind) {
            onBind(assetId, sceneNumber);
        }
        setSelectedScene(null);
    };

    return (
        <div className="flex flex-col h-full bg-[#0d0d0f] rounded-xl border border-white/5 overflow-hidden">
            {/* Header */}
            <div className="p-4 border-b border-white/5 flex justify-between items-center bg-surface/30">
                <div className="flex items-center gap-3">
                    <Image size={16} className="text-primary" />
                    <div>
                        <h3 className="text-sm font-bold text-white">Entity Library</h3>
                        <p className="text-[10px] text-zinc-500 font-mono">Custom images for scene binding</p>
                    </div>
                </div>
                <span className="text-[10px] text-zinc-600">{customAssets.length} assets</span>
            </div>

            {/* Upload Zone */}
            <div
                onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={handleDrop}
                className={`m-4 p-6 border-2 border-dashed rounded-xl flex flex-col items-center justify-center gap-3 transition-all cursor-pointer ${dragOver
                        ? 'border-primary bg-primary/10'
                        : 'border-zinc-700 hover:border-zinc-500 hover:bg-white/5'
                    }`}
                onClick={() => fileInputRef.current?.click()}
            >
                <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    multiple
                    onChange={handleFileSelect}
                    className="hidden"
                />
                <Upload size={24} className={dragOver ? 'text-primary' : 'text-zinc-500'} />
                <div className="text-center">
                    <p className="text-sm text-zinc-400">Drop images here</p>
                    <p className="text-[10px] text-zinc-600">or click to browse</p>
                </div>
            </div>

            {/* Asset Grid */}
            <div className="flex-1 overflow-y-auto p-4">
                {customAssets.length === 0 ? (
                    <div className="text-center py-8">
                        <Image size={32} className="text-zinc-700 mx-auto mb-2" />
                        <p className="text-sm text-zinc-600">No custom assets yet</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-2 gap-3">
                        {customAssets.map((asset) => (
                            <div
                                key={asset.id}
                                className="relative group rounded-lg overflow-hidden border border-white/5 bg-surface/30"
                            >
                                <img
                                    src={asset.previewUrl}
                                    alt={asset.name}
                                    className="w-full aspect-video object-cover"
                                />

                                {/* Overlay */}
                                <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                                    <button
                                        onClick={() => setSelectedScene(asset.id)}
                                        className="p-2 rounded-lg bg-primary text-black hover:bg-primary/90 transition-colors"
                                        title="Bind to Scene"
                                    >
                                        <Link2 size={14} />
                                    </button>
                                    <button
                                        onClick={() => onRemove && onRemove(asset.id)}
                                        className="p-2 rounded-lg bg-red-600 text-white hover:bg-red-500 transition-colors"
                                        title="Remove"
                                    >
                                        <Trash2 size={14} />
                                    </button>
                                </div>

                                {/* Bound Scene Badge */}
                                {asset.boundScene && (
                                    <div className="absolute top-2 left-2 px-2 py-1 rounded bg-green-600/80 text-[10px] font-bold text-white flex items-center gap-1">
                                        <Check size={10} /> Scene {asset.boundScene}
                                    </div>
                                )}

                                {/* Name */}
                                <div className="p-2 bg-black/40">
                                    <p className="text-[10px] text-zinc-400 truncate">{asset.name}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Scene Binding Modal */}
            {selectedScene && (
                <div className="absolute inset-0 bg-black/90 flex items-center justify-center z-10">
                    <div className="bg-surface/80 rounded-xl p-4 w-64 border border-white/10">
                        <h4 className="text-sm font-bold text-white mb-3">Bind to Scene</h4>
                        <div className="space-y-2 max-h-48 overflow-y-auto">
                            {scenes.map((scene) => (
                                <button
                                    key={scene.scene_number}
                                    onClick={() => handleBind(selectedScene, scene.scene_number)}
                                    className="w-full p-2 rounded-lg bg-white/5 hover:bg-primary/20 text-left text-sm text-zinc-300 transition-colors"
                                >
                                    Scene {scene.scene_number}: {scene.description?.substring(0, 30)}...
                                </button>
                            ))}
                        </div>
                        <button
                            onClick={() => setSelectedScene(null)}
                            className="mt-3 w-full p-2 rounded-lg bg-white/5 text-zinc-400 text-sm hover:bg-white/10"
                        >
                            Cancel
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default EntityEditor;
