<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';

    // Define Interface locally
    interface Love {
        id: number;
        name: string;
        category: string;
        description: string;
        link?: string; 
    }

    let loves = $state<Love[]>([]);
    let isAdding = $state(false);
    
    // Form Inputs
    let newName = $state("");
    let newCategory = $state("book");
    let newDesc = $state("");
    let newLink = $state("");

    onMount(async () => {
        if (typeof localStorage !== 'undefined') {
            const saved = localStorage.getItem('resinen_loves');
            if (saved) loves = JSON.parse(saved);
        }

        try {
            const data = await api.widgets.loadDashboard();
            if (data && data.loves) {
                loves = data.loves;
                saveLocal();
            }
        } catch(e) { console.log("Offline"); }
    });

    async function addLove() {
        if (!newName.trim()) return;
        
        const tempName = newName;
        const tempCat = newCategory;
        const tempDesc = newDesc;
        const tempLink = newLink;
        
        // Reset Form
        newName = ""; newDesc = ""; newLink = "";
        isAdding = false;

        try {
            const res = await api.widgets.createLove(tempName, tempCat, tempDesc, tempLink);
            loves = [res, ...loves];
            saveLocal();
        } catch(e) {
            alert("Could not save to collection.");
            // Restore on fail
            newName = tempName;
            newDesc = tempDesc;
            newLink = tempLink;
            isAdding = true;
        }
    }

    async function removeLove(id: number) {
        if(!confirm("Remove from favorites?")) return;
        loves = loves.filter(l => l.id !== id);
        saveLocal();
        try { await api.widgets.deleteLove(id); } catch(e) {}
    }

    function saveLocal() {
        if (typeof localStorage !== 'undefined') localStorage.setItem('resinen_loves', JSON.stringify(loves));
    }

    function getIcon(cat: string) {
        switch(cat) {
            case 'book': return '📚';
            case 'movie': return '🎬';
            case 'person': return '👤';
            case 'quote': return '❝';
            case 'music': return '🎵';
            default: return '❤️';
        }
    }
</script>

