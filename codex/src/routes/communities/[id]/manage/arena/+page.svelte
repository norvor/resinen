<script lang="ts">
    import { onMount } from 'svelte';
    import { api, type Match } from '$lib/api';
    import { fade, scale } from 'svelte/transition';

    export let data;
    $: community = data.community;

    let matches: Match[] = [];
    let loading = true;
    let showCreate = false;
    let activeMatch: Match | null = null; // For the Score/Status Editor

    // Form Data
    let newMatch = {
        title: '',
        team_a_name: '',
        team_b_name: '',
        start_time: '',
        venue: ''
    };

    onMount(async () => {
        await loadMatches();
    });

    async function loadMatches() {
        loading = true;
        try {
            const res = await api.getMatches(community.id);
            matches = Array.isArray(res) ? res : [];
        } catch (e) {
            console.error(e);
        } finally {
            loading = false;
        }
    }

    async function handleCreate() {
        try {
            await api.createMatch(community.id, newMatch);
            showCreate = false;
            await loadMatches(); // Refresh list
            // Reset form
            newMatch = { title: '', team_a_name: '', team_b_name: '', start_time: '', venue: '' };
        } catch (e) {
            alert('Failed to create match');
        }
    }

    async function updateScore(match: Match, team: 'a' | 'b', delta: number) {
        const newScoreA = team === 'a' ? match.score_a + delta : match.score_a;
        const newScoreB = team === 'b' ? match.score_b + delta : match.score_b;
        
        // Optimistic UI
        match.score_a = newScoreA;
        match.score_b = newScoreB;
        matches = matches;

        try {
            await api.updateMatchScore(match.id, newScoreA, newScoreB);
        } catch (e) {
            console.error("Score update failed");
        }
    }

    async function changeStatus(match: Match, status: string) {
        match.status = status as any;
        matches = matches;
        await api.setMatchStatus(match.id, status);
    }
</script>

