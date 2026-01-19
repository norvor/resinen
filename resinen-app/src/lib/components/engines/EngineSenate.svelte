<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    export let community: any;

    let proposals: any[] = [];
    let loading = true;

    async function loadProposals() {
        loading = true;
        try {
            proposals = await api.getProposals(community.id);
        } catch (e) {
            console.error(e);
        } finally {
            loading = false;
        }
    }

    onMount(loadProposals);

    async function vote(id: string, choice: string) {
        try {
            await api.voteProposal(id, choice);
            // Refresh to see updated counts
            await loadProposals(); 
        } catch (e) {
            alert("Vote failed. You might have already voted.");
        }
    }

    function getPercentage(p: any, type: 'yes' | 'no') {
        const total = p.votes_yes + p.votes_no + p.votes_abstain;
        if (total === 0) return 0;
        const count = type === 'yes' ? p.votes_yes : p.votes_no;
        return (count / total) * 100;
    }
</script>

{#if loading}
    <div class="p-8 text-center animate-pulse text-skin-muted font-bold uppercase">Loading Senate...</div>
{:else}
    <div class="space-y-6">
        {#each proposals as p}
            <div class="skin-card p-6 relative overflow-hidden group">
                <div class="absolute top-4 right-4 text-[10px] font-black uppercase px-2 py-1 rounded border 
                    {p.status === 'active' ? 'bg-green-500/10 text-green-500 border-green-500/20' : 'bg-skin-surface text-skin-muted border-skin-border'}">
                    {p.status}
                </div>

                <div class="mb-4">
                    <div class="text-[10px] font-mono text-skin-muted mb-1 opacity-50">PROP_ID: {p.id.split('-')[0]}</div>
                    <h3 class="text-xl font-black uppercase tracking-tight text-skin-text leading-none">{p.title}</h3>
                </div>

                <p class="text-sm text-skin-muted leading-relaxed mb-6 max-w-2xl">
                    {p.description}
                </p>
                
                <div class="space-y-3 mb-6 bg-skin-surface/50 p-4 rounded-lg border border-skin-border/50">
                    <div class="flex items-center text-xs font-bold gap-4">
                        <span class="w-8 text-right text-green-500">YES</span>
                        <div class="flex-1 h-3 bg-skin-fill rounded-full overflow-hidden border border-skin-border/30 relative">
                            <div class="h-full bg-green-500 transition-all duration-500" style="width: {getPercentage(p, 'yes')}%"></div>
                        </div>
                        <span class="w-8 text-left opacity-60">{p.votes_yes}</span>
                    </div>

                    <div class="flex items-center text-xs font-bold gap-4">
                        <span class="w-8 text-right text-red-500">NO</span>
                        <div class="flex-1 h-3 bg-skin-fill rounded-full overflow-hidden border border-skin-border/30 relative">
                            <div class="h-full bg-red-500 transition-all duration-500" style="width: {getPercentage(p, 'no')}%"></div>
                        </div>
                        <span class="w-8 text-left opacity-60">{p.votes_no}</span>
                    </div>
                </div>

                {#if !p.user_vote && p.status === 'active'}
                    <div class="grid grid-cols-2 gap-4">
                        <button on:click={() => vote(p.id, 'yes')} class="py-3 border border-green-500/30 text-green-500 font-bold uppercase text-xs hover:bg-green-500 hover:text-white transition-all rounded">
                            Vote Affirmative
                        </button>
                        <button on:click={() => vote(p.id, 'no')} class="py-3 border border-red-500/30 text-red-500 font-bold uppercase text-xs hover:bg-red-500 hover:text-white transition-all rounded">
                            Vote Negative
                        </button>
                    </div>
                {:else}
                    <div class="text-center p-3 bg-skin-surface/30 rounded border border-skin-border/30">
                        <span class="text-xs font-bold uppercase text-skin-muted">
                            {#if p.user_vote}
                                You voted: <span class="text-skin-text">{p.user_vote}</span>
                            {:else}
                                Voting Closed
                            {/if}
                        </span>
                    </div>
                {/if}
            </div>
        {/each}

        {#if proposals.length === 0}
            <div class="p-12 text-center border-2 border-dashed border-skin-border rounded-xl">
                <div class="text-4xl mb-2">⚖️</div>
                <div class="font-bold text-skin-muted uppercase tracking-widest text-xs">No Active Proposals</div>
            </div>
        {/if}
    </div>
{/if}