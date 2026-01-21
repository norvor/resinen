<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';

    export let communityId: string;

    let proposal: any = null;
    let loading = true;
    let voting = false;

    onMount(async () => {
        try {
            const props = await api.getProposals(communityId);
            // Prioritize active proposals, otherwise show the most recent one
            proposal = props.find((p: any) => p.status === 'active') || props[0] || null;
        } catch (e) {
            console.error(e);
        } finally {
            loading = false;
        }
    });

    async function vote(choice: 'yes' | 'no') {
        if (!proposal) return;
        voting = true;
        try {
            await api.castVote(proposal.id, choice);
            // Optimistic update
            proposal.user_vote = choice;
            if (choice === 'yes') proposal.votes_yes++;
            else proposal.votes_no++;
        } catch (e) {
            alert("Vote failed. Polls might be closed.");
        } finally {
            voting = false;
        }
    }

    function getApproval(p: any) {
        const total = (p.votes_yes || 0) + (p.votes_no || 0) + (p.votes_abstain || 0);
        if (total === 0) return 0;
        return Math.round((p.votes_yes / total) * 100);
    }
</script>

<div class="h-full w-full">
    {#if loading}
        <div class="h-full bg-skin-surface/50 animate-pulse rounded-2xl border border-skin-border"></div>
    {:else if proposal}
        
        <a href="/communities/{communityId}?tab=senate" class="block h-full bg-white border-2 border-zinc-900 rounded-2xl p-5 flex flex-col justify-between relative group hover:-translate-y-1 hover:shadow-[4px_4px_0px_rgba(0,0,0,1)] transition-all duration-200">
            
            <div class="absolute inset-0 flex items-center justify-center pointer-events-none opacity-5">
                <span class="text-8xl">⚖️</span>
            </div>

            <div class="relative z-10 flex justify-between items-start">
                <div>
                    <span class="text-[9px] font-black uppercase bg-zinc-900 text-white px-1.5 py-0.5 mb-1 inline-block">
                        Referendum
                    </span>
                    {#if proposal.status === 'active'}
                        <span class="ml-1 text-[9px] font-bold text-green-600 uppercase animate-pulse">● Live</span>
                    {/if}
                </div>
                
                <div class="flex flex-col items-end">
                    <span class="text-[10px] font-black text-zinc-400">{getApproval(proposal)}% Yes</span>
                    <div class="w-12 h-1.5 bg-zinc-100 rounded-full overflow-hidden mt-0.5">
                        <div class="h-full bg-green-500" style="width: {getApproval(proposal)}%"></div>
                    </div>
                </div>
            </div>

            <div class="relative z-10 mt-3 flex-1">
                <h3 class="text-lg font-black uppercase leading-tight line-clamp-3 text-zinc-900">
                    {proposal.title}
                </h3>
                <p class="text-[10px] text-zinc-500 mt-2 font-mono line-clamp-2">
                    PROP_ID: {proposal.id.split('-')[0]}
                </p>
            </div>

            <div class="relative z-10 mt-4 pt-3 border-t border-dashed border-zinc-200">
                {#if proposal.user_vote}
                    <div class="w-full py-2 bg-zinc-50 border border-zinc-200 text-center rounded-lg">
                        <span class="text-[10px] font-bold uppercase text-zinc-400">You Voted</span>
                        <span class="ml-1 text-xs font-black uppercase {proposal.user_vote === 'yes' ? 'text-green-600' : 'text-red-600'}">
                            {proposal.user_vote}
                        </span>
                    </div>
                {:else if proposal.status === 'active'}
                    <div class="flex gap-2" on:click|preventDefault>
                        <button 
                            on:click|stopPropagation={() => vote('yes')}
                            disabled={voting}
                            class="flex-1 py-2 bg-white border border-zinc-300 hover:bg-green-500 hover:text-white hover:border-green-600 transition-colors text-[10px] font-black uppercase rounded shadow-sm"
                        >
                            Aye
                        </button>
                        <button 
                            on:click|stopPropagation={() => vote('no')}
                            disabled={voting}
                            class="flex-1 py-2 bg-white border border-zinc-300 hover:bg-red-500 hover:text-white hover:border-red-600 transition-colors text-[10px] font-black uppercase rounded shadow-sm"
                        >
                            Nay
                        </button>
                    </div>
                {:else}
                    <div class="w-full py-2 bg-zinc-100 text-center rounded text-[10px] font-bold uppercase text-zinc-400">
                        Voting Closed
                    </div>
                {/if}
            </div>
        </a>

    {:else}
        <div class="h-full bg-zinc-50 rounded-2xl border-2 border-dashed border-zinc-200 flex items-center justify-center flex-col text-zinc-400">
            <span class="text-2xl mb-1">🏛️</span>
            <span class="text-[10px] font-bold uppercase">Senate Recess</span>
        </div>
    {/if}
</div>