<script lang="ts">
    import { onMount } from 'svelte';
    import { api, type Travel } from '$lib/api';

    let trips = $state<Travel[]>([]);
    let newDest = $state("");
    let newDate = $state("");
    let isAdding = $state(false);

    onMount(async () => {
        // 1. Local Cache
        if (typeof localStorage !== 'undefined') {
            const saved = localStorage.getItem('resinen_travel');
            if (saved) trips = JSON.parse(saved);
        }

        // 2. Cloud Sync
        try {
            const data = await api.widgets.loadDashboard();
            if (data && data.travel) {
                trips = data.travel;
                saveLocal();
            }
        } catch(e) { console.log("Offline"); }
    });

    async function addTrip() {
        if (!newDest || !newDate) return;
        
        const tempTrip = { destination: newDest, date_range: newDate, status: 'planned' };
        newDest = "";
        newDate = "";
        isAdding = false;

        try {
            const res = await api.widgets.createTravel(tempTrip.destination, tempTrip.date_range);
            trips = [...trips, res];
            saveLocal();
        } catch(e) {
            alert("Could not book trip.");
        }
    }

    function saveLocal() {
        if (typeof localStorage !== 'undefined') localStorage.setItem('resinen_travel', JSON.stringify(trips));
    }

    function getStatusColor(status: string) {
        if (status === 'booked') return '#10b981'; // Green
        if (status === 'completed') return '#64748b'; // Gray
        return '#fbbf24'; // Yellow (Planned)
    }
</script>

<div class="card travel-widget">
    <div class="header">
        <span>TRAVEL LOG</span>
        <button class="add-btn" onclick={() => isAdding = !isAdding}>{isAdding ? '×' : '+'}</button>
    </div>

    {#if isAdding}
        <div class="add-form">
            <input type="text" bind:value={newDest} placeholder="Destination (e.g. Tokyo)" />
            <input type="text" bind:value={newDate} placeholder="Dates (e.g. Oct 12-15)" />
            <button onclick={addTrip}>BOOK</button>
        </div>
    {/if}

    <div class="trip-list">
        {#each trips as trip}
            <div class="trip-card">
                <div class="icon">✈️</div>
                <div class="info">
                    <div class="dest">{trip.destination}</div>
                    <div class="date">{trip.date_range}</div>
                </div>
                <div class="status">
                    <span class="dot" style="background: {getStatusColor(trip.status)}"></span>
                    {trip.status.toUpperCase()}
                </div>
            </div>
        {/each}
        {#if trips.length === 0 && !isAdding}
            <div class="empty-state">No upcoming vectors.</div>
        {/if}
    </div>
</div>

<style>
    .travel-widget {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(10px);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 15px;
        display: flex;
        flex-direction: column;
        gap: 15px;
        min-height: 200px;
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

    .add-form { display: flex; flex-direction: column; gap: 8px; animation: slideDown 0.2s; }
    .add-form input {
        background: rgba(0,0,0,0.3); border: 1px solid #334155; color: #fff;
        padding: 8px; border-radius: 4px; font-family: 'Space Grotesk'; outline: none;
    }
    .add-form button {
        background: #2dd4bf; color: #000; border: none; padding: 8px;
        font-weight: bold; border-radius: 4px; cursor: pointer;
    }

    .trip-list { display: flex; flex-direction: column; gap: 10px; overflow-y: auto; max-height: 250px; }
    
    .trip-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 10px;
        display: flex; align-items: center; gap: 12px;
        transition: 0.2s;
    }
    .trip-card:hover { border-color: #2dd4bf; transform: translateX(2px); }

    .icon { font-size: 1.2rem; }
    
    .info { flex: 1; display: flex; flex-direction: column; }
    .dest { font-weight: bold; color: #f8fafc; font-size: 0.95rem; }
    .date { font-size: 0.75rem; color: #94a3b8; font-family: 'JetBrains Mono'; }

    .status { 
        display: flex; align-items: center; gap: 6px;
        font-size: 0.65rem; font-family: 'JetBrains Mono'; color: #cbd5e1;
        background: rgba(0,0,0,0.2); padding: 4px 8px; border-radius: 20px;
    }
    .dot { width: 6px; height: 6px; border-radius: 50%; }

    .empty-state { text-align: center; color: #64748b; font-size: 0.8rem; margin-top: 20px; font-style: italic; }

    @keyframes slideDown { from { opacity: 0; transform: translateY(-5px); } to { opacity: 1; transform: translateY(0); } }
</style>