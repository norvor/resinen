<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    export let community: any;

    let matches: any[] = [];
    let loading = true;

    async function loadMatches() {
        try {
            matches = await api.getMatches(community.id);
        } catch (e) {
            console.error(e);
        } finally {
            loading = false;
        }
    }

    onMount(loadMatches);

    async function predict(matchId: string, teamId: string) {
        try {
            await api.predictMatch(matchId, teamId);
            // Optimistic update: Set user's pick locally
            matches = matches.map(m => m.id === matchId ? {...m, user_pick_id: teamId} : m);
        } catch (e) {
            alert("Prediction failed. Match might be locked.");
        }
    }
</script>

{#if loading}
    <div class="p-8 text-center animate-pulse text-skin-muted font-bold uppercase">Loading Arena...</div>
{:else}
    <div class="space-y-6">
        {#each matches as m}
            <div class="skin-card border-2 border-skin-border relative overflow-hidden">
                
                <div class="bg-skin-surface border-b border-skin-border p-2 flex justify-between items-center px-4">
                    <span class="text-[10px] font-black uppercase tracking-widest text-skin-muted">
                        {new Date(m.start_time).toLocaleDateString()}
                    </span>
                    <span class="text-[10px] font-black uppercase px-2 py-0.5 rounded
                        {m.status === 'live' ? 'bg-red-500 text-white animate-pulse' : 
                         m.status === 'finished' ? 'bg-skin-muted text-skin-fill' : 'bg-skin-accent/20 text-skin-accent'}">
                        {m.status === 'live' ? '● LIVE' : m.status}
                    </span>
                </div>

                <div class="p-6 grid grid-cols-3 gap-4 items-center">
                    
                    <div class="text-center">
                        <div class="w-16 h-16 mx-auto bg-skin-surface rounded-full flex items-center justify-center border-2 border-skin-border mb-2 text-2xl">
                            {m.team_a.logo_url ? '' : '🦁'}
                        </div>
                        <div class="font-black uppercase text-lg leading-none">{m.team_a.short_code}</div>
                        <div class="text-[10px] font-bold text-skin-muted">{m.team_a.name}</div>
                    </div>

                    <div class="text-center flex flex-col items-center">
                        {#if m.status === 'scheduled'}
                            <div class="text-2xl font-black text-skin-muted opacity-30">VS</div>
                            <div class="text-xs font-bold text-skin-accent mt-1">
                                {new Date(m.start_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                            </div>
                        {:else}
                            <div class="text-4xl font-mono font-black text-white tracking-widest">
                                {m.score_a}-{m.score_b}
                            </div>
                            <div class="text-xs font-mono font-bold text-red-500 mt-1">{m.time_display}</div>
                        {/if}
                    </div>

                    <div class="text-center">
                        <div class="w-16 h-16 mx-auto bg-skin-surface rounded-full flex items-center justify-center border-2 border-skin-border mb-2 text-2xl">
                            {m.team_b.logo_url ? '' : '🦅'}
                        </div>
                        <div class="font-black uppercase text-lg leading-none">{m.team_b.short_code}</div>
                        <div class="text-[10px] font-bold text-skin-muted">{m.team_b.name}</div>
                    </div>
                </div>

                <div class="px-6 pb-6 pt-2">
                    {#if m.status === 'scheduled' && !m.user_pick_id}
                        <div class="flex gap-4">
                            <button on:click={() => predict(m.id, m.team_a.id)} class="flex-1 py-3 border border-skin-border hover:bg-skin-accent hover:text-white hover:border-skin-accent transition-all text-xs font-bold uppercase rounded">
                                Pick {m.team_a.short_code}
                            </button>
                            <button on:click={() => predict(m.id, m.team_b.id)} class="flex-1 py-3 border border-skin-border hover:bg-skin-accent hover:text-white hover:border-skin-accent transition-all text-xs font-bold uppercase rounded">
                                Pick {m.team_b.short_code}
                            </button>
                        </div>
                    {:else}
                        <div class="space-y-1">
                            <div class="flex justify-between text-[10px] font-bold uppercase text-skin-muted mb-1">
                                <span>Prediction Consensus</span>
                                <span>{m.total_predictions} Picks</span>
                            </div>
                            <div class="flex h-2 rounded-full overflow-hidden">
                                <div class="bg-skin-text transition-all duration-500" style="width: {m.pick_pct_a}%"></div>
                                <div class="bg-skin-border transition-all duration-500" style="width: {m.pick_pct_b}%"></div>
                            </div>
                            <div class="flex justify-between text-[10px] font-bold">
                                <span>{m.pick_pct_a}% {m.team_a.short_code}</span>
                                <span>{m.team_b.short_code} {m.pick_pct_b}%</span>
                            </div>
                        </div>

                        {#if m.user_pick_id}
                             <div class="mt-4 text-center text-xs font-bold uppercase text-skin-accent">
                                You Picked: {m.user_pick_id === m.team_a.id ? m.team_a.name : m.team_b.name}
                             </div>
                        {/if}
                    {/if}
                </div>

            </div>
        {/each}

        {#if matches.length === 0}
            <div class="p-12 text-center border-2 border-dashed border-skin-border rounded-xl">
                <div class="text-4xl mb-2">⚔️</div>
                <div class="font-bold text-skin-muted uppercase tracking-widest text-xs">No Matches Scheduled</div>
            </div>
        {/if}
    </div>
{/if}