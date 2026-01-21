<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    import { scale } from 'svelte/transition';
    import type { Community, User } from '$lib/types';

    // Define the interface locally if not yet exported globally
    interface Proposal {
        id: string;
        title: string;
        description: string;
        status: 'active' | 'passed' | 'rejected' | 'vetoed';
        votes_for: number;
        votes_against: number;
        total_seats?: number;
        end_date?: string;
    }

    export let community: Community;
    export let currentUser: User | null;

    let proposals: Proposal[] = [];
    let loading = true;
    let selectedProp: Proposal | null = null;
    let error: string | null = null;

    onMount(async () => {
        if (!community?.id) return;
        try {
            // Fetch real proposals
            const res = await api.getProposals(community.id);
            // Handle pagination wrapper if present
            proposals = Array.isArray(res) ? res : (res as any).items || [];
            
            if (proposals.length > 0) {
                selectedProp = proposals[0];
            }
        } catch (e) {
            console.error("Senate Load Error:", e);
            error = "Could not retrieve the docket.";
        } finally {
            loading = false;
        }
    });

    async function castVote(choice: 'for' | 'against') {
        if (!selectedProp || selectedProp.status !== 'active') return;
        
        // Optimistic UI Update
        if (choice === 'for') selectedProp.votes_for++;
        else selectedProp.votes_against++;
        
        // Force reactivity for the visualizer to redraw
        selectedProp = { ...selectedProp };

        try {
            await api.voteProposal(selectedProp.id, choice);
        } catch (e) {
            console.error("Vote failed", e);
            // Revert on failure
            if (choice === 'for') selectedProp.votes_for--;
            else selectedProp.votes_against--;
            selectedProp = { ...selectedProp };
            alert("Vote Failed: System Error");
        }
    }

    // Generate dots for the parliament visualizer
    function getSeats(prop: Proposal) {
        const total = prop.total_seats || 100;
        const yes = prop.votes_for || 0;
        const no = prop.votes_against || 0;
        // Clamp empty seats so we don't get negative numbers
        const empty = Math.max(0, total - yes - no);
        
        let seats = [];
        for (let i = 0; i < yes; i++) seats.push('bg-green-600');
        for (let i = 0; i < no; i++) seats.push('bg-red-600');
        for (let i = 0; i < empty; i++) seats.push('bg-zinc-200');
        
        return seats;
    }
</script>

<div class="max-w-6xl mx-auto pb-20 px-4 flex flex-col lg:flex-row gap-8 min-h-[80vh]">

    <div class="w-full lg:w-1/3 border-r-2 border-zinc-200 pr-0 lg:pr-8">
        <div class="mb-8 border-b-2 border-zinc-900 pb-4">
            <h2 class="text-3xl font-serif font-black uppercase text-zinc-900">The Docket</h2>
            <p class="text-xs font-bold uppercase text-zinc-400 tracking-widest mt-1">Legislative Branch</p>
        </div>

        {#if error}
             <div class="p-4 bg-red-50 text-red-600 text-xs font-bold border border-red-200 rounded">
                 {error}
             </div>
        {/if}

        <div class="space-y-4">
            {#each proposals as p}
                <button 
                    on:click={() => selectedProp = p}
                    class="w-full text-left p-4 border-2 transition-all duration-200 group relative
                    {selectedProp?.id === p.id 
                        ? 'bg-purple-900 text-white border-purple-900 shadow-lg' 
                        : 'bg-white border-zinc-200 text-zinc-500 hover:border-purple-300'}"
                >
                    <div class="flex justify-between items-start mb-2">
                        <span class="text-[10px] font-black uppercase tracking-widest opacity-70">
                            #{p.id.slice(0, 6)}
                        </span>
                        {#if p.status === 'active'}
                            <span class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                        {:else}
                            <span class="text-[9px] font-bold border border-current px-1 rounded uppercase">{p.status}</span>
                        {/if}
                    </div>
                    <h3 class="font-bold text-lg leading-tight font-serif mb-1 group-hover:underline decoration-2 underline-offset-2 line-clamp-2">
                        {p.title}
                    </h3>
                </button>
            {/each}

            {#if !loading && proposals.length === 0 && !error}
                <div class="text-center py-12 border-2 border-dashed border-zinc-200 text-zinc-400">
                    <div class="text-4xl mb-2">⚖️</div>
                    <div class="text-xs font-bold uppercase">No Active Bills</div>
                </div>
            {/if}
        </div>
    </div>

    <div class="flex-1 bg-zinc-50 rounded-2xl p-8 border border-zinc-200 relative overflow-hidden flex flex-col">
        
        {#if selectedProp}
            <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-9xl text-zinc-200 pointer-events-none opacity-20 font-serif font-black">
                ⚖️
            </div>

            <div class="relative z-10 text-center mb-12">
                <div class="inline-block border-b-2 border-zinc-300 pb-1 mb-4 text-[10px] font-black uppercase tracking-[0.3em] text-zinc-400">
                    Active Session
                </div>
                <h1 class="text-4xl md:text-5xl font-serif font-black text-zinc-900 mb-6 leading-tight">
                    {selectedProp.title}
                </h1>
                <p class="text-zinc-600 font-serif text-lg italic max-w-2xl mx-auto leading-relaxed">
                    "{selectedProp.description}"
                </p>
            </div>

            <div class="relative z-10 flex-1 flex flex-col items-center justify-center mb-12">
                <div class="flex flex-wrap justify-center gap-1.5 max-w-lg mx-auto">
                    {#each getSeats(selectedProp) as seatClass, i}
                        <div class="w-3 h-3 rounded-full {seatClass} transition-colors duration-500 shadow-sm"
                             in:scale={{ delay: i * 2, duration: 200 }}>
                        </div>
                    {/each}
                </div>
                
                <div class="flex gap-6 mt-6 text-[10px] font-bold uppercase text-zinc-400">
                    <div class="flex items-center gap-2"><div class="w-3 h-3 bg-green-600 rounded-full"></div> Ayes ({selectedProp.votes_for})</div>
                    <div class="flex items-center gap-2"><div class="w-3 h-3 bg-red-600 rounded-full"></div> Nays ({selectedProp.votes_against})</div>
                </div>
            </div>

            <div class="relative z-10 mt-auto border-t border-zinc-200 pt-8 flex justify-center gap-4">
                {#if selectedProp.status === 'active'}
                    <button 
                        on:click={() => castVote('for')}
                        class="px-8 py-4 bg-white border-2 border-green-600 text-green-700 font-black uppercase tracking-widest hover:bg-green-600 hover:text-white transition-all shadow-[0_4px_0_#16a34a] active:translate-y-1 active:shadow-none rounded-lg"
                    >
                        Aye (Approve)
                    </button>
                    <button 
                        on:click={() => castVote('against')}
                        class="px-8 py-4 bg-white border-2 border-red-600 text-red-700 font-black uppercase tracking-widest hover:bg-red-600 hover:text-white transition-all shadow-[0_4px_0_#dc2626] active:translate-y-1 active:shadow-none rounded-lg"
                    >
                        Nay (Reject)
                    </button>
                {:else}
                    <div class="px-8 py-4 bg-zinc-200 text-zinc-500 font-black uppercase tracking-widest rounded-lg cursor-not-allowed">
                        Voting Closed
                    </div>
                {/if}
            </div>

        {:else}
            <div class="flex items-center justify-center h-full text-zinc-300 font-black uppercase text-2xl text-center">
                {#if loading}
                    Reading Docket...
                {:else}
                    Select a Bill from the Docket
                {/if}
            </div>
        {/if}
    </div>

</div>