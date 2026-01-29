<script lang="ts">
    import { onMount } from 'svelte';
    import { api, type Task } from '$lib/api';

    let tasks = $state<Task[]>([]);
    let newTask = $state("");
    let priority = $state("medium");
    let isAdding = $state(false);
    let isLoading = $state(false);

    onMount(async () => {
        // 1. Local Cache
        if (typeof localStorage !== 'undefined') {
            const saved = localStorage.getItem('resinen_tasks');
            if (saved) tasks = JSON.parse(saved);
        }

        // 2. Cloud Sync
        try {
            const data = await api.widgets.loadDashboard();
            if (data && data.tasks) {
                tasks = data.tasks;
                saveLocal();
            }
        } catch(e) { console.log("Offline"); }
    });

    async function addTask() {
        if (!newTask.trim() || isLoading) return;
        
        const tempContent = newTask;
        const tempPrio = priority;
        isLoading = true;

        try {
            const res = await api.widgets.createTask(tempContent, tempPrio);
            tasks = [...tasks, res];
            saveLocal();
            // Reset
            newTask = "";
            isAdding = false;
        } catch(e) {
            alert("Could not create task.");
        } finally {
            isLoading = false;
        }
    }

    async function toggleTask(t: Task) {
        // Optimistic
        t.is_done = !t.is_done;
        saveLocal();

        try {
            await api.widgets.updateTask(t.id, { is_done: t.is_done });
        } catch(e) { 
            console.error("Sync failed");
            // Revert on fail
            t.is_done = !t.is_done; 
        }
    }

    async function removeTask(id: number) {
        const previousTasks = [...tasks];
        tasks = tasks.filter(t => t.id !== id);
        saveLocal();
        try { 
            await api.widgets.deleteTask(id); 
        } catch(e) {
            tasks = previousTasks; // Revert
        }
    }

    function saveLocal() {
        if (typeof localStorage !== 'undefined') localStorage.setItem('resinen_tasks', JSON.stringify(tasks));
    }

    function getPriorityColor(p: string) {
        if (p === 'high') return '#ef4444';
        if (p === 'low') return '#3b82f6';
        return '#eab308'; // Medium
    }
</script>

