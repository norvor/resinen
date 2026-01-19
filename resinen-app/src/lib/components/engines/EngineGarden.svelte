<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    export let community: any;

    let habits: any[] = [];
    let loading = true;

    async function loadGarden() {
        try {
            habits = await api.getGarden(community.id);
        } catch (e) {
            console.error(e);
        } finally {
            loading = false;
        }
    }

    onMount(loadGarden);

    async function waterPlant(id: string) {
        try {
            const res = await api.checkInHabit(id);
            if (res.status === 'success') {
                // Optimistic update
                habits = habits.map(h => h.id === id ? {
                    ...h, 
                    is_completed_today: true,
                    streak_current: res.streak
                } : h);
            }
        } catch (e) {
            alert("Could not water plant.");
        }
    }
</script>

{#if loading}
    <div class="p-8 text-center animate-pulse text-skin-muted font-bold uppercase">Loading Garden...</div>
{:else}
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        
        <button class="skin-card border-2 border-dashed border-skin-border flex flex-col items-center justify-center p-6 opacity-50 hover:opacity-100 hover:border-skin-accent hover:text-skin-accent transition-all group">
            <div class="text-4xl mb-2 group-hover:scale-110 transition-transform">➕</div>
            <div class="font-bold text-xs uppercase">Plant Seed</div>
        </button>

        {#each habits as h}
            <div class="skin-card relative overflow-hidden group transition-all duration-500
                {h.is_completed_today 
                    ? 'border-green-500/50 bg-green-500/5 shadow-[0_0_20px_rgba(34,197,94,0.1)]' 
                    : 'hover:border-skin-text'}">
                
                <div class="absolute bottom-0 left-0 h-1 bg-skin-border w-full">
                    <div class="h-full bg-green-500" style="width: {Math.min(h.streak_current * 5, 100)}%"></div>
                </div>

                <div class="p-6 flex flex-col items-center text-center z-10 relative">
                    <div class="text-5xl mb-4 transition-transform duration-500 
                        {h.is_completed_today ? 'scale-110 drop-shadow-lg' : 'grayscale opacity-70 scale-90'}">
                        {h.icon}
                    </div>

                    <h3 class="font-black uppercase text-sm mb-1">{h.title}</h3>
                    
                    <div class="text-[10px] font-bold uppercase tracking-widest mb-4
                        {h.is_completed_today ? 'text-green-500' : 'text-skin-muted'}">
                        🔥 {h.streak_current} Day Streak
                    </div>

                    {#if !h.is_completed_today}
                        <button on:click={() => waterPlant(h.id)} class="w-full py-2 bg-skin-surface border border-skin-border rounded text-xs font-bold uppercase hover:bg-green-500 hover:text-white hover:border-green-500 transition-all shadow-sm">
                            Check In
                        </button>
                    {:else}
                        <div class="w-full py-2 bg-green-500/20 text-green-600 border border-green-500/20 rounded text-xs font-bold uppercase cursor-default">
                            ✓ Done Today
                        </div>
                    {/if}
                </div>
                
                </div>
        {/each}
        
    </div>

    {#if habits.length === 0}
        <div class="mt-8 p-8 text-center border border-skin-border/50 rounded-xl bg-skin-surface/20">
            <div class="text-sm text-skin-muted">This garden is empty. Start planting habits to track your growth.</div>
        </div>
    {/if}
{/if}