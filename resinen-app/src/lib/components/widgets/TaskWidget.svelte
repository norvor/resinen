<script lang="ts">
    import { onMount } from 'svelte';
    import { api, type Task } from '$lib/api';

    let tasks = $state<Task[]>([]);
    let newTask = $state("");
    let priority = $state("medium");
    let isAdding = $state(false);

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
        if (!newTask.trim()) return;
        
        const tempContent = newTask;
        const tempPrio = priority;
        newTask = "";
        isAdding = false;

        // Optimistic UI update could be complex with IDs, so we wait or use temp ID. 
        // For simplicity, we just call API and refresh list, or append result.
        try {
            const res = await api.widgets.createTask(tempContent, tempPrio);
            tasks = [...tasks, res];
            saveLocal();
        } catch(e) {
            alert("Could not create task.");
        }
    }

    async function toggleTask(t: Task) {
        // Optimistic
        t.is_done = !t.is_done;
        tasks = [...tasks];
        saveLocal();

        try {
            await api.widgets.updateTask(t.id, { is_done: t.is_done });
        } catch(e) { console.error("Sync failed"); }
    }

    async function removeTask(id: number) {
        tasks = tasks.filter(t => t.id !== id);
        saveLocal();
        try { await api.widgets.deleteTask(id); } catch(e) {}
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
        <span>ACTION ITEMS</span>
        <button class="add-btn" onclick={() => isAdding = !isAdding}>{isAdding ? '×' : '+'}</button>
    </div>

    {#if isAdding}
        <div class="add-row">
            <input type="text" bind:value={newTask} placeholder="New Directive..." onkeydown={(e) => e.key === 'Enter' && addTask()} autoFocus />
            <select bind:value={priority}>
                <option value="high">High</option>
                <option value="medium">Med</option>
                <option value="low">Low</option>
            </select>
            <button onclick={addTask}>SET</button>
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
                ></button>
                <span class="content">{t.content}</span>
                <button class="del-btn" onclick={() => removeTask(t.id)}>×</button>
            </div>
        {/each}
        {#if tasks.length === 0 && !isAdding}
            <div class="empty-state">All systems nominal. No tasks.</div>
        {/if}
    </div>
</div>

<style>
    /* === DEFAULT (DARK / NIGHT AURORA) === */
    .task-widget {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(10px);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 15px;
        display: flex;
        flex-direction: column;
        gap: 15px;
        min-height: 250px;
        overflow: hidden;
        transition: 0.3s;
    }

    .header {
        display: flex; justify-content: space-between; align-items: center;
        font-family: 'JetBrains Mono'; color: #2dd4bf; font-size: 0.8rem;
        border-bottom: 1px solid #334155; padding-bottom: 10px;
        transition: 0.3s;
    }

    .add-btn {
        background: none; border: 1px solid #2dd4bf; color: #2dd4bf;
        width: 24px; height: 24px; border-radius: 4px; cursor: pointer;
        display: flex; align-items: center; justify-content: center;
        transition: 0.2s;
    }
    .add-btn:hover { background: #2dd4bf; color: #000; }

    .add-row { display: flex; gap: 5px; animation: slideDown 0.2s; }
    .add-row input {
        flex: 1; background: rgba(0,0,0,0.3); border: 1px solid #334155;
        color: #fff; padding: 8px; border-radius: 4px; font-family: 'Space Grotesk';
        outline: none; font-size: 0.9rem;
    }
    .add-row select {
        background: #1e293b; color: #fff; border: 1px solid #334155; border-radius: 4px;
    }
    .add-row button {
        background: #2dd4bf; color: #000; border: none; padding: 0 15px;
        font-weight: bold; border-radius: 4px; cursor: pointer;
    }

    .task-list { overflow-y: auto; display: flex; flex-direction: column; gap: 8px; padding-right: 2px; flex: 1; }

    .task-row {
        display: flex; align-items: center; gap: 10px;
        background: rgba(255,255,255,0.03); padding: 10px; border-radius: 6px;
        transition: 0.2s; border: 1px solid transparent;
    }
    .task-row:hover { background: rgba(255,255,255,0.07); }
    .task-row.done { opacity: 0.5; }
    .task-row.done .content { text-decoration: line-through; color: #94a3b8; }

    .check-circle {
        width: 18px; height: 18px; border-radius: 50%;
        border: 2px solid #ccc; background: transparent; cursor: pointer;
        transition: 0.2s; flex-shrink: 0;
    }
    .check-circle.checked { background: #10b981; border-color: #10b981; }

    .content { flex: 1; font-size: 0.9rem; color: #e2e8f0; font-family: 'Space Grotesk'; }

    .del-btn { background: none; border: none; color: #475569; cursor: pointer; font-size: 1.2rem; }
    .del-btn:hover { color: #ef4444; }

    .empty-state { text-align: center; color: #64748b; font-size: 0.8rem; margin-top: 40px; font-style: italic; }

    @keyframes slideDown { from { opacity: 0; transform: translateY(-5px); } to { opacity: 1; transform: translateY(0); } }
    
    .task-list::-webkit-scrollbar { width: 4px; }
    .task-list::-webkit-scrollbar-thumb { background: #334155; border-radius: 2px; }

    /* === CLOUDY THEME OVERRIDES === */
    :global(body.cloudy) .task-widget {
        background: rgba(255, 255, 255, 0.6);
        border: 1px solid #cbd5e1;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        color: #334155;
    }

    :global(body.cloudy) .header {
        border-bottom-color: #cbd5e1;
        color: #0f172a; /* Darker Slate */
        font-weight: bold;
    }

    :global(body.cloudy) .add-btn {
        border-color: #0ea5e9; color: #0ea5e9;
    }
    :global(body.cloudy) .add-btn:hover {
        background: #0ea5e9; color: #fff;
    }

    :global(body.cloudy) .add-row input,
    :global(body.cloudy) .add-row select {
        background: #fff; border-color: #cbd5e1; color: #334155;
    }
    :global(body.cloudy) .add-row button {
        background: #0ea5e9; color: #fff;
    }

    :global(body.cloudy) .task-row {
        background: rgba(255,255,255,0.5);
        border-color: #e2e8f0;
    }
    :global(body.cloudy) .task-row:hover {
        background: #fff;
        border-color: #cbd5e1;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    :global(body.cloudy) .content {
        color: #334155; font-weight: 500;
    }
    :global(body.cloudy) .task-row.done .content {
        color: #94a3b8;
    }

    :global(body.cloudy) .empty-state {
        color: #64748b;
    }
    
    :global(body.cloudy) .task-list::-webkit-scrollbar-thumb { background: #cbd5e1; }
</style>