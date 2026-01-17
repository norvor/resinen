<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';

    let status = 'CONNECTING...';
    let isOnline = false;
    let stats = {
        journeys: 0,
        stops: 0
    };

    onMount(async () => {
        try {
            // 1. Check Connection
            const res = await api.healthCheck();
            status = res.status ? res.status.toUpperCase() : 'ACTIVE';
            isOnline = true;

            // 2. Load Stats
            const journeys = await api.getJourneys();
            stats.journeys = journeys.length;
            stats.stops = journeys.reduce((acc, j) => acc + (j.stops?.length || 0), 0);
        } catch (e) {
            status = 'SYSTEM OFFLINE';
            isOnline = false;
        }
    });
</script>

<div class="p-8 max-w-6xl mx-auto space-y-8 animate-in fade-in duration-700">
    <header class="flex justify-between items-end border-b border-slate-800 pb-8">
        <div>
            <h2 class="text-4xl font-black text-white tracking-tighter">COMMAND DECK</h2>
            <p class="text-slate-400 mt-1 font-mono text-sm">RESINEN // LIFE_OS_ADMIN</p>
        </div>
        <div class="text-right hidden md:block">
            <span class="text-[10px] font-bold text-slate-500 uppercase tracking-[0.2em]">System Status</span>
            <div class="flex items-center justify-end gap-2 mt-1">
                <div class={`w-2 h-2 rounded-full ${isOnline ? 'bg-orange-500 animate-pulse' : 'bg-red-500'}`}></div>
                <p class="text-white font-mono text-sm">{status}</p>
            </div>
        </div>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="p-6 rounded-2xl border border-slate-800 bg-slate-950/50">
            <h3 class="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-4">Core Signal</h3>
            <div class="flex items-center gap-3">
                 <span class="text-3xl font-black italic text-white tracking-tight">
                    {isOnline ? 'ONLINE' : 'LOST'}
                 </span>
                 {#if isOnline}
                    <span class="px-2 py-0.5 rounded bg-orange-500/20 text-orange-500 text-[10px] font-bold">STABLE</span>
                 {/if}
            </div>
        </div>

        <div class="p-6 rounded-2xl border border-slate-800 bg-slate-950/50">
            <h3 class="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-4">Active Journeys</h3>
            <div class="flex items-baseline gap-2">
                <span class="text-4xl font-black text-orange-500">{stats.journeys}</span>
                <span class="text-slate-500 font-mono text-xs">PATHS</span>
            </div>
        </div>

        <div class="p-6 rounded-2xl border border-slate-800 bg-slate-950/50">
            <h3 class="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-4">World Data</h3>
            <div class="flex items-baseline gap-2">
                <span class="text-4xl font-black text-white">{stats.stops}</span>
                <span class="text-slate-500 font-mono text-xs">STOPS</span>
            </div>
        </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4">
        <a href="/journeys/new" class="group relative overflow-hidden p-10 rounded-3xl bg-orange-600 text-white transition-all hover:scale-[1.01] hover:shadow-2xl hover:shadow-orange-900/20">
            <div class="relative z-10">
                <h3 class="text-3xl font-black leading-none mb-3">BUILD NEW JOURNEY</h3>
                <p class="text-orange-100 font-medium max-w-xs">Create a new progression path (Farming, Travel, Repair).</p>
            </div>
            <div class="absolute -right-8 -bottom-8 text-9xl opacity-20 rotate-12 group-hover:rotate-6 transition-transform">
                🌱
            </div>
        </a>

        <a href="/journeys" class="group relative p-10 rounded-3xl bg-slate-800 text-white transition-all hover:bg-slate-700">
            <h3 class="text-3xl font-black leading-none mb-3">MANAGE CONTENT</h3>
            <p class="text-slate-400 font-medium">Edit existing stops, update images, or fix typos.</p>
        </a>
    </div>
</div>