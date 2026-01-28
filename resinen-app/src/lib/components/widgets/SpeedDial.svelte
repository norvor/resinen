<script lang="ts">
    import { onMount } from 'svelte';

    type Slot = { name: string; url: string; color: string };
    let slots = $state<Slot[]>(Array(6).fill({ name: "EMPTY", url: "", color: "#334155" }));
    
    let editIndex = $state<number | null>(null);
    let editName = $state("");
    let editUrl = $state("");

    function openEdit(i: number, e: Event) {
        e.preventDefault();
        e.stopPropagation(); // prevent link click
        editIndex = i;
        editName = slots[i].name !== "EMPTY" ? slots[i].name : "";
        editUrl = slots[i].url;
    }

    function saveSlot() {
        if (editIndex === null) return;
        if (!editName) {
            slots[editIndex] = { name: "EMPTY", url: "", color: "#334155" };
        } else {
            const colors = ["#fbbf24", "#34d399", "#60a5fa", "#a78bfa", "#f472b6", "#2dd4bf"];
            const color = colors[editIndex % colors.length];
            slots[editIndex] = { name: editName, url: editUrl, color };
        }
        editIndex = null;
        localStorage.setItem('resinen_speed_dial', JSON.stringify(slots));
    }

    onMount(() => {
        const s = localStorage.getItem('resinen_speed_dial');
        if (s) slots = JSON.parse(s);
    });
</script>

<div class="card dial-widget">
    <div class="head">SPEED DIAL <span class="hint">(Right Click to Edit)</span></div>
    
    {#if editIndex !== null}
        <div class="edit-overlay">
            <input bind:value={editName} placeholder="Name" />
            <input bind:value={editUrl} placeholder="https://..." />
            <div class="btns">
                <button onclick={() => editIndex = null}>Cancel</button>
                <button class="save" onclick={saveSlot}>Save</button>
            </div>
        </div>
    {/if}

    <div class="grid-slots">
        {#each slots as slot, i}
            {#if slot.url}
                <a href={slot.url} target="_blank" class="slot filled" style="--c: {slot.color}" oncontextmenu={(e) => openEdit(i, e)}>
                    <div class="icon" style="background: {slot.color}"></div>
                    <span class="label">{slot.name}</span>
                </a>
            {:else}
                <button class="slot empty" oncontextmenu={(e) => openEdit(i, e)} onclick={(e) => openEdit(i, e)}>+</button>
            {/if}
        {/each}
    </div>
</div>

<style>
    .dial-widget { height: 220px; display: flex; flex-direction: column; background: rgba(30, 41, 59, 0.4); backdrop-filter: blur(10px); border: 1px solid #334155; border-radius: 12px; position: relative; }
    .head { padding: 10px 15px; border-bottom: 1px solid #334155; color: #a78bfa; font-family: 'JetBrains Mono'; font-size: 0.7rem; display: flex; justify-content: space-between; }
    .hint { opacity: 0.5; font-size: 0.6rem; }

    .grid-slots { padding: 15px; display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr 1fr; gap: 10px; flex: 1; }
    
    .slot { border-radius: 8px; display: flex; align-items: center; gap: 10px; text-decoration: none; padding: 0 10px; transition: 0.2s; border: 1px solid transparent; }
    .slot.empty { background: rgba(255,255,255,0.02); border: 1px dashed #334155; color: #64748b; justify-content: center; cursor: pointer; }
    .slot.empty:hover { border-color: #a78bfa; color: #a78bfa; }
    
    .slot.filled { background: rgba(255,255,255,0.05); border: 1px solid #334155; }
    .slot.filled:hover { border-color: var(--c); transform: translateX(5px); background: rgba(255,255,255,0.08); }
    
    .icon { width: 8px; height: 8px; border-radius: 50%; box-shadow: 0 0 5px var(--c); }
    .label { color: #e2e8f0; font-family: 'Space Grotesk'; font-size: 0.8rem; font-weight: bold; }

    .edit-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: #0f172a; z-index: 10; display: flex; flex-direction: column; gap: 10px; padding: 20px; justify-content: center; }
    input { background: rgba(255,255,255,0.1); border: 1px solid #334155; color: #fff; padding: 8px; border-radius: 4px; }
    .btns { display: flex; gap: 10px; }
    .btns button { flex: 1; padding: 8px; cursor: pointer; border-radius: 4px; border: none; }
    .save { background: #a78bfa; color: #000; font-weight: bold; }
</style>