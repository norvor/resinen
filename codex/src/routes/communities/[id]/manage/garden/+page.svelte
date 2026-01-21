<script lang="ts">
    import { onMount } from 'svelte';
    import { api, type Resource } from '$lib/api';
    import { fade, scale } from 'svelte/transition';

    export let data;
    $: community = data.community;

    let resources: Resource[] = [];
    let loading = true;
    let showAdd = false;

    let newResource = {
        title: '',
        url: '',
        category: 'Tools',
        description: ''
    };

    onMount(async () => {
        await loadGarden();
    });

    async function loadGarden() {
        loading = true;
        try {
            const res = await api.getGarden(community.id);
            resources = Array.isArray(res) ? res : [];
        } catch (e) { console.error(e); } 
        finally { loading = false; }
    }

    async function handlePlant() {
        try {
            await api.plantResource(community.id, newResource);
            showAdd = false;
            newResource = { title: '', url: '', category: 'Tools', description: '' };
            await loadGarden();
        } catch (e) { alert("Planting failed."); }
    }

    async function handleDelete(id: string) {
        if (!confirm("Prune this resource?")) return;
        try {
            await api.pruneResource(id);
            await loadGarden();
        } catch (e) { alert("Pruning failed."); }
    }
</script>

<div class="space-y-8 animate-fade-in-up">
    
    <div class="flex items-end justify-between border-b-4 border-black pb-6">
        <div>
            <div class="text-xs font-black uppercase text-green-600 tracking-widest mb-1 flex items-center gap-2">
                <span>🌻</span> Garden Engine
            </div>
            <h1 class="text-4xl font-black uppercase tracking-tighter">
                Resource Management
            </h1>
        </div>
        <button 
            on:click={() => showAdd = true}
            class="px-6 py-3 bg-green-600 text-white font-black rounded uppercase text-xs shadow-[4px_4px_0px_black] hover:-translate-y-1 hover:shadow-[6px_6px_0px_black] transition-all"
        >
            + Plant Seed
        </button>
    </div>

    {#if loading}
        <div class="p-12 text-center text-gray-400 font-bold animate-pulse">Checking Soil...</div>
    {:else if resources.length === 0}
        <div class="p-20 text-center border-4 border-dashed border-gray-200 rounded-xl text-gray-400">
            <span class="text-4xl block mb-2">🌱</span>
            <span class="font-bold uppercase tracking-widest">Garden is Empty</span>
        </div>
    {:else}
        <div class="bg-white border-2 border-gray-200 rounded-xl overflow-hidden shadow-sm">
            <table class="w-full text-left">
                <thead class="bg-gray-50 border-b border-gray-200 text-xs font-black uppercase text-gray-400 tracking-widest">
                    <tr>
                        <th class="p-4">Title</th>
                        <th class="p-4">Category</th>
                        <th class="p-4">Link</th>
                        <th class="p-4 text-right">Actions</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-100 text-sm">
                    {#each resources as r}
                        <tr class="hover:bg-gray-50 transition-colors">
                            <td class="p-4 font-bold text-gray-900">{r.title}</td>
                            <td class="p-4">
                                <span class="px-2 py-1 bg-green-50 text-green-700 rounded text-[10px] font-bold uppercase border border-green-100">
                                    {r.category}
                                </span>
                            </td>
                            <td class="p-4 font-mono text-gray-500 truncate max-w-[200px]">
                                <a href={r.url} target="_blank" class="hover:text-black hover:underline">{r.url}</a>
                            </td>
                            <td class="p-4 text-right">
                                <button 
                                    on:click={() => handleDelete(r.id)}
                                    class="text-red-500 font-bold hover:text-red-700 text-xs uppercase"
                                >
                                    Prune 🗑️
                                </button>
                            </td>
                        </tr>
                    {/each}
                </tbody>
            </table>
        </div>
    {/if}

    {#if showAdd}
        <div class="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4 backdrop-blur-sm" transition:fade>
            <div class="bg-white w-full max-w-lg rounded-xl p-8 shadow-2xl" in:scale>
                <h2 class="font-black text-2xl uppercase mb-6">Plant New Seed</h2>
                
                <div class="space-y-4">
                    <div>
                        <label class="block text-xs font-bold uppercase text-gray-500 mb-1">Title</label>
                        <input bind:value={newResource.title} class="w-full border-2 border-gray-200 p-3 rounded font-bold focus:border-black outline-none" />
                    </div>
                    <div>
                        <label class="block text-xs font-bold uppercase text-gray-500 mb-1">URL</label>
                        <input bind:value={newResource.url} class="w-full border-2 border-gray-200 p-3 rounded font-bold focus:border-black outline-none" />
                    </div>
                    <div>
                        <label class="block text-xs font-bold uppercase text-gray-500 mb-1">Category</label>
                        <select bind:value={newResource.category} class="w-full border-2 border-gray-200 p-3 rounded font-bold focus:border-black outline-none bg-white">
                            <option>Tools</option>
                            <option>Assets</option>
                            <option>Reading</option>
                            <option>Inspiration</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-bold uppercase text-gray-500 mb-1">Description</label>
                        <textarea bind:value={newResource.description} class="w-full border-2 border-gray-200 p-3 rounded font-bold focus:border-black outline-none resize-none h-20"></textarea>
                    </div>
                </div>

                <div class="flex gap-2 mt-8">
                    <button on:click={() => showAdd = false} class="flex-1 py-3 text-gray-500 font-bold hover:bg-gray-100 rounded">Cancel</button>
                    <button on:click={handlePlant} class="flex-1 py-3 bg-green-600 text-white font-bold uppercase rounded">Plant</button>
                </div>
            </div>
        </div>
    {/if}

</div>