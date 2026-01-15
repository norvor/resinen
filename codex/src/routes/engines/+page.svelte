<script lang="ts">
    import { onMount } from 'svelte';
    import { api, type Engine } from '$lib/api';
    import { Plus, Loader, Zap } from 'lucide-svelte';

    let engines: Engine[] = [];
    let loading = true;
    let error = '';

    onMount(async () => {
        try {
            engines = await api.getEngines();
        } catch (e) {
            error = 'Failed to load engines.';
        } finally {
            loading = false;
        }
    });
</script>

<div class="p-8 max-w-7xl mx-auto">
    <div class="flex justify-between items-center mb-8">
        <div>
            <h1 class="text-3xl font-bold text-white mb-2">Operational Engines</h1>
            <p class="text-gray-400">Manage the tactical systems and capabilities.</p>
        </div>
        <a href="/engines/new" class="flex items-center gap-2 bg-green-600 hover:bg-green-500 text-white px-4 py-2 rounded font-bold transition-colors">
            <Plus size={18} />
            New Engine
        </a>
    </div>

    {#if loading}
        <div class="flex items-center gap-3 text-gray-500">
            <Loader class="animate-spin" /> Loading data...
        </div>
    {:else if error}
        <div class="p-4 bg-red-900/20 border border-red-500/50 text-red-400 rounded">{error}</div>
    {:else if engines.length === 0}
        <div class="text-center py-20 border border-dashed border-gray-800 rounded-xl">
            <p class="text-gray-500 mb-4">No engines operational.</p>
            <a href="/engines/new" class="text-green-500 hover:underline">Initialize System &rarr;</a>
        </div>
    {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each engines as eng}
                <div class="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-green-500/50 transition-colors group">
                    <div class="flex justify-between items-start mb-4">
                        <div class="p-2 bg-gray-800 rounded text-green-500 group-hover:text-white transition-colors">
                            <Zap size={24} />
                        </div>
                        <span class="text-xs font-mono text-gray-600 border border-gray-800 px-2 py-1 rounded">{eng.id}</span>
                    </div>
                    <h3 class="text-xl font-bold text-white mb-2">{eng.name}</h3>
                    <p class="text-sm text-gray-400 line-clamp-3 mb-4">{eng.description}</p>
                    <div class="flex gap-2 border-t border-gray-800 pt-4 mt-4">
                        <button class="text-xs font-bold text-gray-500 hover:text-white">CONFIGURE</button>
                    </div>
                </div>
            {/each}
        </div>
    {/if}
</div>