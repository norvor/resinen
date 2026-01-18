<script lang="ts">
    import { onMount } from 'svelte';
    import { api, type Community } from '$lib/api';

    let communities: Community[] = [];
    let loading = true;

    onMount(async () => {
        try {
            communities = await api.getCommunities();
        } catch (e) {
            console.error("Failed to load communities", e);
        } finally {
            loading = false;
        }
    });
</script>

<div class="max-w-6xl mx-auto p-8">
    <div class="flex justify-between items-center mb-8 border-b border-slate-800 pb-6">
        <h1 class="text-3xl font-bold text-white">Territories</h1>
        <a href="/communities/new" class="bg-orange-600 hover:bg-orange-500 text-white font-bold py-2 px-6 rounded-lg transition-colors">
            + New
        </a>
    </div>

    {#if loading}
        <div class="text-slate-500 animate-pulse">Loading...</div>
    {:else if communities.length === 0}
        <div class="text-center py-24 border border-dashed border-slate-800 rounded-xl">
            <h3 class="text-white font-bold">No Territories</h3>
            <p class="text-slate-500 text-sm mt-1">Initialize your first node to begin.</p>
        </div>
    {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each communities as comm}
                <a href="/communities/{comm.id}" class="block bg-slate-950 border border-slate-800 rounded-xl p-6 hover:border-orange-500 transition-colors group">
                    <div class="flex justify-between items-start mb-4">
                        <span class="font-bold text-lg text-white group-hover:text-orange-500 transition-colors">
                            {comm.name}
                        </span>
                        {#if comm.is_private}
                            <span class="bg-slate-900 text-orange-500 text-[10px] px-2 py-1 rounded uppercase font-bold border border-slate-800">
                                Private
                            </span>
                        {/if}
                    </div>
                    
                    <p class="text-slate-400 text-sm line-clamp-2 mb-4 h-10">
                        {comm.description || 'No description provided.'}
                    </p>

                    <div class="flex items-center justify-between text-xs text-slate-500 border-t border-slate-900 pt-4">
                        <span class="font-mono opacity-50">{comm.slug}</span>
                        <span class="font-bold">{comm.member_count || 0} Citizens</span>
                    </div>
                </a>
            {/each}
        </div>
    {/if}
</div>