<div class="space-y-8 animate-fade-in-up">
    
    <div class="flex items-end justify-between border-b-4 border-black pb-6">
        <div>
            <div class="text-xs font-black uppercase text-red-600 tracking-widest mb-1 flex items-center gap-2">
                <span>🏆</span> Arena Engine
            </div>
            <h1 class="text-4xl font-black uppercase tracking-tighter">
                Match Control
            </h1>
        </div>
        <button 
            on:click={() => showCreate = true}
            class="px-6 py-3 bg-red-600 text-white font-black rounded uppercase text-xs shadow-[4px_4px_0px_black] hover:-translate-y-1 hover:shadow-[6px_6px_0px_black] transition-all"
        >
            + Schedule Match
        </button>
    </div>

    {#if loading}
        <div class="p-12 text-center text-gray-400 font-bold animate-pulse">LOADING FIXTURES...</div>
    {:else if matches.length === 0}
        <div class="p-20 text-center border-4 border-dashed border-gray-200 rounded-xl text-gray-400">
            <span class="text-4xl block mb-2">🏟️</span>
            <span class="font-bold uppercase tracking-widest">No Matches Scheduled</span>
        </div>
    {:else}
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {#each matches as match}
                <div class="bg-white border-2 border-gray-200 rounded-xl p-6 relative group hover:border-black transition-colors">
                    
                    <div class="absolute top-4 right-4">
                        {#if match.status === 'LIVE'}
                            <span class="px-2 py-1 bg-red-600 text-white text-[10px] font-black uppercase rounded animate-pulse">
                                Live
                            </span>
                        {:else if match.status === 'COMPLETED'}
                            <span class="px-2 py-1 bg-gray-100 text-gray-500 text-[10px] font-black uppercase rounded">
                                Final
                            </span>
                        {:else}
                            <span class="px-2 py-1 bg-blue-100 text-blue-600 text-[10px] font-black uppercase rounded">
                                Upcoming
                            </span>
                        {/if}
                    </div>

                    <div class="text-xs font-bold text-gray-400 mb-4 uppercase">
                        {new Date(match.start_time).toLocaleString()} • {match.venue || 'Main Stadium'}
                    </div>

                    <div class="flex items-center justify-between mb-6">
                        <div class="text-center w-1/3">
                            <h3 class="text-xl font-black uppercase leading-none mb-2">{match.team_a_name}</h3>
                            <div class="text-4xl font-mono font-bold text-gray-900">{match.score_a}</div>
                        </div>
                        <div class="text-2xl font-black text-gray-300">VS</div>
                        <div class="text-center w-1/3">
                            <h3 class="text-xl font-black uppercase leading-none mb-2">{match.team_b_name}</h3>
                            <div class="text-4xl font-mono font-bold text-gray-900">{match.score_b}</div>
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-2 pt-4 border-t border-gray-100">
                        <button 
                            on:click={() => activeMatch = match}
                            class="bg-black text-white py-2 text-xs font-bold uppercase rounded hover:bg-gray-800"
                        >
                            Open Console
                        </button>
                        
                        {#if match.status === 'SCHEDULED'}
                             <button 
                                on:click={() => changeStatus(match, 'LIVE')}
                                class="border-2 border-red-600 text-red-600 py-2 text-xs font-bold uppercase rounded hover:bg-red-50"
                            >
                                Go Live
                            </button>
                        {:else if match.status === 'LIVE'}
                            <button 
                                on:click={() => changeStatus(match, 'COMPLETED')}
                                class="border-2 border-gray-200 text-gray-500 py-2 text-xs font-bold uppercase rounded hover:bg-gray-50"
                            >
                                End Match
                            </button>
                        {:else}
                            <button disabled class="bg-gray-100 text-gray-400 py-2 text-xs font-bold uppercase rounded cursor-not-allowed">
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
                <h2 class="font-black text-2xl uppercase mb-6">Schedule Match</h2>
                <div class="space-y-4">
                    <input bind:value={newMatch.team_a_name} placeholder="Team A Name (e.g. Tigers)" class="w-full border-2 border-gray-200 p-3 rounded font-bold uppercase focus:border-black outline-none" />
                    <input bind:value={newMatch.team_b_name} placeholder="Team B Name (e.g. Dragons)" class="w-full border-2 border-gray-200 p-3 rounded font-bold uppercase focus:border-black outline-none" />
                    <input bind:value={newMatch.start_time} type="datetime-local" class="w-full border-2 border-gray-200 p-3 rounded font-bold focus:border-black outline-none" />
                    <input bind:value={newMatch.venue} placeholder="Venue / Location" class="w-full border-2 border-gray-200 p-3 rounded font-bold focus:border-black outline-none" />
                </div>
                <div class="flex gap-2 mt-8">
                    <button on:click={() => showCreate = false} class="flex-1 py-3 text-gray-500 font-bold hover:bg-gray-100 rounded">Cancel</button>
                    <button on:click={handleCreate} class="flex-1 py-3 bg-black text-white font-bold uppercase rounded">Create Fixture</button>
                </div>
            </div>
        </div>
    {/if}

    {#if activeMatch}
        <div class="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-4 backdrop-blur-md" transition:fade>
            <div class="bg-zinc-900 w-full max-w-2xl rounded-xl p-8 shadow-2xl border border-zinc-700 text-white" in:scale>
                
                <div class="flex justify-between items-center mb-8 border-b border-zinc-700 pb-4">
                    <h2 class="font-black text-xl uppercase tracking-widest text-red-500 flex items-center gap-2">
                        <span class="w-3 h-3 bg-red-500 rounded-full animate-pulse"></span> Live Console
                    </h2>
                    <button on:click={() => activeMatch = null} class="text-zinc-500 hover:text-white">✕ Close</button>
                </div>

                <div class="grid grid-cols-3 gap-8 items-center text-center">
                    <div class="space-y-4">
                        <h3 class="text-2xl font-black uppercase">{activeMatch.team_a_name}</h3>
                        <div class="text-6xl font-mono font-bold">{activeMatch.score_a}</div>
                        <div class="flex gap-2 justify-center">
                            <button on:click={() => updateScore(activeMatch, 'a', -1)} class="w-10 h-10 rounded bg-zinc-800 hover:bg-zinc-700 font-bold">-</button>
                            <button on:click={() => updateScore(activeMatch, 'a', 1)} class="w-10 h-10 rounded bg-green-600 hover:bg-green-500 font-bold text-white shadow-lg shadow-green-900/50">+</button>
                        </div>
                    </div>

                    <div class="text-zinc-500 font-bold text-sm uppercase">
                        <div>VS</div>
                        <div class="mt-4 px-2 py-1 bg-zinc-800 rounded text-xs">{activeMatch.status}</div>
                    </div>

                    <div class="space-y-4">
                        <h3 class="text-2xl font-black uppercase">{activeMatch.team_b_name}</h3>
                        <div class="text-6xl font-mono font-bold">{activeMatch.score_b}</div>
                        <div class="flex gap-2 justify-center">
                            <button on:click={() => updateScore(activeMatch, 'b', -1)} class="w-10 h-10 rounded bg-zinc-800 hover:bg-zinc-700 font-bold">-</button>
                            <button on:click={() => updateScore(activeMatch, 'b', 1)} class="w-10 h-10 rounded bg-green-600 hover:bg-green-500 font-bold text-white shadow-lg shadow-green-900/50">+</button>
                        </div>
                    </div>
                </div>

                <div class="mt-12 pt-6 border-t border-zinc-700 flex justify-between items-center">
                    <div class="text-xs text-zinc-500 font-mono">ID: {activeMatch.id}</div>
                    <div class="flex gap-2">
                        {#if activeMatch.status === 'SCHEDULED'}
                             <button on:click={() => changeStatus(activeMatch, 'LIVE')} class="px-4 py-2 bg-red-600 text-white font-bold uppercase rounded hover:bg-red-500">Start Match</button>
                        {:else if activeMatch.status === 'LIVE'}
                             <button on:click={() => changeStatus(activeMatch, 'COMPLETED')} class="px-4 py-2 bg-zinc-700 text-white font-bold uppercase rounded hover:bg-zinc-600">Finish Game</button>
                        {/if}
                    </div>
                </div>

            </div>
        </div>
    {/if}

</div>