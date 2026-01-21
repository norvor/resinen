<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    import type { Community } from '$lib/types'; // Using the strong type
    import { fade, fly } from 'svelte/transition';

    let communities: Community[] = [];
    let loading = true;

    // A helper to give cards a random-ish rotation without hydration errors
    function getRotation(index: number) {
        const rotations = ['rotate-1', '-rotate-2', 'rotate-3', '-rotate-1'];
        return rotations[index % rotations.length];
    }

    function getPinColor(index: number) {
        const colors = ['bg-red-500', 'bg-blue-500', 'bg-green-500', 'bg-yellow-500'];
        return colors[index % colors.length];
    }

    onMount(async () => {
        try {
            // The API now returns the real list from Postgres
            const res = await api.getCommunities();
            // Handle if backend returns wrapped object or array
            communities = Array.isArray(res) ? res : (res as any).items || [];
        } catch (e) {
            console.error("Failed to load territories:", e);
        } finally {
            loading = false;
        }
    });
</script>

<div class="w-full max-w-6xl mx-auto">
    
    <div class="mb-12 text-center relative">
        <div class="inline-block bg-white p-6 border-4 border-black shadow-[8px_8px_0px_rgba(0,0,0,0.2)] transform -rotate-1 relative">
            <div class="absolute -top-3 -left-3 w-6 h-6 rounded-full bg-red-500 border-2 border-black shadow-sm"></div>
            <div class="absolute -top-3 -right-3 w-6 h-6 rounded-full bg-red-500 border-2 border-black shadow-sm"></div>

            <h1 class="text-4xl md:text-6xl font-black uppercase tracking-tighter text-black mb-2">
                Campus Directory
            </h1>
            <p class="font-mono text-xs md:text-sm font-bold text-gray-500 uppercase tracking-widest">
                Term Spring_25 // Select a Territory
            </p>
        </div>
    </div>

    {#if loading}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 px-4">
            {#each Array(6) as _, i}
                <div class="h-64 bg-white/50 border-2 border-black/10 rounded-xl animate-pulse transform {getRotation(i)}"></div>
            {/each}
        </div>
    
    {:else if communities.length === 0}
        <div class="flex justify-center py-20">
            <div class="bg-yellow-100 p-8 md:p-12 shadow-[4px_4px_0px_rgba(0,0,0,0.1)] border-2 border-black rotate-2 max-w-md text-center relative">
                <div class="absolute -top-4 left-1/2 -translate-x-1/2 w-32 h-8 bg-white/40 border border-white/60 shadow-sm backdrop-blur-sm rotate-1"></div>
                <h3 class="text-2xl font-black text-gray-800 mb-2 uppercase">Quiet... Too Quiet.</h3>
                <p class="font-mono text-sm text-gray-600 mb-6">No territories found. Why not start your own club?</p>
                <a href="/communities/new" class="inline-block px-6 py-3 bg-black text-white font-black uppercase tracking-widest hover:scale-105 transition-transform">
                    + Initialize Territory
                </a>
            </div>
        </div>

    {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10 px-4 pb-20">
            {#each communities as c, i}
                <a href="/communities/{c.slug}" 
                   class="group relative block bg-white border-2 border-black p-6 shadow-[6px_6px_0px_rgba(0,0,0,0.2)] transition-all duration-300 hover:scale-105 hover:shadow-[12px_12px_0px_rgba(0,0,0,0.2)] hover:rotate-0 z-10 hover:z-20 {getRotation(i)}"
                >
                    <div class="absolute -top-3 left-1/2 -translate-x-1/2 w-4 h-4 rounded-full {getPinColor(i)} border-2 border-black shadow-sm group-hover:-translate-y-2 transition-transform"></div>

                    <div class="flex justify-between items-start mb-4">
                        <span class="inline-block px-2 py-1 bg-gray-100 border border-black text-[10px] font-black uppercase tracking-wider">
                            {(c as any).archetypes?.[0] || 'General'}
                        </span>
                        <span class="flex items-center gap-1 text-xs font-bold text-gray-500 bg-gray-50 px-2 py-0.5 rounded border border-gray-200">
                            👤 {(c as any).member_count ?? c._count?.members ?? 0}
                        </span>
                    </div>

                    <div class="mb-6">
                        <h2 class="text-2xl font-black uppercase leading-tight mb-3 group-hover:text-blue-600 transition-colors break-words">
                            {c.name}
                        </h2>
                        <p class="text-sm font-medium text-gray-500 leading-relaxed line-clamp-3 border-l-2 border-gray-200 pl-3">
                            {c.description || "No description provided for this territory."}
                        </p>
                    </div>

                    <div class="mt-auto border-t-2 border-dashed border-gray-200 pt-4 flex items-center justify-between">
                        <div class="flex -space-x-2">
                            <div class="w-6 h-6 rounded-full bg-gray-200 border border-black"></div>
                            <div class="w-6 h-6 rounded-full bg-gray-300 border border-black"></div>
                        </div>
                        <span class="text-xs font-black uppercase text-black bg-yellow-300 px-2 py-1 border border-black transform -rotate-2 group-hover:rotate-0 transition-transform">
                            Enter ->
                        </span>
                    </div>
                </a>
            {/each}

            <a href="/communities/new" class="group flex flex-col items-center justify-center bg-gray-100 border-2 border-dashed border-gray-400 p-6 min-h-[250px] hover:bg-white hover:border-black hover:border-solid transition-all cursor-pointer opacity-70 hover:opacity-100">
                <div class="w-16 h-16 rounded-full bg-white border-2 border-gray-400 group-hover:border-black flex items-center justify-center mb-4 transition-colors">
                    <span class="text-3xl font-black text-gray-400 group-hover:text-black">+</span>
                </div>
                <span class="font-black uppercase text-gray-400 group-hover:text-black tracking-widest">Create New</span>
            </a>
        </div>
    {/if}
</div>