<div class="card task-widget">
    <div class="header">
        <span class="title">ACTION ITEMS <span class="count">{tasks.filter(t => !t.is_done).length}</span></span>
        <button class="add-btn" class:active={isAdding} onclick={() => isAdding = !isAdding}>
            {isAdding ? '×' : '+'}
        </button>
    </div>

    {#if isAdding}
        <div class="add-row">
            <input 
                type="text" 
                bind:value={newTask} 
                placeholder="New Directive..." 
                onkeydown={(e) => e.key === 'Enter' && addTask()} 
                disabled={isLoading}
                autofocus 
            />
            <select bind:value={priority} disabled={isLoading}>
                <option value="high">High</option>
                <option value="medium">Med</option>
                <option value="low">Low</option>
            </select>
            <button onclick={addTask} disabled={isLoading}>
                {isLoading ? '...' : 'SET'}
            </button>
        </div>
    {/if}

    <div class="task-list">
        {#each tasks as t (t.id)}
            <div class="task-row" class:done={t.is_done}>
                <button 
                    class="check-circle" 
                    style="border-color: {getPriorityColor(t.priority)}"
                    class:checked={t.is_done}
                    onclick={() => toggleTask(t)}
                    aria-label="Toggle Task"
                >
                    {#if t.is_done}✓{/if}
                </button>
                <span class="content">{t.content}</span>
                <button class="del-btn" onclick={() => removeTask(t.id)} aria-label="Delete">×</button>
            </div>
        {/each}
        {#if tasks.length === 0 && !isAdding}
            <div class="empty-state">
                <span class="icon">★</span>
                All systems nominal. No directives.
            </div>
        {/if}
    </div>
</div>

<style>
    /* === WIDGET CORE === */
    .task-widget {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(10px);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 15px;
        display: flex;
        flex-direction: column;
        gap: 15px;
        /* Using fit-content with constraints instead of rigid min-height */
        width: 100%;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }

    .header {
        display: flex; justify-content: space-between; align-items: center;
        font-family: 'JetBrains Mono'; color: #2dd4bf; font-size: 0.85rem;
        border-bottom: 1px solid #334155; padding-bottom: 10px;
        user-select: none;
    }
    
    .title { display: flex; align-items: center; gap: 8px; font-weight: bold; letter-spacing: 1px; }
    .count { 
        background: rgba(45, 212, 191, 0.1); color: #2dd4bf; 
        padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; 
    }

    .add-btn {
        background: transparent; border: 1px solid #2dd4bf; color: #2dd4bf;
        width: 26px; height: 26px; border-radius: 6px; cursor: pointer;
        display: flex; align-items: center; justify-content: center;
        transition: all 0.2s ease; font-size: 1.2rem; line-height: 0;
    }
    .add-btn:hover, .add-btn.active { background: #2dd4bf; color: #000; box-shadow: 0 0 10px rgba(45, 212, 191, 0.3); }

    /* === ADD INPUT === */
    .add-row { display: flex; gap: 8px; animation: slideDown 0.2s cubic-bezier(0.16, 1, 0.3, 1); margin-bottom: 5px; }
    .add-row input {
        flex: 1; background: rgba(0,0,0,0.3); border: 1px solid #334155;
        color: #fff; padding: 8px 12px; border-radius: 6px; font-family: 'Space Grotesk';
        outline: none; font-size: 0.9rem; transition: border-color 0.2s;
    }
    .add-row input:focus { border-color: #2dd4bf; }
    
    .add-row select {
        background: #0f172a; color: #fff; border: 1px solid #334155; 
        border-radius: 6px; padding: 0 5px; font-family: 'JetBrains Mono'; font-size: 0.8rem;
        cursor: pointer;
    }
    .add-row button {
        background: #2dd4bf; color: #000; border: none; padding: 0 15px;
        font-weight: bold; border-radius: 6px; cursor: pointer;
        font-family: 'JetBrains Mono'; font-size: 0.8rem;
    }
    .add-row button:disabled { opacity: 0.5; cursor: wait; }

    /* === LIST & SCROLLING === */
    .task-list { 
        display: flex; flex-direction: column; gap: 6px; 
        /* FIXED MAX HEIGHT for scrolling after ~4 items (approx 45px each) */
        max-height: 200px; 
        overflow-y: auto;
        padding-right: 4px; /* Space for scrollbar */
    }

    /* Scrollbar Styling */
    .task-list::-webkit-scrollbar { width: 4px; }
    .task-list::-webkit-scrollbar-track { background: rgba(0,0,0,0.1); border-radius: 2px; }
    .task-list::-webkit-scrollbar-thumb { background: #475569; border-radius: 2px; }
    .task-list::-webkit-scrollbar-thumb:hover { background: #64748b; }

    .task-row {
        display: flex; align-items: center; gap: 12px;
        background: rgba(255,255,255,0.03); padding: 8px 10px; border-radius: 6px;
        transition: all 0.2s; border: 1px solid transparent;
        min-height: 40px;
    }
    .task-row:hover { background: rgba(255,255,255,0.06); border-color: rgba(255,255,255,0.1); transform: translateX(2px); }
    .task-row.done { opacity: 0.5; background: transparent; }
    .task-row.done .content { text-decoration: line-through; color: #64748b; }

    .check-circle {
        width: 18px; height: 18px; border-radius: 50%;
        border: 2px solid #ccc; background: transparent; cursor: pointer;
        display: flex; align-items: center; justify-content: center;
        transition: all 0.2s; flex-shrink: 0; padding: 0;
        font-size: 10px; color: #000; font-weight: bold;
    }
    .check-circle:hover { transform: scale(1.1); }
    .check-circle.checked { background: #10b981; border-color: #10b981; }

    .content { flex: 1; font-size: 0.9rem; color: #f1f5f9; font-family: 'Space Grotesk'; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

    .del-btn { 
        background: none; border: none; color: #475569; cursor: pointer; 
        font-size: 1.2rem; opacity: 0; transition: 0.2s; padding: 0 5px;
    }
    .task-row:hover .del-btn { opacity: 1; }
    .del-btn:hover { color: #ef4444; transform: scale(1.2); }

    .empty-state { 
        text-align: center; color: #64748b; font-size: 0.85rem; 
        padding: 30px 0; font-style: italic; display: flex; 
        flex-direction: column; align-items: center; gap: 5px;
    }
    .empty-state .icon { font-size: 1.2rem; color: #334155; }

    @keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }

    /* === CLOUDY THEME OVERRIDES === */
    :global(body.cloudy) .task-widget {
        background: rgba(255, 255, 255, 0.7);
        border: 1px solid #cbd5e1;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    :global(body.cloudy) .header { border-bottom-color: #e2e8f0; color: #334155; }
    :global(body.cloudy) .count { background: #e0f2fe; color: #0ea5e9; }
    :global(body.cloudy) .add-btn { border-color: #0ea5e9; color: #0ea5e9; }
    :global(body.cloudy) .add-btn:hover { background: #0ea5e9; color: #fff; }
    
    :global(body.cloudy) .add-row input { background: #fff; border-color: #cbd5e1; color: #0f172a; }
    :global(body.cloudy) .add-row select { background: #fff; border-color: #cbd5e1; color: #0f172a; }
    :global(body.cloudy) .add-row button { background: #0ea5e9; color: #fff; }
    
    :global(body.cloudy) .task-row { background: rgba(255,255,255,0.6); border-color: transparent; }
    :global(body.cloudy) .task-row:hover { background: #fff; border-color: #cbd5e1; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    :global(body.cloudy) .content { color: #334155; }
    :global(body.cloudy) .task-row.done .content { color: #94a3b8; }
    :global(body.cloudy) .task-list::-webkit-scrollbar-thumb { background: #cbd5e1; }
</style>