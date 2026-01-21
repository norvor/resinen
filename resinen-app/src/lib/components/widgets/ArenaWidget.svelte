<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';

    export let communityId: string;
    
    let match: any = null;
    let loading = true;
    let betting = false;

    // Mock Data Fallback (in case no matches exist yet)
    const MOCK_MATCH = {
        id: 'demo',
        team_a: { name: 'Tigers', color: 'text-orange-600' },
        team_b: { name: 'Falcons', color: 'text-blue-600' },
        score_a: 0,
        score_b: 0,
        status: 'SCHEDULED', // or LIVE
        start_time: new Date(),
        user_pick_id: null
    };

    onMount(async () => {
        try {
            const matches = await api.getMatches(communityId);
            match = matches[0] || null; // Get the next relevant match
        } catch {
            match = null;
        } finally {
            loading = false;
        }
    });

    async function placeBet(teamId: string) {
        if (!match) return;
        betting = true;
        try {
            await api.predictMatch(match.id, teamId);
            match.user_pick_id = teamId; // Optimistic update
        } catch (e) {
            alert("Bookie rejected the bet.");
        } finally {
            betting = false;
        }
    }
</script>

<div class="h-full w-full relative group perspective-1000">
    
    {#if loading}
        <div class="h-full bg-gray-100 animate-pulse rounded-2xl"></div>
    {:else if match || MOCK_MATCH}
        {@const m = match || MOCK_MATCH}
        
        <div class="h-full bg-white rounded-2xl border-2 border-zinc-200 shadow-sm flex flex-col relative overflow-hidden transition-transform group-hover:scale-[1.02] group-hover:shadow-md">
            
            <div class="bg-zinc-900 text-white p-3 flex justify-between items-center z-10">
                <span class="text-[10px] font-black uppercase tracking-widest text-zinc-400">Varsity League</span>
                {#if m.status === 'LIVE'}
                    <span class="bg-red-600 text-white px-2 py-0.5 text-[9px] font-black uppercase rounded animate-pulse">Live</span>
                {:else}
                    <span class="text-[9px] font-mono font-bold">{new Date(m.start_time).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}</span>
                {/if}
            </div>

            <div class="flex-1 flex items-center justify-between px-4 py-2 z-10">
                <div class="text-center flex-1">
                    <div class="text-2xl font-black uppercase leading-none tracking-tighter text-orange-600">{m.team_a.name}</div>
                    {#if m.status !== 'SCHEDULED'}
                        <div class="text-3xl font-mono font-bold text-black">{m.score_a}</div>
                    {/if}
                    
                    {#if m.status === 'SCHEDULED'}
                        <button 
                            on:click={() => placeBet(m.team_a.id)}
                            disabled={!!m.user_pick_id}
                            class="mt-2 text-[9px] font-black uppercase border border-black px-2 py-1 rounded hover:bg-black hover:text-white transition-colors {m.user_pick_id === m.team_a.id ? 'bg-black text-white' : ''}"
                        >
                            {m.user_pick_id === m.team_a.id ? 'PICKED' : 'BET'}
                        </button>
                    {/if}
                </div>

                <div class="flex flex-col items-center px-2">
                    <span class="text-xl font-black italic text-zinc-200">VS</span>
                </div>

                <div class="text-center flex-1">
                    <div class="text-2xl font-black uppercase leading-none tracking-tighter text-blue-600">{m.team_b.name}</div>
                    {#if m.status !== 'SCHEDULED'}
                        <div class="text-3xl font-mono font-bold text-black">{m.score_b}</div>
                    {/if}

                    {#if m.status === 'SCHEDULED'}
                        <button 
                            on:click={() => placeBet(m.team_b.id)}
                            disabled={!!m.user_pick_id}
                            class="mt-2 text-[9px] font-black uppercase border border-black px-2 py-1 rounded hover:bg-black hover:text-white transition-colors {m.user_pick_id === m.team_b.id ? 'bg-black text-white' : ''}"
                        >
                            {m.user_pick_id === m.team_b.id ? 'PICKED' : 'BET'}
                        </button>
                    {/if}
                </div>
            </div>

            <div class="absolute top-1/2 -left-3 w-6 h-6 bg-zinc-100 rounded-full z-20"></div>
            <div class="absolute top-1/2 -right-3 w-6 h-6 bg-zinc-100 rounded-full z-20"></div>
            <div class="absolute top-1/2 left-4 right-4 h-[2px] border-t-2 border-dashed border-zinc-200 z-0"></div>

        </div>
    {:else}
        <div class="h-full bg-zinc-50 rounded-2xl border-2 border-dashed border-zinc-200 flex items-center justify-center">
            <span class="text-xs font-bold text-zinc-400 uppercase">No Matches</span>
        </div>
    {/if}
</div>