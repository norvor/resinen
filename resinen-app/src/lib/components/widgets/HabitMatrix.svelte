<script lang="ts">
    import { onMount } from 'svelte';
    import * as api from '$lib/api'; // <--- 1. Import API

    type Habit = { name: string; grid: boolean[]; };

    let habits = $state<Habit[]>([
        { name: "WORKOUT", grid: Array(35).fill(false) },
        { name: "READING", grid: Array(35).fill(false) },
        { name: "CODING", grid: Array(35).fill(false) },
        { name: "MEDITATE", grid: Array(35).fill(false) }
    ]);

    let currentIndex = $state(0);
    let currentHabit = $derived(habits[currentIndex]);
    const COLORS = ["#f472b6", "#2dd4bf", "#fbbf24", "#a78bfa"];
    let activeColor = $derived(COLORS[currentIndex]);
    let totalCount = $derived(currentHabit.grid.filter(Boolean).length);

    function toggle(i: number) {
        habits[currentIndex].grid[i] = !habits[currentIndex].grid[i];
        save();
    }

    function nextHabit() { currentIndex = (currentIndex + 1) % habits.length; }
    function prevHabit() { currentIndex = (currentIndex - 1 + habits.length) % habits.length; }

    // --- 2. UPDATED SAVE FUNCTION ---
    function save() {
        // Now saves to Cloud + LocalStorage
        api.saveData('resinen_habits_v2', habits); 
    }

    onMount(() => {
        // We still load from LocalStorage for instant render
        // (The +page.svelte sync keeps this fresh)
        const saved = localStorage.getItem('resinen_habits_v2');
        if (saved) {
            try { habits = JSON.parse(saved); } catch (e) {}
        }
    });
</script>

<div class="card habit-widget" style="--theme: {activeColor}">
    <div class="head">
        <button class="nav-btn" onclick={prevHabit}>‹</button>
        <div class="title-area">
            <input type="text" class="habit-name" bind:value={habits[currentIndex].name} oninput={save} maxlength="12"/>
            <div class="counter">{totalCount} SESSIONS</div>
        </div>
        <button class="nav-btn" onclick={nextHabit}>›</button>
    </div>
    <div class="matrix-container">
        <div class="pagination">{#each habits as _, i}<div class="dot" class:active={i === currentIndex}></div>{/each}</div>
        <div class="matrix-grid">
            {#each currentHabit.grid as active, i}
                <button class="cell" class:active={active} onclick={() => toggle(i)}></button>
            {/each}
        </div>
    </div>
</div>

<style>
    /* ... Copy styles from previous HabitMatrix response ... */
    .habit-widget { height: 220px; display: flex; flex-direction: column; background: rgba(30, 41, 59, 0.4); backdrop-filter: blur(10px); border: 1px solid #334155; border-radius: 12px; transition: border-color 0.3s; } .habit-widget:hover { border-color: var(--theme); } .head { padding: 8px 10px; border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between; align-items: center; gap: 10px; } .nav-btn { background: rgba(255,255,255,0.05); border: 1px solid transparent; color: #94a3b8; width: 24px; height: 24px; border-radius: 4px; cursor: pointer; display: flex; justify-content: center; align-items: center; font-family: monospace; transition: 0.2s; } .nav-btn:hover { background: var(--theme); color: #000; } .title-area { flex: 1; text-align: center; display: flex; flex-direction: column; align-items: center; } .habit-name { background: transparent; border: none; color: var(--theme); font-family: 'Space Grotesk', sans-serif; font-weight: bold; font-size: 0.9rem; text-align: center; width: 100%; outline: none; text-transform: uppercase; letter-spacing: 1px; text-shadow: 0 0 10px rgba(0,0,0,0.5); } .habit-name:focus { border-bottom: 1px dashed var(--theme); } .counter { font-size: 0.6rem; color: #64748b; font-family: 'JetBrains Mono', monospace; } .matrix-container { flex: 1; padding: 10px 15px 15px 15px; display: flex; gap: 10px; flex-direction: row; } .pagination { display: flex; flex-direction: column; justify-content: center; gap: 6px; } .dot { width: 4px; height: 4px; border-radius: 50%; background: #334155; transition: 0.3s; } .dot.active { background: var(--theme); height: 12px; border-radius: 4px; box-shadow: 0 0 5px var(--theme); } .matrix-grid { flex: 1; display: grid; grid-template-columns: repeat(7, 1fr); grid-template-rows: repeat(5, 1fr); gap: 6px; } .cell { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 3px; cursor: pointer; transition: all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275); padding: 0; } .cell:hover { border-color: var(--theme); } .cell.active { background: var(--theme); border-color: var(--theme); box-shadow: 0 0 8px var(--theme); transform: scale(1.05); } .cell:active { transform: scale(0.9); }
</style>