<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    import { slide, fade } from 'svelte/transition';

    type Habit = {
        id: number;
        name: string;
        grid: number[]; // 35 days (7x5 grid)
    };

    let habits = $state<Habit[]>([]);
    let activeIndex = $state(0);
    let newHabitName = $state("");
    let isAdding = $state(false);

    // Derived active habit
    let currentHabit = $derived(habits[activeIndex]);

    onMount(async () => {
        // 1. Local Load
        if (typeof localStorage !== 'undefined') {
            const saved = localStorage.getItem('resinen_habits');
            if (saved) habits = JSON.parse(saved);
        }

        // 2. Cloud Sync
        try {
            const data = await api.widgets.loadDashboard();
            if (data && data.habits && data.habits.grid_data) {
                // Parse the big blob
                const parsed = typeof data.habits.grid_data === 'string' 
                    ? JSON.parse(data.habits.grid_data) 
                    : data.habits.grid_data;
                
                if (Array.isArray(parsed)) {
                    habits = parsed.map((h: any) => ({
                        ...h,
                        // Ensure grid is always 35 long for the matrix view
                        grid: (h.grid && h.grid.length === 35) ? h.grid : Array(35).fill(0)
                    }));
                }
                saveLocal();
            }
        } catch(e) { console.log("Offline"); }
    });

    async function syncBackend() {
        saveLocal();
        try {
            // Send the entire array as one JSON string
            await api.widgets.updateHabits({ 
                grid_data: JSON.stringify(habits) 
            });
        } catch(e) { console.error("Sync failed", e); }
    }

    function addHabit() {
        if (!newHabitName.trim()) return;
        
        const newH: Habit = {
            id: Date.now(),
            name: newHabitName,
            grid: Array(35).fill(0) // 7 cols x 5 rows
        };

        habits = [...habits, newH];
        activeIndex = habits.length - 1; // Jump to new
        newHabitName = "";
        isAdding = false;
        
        syncBackend();
    }

    function toggleCell(index: number) {
        if (!currentHabit) return;
        
        // Toggle 0/1
        const newGrid = [...currentHabit.grid];
        newGrid[index] = newGrid[index] ? 0 : 1;
        
        // Update state
        habits[activeIndex].grid = newGrid;
        
        syncBackend();
    }

    function deleteCurrent() {
        if(!confirm("Delete this habit grid?")) return;
        
        habits = habits.filter((_, i) => i !== activeIndex);
        if (activeIndex >= habits.length) activeIndex = Math.max(0, habits.length - 1);
        
        syncBackend();
    }

    function next() {
        if (activeIndex < habits.length - 1) activeIndex++;
        else activeIndex = 0; // Loop
    }

    function prev() {
        if (activeIndex > 0) activeIndex--;
        else activeIndex = habits.length - 1; // Loop
    }

    function saveLocal() {
        if (typeof localStorage !== 'undefined') 
            localStorage.setItem('resinen_habits', JSON.stringify(habits));
    }
</script>

