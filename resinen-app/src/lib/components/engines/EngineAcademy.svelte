<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    import { fly, scale, fade } from 'svelte/transition';
    import type { Community, User } from '$lib/types';

    export let community: Community;
    export let currentUser: User | null;

    // Local interfaces for strict typing
    interface Lesson {
        id: string;
        title: string;
        type: 'video' | 'text' | 'project';
        duration: string;
        xp: number;
        status: 'locked' | 'unlocked' | 'completed';
    }

    interface Module {
        id: string;
        title: string;
        lessons: Lesson[];
    }

    // --- STATE ---
    let modules: Module[] = [];
    let loading = true;
    let activeLesson: Lesson | null = null;
    let showCompleteAnim = false;
    let error: string | null = null;

    onMount(async () => {
        if (!community?.id) return;
        try {
            // Fetch real curriculum
            const res = await api.getCurriculum(community.id);
            // Handle array vs wrapper
            modules = Array.isArray(res) ? res : (res as any).items || [];
        } catch (e) {
            console.error("Academy Load Failed:", e);
            error = "Star Chart Offline.";
        } finally {
            loading = false;
        }
    });

    function selectLesson(lesson: Lesson) {
        if (lesson.status === 'locked') return;
        activeLesson = lesson;
    }

    async function completeLesson() {
        if (!activeLesson) return;
        
        // Optimistic UI Update
        activeLesson.status = 'completed';
        // Trigger Animation
        showCompleteAnim = true;

        try {
            await api.completeLesson(activeLesson.id);
            // Refresh user XP (global)
            await api.getMe(); 
        } catch (e) {
            console.error(e);
            activeLesson.status = 'unlocked'; // Revert on fail
            showCompleteAnim = false;
        }

        setTimeout(() => {
            showCompleteAnim = false;
            activeLesson = null; // Close modal
        }, 2000);
    }

    function getNodeColor(status: string) {
        if (status === 'completed') return 'bg-cyan-400 shadow-[0_0_20px_rgba(34,211,238,0.6)] border-cyan-200';
        if (status === 'unlocked') return 'bg-white shadow-[0_0_20px_rgba(255,255,255,0.4)] border-white animate-pulse-slow';
        return 'bg-slate-800 border-slate-700 opacity-50';
    }
</script>

