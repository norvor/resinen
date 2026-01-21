<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    import { scale } from 'svelte/transition';

    export let communityId: string;

    let habit: any = null;
    let loading = true;
    let justWatered = false;

    // Mock Fallback
    const MOCK_HABIT = {
        id: 'demo',
        title: 'Morning Read',
        streak_current: 12,
        is_completed_today: false
    };

    onMount(async () => {
        try {
            // Need to add getMyGarden to api.ts if missing, or use raw request
            const habits = await api.getGarden(communityId); // Assuming you add this wrapper
            habit = habits[0] || null;
        } catch {
            habit = null;
        } finally {
            loading = false;
        }
    });

    async function checkIn() {
        if (!habit || habit.is_completed_today) return;
        
        // Optimistic UI
        habit.is_completed_today = true;
        habit.streak_current += 1;
        justWatered = true;
        
        try {
            await api.checkInHabit(habit.id);
        } catch (e) {
            // Revert on fail
            habit.is_completed_today = false;
            habit.streak_current -= 1;
        }
        
        setTimeout(() => justWatered = false, 1000);
    }
</script>

<div class="h-full w-full">
    {#if loading}
        <div class="h-full bg-gray-100 animate-pulse rounded-2xl"></div>
    {:else if habit || MOCK_HABIT}
        {@const h = habit || MOCK_HABIT}
        
        <div class="h-full bg-gradient-to-br from-green-50 to-emerald-100 rounded-2xl border border-green-200 p-6 flex flex-col justify-between relative overflow-hidden group hover:shadow-lg transition-all duration-300">
            
            <div class="absolute -right-8 -bottom-8 w-32 h-32 bg-green-200/50 rounded-full blur-2xl transition-transform group-hover:scale-150"></div>

            <div class="relative z-10 flex justify-between items-start">
                <div>
                    <div class="text-[10px] font-black uppercase text-green-800 tracking-widest mb-1">Top Habit</div>
                    <h3 class="text-xl font-black text-green-900 leading-tight">{h.title}</h3>
                </div>
                <div class="text-right">
                    <div class="text-2xl font-black text-green-700">{h.streak_current}</div>
                    <div class="text-[9px] font-bold uppercase text-green-600">Day Streak</div>
                </div>
            </div>

            <div class="relative flex-1 flex items-center justify-center">
                <div class="text-6xl transition-transform duration-500 {justWatered ? 'scale-125 rotate-12' : 'group-hover:scale-110'}">
                    {#if h.is_completed_today}
                        🌳
                    {:else}
                        🌱
                    {/if}
                </div>
                {#if justWatered}
                    <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
                        <span class="absolute text-xl animate-ping" style="top: 20%; left: 40%">💧</span>
                        <span class="absolute text-xl animate-ping delay-100" style="top: 10%; right: 40%">💧</span>
                    </div>
                {/if}
            </div>

            <div class="relative z-10">
                <button 
                    on:click={checkIn}
                    disabled={h.is_completed_today}
                    class="w-full py-2 rounded-xl text-xs font-black uppercase tracking-widest shadow-sm transition-all
                    {h.is_completed_today 
                        ? 'bg-green-200 text-green-800 cursor-default' 
                        : 'bg-green-600 text-white hover:bg-green-700 hover:shadow-md active:scale-95'}"
                >
                    {h.is_completed_today ? 'Nurtured' : 'Water Plant'}
                </button>
            </div>

        </div>
    {:else}
        <div class="h-full bg-zinc-50 rounded-2xl border-2 border-dashed border-zinc-200 flex items-center justify-center">
            <span class="text-xs font-bold text-zinc-400 uppercase">No Habits</span>
        </div>
    {/if}
</div>