<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    import { fly, scale, fade } from 'svelte/transition';
    import { cubicOut } from 'svelte/easing';
    import type { Community, User } from '$lib/types';

    export let community: Community;
    export let currentUser: User | null;

    interface Habit {
        id: string;
        title: string;
        streak: number;
        completed_today: boolean;
        color?: string;
        history?: string[]; // Array of dates
    }

    let habits: Habit[] = [];
    let loading = true;
    let selectedHabit: Habit | null = null; // For the detail view
    let wateringId: string | null = null; // For animation state
    let error: string | null = null;

    onMount(async () => {
        if (!community?.id) return;
        try {
            // Fetch real garden data
            const res = await api.getGarden(community.id);
            habits = Array.isArray(res) ? res : (res as any).items || [];
        } catch (e) {
            console.error("Garden Withered:", e);
            error = "Could not open the gate.";
        } finally {
            loading = false;
        }
    });

    async function waterPlant(habit: Habit) {
        if (habit.completed_today) return;
        
        wateringId = habit.id;
        
        // Optimistic UI Update first for responsiveness
        const originalStreak = habit.streak;
        habit.completed_today = true;
        habit.streak += 1;
        habits = habits; // Trigger reactivity

        try {
            await api.checkInHabit(habit.id);
        } catch (e) {
            console.error(e);
            // Revert on failure
            habit.completed_today = false;
            habit.streak = originalStreak;
            habits = habits;
            alert("Failed to water plant.");
        }

        // Reset animation state
        setTimeout(() => {
            wateringId = null;
        }, 1500); 
    }

    // --- LOGIC: PLANT EVOLUTION ---
    function getPlantEmoji(streak: number) {
        if (streak === 0) return '🌰'; // Seed
        if (streak < 3) return '🌱';  // Sprout
        if (streak < 10) return '🌿'; // Herb
        if (streak < 30) return '🪴'; // Potted
        if (streak < 60) return '🎍'; // Bamboo
        if (streak < 100) return '🌳'; // Tree
        return '🌲'; // Ancient
    }

    function getGrid(streak: number) {
        // Generates a visual heatmap. 
        // In a real app, use habit.history dates to map this accurately.
        // Here we simulate recent activity density based on streak.
        const density = Math.min(streak / 30, 1);
        return Array(30).fill(0).map((_, i) => Math.random() < density);
    }
</script>

