import React, { useState } from 'react';
import { Play, X, Plus, Image, Film, Check } from 'lucide-react';
import FluxOrb from './FluxOrb';

/**
 * MediaCard - Shows subagent output prompt with liquid shimmer placeholder and FluxOrb
 */
const MediaCard = ({
    sceneNumber,
    prompt,
    status, // 'generating' | 'complete'
    progress = 0,
    thumbnailUrl = null,
    mediaType = 'image', // 'image' | 'video' | 'speech'
}) => {
    const isGenerating = status === 'generating';
    const isComplete = status === 'complete';

    return (
        <div className="relative group">
            <div className={`
                relative overflow-hidden rounded-xl 
                bg-surface/40 border transition-all duration-500
                ${isGenerating ? 'border-primary/30' : 'border-white/5'}
                ${isComplete ? 'border-green-500/20' : ''}
            `}>
                {/* Thumbnail Area */}
                <div className="relative aspect-video overflow-hidden rounded-t-xl">

                    {/* GENERATING: Liquid Shimmer + FluxOrb */}
                    {isGenerating && (
                        <div className="absolute inset-0">
                            <div className="liquid-shimmer" />

                            {/* FluxOrb Spinner centered */}
                            <div className="absolute inset-0 flex flex-col items-center justify-center gap-3">
                                <FluxOrb size="md" />
                                <span className="text-sm font-mono text-white/80">{progress}%</span>
                            </div>
                        </div>
                    )}

                    {/* COMPLETE: Show thumbnail */}
                    {isComplete && thumbnailUrl && (
                        <img
                            src={thumbnailUrl}
                            alt={prompt}
                            className="absolute inset-0 w-full h-full object-cover"
                        />
                    )}

                    {/* Complete placeholder */}
                    {isComplete && !thumbnailUrl && (
                        <div className="absolute inset-0 bg-gradient-to-br from-green-900/30 to-emerald-900/20 flex items-center justify-center">
                            <Check size={24} className="text-green-400" />
                        </div>
                    )}

                    {/* Media Type Badge */}
                    <div className="absolute bottom-2 left-2 px-2 py-1 rounded-md bg-black/60 backdrop-blur-sm flex items-center gap-1.5">
                        {mediaType === 'video' ? (
                            <Film size={12} className="text-primary" />
                        ) : (
                            <Image size={12} className="text-primary" />
                        )}
                        <span className="text-[10px] uppercase font-bold text-white/80">{mediaType}</span>
                    </div>

                    {/* Scene Badge */}
                    <div className="absolute top-2 left-2 px-2 py-0.5 rounded bg-black/60 backdrop-blur-sm">
                        <span className="text-[10px] font-mono text-white/70">SCENE {sceneNumber}</span>
                    </div>
                </div>

                {/* Subagent Prompt */}
                <div className="p-3 bg-black/20">
                    <p className="text-xs text-zinc-300 leading-relaxed line-clamp-3">{prompt}</p>
                    <div className="mt-2">
                        <span className={`text-[9px] uppercase font-bold px-1.5 py-0.5 rounded ${isComplete ? 'bg-green-500/20 text-green-400' : 'bg-primary/20 text-primary'
                            }`}>
                            {isGenerating ? 'Generating...' : 'Complete'}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    );
};

/**
 * JobTab - Tab for orchestrator workflow
 */
const JobTab = ({ job, isActive, onClick, onClose }) => (
    <button
        onClick={onClick}
        className={`
            relative flex items-center gap-2 px-3 py-2 rounded-t-lg text-xs transition-all
            ${isActive
                ? 'bg-surface/40 border-t border-l border-r border-white/10 text-white'
                : 'bg-transparent text-zinc-500 hover:text-zinc-300 hover:bg-white/5'
            }
        `}
    >
        {job.status === 'generating' && (
            <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
        )}
        {job.status === 'complete' && (
            <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
        )}
        {job.status === 'idle' && (
            <span className="w-1.5 h-1.5 rounded-full bg-zinc-600" />
        )}
        <span className="font-medium truncate max-w-20">{job.name}</span>
        <button
            onClick={(e) => { e.stopPropagation(); onClose(); }}
            className="p-0.5 rounded hover:bg-white/10 text-zinc-500 hover:text-white transition-colors"
        >
            <X size={12} />
        </button>
    </button>
);

