<script lang="ts">
    import { onMount } from 'svelte';
    import { api, type Bounty } from '$lib/api';
    import { fade, scale } from 'svelte/transition';

    export let data;
    $: community = data.community;

    let bounties: Bounty[] = [];
    let loading = true;
    let showCreate = false;

    // Form
    let newBounty = {
        title: '',
        reward: '',
        difficulty: 'Medium',
        tags: ''
    };

    onMount(async () => {
        await loadBounties();
    });

    async function loadBounties() {
        loading = true;
        try {
            const res = await api.getBounties(community.id);
            bounties = Array.isArray(res) ? res : [];
        } catch (e) { console.error(e); } 
        finally { loading = false; }
    }

    async function handleCreate() {
        try {
            const payload = {
                ...newBounty,
                tags: newBounty.tags.split(',').map(t => t.trim()),
                status: 'open'
            };
            await api.createBounty(community.id, payload);
            showCreate = false;
            await loadBounties();
            newBounty = { title: '', reward: '', difficulty: 'Medium', tags: '' };
        } catch (e) {
            alert("Failed to post contract.");
        }
    }

    async function closeBounty(id: string) {
        if (!confirm("Are you sure you want to close this contract?")) return;
        try {
            await api.closeBounty(id);
            await loadBounties();
        } catch(e) { alert("Error closing bounty."); }
    }
</script>

<div class="space-y-8 animate-fade-in-up">
    
    <div class="flex items-end justify-between border-b-4 border-black pb-6">
        <div>
            <div class="text-xs font-black uppercase text-yellow-600 tracking-widest mb-1 flex items-center gap-2">
                <span>💰</span> Guild Engine
            </div>
            <h1 class="text-4xl font-black uppercase tracking-tighter">
                Contract Management
            </h1>
        </div>
        <button 
            on:click={() => showCreate = true}
            class="px-6 py-3 bg-yellow-400 text-black font-black rounded uppercase text-xs shadow-[4px_4px_0px_black] hover:-translate-y-1 hover:shadow-[6px_6px_0px_black] transition-all"
        >
            + Post Bounty
        </button>
    </div>

    {#if loading}
        <div class="p-12 text-center text-gray-400 font-bold animate-pulse">LOADING LEDGER...</div>
    {:else if bounties.length === 0}
        <div class="p-20 text-center border-4 border-dashed border-gray-200 rounded-xl text-gray-400">
            <span class="text-4xl block mb-2">📜</span>
            <span class="font-bold uppercase tracking-widest">No Active Contracts</span>
        </div>
    {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each bounties as bounty}
                <div class="bg-white border-2 border-gray-200 p-6 flex flex-col relative group hover:border-black transition-colors">
                    
                    <div class="flex justify-between items-start mb-4">
                        <span class="text-2xl font-black text-black">{bounty.reward}</span>
                        <span class="px-2 py-1 bg-gray-100 text-[10px] font-bold uppercase rounded border border-gray-200">
                            {bounty.difficulty}
                        </span>
                    </div>

                    <h3 class="font-black uppercase text-lg leading-tight mb-2">{bounty.title}</h3>
                    
                    <div class="flex flex-wrap gap-2 mb-6">
                        {#each bounty.tags as tag}
                            <span class="text-[10px] font-bold text-gray-400">#{tag}</span>
                        {/each}
                    </div>

                    <div class="mt-auto pt-4 border-t border-gray-100 flex justify-between items-center">
                        <span class="text-[10px] font-bold uppercase {bounty.status === 'open' ? 'text-green-600' : 'text-gray-400'}">
                            ● {bounty.status}
                        </span>
                        
                        {#if bounty.status === 'open'}
                            <button 
                                on:click={() => closeBounty(bounty.id)}
                                class="text-xs font-bold text-red-600 hover:underline"
                            >
                                Close Contract
                            </button>
                        {/if}
                    </div>
                </div>
            {/each}
        </div>
    {/if}

    {#if showCreate}
        <div class="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4 backdrop-blur-sm" transition:fade>
            <div class="bg-white w-full max-w-lg rounded-xl p-8 shadow-2xl" in:scale>
                <h2 class="font-black text-2xl uppercase mb-6">Issue New Contract</h2>
                
                <div class="space-y-4">
                    <div>
                        <label class="block text-xs font-bold uppercase text-gray-500 mb-1">Title</label>
                        <input bind:value={newBounty.title} class="w-full border-2 border-gray-200 p-3 rounded font-bold focus:border-black outline-none" placeholder="e.g. Design Logo" />
                    </div>
                    
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs font-bold uppercase text-gray-500 mb-1">Reward</label>
                            <input bind:value={newBounty.reward} class="w-full border-2 border-gray-200 p-3 rounded font-bold focus:border-black outline-none" placeholder="$500" />
                        </div>
                        <div>
                            <label class="block text-xs font-bold uppercase text-gray-500 mb-1">Difficulty</label>
                            <select bind:value={newBounty.difficulty} class="w-full border-2 border-gray-200 p-3 rounded font-bold focus:border-black outline-none bg-white">
                                <option>Easy</option>
                                <option>Medium</option>
                                <option>Hard</option>
                            </select>
                        </div>
                    </div>

                    <div>
                        <label class="block text-xs font-bold uppercase text-gray-500 mb-1">Tags (Comma Separated)</label>
                        <input bind:value={newBounty.tags} class="w-full border-2 border-gray-200 p-3 rounded font-bold focus:border-black outline-none" placeholder="Design, Frontend, React" />
                    </div>
                </div>

                <div class="flex gap-2 mt-8">
                    <button on:click={() => showCreate = false} class="flex-1 py-3 text-gray-500 font-bold hover:bg-gray-100 rounded">Cancel</button>
                    <button on:click={handleCreate} class="flex-1 py-3 bg-black text-white font-bold uppercase rounded">Publish Contract</button>
                </div>
            </div>
        </div>
    {/if}

</div>