<div class="card habit-widget">
    <div class="header">
        <span>HABIT MATRIX</span>
        <button class="add-btn" onclick={() => isAdding = !isAdding}>{isAdding ? '×' : '+'}</button>
    </div>

    {#if isAdding}
        <div class="add-overlay" transition:slide>
            <input type="text" bind:value={newHabitName} placeholder="PROTOCOL NAME..." onkeydown={(e) => e.key === 'Enter' && addHabit()} autoFocus />
            <button onclick={addHabit}>INITIALIZE</button>
        </div>
    {/if}

    <div class="carousel-stage">
        {#if habits.length > 0}
            <button class="nav-btn left" onclick={prev}>‹</button>

            <div class="habit-card" in:fade={{ duration: 200 }}>
                <div class="habit-meta">
                    <span class="habit-name">{currentHabit.name}</span>
                    <button class="del-btn" onclick={deleteCurrent}>🗑</button>
                </div>

                <div class="matrix-grid">
                    {#each currentHabit.grid as cell, i}
                        <button 
                            class="cell" 
                            class:active={cell === 1}
                            onmousedown={() => toggleCell(i)}
                            onmouseenter={(e) => e.buttons === 1 && toggleCell(i)} 
                        ></button>
                    {/each}
                </div>
                
                <div class="page-indicator">
                    {activeIndex + 1} / {habits.length}
                </div>
            </div>

            <button class="nav-btn right" onclick={next}>›</button>
        
        {:else}
            <div class="empty-state">
                NO ACTIVE PROTOCOLS.<br>
                CLICK + TO START.
            </div>
        {/if}
    </div>
</div>

<style>
    .habit-widget {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(10px);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 15px;
        display: flex; flex-direction: column;
        min-height: 280px; /* Taller for the matrix */
        position: relative;
        overflow: hidden;
    }

    /* HEADER */
    .header {
        display: flex; justify-content: space-between; align-items: center;
        font-family: 'JetBrains Mono'; color: #2dd4bf; font-size: 0.8rem;
        border-bottom: 1px solid #334155; padding-bottom: 10px; margin-bottom: 10px;
    }
    .add-btn {
        background: none; border: 1px solid #2dd4bf; color: #2dd4bf;
        width: 24px; height: 24px; border-radius: 4px; cursor: pointer;
        display: flex; align-items: center; justify-content: center;
        transition: 0.2s;
    }
    .add-btn:hover { background: #2dd4bf; color: #000; }

    /* ADD OVERLAY */
    .add-overlay {
        position: absolute; top: 50px; left: 0; right: 0; 
        background: #0f172a; padding: 20px; z-index: 10;
        border-bottom: 1px solid #334155;
        display: flex; gap: 10px;
    }
    .add-overlay input {
        flex: 1; background: #1e293b; border: 1px solid #334155; color: #fff;
        padding: 8px; outline: none; font-family: 'Space Grotesk';
    }
    .add-overlay button {
        background: #2dd4bf; color: #000; border: none; padding: 0 15px;
        font-weight: bold; cursor: pointer;
    }

    /* CAROUSEL */
    .carousel-stage {
        flex: 1; display: flex; align-items: center; justify-content: space-between;
        position: relative;
    }

    .nav-btn {
        background: transparent; border: none; color: #64748b;
        font-size: 2rem; cursor: pointer; padding: 0 5px; transition: 0.2s;
        z-index: 5;
    }
    .nav-btn:hover { color: #fff; transform: scale(1.2); }

    .habit-card {
        flex: 1; display: flex; flex-direction: column; align-items: center;
        gap: 10px; width: 100%;
    }

    .habit-meta {
        width: 100%; display: flex; justify-content: space-between; align-items: center;
        padding: 0 10px;
    }
    .habit-name { font-weight: bold; color: #fff; font-size: 1rem; letter-spacing: 1px; }
    .del-btn { background: none; border: none; cursor: pointer; font-size: 1rem; opacity: 0.5; }
    .del-btn:hover { opacity: 1; }

    /* THE MATRIX GRID */
    .matrix-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr); /* 7 Days wide */
        grid-template-rows: repeat(5, 1fr);    /* 5 Weeks high */
        gap: 6px;
        background: #0f172a;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #334155;
    }

    .cell {
        width: 24px; height: 24px;
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 4px;
        cursor: pointer;
        transition: 0.1s;
        padding: 0;
    }
    .cell:hover { border-color: #2dd4bf; }
    .cell.active { 
        background: #2dd4bf; 
        box-shadow: 0 0 8px #2dd4bf; 
        border-color: #2dd4bf; 
    }

    .page-indicator {
        font-family: 'JetBrains Mono'; font-size: 0.7rem; color: #64748b; margin-top: 5px;
    }

    .empty-state {
        width: 100%; text-align: center; color: #64748b; font-size: 0.8rem; font-style: italic;
    }

    /* === CLOUDY THEME === */
    :global(body.cloudy) .habit-widget {
        background: rgba(255, 255, 255, 0.6);
        border-color: #cbd5e1;
        color: #334155;
    }
    :global(body.cloudy) .header { border-bottom-color: #cbd5e1; color: #0f172a; }
    :global(body.cloudy) .add-btn { color: #0ea5e9; border-color: #0ea5e9; }
    :global(body.cloudy) .add-btn:hover { background: #0ea5e9; color: #fff; }
    
    :global(body.cloudy) .matrix-grid { background: #f1f5f9; border-color: #cbd5e1; }
    :global(body.cloudy) .cell { background: #fff; border-color: #cbd5e1; }
    :global(body.cloudy) .cell.active { background: #0ea5e9; border-color: #0ea5e9; box-shadow: 0 0 5px rgba(14, 165, 233, 0.5); }
    
    :global(body.cloudy) .habit-name { color: #334155; }
    :global(body.cloudy) .nav-btn { color: #94a3b8; }
    :global(body.cloudy) .nav-btn:hover { color: #0ea5e9; }
</style>