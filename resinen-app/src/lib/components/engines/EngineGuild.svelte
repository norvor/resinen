<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    import { fly, fade } from 'svelte/transition';
    import type { Community, User } from '$lib/types';

    export let community: Community;
    export let currentUser: User | null;

    // --- TYPES ---
    interface Bounty {
        id: string;
        title: string;
        reward: string;
        difficulty: 'Easy' | 'Medium' | 'Hard';
        status: 'open' | 'claimed' | 'closed';
        tags: string[];
    }

    interface Project {
        id: string;
        title: string;
        author_name: string;
        likes_count: number;
        tech_stack: string[];
        image_url?: string;
        image?: string;
    }

    // --- STATE ---
    let bounties: Bounty[] = [];
    let projects: Project[] = [];
    let loading = true;
    let view: 'contracts' | 'patents' = 'contracts';
    let error: string | null = null;

    onMount(async () => {
        if (!community?.id) return;
        try {
            const [b, p] = await Promise.all([
                api.getBounties(community.id),
                api.getProjects(community.id)
            ]);
            
            // Handle array vs pagination wrapper
            bounties = Array.isArray(b) ? b : (b as any).items || [];
            projects = Array.isArray(p) ? p : (p as any).items || [];

        } catch (e) {
            console.error("Guild Offline:", e);
            error = "Workshop currently closed.";
        } finally {
            loading = false;
        }
    });

    function getDifficultyColor(diff: string) {
        if (diff === 'Easy') return 'bg-green-100 text-green-700 border-green-300';
        if (diff === 'Medium') return 'bg-yellow-100 text-yellow-700 border-yellow-300';
        return 'bg-red-100 text-red-700 border-red-300';
    }
</script>