<div class="max-w-6xl mx-auto space-y-8">

    <div class="relative bg-gradient-to-b from-sky-300 to-sky-100 h-48 rounded-t-3xl border-x-4 border-t-4 border-black overflow-hidden flex items-end p-8">
        <div class="absolute top-4 right-8 w-16 h-16 bg-yellow-400 rounded-full border-4 border-black shadow-[4px_4px_0px_rgba(0,0,0,0.2)] animate-pulse"></div>
        
        <div class="absolute top-10 left-20 text-6xl opacity-80 animate-float-slow">☁️</div>
        <div class="absolute top-20 right-40 text-4xl opacity-60 animate-float-slower">☁️</div>

        <div class="relative z-10">
            <h2 class="text-5xl font-black uppercase tracking-tighter text-sky-900 leading-none">
                The <span class="text-green-700">Garden</span>
            </h2>
            <p class="font-mono font-bold text-sky-700 mt-2">CONSISTENCY IS THE WATER.</p>
        </div>
    </div>

    {#if loading}
         <div class="p-12 text-center font-bold text-gray-400 animate-pulse">GERMINATING SEEDS...</div>
    {:else if error}
         <div class="p-12 text-center font-bold text-red-400 uppercase">{error}</div>
    {:else if habits.length === 0}
         <div class="p-20 text-center border-4 border-dashed border-stone-300 rounded-3xl text-stone-400">
            <span class="text-6xl block mb-4">🏜️</span>
            <span class="font-black uppercase tracking-widest">No Habits Planted Yet</span>
         </div>
    {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 px-4">
            
            {#each habits as habit, i (habit.id)}
                <div 
                    class="bg-[#f5f5f0] border-4 border-stone-300 rounded-3xl p-2 relative group hover:-translate-y-2 hover:border-stone-400 hover:shadow-[0px_10px_0px_#d6d3d1] transition-all duration-300 cursor-pointer"
                    in:fly={{ y: 50, delay: i * 100 }}
                    on:click={() => selectedHabit = habit}
                >
                    <div class="absolute bottom-4 left-2 right-2 h-4 bg-stone-200 rounded-full z-0"></div>

                    <div class="relative z-10 flex flex-col items-center pt-8 pb-4">
                        
                        <div class="text-8xl filter drop-shadow-xl transition-transform duration-500 {wateringId === habit.id ? 'animate-shake' : 'group-hover:scale-110'}">
                            {getPlantEmoji(habit.streak)}
                        </div>

                        {#if wateringId === habit.id}
                            <div class="absolute inset-0 flex justify-center pt-10 pointer-events-none z-20">
                                <span class="text-4xl absolute animate-drop" style="left: 45%; animation-delay: 0.1s">💧</span>
                                <span class="text-4xl absolute animate-drop" style="left: 55%; animation-delay: 0.3s">💧</span>
                                <span class="text-4xl absolute animate-drop" style="left: 50%; animation-delay: 0.5s">💧</span>
                            </div>
                        {/if}

                        <div class="mt-4 w-full bg-white border-2 border-stone-200 rounded-xl p-4 text-center shadow-sm relative overflow-hidden">
                            <div class="absolute bottom-0 left-0 h-1 bg-green-500 transition-all duration-1000" style="width: {Math.min(habit.streak, 100)}%"></div>
                            
                            <h3 class="font-black uppercase text-stone-800 text-lg leading-none">{habit.title}</h3>
                            
                            <div class="flex justify-center items-center gap-2 mt-2">
                                <span class="text-xs font-bold text-stone-400 uppercase">Streak</span>
                                <span class="text-xl font-black {habit.completed_today ? 'text-green-600' : 'text-stone-600'}">
                                    {habit.streak}
                                </span>
                            </div>

                            <button 
                                on:click|stopPropagation={() => waterPlant(habit)}
                                disabled={habit.completed_today || !!wateringId}
                                class="mt-4 w-full py-2 rounded-lg font-black uppercase text-xs transition-all active:scale-95
                                {habit.completed_today 
                                    ? 'bg-green-100 text-green-700 border border-green-200' 
                                    : 'bg-blue-500 text-white shadow-[0_4px_0_#1e40af] hover:bg-blue-400 hover:shadow-[0_4px_0_#3b82f6]'}"
                            >
                                {habit.completed_today ? 'Thriving' : '💧 Water Now'}
                            </button>
                        </div>

                    </div>
                </div>
            {/each}

            <div class="border-4 border-dashed border-stone-300 rounded-3xl flex flex-col items-center justify-center p-8 text-stone-300 hover:text-stone-400 hover:border-stone-400 transition-colors cursor-pointer group">
                <span class="text-6xl group-hover:scale-110 transition-transform">🌱</span>
                <span class="font-black uppercase mt-4">Plant Seed</span>
            </div>

        </div>
    {/if}

    {#if selectedHabit}
        <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-stone-900/80 backdrop-blur-sm" transition:fade>
            <div 
                class="bg-[#fdfbf7] w-full max-w-lg rounded-2xl border-4 border-stone-800 shadow-2xl overflow-hidden relative"
                in:scale={{ start: 0.9, duration: 200, easing: cubicOut }}
            >
                <button on:click={() => selectedHabit = null} class="absolute top-4 right-4 w-8 h-8 bg-stone-200 rounded-full flex items-center justify-center font-bold text-stone-500 hover:bg-red-500 hover:text-white transition-colors z-20">✕</button>

                <div class="p-8">
                    <div class="flex items-center gap-4 mb-6">
                        <div class="text-6xl">{getPlantEmoji(selectedHabit.streak)}</div>
                        <div>
                            <div class="text-xs font-black uppercase text-stone-400">Specimen #{selectedHabit.id}</div>
                            <h2 class="text-3xl font-black uppercase text-stone-800">{selectedHabit.title}</h2>
                        </div>
                    </div>

                    <div class="bg-white border-2 border-stone-200 p-4 rounded-xl mb-6">
                        <h4 class="text-xs font-bold uppercase text-stone-400 mb-2">Growth Density</h4>
                        <div class="flex flex-wrap gap-1">
                            {#each getGrid(selectedHabit.streak) as active}
                                <div class="w-3 h-3 rounded-sm {active ? 'bg-green-500' : 'bg-stone-100'}"></div>
                            {/each}
                        </div>
                    </div>

                    <div class="flex justify-between items-center text-sm font-bold text-stone-500 border-t-2 border-dashed border-stone-200 pt-4">
                        <span>Status</span>
                        <span class="{selectedHabit.completed_today ? 'text-green-600' : 'text-orange-500'}">
                            {selectedHabit.completed_today ? 'Watered Today' : 'Needs Water'}
                        </span>
                    </div>
                </div>

                <div class="bg-stone-100 p-4 flex gap-4">
                    <button class="flex-1 py-3 bg-white border-2 border-stone-300 rounded-xl font-black uppercase text-xs hover:border-red-400 hover:text-red-500">
                        Prune (Edit)
                    </button>
                    <button 
                        on:click={() => { if(selectedHabit) waterPlant(selectedHabit); selectedHabit = null; }}
                        disabled={selectedHabit.completed_today}
                        class="flex-[2] py-3 bg-blue-500 text-white rounded-xl font-black uppercase text-xs shadow-[0_4px_0_#1e40af] active:translate-y-1 active:shadow-none disabled:bg-stone-300 disabled:shadow-none"
                    >
                        {selectedHabit.completed_today ? 'Already Watered' : 'Water Plant'}
                    </button>
                </div>
            </div>
        </div>
    {/if}

</div>

<style>
    @keyframes drop {
        0% { transform: translateY(-20px) scale(0); opacity: 0; }
        50% { opacity: 1; }
        100% { transform: translateY(40px) scale(1); opacity: 0; }
    }
    .animate-drop {
        animation: drop 1s ease-in-out forwards;
    }
    
    @keyframes shake {
        0%, 100% { transform: rotate(0deg); }
        25% { transform: rotate(-5deg); }
        75% { transform: rotate(5deg); }
    }
    .animate-shake {
        animation: shake 0.5s ease-in-out infinite;
    }

    @keyframes float-slow {
        0%, 100% { transform: translateX(0); }
        50% { transform: translateX(20px); }
    }
    .animate-float-slow { animation: float-slow 10s ease-in-out infinite; }
    
    @keyframes float-slower {
        0%, 100% { transform: translateX(0); }
        50% { transform: translateX(-30px); }
    }
    .animate-float-slower { animation: float-slower 15s ease-in-out infinite; }
</style>