<div class="relative min-h-screen bg-[#0f172a] text-white overflow-hidden font-sans">
    
    <div class="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/stardust.png')] opacity-30 animate-twinkle"></div>
    <div class="absolute top-0 left-0 w-full h-full bg-gradient-to-b from-[#0f172a] via-transparent to-[#0f172a] z-10 pointer-events-none"></div>

    <div class="relative z-20 pt-12 pb-8 text-center">
        <div class="text-[10px] font-black uppercase tracking-[0.3em] text-cyan-400 mb-2">Curriculum Map</div>
        <h2 class="text-4xl md:text-6xl font-black uppercase tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-cyan-200 to-blue-500">
            Star Chart
        </h2>
        
        {#if currentUser}
            <div class="mt-4 inline-flex items-center gap-2 bg-slate-800/50 backdrop-blur rounded-full px-4 py-1 border border-slate-700">
                <span class="text-cyan-400 text-xs">★</span>
                <span class="text-xs font-bold uppercase tracking-widest text-slate-300">Total XP: {currentUser.xp || 0}</span>
            </div>
        {/if}
    </div>

    <div class="relative z-20 max-w-3xl mx-auto px-6 pb-40">
        
        <div class="absolute left-6 md:left-1/2 top-40 bottom-0 w-[2px] bg-gradient-to-b from-cyan-500/50 via-blue-500/20 to-transparent"></div>

        {#if error}
             <div class="text-center mt-20 text-red-400 font-mono">{error}</div>
        {/if}

        <div class="space-y-24 mt-12">
            {#each modules as module, mIndex}
                <div class="relative">
                    
                    <div class="sticky top-4 z-10 mb-12 flex justify-start md:justify-center">
                        <span class="bg-[#0f172a]/90 backdrop-blur border border-cyan-500/30 text-cyan-100 px-4 py-2 rounded text-xs font-black uppercase tracking-widest shadow-xl">
                            {module.title}
                        </span>
                    </div>

                    <div class="space-y-16">
                        {#each module.lessons as lesson, lIndex}
                            {@const isLeft = lIndex % 2 === 0}
                            
                            <div 
                                class="relative flex md:justify-center items-center group"
                                in:fly={{ y: 20, delay: (mIndex * 100) + (lIndex * 50) }}
                            >
                                <button 
                                    on:click={() => selectLesson(lesson)}
                                    disabled={lesson.status === 'locked'}
                                    class="relative z-20 w-12 h-12 md:w-16 md:h-16 rounded-full border-4 transition-all duration-300 transform hover:scale-110 flex items-center justify-center {getNodeColor(lesson.status)}"
                                >
                                    {#if lesson.status === 'locked'}
                                        <span class="text-slate-500 text-lg">🔒</span>
                                    {:else if lesson.status === 'completed'}
                                        <span class="text-cyan-900 text-xl font-black">✓</span>
                                    {:else}
                                        <span class="text-slate-900 text-xl font-black">▶</span>
                                    {/if}
                                </button>

                                <div 
                                    class="absolute left-16 md:left-auto md:{isLeft ? 'right-[calc(50%+4rem)]' : 'left-[calc(50%+4rem)]'} 
                                    w-64 transition-all duration-300 group-hover:translate-x-1
                                    {isLeft ? 'md:text-right' : 'md:text-left'} text-left"
                                >
                                    <h4 class="text-lg font-bold text-slate-100 leading-tight group-hover:text-cyan-300 transition-colors">
                                        {lesson.title}
                                    </h4>
                                    <div class="flex items-center gap-3 mt-1 {isLeft ? 'md:justify-end' : 'md:justify-start'}">
                                        <span class="text-[10px] font-mono text-slate-500 uppercase">{lesson.duration}</span>
                                        <span class="text-[10px] font-black text-cyan-600 uppercase border border-cyan-900/50 px-1 rounded">
                                            +{lesson.xp} XP
                                        </span>
                                    </div>
                                </div>

                                <div class="absolute left-6 md:left-1/2 w-8 md:w-16 h-[1px] bg-slate-700/50 md:block hidden {isLeft ? '-translate-x-full' : ''}"></div>
                            </div>
                        {/each}
                    </div>
                </div>
            {/each}
        </div>
    </div>

    {#if activeLesson}
        <div class="fixed inset-0 z-50 bg-[#0f172a] flex flex-col" transition:fly={{ y: 1000, duration: 500, opacity: 1 }}>
            
            <div class="h-16 flex items-center justify-between px-6 border-b border-slate-800">
                <div class="flex items-center gap-4">
                    <button on:click={() => activeLesson = null} class="text-slate-400 hover:text-white transition-colors">
                        ✕ ESC
                    </button>
                    <div class="h-4 w-[1px] bg-slate-700"></div>
                    <h3 class="font-bold text-sm uppercase tracking-wide text-white">{activeLesson.title}</h3>
                </div>
                <div class="text-xs font-mono font-bold text-cyan-400">
                    +{activeLesson.xp} XP
                </div>
            </div>

            <div class="flex-1 overflow-y-auto flex items-center justify-center p-4 md:p-10 relative">
                
                {#if showCompleteAnim}
                     <div class="absolute inset-0 flex flex-col items-center justify-center z-50 bg-[#0f172a]/90 backdrop-blur-sm" in:scale>
                        <div class="text-8xl mb-4 animate-bounce">🌟</div>
                        <h2 class="text-4xl font-black uppercase text-white tracking-widest mb-2">Lesson Complete!</h2>
                        <p class="text-cyan-400 font-mono font-bold text-xl">+{activeLesson.xp} XP Gained</p>
                     </div>
                {/if}

                <div class="max-w-3xl w-full space-y-8">
                    
                    {#if activeLesson.type === 'video'}
                        <div class="aspect-video bg-black rounded-2xl border border-slate-700 shadow-2xl flex items-center justify-center relative group cursor-pointer overflow-hidden">
                            <div class="absolute inset-0 bg-gradient-to-tr from-cyan-900/20 to-purple-900/20"></div>
                            <div class="w-20 h-20 rounded-full bg-white/10 backdrop-blur border border-white/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                                <span class="text-4xl ml-1">▶</span>
                            </div>
                        </div>
                    {:else}
                        <div class="prose prose-invert prose-lg max-w-none">
                            <h1>{activeLesson.title}</h1>
                            <p class="lead">Here is the fundamental knowledge you need to master this concept.</p>
                            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
                            <h3>Key Takeaways</h3>
                            <ul>
                                <li>Systematic approach to problem solving</li>
                                <li>Understanding the core constraints</li>
                                <li>Iterative design process</li>
                            </ul>
                        </div>
                    {/if}

                    <div class="pt-10 flex justify-center">
                        {#if activeLesson.status === 'completed'}
                            <button disabled class="px-8 py-4 bg-slate-800 text-slate-400 rounded-full font-black uppercase tracking-widest cursor-default">
                                Completed
                            </button>
                        {:else}
                            <button 
                                on:click={completeLesson}
                                class="px-10 py-4 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-full font-black uppercase tracking-widest shadow-[0_0_30px_rgba(6,182,212,0.4)] hover:shadow-[0_0_50px_rgba(6,182,212,0.6)] hover:scale-105 transition-all active:scale-95"
                            >
                                Complete Lesson
                            </button>
                        {/if}
                    </div>

                </div>
            </div>
        </div>
    {/if}

</div>

<style>
    @keyframes twinkle {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 0.5; }
    }
    .animate-twinkle { animation: twinkle 4s infinite ease-in-out; }
    
    @keyframes pulse-slow {
        0%, 100% { box-shadow: 0 0 20px rgba(255,255,255,0.4); }
        50% { box-shadow: 0 0 40px rgba(255,255,255,0.7); }
    }
    .animate-pulse-slow { animation: pulse-slow 3s infinite; }
</style>