<div class="card love-widget">
    <div class="header">
        <span>CURATED LOVES</span>
        <button class="add-btn" onclick={() => isAdding = !isAdding}>{isAdding ? '×' : '+'}</button>
    </div>

    {#if isAdding}
        <div class="add-form">
            <div class="row">
                <input type="text" bind:value={newName} placeholder="Title / Name..." autoFocus />
                <select bind:value={newCategory}>
                    <option value="book">Book</option>
                    <option value="movie">Movie</option>
                    <option value="person">Person</option>
                    <option value="music">Music</option>
                    <option value="quote">Quote</option>
                </select>
            </div>
            
            <input type="text" bind:value={newLink} placeholder="Link (Optional)..." />
            <input type="text" bind:value={newDesc} placeholder="Why do you love this?" />
            
            <button class="save-btn" onclick={addLove}>ADD TO COLLECTION</button>
        </div>
    {/if}

    <div class="love-list">
        {#each loves as item (item.id)}
            <div class="love-item">
                <div class="icon">{getIcon(item.category)}</div>
                <div class="content">
                    <div class="name">
                        {#if item.link}
                            <a href={item.link} target="_blank" rel="noopener noreferrer">{item.name}</a>
                        {:else}
                            {item.name}
                        {/if}
                    </div>
                    {#if item.description}
                        <div class="desc">{item.description}</div>
                    {/if}
                </div>
                <button class="del-btn" onclick={() => removeLove(item.id)}>×</button>
            </div>
        {/each}
        {#if loves.length === 0 && !isAdding}
            <div class="empty-state">No inspirations curated.</div>
        {/if}
    </div>
</div>

<style>
    /* === DEFAULT (DARK / NIGHT AURORA) === */
    .love-widget {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(10px);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 15px;
        display: flex;
        flex-direction: column;
        gap: 15px;
        min-height: 250px;
        max-height: 400px;
        transition: 0.3s;
    }

    .header {
        display: flex; justify-content: space-between; align-items: center;
        font-family: 'JetBrains Mono'; color: #2dd4bf; font-size: 0.8rem;
        border-bottom: 1px solid #334155; padding-bottom: 10px;
    }

    .add-btn {
        background: none; border: 1px solid #2dd4bf; color: #2dd4bf;
        width: 24px; height: 24px; border-radius: 4px; cursor: pointer;
        display: flex; align-items: center; justify-content: center;
        transition: 0.2s;
    }
    .add-btn:hover { background: #2dd4bf; color: #000; }

    .add-form { display: flex; flex-direction: column; gap: 8px; animation: slideDown 0.2s; margin-bottom: 10px; }
    .row { display: flex; gap: 5px; }
    
    input, select {
        background: rgba(0,0,0,0.3); border: 1px solid #334155; color: #fff;
        padding: 8px; border-radius: 4px; font-family: 'Inter', sans-serif; outline: none;
        font-size: 0.85rem;
    }
    input { width: 100%; }
    .row input { flex: 1; }
    
    .save-btn {
        background: #2dd4bf; color: #000; border: none; padding: 8px;
        font-weight: bold; border-radius: 4px; cursor: pointer; margin-top: 5px;
    }

    .love-list { overflow-y: auto; display: flex; flex-direction: column; gap: 8px; padding-right: 4px; flex: 1; }
    
    .love-item {
        background: rgba(255,255,255,0.03); border: 1px solid #334155;
        border-radius: 8px; padding: 10px; display: flex; align-items: flex-start; gap: 10px;
        transition: 0.2s;
    }
    .love-item:hover { border-color: #64748b; background: rgba(255,255,255,0.05); }

    .icon { font-size: 1.2rem; padding-top: 2px; }
    .content { flex: 1; }
    .name { font-weight: bold; font-size: 0.95rem; color: #f1f5f9; }
    .name a { color: #f1f5f9; text-decoration: none; border-bottom: 1px dotted #94a3b8; }
    .name a:hover { color: #2dd4bf; border-color: #2dd4bf; }
    
    .desc { font-size: 0.8rem; color: #94a3b8; margin-top: 2px; line-height: 1.3; }

    .del-btn { background: none; border: none; color: #475569; cursor: pointer; font-size: 1.2rem; line-height: 1; padding: 0; }
    .del-btn:hover { color: #ef4444; }

    .empty-state { text-align: center; color: #64748b; font-size: 0.8rem; margin-top: 40px; font-style: italic; }

    @keyframes slideDown { from { opacity: 0; transform: translateY(-5px); } to { opacity: 1; transform: translateY(0); } }
    
    .love-list::-webkit-scrollbar { width: 4px; }
    .love-list::-webkit-scrollbar-thumb { background: #334155; border-radius: 2px; }

    /* === CLOUDY THEME OVERRIDES === */
    :global(body.cloudy) .love-widget {
        background: rgba(255, 255, 255, 0.6);
        border: 1px solid #cbd5e1;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        color: #334155;
    }

    :global(body.cloudy) .header {
        border-bottom-color: #cbd5e1;
        color: #0f172a;
        font-weight: bold;
    }

    :global(body.cloudy) .add-btn {
        border-color: #0ea5e9; color: #0ea5e9;
    }
    :global(body.cloudy) .add-btn:hover {
        background: #0ea5e9; color: #fff;
    }

    :global(body.cloudy) input,
    :global(body.cloudy) select {
        background: #fff; border-color: #cbd5e1; color: #334155;
    }
    :global(body.cloudy) .save-btn {
        background: #0ea5e9; color: #fff;
    }

    :global(body.cloudy) .love-item {
        background: rgba(255,255,255,0.5);
        border-color: #e2e8f0;
    }
    :global(body.cloudy) .love-item:hover {
        background: #fff;
        border-color: #cbd5e1;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    :global(body.cloudy) .name { color: #334155; }
    :global(body.cloudy) .name a { color: #0284c7; border-color: #0284c7; }
    :global(body.cloudy) .desc { color: #64748b; }

    :global(body.cloudy) .empty-state { color: #94a3b8; }
    :global(body.cloudy) .love-list::-webkit-scrollbar-thumb { background: #cbd5e1; }
</style>