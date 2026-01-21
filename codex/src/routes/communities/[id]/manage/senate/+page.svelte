<script lang="ts">
    import { onMount } from 'svelte';
    import { api, type Proposal } from '$lib/api';
    import { fade, scale } from 'svelte/transition';

    export let data;
    $: community = data.community;

    let proposals: Proposal[] = [];
    let loading = true;
    let showCreate = false;

    let newProposal = {
        title: '',
        description: '',
        end_date: ''
    };

    onMount(async () => {
        await loadSenate();
    });

    async function loadSenate() {
        loading = true;
        try {
            const res = await api.getProposals(community.id);
            proposals = Array.isArray(res) ? res : [];
        } catch (e) { console.error(e); } 
        finally { loading = false; }
    }

    async function handleCreate() {
        try {
            await api.createProposal(community.id, newProposal);
            showCreate = false;
            newProposal = { title: '', description: '', end_date: '' };
            await loadSenate();
        } catch (e) { alert("Failed to propose legislation."); }
    }

    async function handleVeto(id: string) {
        if (!confirm("VETO this proposal? It will be rejected immediately.")) return;
        try {
            await api.vetoProposal(id);
            await loadSenate();
        } catch (e) { alert("Veto failed."); }
    }
</script>

<div class="space-y-8 animate-fade-in-up">
    
    <div class="flex items-end justify-between border-b-4 border-black pb-6">
        <div>
            <div class="text-xs font-black uppercase text-purple-600 tracking-widest mb-1 flex items-center gap-2">
                <span>⚖️</span> Senate Engine
            </div>
            <h1 class="text-4xl font-black uppercase tracking-tighter">
                Governance Control
            </h1>
        </div>
        <button 
            on:click={() => showCreate = true}
            class="px-6 py-3 bg-purple-600 text-white font-black rounded uppercase text-xs shadow-[4px_4px_0px_black] hover:-translate-y-1 hover:shadow-[6px_6px_0px_black] transition-all"
        >
            + Executive Order
        </button>
    </div>

    {#if loading}
        <div class="p-12 text-center text-gray-400 font-bold animate-pulse">Counting Ballots...</div>
    {:else if proposals.length === 0}
        <div class="p-20 text-center border-4 border-dashed border-gray-200 rounded-xl text-gray-400">
            <span class="text-4xl block mb-2">🏛️</span>
            <span class="font-bold uppercase tracking-widest">No Active Legislation</span>
        </div>
    {:else}
        <div class="grid grid-cols-1 gap-4">
            {#each proposals as p}
                <div class="bg-white border-2 border-gray-200 p-6 rounded-xl flex flex-col md:flex-row gap-6 items-start md:items-center relative group hover:border-black transition-colors">
                    
                    <div class="flex-1">
                        <div class="flex items-center gap-2 mb-2">
                            <span class="px-2 py-0.5 bg-gray-100 text-[9px] font-black uppercase rounded text-gray-500">
                                Prop #{p.id.substring(0,4)}
                            </span>
                            {#if p.status === 'active'}
                                <span class="px-2 py-0.5 bg-green-100 text-green-700 text-[9px] font-black uppercase rounded animate-pulse">
                                    Voting Open
                                </span>
                            {:else}
                                <span class="px-2 py-0.5 bg-gray-100 text-gray-500 text-[9px] font-black uppercase rounded">
                                    {p.status}
                                </span>
                            {/if}
                        </div>
                        <h3 class="text-xl font-black uppercase mb-1">{p.title}</h3>
                        <p class="text-sm text-gray-500 font-bold line-clamp-1">{p.description}</p>
                    </div>

                    <div class="w-full md:w-64">
                        <div class="flex justify-between text-[10px] font-black uppercase mb-1">
                            <span class="text-green-600">Yes: {p.votes_for}</span>
                            <span class="text-red-600">No: {p.votes_against}</span>
                        </div>
                        <div class="h-2 bg-gray-200 rounded-full overflow-hidden flex">
                            <div class="bg-green-500 h-full" style="width: {(p.votes_for / (p.votes_for + p.votes_against || 1)) * 100}%"></div>
                            <div class="bg-red-500 h-full flex-1"></div>
                        </div>
                    </div>

                    <div>
                        {#if p.status === 'active'}
                            <button 
                                on:click={() => handleVeto(p.id)}
                                class="px-4 py-2 border-2 border-red-100 text-red-600 font-black uppercase text-xs rounded hover:bg-red-600 hover:text-white transition-colors"
                            >
                                Veto
                            </button>
                        {:else}
                            <button disabled class="px-4 py-2 bg-gray-100 text-gray-400 font-black uppercase text-xs rounded cursor-not-allowed">
                                Archived
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
                <h2 class="font-black text-2xl uppercase mb-6">Draft Executive Order</h2>
                
                <div class="space-y-4">
                    <div>
                        <label class="block text-xs font-bold uppercase text-gray-500 mb-1">Title</label>
                        <input bind:value={newProposal.title} class="w-full border-2 border-gray-200 p-3 rounded font-bold focus:border-black outline-none" placeholder="e.g. Increase Budget" />
                    </div>
                    <div>
                        <label class="block text-xs font-bold uppercase text-gray-500 mb-1">Details</label>
                        <textarea bind:value={newProposal.description} class="w-full border-2 border-gray-200 p-3 rounded font-bold focus:border-black outline-none resize-none h-32"></textarea>
                    </div>
                    <div>
                        <label class="block text-xs font-bold uppercase text-gray-500 mb-1">Voting Deadline</label>
                        <input type="datetime-local" bind:value={newProposal.end_date} class="w-full border-2 border-gray-200 p-3 rounded font-bold focus:border-black outline-none" />
                    </div>
                </div>

                <div class="flex gap-2 mt-8">
                    <button on:click={() => showCreate = false} class="flex-1 py-3 text-gray-500 font-bold hover:bg-gray-100 rounded">Cancel</button>
                    <button on:click={handleCreate} class="flex-1 py-3 bg-purple-600 text-white font-bold uppercase rounded">Submit Order</button>
                </div>
            </div>
        </div>
    {/if}

</div>