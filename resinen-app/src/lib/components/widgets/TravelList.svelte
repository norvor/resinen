<script lang="ts">
    // PROPS: We accept an 'onOpenPlace' callback to bubble up to the parent page
    let { places = [], onOpenPlace, onAddPlace, onDeletePlace } = $props();

    let newPlaceName = $state("");

    function handleAdd() {
        if (!newPlaceName.trim()) return;
        onAddPlace(newPlaceName);
        newPlaceName = "";
    }
</script>

<div class="card travel-widget">
    <div class="head">
        <span>TRAVEL LIST</span>
        <div class="add-mini">
            <input type="text" bind:value={newPlaceName} placeholder="New Destination..." onkeydown={(e)=>e.key==='Enter'&&handleAdd()} />
            <button onclick={handleAdd}>+</button>
        </div>
    </div>

    <div class="places-list">
        {#each places as place}
            <button class="place-row" onclick={() => onOpenPlace(place)}>
                <div class="icon">✈️</div>
                <div class="info">
                    <div class="name">{place.name}</div>
                    <div class="count">{place.photos?.length || 0} PHOTOS</div>
                </div>
                <div class="arrow" onclick={(e) => { e.stopPropagation(); onDeletePlace(place.id); }}>×</div>
            </button>
        {/each}
        {#if places.length === 0}
            <div class="empty">NO TRIPS PLANNED</div>
        {/if}
    </div>
</div>

<style>
    .travel-widget { height: 220px; display: flex; flex-direction: column; background: rgba(30, 41, 59, 0.4); backdrop-filter: blur(10px); border: 1px solid #334155; border-radius: 12px; }
    .head { padding: 10px 15px; border-bottom: 1px solid #334155; color: #60a5fa; font-family: 'JetBrains Mono'; font-size: 0.7rem; display: flex; justify-content: space-between; align-items: center; }
    
    .add-mini { display: flex; gap: 5px; }
    .add-mini input { background: rgba(0,0,0,0.3); border: 1px solid #334155; color: #fff; padding: 2px 8px; border-radius: 4px; font-family: var(--mono); font-size: 0.7rem; width: 100px; outline: none; }
    .add-mini button { background: #60a5fa; border: none; color: #000; font-weight: bold; padding: 2px 8px; border-radius: 4px; cursor: pointer; }

    .places-list { flex: 1; overflow-y: auto; padding: 10px; display: flex; flex-direction: column; gap: 6px; }
    
    .place-row { background: rgba(255,255,255,0.03); border: 1px solid transparent; border-radius: 6px; padding: 8px 10px; display: flex; align-items: center; gap: 10px; cursor: pointer; transition: 0.2s; text-align: left; width: 100%; }
    .place-row:hover { background: rgba(255,255,255,0.08); border-color: #60a5fa; }
    
    .icon { font-size: 1rem; opacity: 0.8; }
    .info { flex: 1; }
    .name { font-weight: bold; color: #fff; font-size: 0.85rem; }
    .count { font-family: 'JetBrains Mono'; font-size: 0.6rem; color: #94a3b8; }
    
    .arrow { color: #64748b; font-size: 1.2rem; line-height: 0.5; padding: 5px; border-radius: 4px; transition: 0.2s; }
    .arrow:hover { color: #ef4444; background: rgba(239, 68, 68, 0.1); }

    .empty { text-align: center; color: #475569; font-family: 'JetBrains Mono'; font-size: 0.7rem; margin-top: 40px; }
</style>