<div class="max-w-7xl mx-auto pb-20 px-4 font-mono">

    <div class="border-b-4 border-black pb-6 mb-8 flex flex-col md:flex-row justify-between items-end gap-6">
        <div>
            <div class="bg-yellow-400 inline-block px-2 py-1 text-xs font-black uppercase tracking-widest border-2 border-black mb-2 shadow-[2px_2px_0px_black]">
                Sector 09 // Economy
            </div>
            <h2 class="text-5xl font-black uppercase tracking-tighter text-black">
                The <span class="text-transparent bg-clip-text bg-gradient-to-r from-yellow-600 to-orange-600">Workshop</span>
            </h2>
        </div>

        <div class="flex bg-black p-1 rounded gap-1">
            <button 
                on:click={() => view = 'contracts'}
                class="px-6 py-2 text-xs font-bold uppercase transition-all {view === 'contracts' ? 'bg-yellow-400 text-black' : 'text-zinc-500 hover:text-white'}"
            >
                Open Contracts
            </button>
            <button 
                on:click={() => view = 'patents'}
                class="px-6 py-2 text-xs font-bold uppercase transition-all {view === 'patents' ? 'bg-yellow-400 text-black' : 'text-zinc-500 hover:text-white'}"
            >
                Patents (Showcase)
            </button>
        </div>
    </div>

    {#if loading}
        <div class="py-20 text-center animate-pulse text-xl font-bold text-zinc-400">LOADING_SCHEMATICS...</div>
    {:else if error}
        <div class="py-20 text-center text-red-500 font-bold uppercase">{error}</div>
    {:else}
        
        {#if view === 'contracts'}
            {#if bounties.length === 0}
                <div class="py-20 text-center border-4 border-dashed border-zinc-200 text-zinc-400">
                    <span class="text-4xl block mb-2">📜</span>
                    <span class="font-bold uppercase tracking-widest">No Contracts Posted</span>
                </div>
            {:else}
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" in:fade>
                    {#each bounties as bounty, i}
                        <div 
                            class="bg-white border-4 border-zinc-200 p-6 relative group hover:border-black hover:shadow-[8px_8px_0px_black] transition-all cursor-pointer flex flex-col min-h-[280px]"
                            in:fly={{ y: 20, delay: i * 50 }}
                        >
                            {#if bounty.status === 'claimed'}
                                <div class="absolute top-4 -right-2 bg-zinc-200 text-zinc-500 px-4 py-1 text-[10px] font-black uppercase rotate-12">
                                    Claimed
                                </div>
                            {:else}
                                <div class="absolute top-4 -right-2 bg-green-500 text-black px-4 py-1 text-[10px] font-black uppercase rotate-12 shadow-sm">
                                    Available
                                </div>
                            {/if}

                            <div class="flex justify-between items-start mb-4">
                                <span class="text-3xl font-black text-black">{bounty.reward}</span>
                                <span class="px-2 py-1 rounded text-[10px] font-bold uppercase border-2 {getDifficultyColor(bounty.difficulty)}">
                                    {bounty.difficulty}
                                </span>
                            </div>

                            <h3 class="text-2xl font-black uppercase leading-tight mb-2">{bounty.title}</h3>
                            
                            <div class="flex flex-wrap gap-2 mt-auto mb-6">
                                {#each bounty.tags as tag}
                                    <span class="bg-zinc-100 text-zinc-600 px-2 py-1 text-[10px] font-bold uppercase">#{tag}</span>
                                {/each}
                            </div>

                            <button class="w-full py-3 bg-black text-yellow-400 font-black uppercase text-xs hover:bg-zinc-800 transition-colors mt-auto">
                                Accept Contract
                            </button>
                            
                            <div class="absolute top-2 left-2 text-zinc-300 text-xs">+</div>
                            <div class="absolute top-2 right-2 text-zinc-300 text-xs">+</div>
                            <div class="absolute bottom-2 left-2 text-zinc-300 text-xs">+</div>
                            <div class="absolute bottom-2 right-2 text-zinc-300 text-xs">+</div>
                        </div>
                    {/each}
                </div>
            {/if}

        {:else}
            {#if projects.length === 0}
                <div class="py-20 text-center border-4 border-dashed border-zinc-200 text-zinc-400">
                    <span class="text-4xl block mb-2">💡</span>
                    <span class="font-bold uppercase tracking-widest">No Patents Filed</span>
                </div>
            {:else}
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8" in:fade>
                    {#each projects as project, i}
                        <div 
                            class="bg-zinc-50 border-2 border-black p-2 shadow-[6px_6px_0px_rgba(0,0,0,0.1)] group hover:-translate-y-1 transition-transform"
                            in:fly={{ y: 20, delay: i * 50 }}
                        >
                            <div class="bg-white border border-zinc-200 h-full flex flex-col">
                                <div class="h-48 border-b-2 border-black overflow-hidden relative">
                                    <img 
                                        src={project.image_url || project.image || '/placeholder_project.jpg'} 
                                        alt={project.title} 
                                        class="w-full h-full object-cover grayscale group-hover:grayscale-0 transition-all duration-500" 
                                    />
                                    <div class="absolute bottom-2 right-2 bg-black text-white px-2 py-1 text-[10px] font-bold uppercase">
                                        Build #{project.id}
                                    </div>
                                </div>

                                <div class="p-5 flex-1 flex flex-col">
                                    <h3 class="text-xl font-black uppercase">{project.title}</h3>
                                    <div class="text-[10px] font-bold text-zinc-400 uppercase mb-4">Fabricated by {project.author_name}</div>
                                    
                                    <div class="flex gap-2 mb-4 flex-wrap">
                                        {#each project.tech_stack as t}
                                            <span class="border border-zinc-300 px-2 py-0.5 text-[9px] font-bold uppercase text-zinc-500">{t}</span>
                                        {/each}
                                    </div>

                                    <div class="mt-auto flex justify-between items-center border-t border-dashed border-zinc-300 pt-3">
                                        <button class="text-xs font-black uppercase flex items-center gap-1 hover:text-red-600">
                                            ♥ {project.likes_count}
                                        </button>
                                        <button class="text-[10px] font-black uppercase underline decoration-2 decoration-yellow-400 hover:bg-yellow-400 hover:no-underline px-1 transition-all">
                                            View Blueprints ->
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    {/each}
                </div>
            {/if}
        {/if}

    {/if}
</div>