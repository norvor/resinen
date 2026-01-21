<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    import { fly, fade } from 'svelte/transition';
    import type { Community, User } from '$lib/types';

    export let community: Community;
    export let currentUser: User | null;

    // --- TYPES ---
    interface Team {
        id: string;
        name: string;
        logo_url?: string;
    }

    interface Match {
        id: string;
        title?: string;
        team_a: Team;
        team_b: Team;
        score_a: number;
        score_b: number;
        start_time: string;
        status: 'SCHEDULED' | 'LIVE' | 'COMPLETED';
        venue?: string;
    }

    interface Standing {
        rank: number;
        name: string;
        w: number;
        l: number;
        d: number;
        pts: number;
    }

    // --- STATE ---
    let matches: Match[] = [];
    let activeMatch: Match | null = null;
    let standings: Standing[] = [];
    let loading = true;
    let view: 'live' | 'schedule' | 'standings' = 'schedule'; // Default: Schedule

    // HYPE STATE (Visual Feedback Only)
    let hypeA = 50; 
    let hypeB = 50;
    let userCheerCount = 0;

    onMount(async () => {
        if (!community?.id) return;

        try {
            // 1. Fetch real matches
            const res = await api.getMatches(community.id);
            matches = Array.isArray(res) ? res : (res as any).items || [];
            
            // 2. Find Active Match (if any)
            activeMatch = matches.find((m) => m.status === 'LIVE') || null;
            
            // 3. Calculate Real Standings from Match History
            calculateStandings(matches);

        } catch (e) {
            console.error("Arena offline:", e);
        } finally {
            loading = false;
        }
    });

    function calculateStandings(matchList: Match[]) {
        const teamsMap = new Map<string, Standing>();

        // Helper to get or create team entry
        const getTeam = (name: string) => {
            if (!teamsMap.has(name)) {
                teamsMap.set(name, { rank: 0, name, w: 0, l: 0, d: 0, pts: 0 });
            }
            return teamsMap.get(name)!;
        };

        matchList.forEach(m => {
            if (m.status === 'COMPLETED') {
                const teamA = getTeam(m.team_a.name);
                const teamB = getTeam(m.team_b.name);

                if (m.score_a > m.score_b) {
                    teamA.w++; teamA.pts += 3;
                    teamB.l++;
                } else if (m.score_b > m.score_a) {
                    teamB.w++; teamB.pts += 3;
                    teamA.l++;
                } else {
                    teamA.d++; teamA.pts += 1;
                    teamB.d++; teamB.pts += 1;
                }
            }
        });

        // Convert to array and sort by points
        standings = Array.from(teamsMap.values())
            .sort((a, b) => b.pts - a.pts)
            .map((s, i) => ({ ...s, rank: i + 1 }));
    }

    async function handleCheer(team: 'A' | 'B') {
        if (!activeMatch) return;

        // Visual Feedback
        if (team === 'A') {
            hypeA = Math.min(hypeA + 2, 90);
            hypeB = Math.max(hypeB - 2, 10);
        } else {
            hypeB = Math.min(hypeB + 2, 90);
            hypeA = Math.max(hypeA - 2, 10);
        }
        userCheerCount++;
        
        // Send Prediction
        try {
            const teamId = team === 'A' ? activeMatch.team_a.id : activeMatch.team_b.id;
            await api.predictMatch(activeMatch.id, teamId);
        } catch (e) {
            console.error("Cheer failed to register", e);
        }
    }

    function getTeamColor(name: string) {
        if (!name) return 'bg-gray-500';
        const colors = ['bg-red-600', 'bg-blue-600', 'bg-green-600', 'bg-purple-600', 'bg-yellow-500'];
        return colors[name.length % colors.length];
    }
</script>