const Timeline = () => {
    const [jobs, setJobs] = useState([]);
    const [activeJobId, setActiveJobId] = useState(null);
    const [jobCounter, setJobCounter] = useState(1);

    // Create new job/tab
    const createJob = () => {
        const newJob = {
            id: `job-${Date.now()}`,
            name: `Workflow ${jobCounter}`,
            status: 'idle',
            artifacts: []
        };
        setJobs([...jobs, newJob]);
        setActiveJobId(newJob.id);
        setJobCounter(jobCounter + 1);
    };

    // Close job/tab
    const closeJob = (jobId) => {
        const newJobs = jobs.filter(j => j.id !== jobId);
        setJobs(newJobs);
        if (activeJobId === jobId) {
            setActiveJobId(newJobs.length > 0 ? newJobs[0].id : null);
        }
    };

    const activeJob = jobs.find(j => j.id === activeJobId);
    const completedCount = activeJob?.artifacts?.filter(a => a.status === 'complete').length || 0;
    const totalCount = activeJob?.artifacts?.length || 0;

    return (
        <section className="flex-[3] flex flex-col bg-surface/20 backdrop-blur-xl border border-white/5 rounded-3xl overflow-hidden relative group">
            {/* Background Effects */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-blue-900/10 blur-[80px] rounded-full pointer-events-none" />
            <div className="absolute bottom-0 left-0 w-64 h-64 bg-red-900/10 blur-[80px] rounded-full pointer-events-none" />

            {/* Header with Tabs */}
            <div className="relative z-10 border-b border-white/5">
                <div className="p-4 pb-0 flex items-end justify-between">
                    <h2 className="text-xs font-bold text-zinc-500 uppercase tracking-widest mb-2">Timeline / Assets</h2>
                    {activeJob && totalCount > 0 && (
                        <div className="flex items-center gap-2 mb-2">
                            <span className="text-[10px] text-zinc-600 font-mono">
                                {completedCount}/{totalCount}
                            </span>
                            {activeJob.status === 'generating' && <FluxOrb size="sm" />}
                        </div>
                    )}
                </div>

                {/* Tabs Bar */}
                <div className="flex items-end gap-1 px-4 overflow-x-auto">
                    {jobs.map(job => (
                        <JobTab
                            key={job.id}
                            job={job}
                            isActive={job.id === activeJobId}
                            onClick={() => setActiveJobId(job.id)}
                            onClose={() => closeJob(job.id)}
                        />
                    ))}

                    {/* Add New Tab Button */}
                    <button
                        onClick={createJob}
                        className="flex items-center gap-1.5 px-3 py-2 rounded-t-lg text-xs text-zinc-500 hover:text-white hover:bg-white/5 transition-all"
                        title="New Workflow"
                    >
                        <Plus size={14} />
                    </button>
                </div>
            </div>

            {/* Main Content Area */}
            <div className="flex-1 overflow-hidden relative z-10">
                {activeJob ? (
                    activeJob.artifacts.length > 0 ? (
                        /* Artifacts Grid */
                        <div className="h-full overflow-y-auto p-4 scrollbar-thin">
                            <div className="mb-4">
                                <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-gradient-to-r from-primary to-blue-400 transition-all duration-700"
                                        style={{ width: `${totalCount > 0 ? (completedCount / totalCount) * 100 : 0}%` }}
                                    />
                                </div>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                {activeJob.artifacts.map((artifact) => (
                                    <MediaCard
                                        key={artifact.id}
                                        sceneNumber={artifact.sceneNumber}
                                        prompt={artifact.prompt}
                                        status={artifact.status}
                                        progress={artifact.progress}
                                        thumbnailUrl={artifact.thumbnailUrl}
                                        mediaType={artifact.mediaType}
                                    />
                                ))}
                            </div>
                        </div>
                    ) : (
                        /* Empty Tab - Clean, no examples */
                        <div className="h-full" />
                    )
                ) : (
                    /* No Tabs - Empty Clean State */
                    <div className="h-full" />
                )}
            </div>

            {/* Final Video Display (Only when complete) */}
            {activeJob?.status === 'complete' && (
                <div className="p-4 border-t border-white/5 bg-black/40 animate-fadeIn relative z-10">
                    <div className="flex items-center justify-between mb-3 px-2">
                        <div className="flex items-center gap-2">
                            <Film size={14} className="text-primary" />
                            <span className="text-[10px] font-bold text-zinc-400 uppercase tracking-widest">Master Assembly Complete</span>
                        </div>
                        <span className="text-[10px] font-mono text-zinc-600">final_render.mp4</span>
                    </div>
                    <div className="relative aspect-video rounded-xl overflow-hidden bg-black border border-white/5 shadow-2xl group/video">
                        <video
                            controls
                            className="w-full h-full object-contain"
                            poster={activeJob.artifacts[0]?.thumbnailUrl}
                        >
                            <source src={`/media/final_${activeJob.id.split('-')[1]}.mp4`} type="video/mp4" />
                            Your browser does not support the video tag.
                        </video>

                        {/* Overlay Gradient */}
                        <div className="absolute inset-0 pointer-events-none bg-gradient-to-t from-black/20 to-transparent" />
                    </div>
                </div>
            )}
        </section>
    );
};

export default Timeline;
