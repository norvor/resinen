<script lang="ts">
    import { onMount } from 'svelte';
    import { api, type Framework } from '$lib/api';
    import { Plus, Loader, FileText } from 'lucide-svelte';

    let frameworks: Framework[] = [];
    let loading = true;
    let error = '';

    onMount(async () => {
        try {
            frameworks = await api.getFrameworks();
        } catch (e) {
            error = 'Failed to load frameworks. Is the backend running?';
        } finally {
            loading = false;
        }
    });
</script>

<div class="p-8 max-w-7xl mx-auto">
    <div class="flex justify-between items-center mb-8">
        <div>
            <h1 class="text-3xl font-bold text-white mb-2">Strategic Frameworks</h1>
            <p class="text-gray-400">Manage the proprietary doctrines displayed on the public site.</p>
        </div>
        <a href="/frameworks/new" class="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-500 text-white px-4 py-2 rounded font-bold transition-colors">
            <Plus size={18} />
            New Framework
        </a>
    </div>

    {#if loading}
        <div class="flex items-center gap-3 text-gray-500">
            <Loader class="animate-spin" /> Loading data...
        </div>
    {:else if error}
        <div class="p-4 bg-red-900/20 border border-red-500/50 text-red-400 rounded">
            {error}
        </div>
    {:else if frameworks.length === 0}
        <div class="text-center py-20 border border-dashed border-gray-800 rounded-xl">
            <p class="text-gray-500 mb-4">No frameworks found in the database.</p>
            <a href="/frameworks/new" class="text-cyan-500 hover:underline">Create your first one &rarr;</a>
        </div>
    {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each frameworks as fw}
                <div class="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-cyan-500/50 transition-colors group">
                    <div class="flex justify-between items-start mb-4">
                        <div class="p-2 bg-gray-800 rounded text-cyan-400 group-hover:text-white transition-colors">
                            <FileText size={24} />
                        </div>
                        <span class="text-xs font-mono text-gray-600 border border-gray-800 px-2 py-1 rounded">{fw.id}</span>
                    </div>
                    <h3 class="text-xl font-bold text-white mb-2">{fw.name}</h3>
                    <p class="text-sm text-gray-400 line-clamp-3 mb-4">{fw.description}</p>
                    <div class="flex gap-2">
                        <button class="text-xs font-bold text-gray-500 hover:text-white">EDIT</button>
                        <span class="text-gray-700">|</span>
                        <button class="text-xs font-bold text-gray-500 hover:text-red-400">DELETE</button>
                    </div>
                </div>
            {/each}
        </div>
    {/if}
</div>