<div class="space-y-8 max-w-6xl mx-auto">

    <div class="flex flex-col md:flex-row justify-between items-end border-b-4 border-black pb-4 gap-4">
        <div>
            <div class="flex items-center gap-2 mb-1">
                 {#if activeMatch}
                    <span class="w-3 h-3 bg-red-600 rounded-full animate-pulse"></span>
                    <span class="text-[10px] font-black uppercase tracking-widest text-red-600">Live Broadcast</span>
                 {:else}
                    <span class="w-3 h-3 bg-gray-400 rounded-full"></span>
                    <span class="text-[10px] font-black uppercase tracking-widest text-gray-400">Offline</span>
                 {/if}
            </div>
            <h2 class="text-4xl md:text-5xl font-black uppercase tracking-tighter italic">
                Varsity<span class="text-transparent bg-clip-text bg-gradient-to-r from-red-600 to-orange-500">Arena</span>
            </h2>
        </div>

        <div class="bg-gray-100 p-1 rounded-full flex">
            <button on:click={() => view = 'schedule'} class="px-6 py-2 rounded-full text-xs font-black uppercase transition-all {view === 'schedule' ? 'bg-black text-white shadow-md' : 'text-gray-400 hover:text-black'}">
                Schedule
            </button>
            <button on:click={() => view = 'live'} class="px-6 py-2 rounded-full text-xs font-black uppercase transition-all {view === 'live' ? 'bg-black text-white shadow-md' : 'text-gray-400 hover:text-black'}">
                Live
            </button>
            <button on:click={() => view = 'standings'} class="px-6 py-2 rounded-full text-xs font-black uppercase transition-all {view === 'standings' ? 'bg-black text-white shadow-md' : 'text-gray-400 hover:text-black'}">
                League Table
            </button>
        </div>
    </div>

    {#if loading}
        <div class="h-96 flex items-center justify-center font-black uppercase text-gray-200 text-2xl animate-pulse">
            Calibrating Cameras...
        </div>
    {:else}

        {#if view === 'schedule'}
            <div class="grid gap-4" in:fade>
                {#each matches as m}
                    <div class="bg-white border border-gray-200 p-4 rounded-xl flex items-center justify-between hover:border-black transition-colors group">
                        <div class="flex items-center gap-4">
                            <div class="text-center w-16">
                                <div class="text-xs font-bold text-gray-400 uppercase">{new Date(m.start_time).toLocaleDateString(undefined, {weekday: 'short'})}</div>
                                <div class="text-lg font-black">{new Date(m.start_time).getDate()}</div>
                            </div>
                            <div class="h-8 w-[1px] bg-gray-200"></div>
                            <div>
                                <div class="text-xl font-black uppercase flex items-center gap-2">
                                    {m.team_a.name} <span class="text-gray-300 text-sm">vs</span> {m.team_b.name}
                                </div>
                                <div class="text-xs font-bold text-gray-500 uppercase">{m.venue || 'Main Stadium'}</div>
                            </div>
                        </div>
                        <div>
                            {#if m.status === 'COMPLETED'}
                                <span class="font-mono font-bold bg-gray-100 px-3 py-1 rounded">{m.score_a} - {m.score_b}</span>
                            {:else if m.status === 'LIVE'}
                                <button on:click={() => { activeMatch = m; view = 'live'; }} class="px-4 py-2 bg-red-600 text-white border border-red-600 text-[10px] font-black uppercase rounded hover:bg-red-700 transition-colors animate-pulse">
                                    Watch Live
                                </button>
                            {:else}
                                <button class="px-4 py-2 border border-black text-[10px] font-black uppercase rounded hover:bg-black hover:text-white transition-colors">
                                    Get Tickets
                                </button>
                            {/if}
                        </div>
                    </div>
                {/each}
                {#if matches.length === 0}
                    <div class="text-center py-20 border-2 border-dashed border-zinc-200 rounded-xl">
                        <span class="text-4xl block mb-2">📅</span>
                        <span class="text-gray-400 font-bold uppercase">Season Schedule Pending</span>
                    </div>
                {/if}
            </div>

        {:else if view === 'live'}
            {#if activeMatch}
                <div class="relative bg-black rounded-3xl overflow-hidden shadow-2xl border-4 border-zinc-800 group" in:fly={{ y: 20 }}>
                    
                    <div class="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] opacity-20"></div>
                    <div class="absolute inset-0 bg-gradient-to-br from-zinc-900 via-black to-zinc-900 opacity-90"></div>
                    
                    <div class="relative z-10 p-6 md:p-12 flex flex-col md:flex-row items-center justify-between gap-8 text-white">
                        
                        <div class="flex-1 text-center group/team">
                            <div class="w-24 h-24 mx-auto rounded-full {getTeamColor(activeMatch.team_a.name)} flex items-center justify-center text-4xl shadow-[0_0_30px_rgba(255,255,255,0.2)] mb-4 border-4 border-white/10 group-hover/team:scale-110 transition-transform">
                                {activeMatch.team_a.name[0]}
                            </div>
                            <h3 class="text-3xl font-black uppercase tracking-tight">{activeMatch.team_a.name}</h3>
                            <div class="text-6xl font-mono font-bold mt-2 text-shadow-glow">{activeMatch.score_a}</div>
                            
                            <button 
                                on:click={() => handleCheer('A')}
                                class="mt-6 px-6 py-2 bg-zinc-800 hover:bg-white hover:text-black border border-zinc-600 rounded-full text-xs font-black uppercase transition-all active:scale-95 flex items-center gap-2 mx-auto"
                            >
                                <span>🔥</span> Hype Team
                            </button>
                        </div>

                        <div class="shrink-0 text-center flex flex-col items-center">
                            <div class="bg-red-600 text-white px-3 py-1 rounded text-[10px] font-black uppercase animate-pulse mb-4">
                                LIVE
                            </div>
                            <span class="text-4xl font-black italic text-zinc-700">VS</span>
                        </div>

                        <div class="flex-1 text-center group/team">
                            <div class="w-24 h-24 mx-auto rounded-full {getTeamColor(activeMatch.team_b.name)} flex items-center justify-center text-4xl shadow-[0_0_30px_rgba(255,255,255,0.2)] mb-4 border-4 border-white/10 group-hover/team:scale-110 transition-transform">
                                {activeMatch.team_b.name[0]}
                            </div>
                            <h3 class="text-3xl font-black uppercase tracking-tight">{activeMatch.team_b.name}</h3>
                            <div class="text-6xl font-mono font-bold mt-2 text-shadow-glow">{activeMatch.score_b}</div>

                            <button 
                                on:click={() => handleCheer('B')}
                                class="mt-6 px-6 py-2 bg-zinc-800 hover:bg-white hover:text-black border border-zinc-600 rounded-full text-xs font-black uppercase transition-all active:scale-95 flex items-center gap-2 mx-auto"
                            >
                                <span>🔥</span> Hype Team
                            </button>
                        </div>

                    </div>

                    <div class="h-4 w-full bg-zinc-800 relative mt-4 border-t border-zinc-700">
                        <div class="absolute left-1/2 top-0 bottom-0 w-[2px] bg-white z-20"></div>
                        <div class="absolute left-0 top-0 bottom-0 bg-gradient-to-r from-transparent to-white/20 transition-all duration-300 z-10" style="width: {hypeA}%"></div>
                        <div class="absolute right-0 top-0 bottom-0 bg-gradient-to-l from-transparent to-white/20 transition-all duration-300 z-10" style="width: {hypeB}%"></div>
                    </div>
                </div>

                <div class="mt-8 bg-zinc-100 p-6 rounded-xl border-2 border-dashed border-zinc-300 text-center">
                    <div class="text-xs font-bold text-gray-400 uppercase mb-2">Live Feed</div>
                    {#if userCheerCount > 0}
                        <div class="text-sm font-bold text-black">You have hyped your team {userCheerCount} times!</div>
                    {:else}
                        <div class="text-sm font-bold text-gray-500">Connecting to commentary stream...</div>
                    {/if}
                 </div>

            {:else}
                <div class="p-20 text-center border-4 border-black bg-white rounded-3xl shadow-[10px_10px_0px_black]">
                    <span class="text-6xl">💤</span>
                    <h3 class="text-2xl font-black uppercase mt-4">Stadium Empty</h3>
                    <p class="text-gray-500 font-bold">No matches are currently broadcasting live.</p>
                </div>
            {/if}

        {:else if view === 'standings'}
            <div class="bg-white border-2 border-black rounded-xl overflow-hidden shadow-lg" in:fade>
                {#if standings.length === 0}
                    <div class="p-10 text-center text-gray-400 font-bold">
                        Standings will be calculated after the first match is completed.
                    </div>
                {:else}
                    <table class="w-full text-left">
                        <thead class="bg-black text-white uppercase text-[10px] font-black tracking-widest">
                            <tr>
                                <th class="p-4">Rank</th>
                                <th class="p-4">Team</th>
                                <th class="p-4 text-center">W</th>
                                <th class="p-4 text-center">L</th>
                                <th class="p-4 text-center">D</th>
                                <th class="p-4 text-right">Points</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-100 text-sm font-bold">
                            {#each standings as team}
                                <tr class="hover:bg-yellow-50 transition-colors">
                                    <td class="p-4 text-gray-400">#{team.rank}</td>
                                    <td class="p-4 uppercase text-black">{team.name}</td>
                                    <td class="p-4 text-center">{team.w}</td>
                                    <td class="p-4 text-center text-gray-400">{team.l}</td>
                                    <td class="p-4 text-center text-gray-400">{team.d}</td>
                                    <td class="p-4 text-right font-black">{team.pts}</td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                {/if}
            </div>
        {/if}

    {/if}
</div>

<style>
    .text-shadow-glow {
        text-shadow: 0 0 20px rgba(255,255,255,0.5);
    }
</style>