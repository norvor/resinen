<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';

    let communities: any[] = [];
    let isLoading = true;

    onMount(async () => {
        try {
            communities = await api.getCommunities();
        } catch (e) {
            alert('Error loading data');
        } finally {
            isLoading = false;
        }
    });
</script>

<div class="max-w-6xl mx-auto">
    <div class="flex justify-between items-center mb-8">
        <div>
            <h1 class="text-3xl font-bold text-white tracking-tight">Communities</h1>
            <p class="text-slate-400 mt-1">The root layer of your ecosystem.</p>
        </div>
        <a href="/communities/new" class="bg-orange-600 hover:bg-orange-500 text-white px-6 py-3 rounded-lg font-bold transition-all shadow-lg hover:shadow-orange-500/20">
            + Initialize New
        </a>
    </div>

    {#if isLoading}
        <div class="text-slate-500 animate-pulse">Syncing with mainframe...</div>
    
    {:else if communities.length === 0}
        <div class="bg-slate-950 border border-slate-800 rounded-2xl p-12 text-center">
            <h3 class="text-xl font-bold text-slate-300">System Empty</h3>
            <p class="text-slate-500 mt-2 mb-6">No communities detected. Start by creating the first one.</p>
            <a href="/communities/new" class="text-orange-500 hover:underline">Create Genesis Community &rarr;</a>
        </div>

    {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each communities as c}
                <a href="/communities/{c.id}" class="group block bg-slate-950 border border-slate-800 hover:border-orange-500/50 rounded-2xl p-6 transition-all hover:-translate-y-1">
                    <div class="flex items-start justify-between mb-4">
                        <div class="h-12 w-12 bg-slate-900 rounded-full flex items-center justify-center text-xl font-bold text-slate-300 group-hover:bg-orange-600 group-hover:text-white transition-colors">
                            {c.name.charAt(0)}
                        </div>
                        <span class="text-xs font-mono text-slate-600 border border-slate-800 rounded px-2 py-1">/{c.slug}</span>
                    </div>
                    <h3 class="text-xl font-bold text-white mb-2">{c.name}</h3>
                    <p class="text-slate-400 text-sm line-clamp-2">{c.description || "No description provided."}</p>
                </a>
            {/each}
        </div>
    {/if}
</div>