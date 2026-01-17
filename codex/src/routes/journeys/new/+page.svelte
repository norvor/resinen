<script lang="ts">
    import { api, type Journey, type Stop } from '$lib/api';
    import { goto } from '$app/navigation';

    let journey: Journey = {
        id: '',
        title: '',
        description: '',
        theme_color: 'green-500'
    };

    // We keep a local list of stops to add AFTER the journey is created
    let stops: Stop[] = [
        { journey_id: '', order_index: 0, title: 'Start', description: '', visual_asset_url: '' }
    ];

    async function handleSubmit() {
        if(!journey.id) return alert("ID is required");

        try {
            // 1. Create Journey
            await api.createJourney(journey);

            // 2. Create All Stops
            for (const [index, stop] of stops.entries()) {
                if(stop.title) {
                    await api.createStop({
                        ...stop,
                        journey_id: journey.id,
                        order_index: index
                    });
                }
            }

            alert("Journey Created!");
            goto('/journeys');
        } catch (e) {
            alert("Error: " + e);
        }
    }

    function addStopField() {
        stops = [...stops, { journey_id: '', order_index: stops.length, title: '', description: '', visual_asset_url: '' }];
    }
</script>

<div class="p-10 max-w-3xl mx-auto space-y-8 pb-20">
    <header>
        <a href="/journeys" class="text-stone-400 hover:text-stone-800 mb-4 inline-block">&larr; Back</a>
        <h1 class="text-3xl font-light">Create New Journey</h1>
    </header>

    <div class="bg-white p-6 rounded-xl border border-stone-200 space-y-4 shadow-sm">
        <h2 class="font-bold text-stone-700 border-b pb-2">1. Core Details</h2>
        
        <div class="grid grid-cols-2 gap-4">
            <label class="block">
                <span class="text-xs font-bold text-stone-500 uppercase">ID (e.g. farming)</span>
                <input bind:value={journey.id} type="text" class="w-full mt-1 p-2 border rounded" placeholder="farming" />
            </label>
            <label class="block">
                <span class="text-xs font-bold text-stone-500 uppercase">Theme Color</span>
                <input bind:value={journey.theme_color} type="text" class="w-full mt-1 p-2 border rounded" placeholder="green-500" />
            </label>
        </div>

        <label class="block">
            <span class="text-xs font-bold text-stone-500 uppercase">Title</span>
            <input bind:value={journey.title} type="text" class="w-full mt-1 p-2 border rounded" placeholder="Tomato Farming" />
        </label>

        <label class="block">
            <span class="text-xs font-bold text-stone-500 uppercase">Description</span>
            <textarea bind:value={journey.description} class="w-full mt-1 p-2 border rounded h-20" placeholder="A cozy journey..."></textarea>
        </label>
    </div>

    <div class="space-y-4">
        <div class="flex justify-between items-end">
            <h2 class="font-bold text-stone-700">2. Define Stops</h2>
            <button on:click={addStopField} class="text-sm text-green-600 hover:underline">+ Add Another Stop</button>
        </div>

        {#each stops as stop, i}
            <div class="bg-stone-50 p-4 rounded-xl border border-stone-200 relative">
                <div class="absolute -left-3 top-4 bg-stone-800 text-white w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold">
                    {i + 1}
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-2">
                    <input bind:value={stop.title} placeholder="Stop Title (e.g. Sprout)" class="p-2 border rounded" />
                    <input bind:value={stop.visual_asset_url} placeholder="Image URL (Unsplash...)" class="p-2 border rounded" />
                </div>
                <textarea bind:value={stop.description} placeholder="What happens here?" class="w-full p-2 border rounded text-sm h-16"></textarea>
            </div>
        {/each}
    </div>

    <div class="fixed bottom-0 left-0 w-full bg-white border-t border-stone-200 p-4 flex justify-end px-10">
        <button on:click={handleSubmit} class="bg-green-600 text-white px-8 py-3 rounded-full font-bold shadow-lg hover:bg-green-500 transition">
            Publish Journey
        </button>
    </div>
</div>