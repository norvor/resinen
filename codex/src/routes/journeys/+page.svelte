<script lang="ts">
    import { onMount } from 'svelte';
    import { api, type Journey } from '$lib/api';

    let journeys: Journey[] = [];
    let loading = true;

    // Load data on page load
    onMount(async () => {
        journeys = await api.getJourneys();
        loading = false;
    });
</script>

<div class="p-10 max-w-5xl mx-auto">
    <div class="flex justify-between items-center mb-8">
        <div>
            <h1 class="text-3xl font-light text-stone-800">Journeys</h1>
            <p class="text-stone-500">The paths users can take.</p>
        </div>
        <a href="/journeys/new" class="bg-stone-800 text-white px-6 py-2 rounded-full hover:bg-stone-700 transition">
            + New Journey
        </a>
    </div>

    {#if loading}
        <div class="text-stone-400">Loading paths...</div>
    {:else if journeys.length === 0}
        <div class="p-10 border-2 border-dashed border-stone-200 rounded-xl text-center text-stone-400">
            No journeys found. Create your first one!
        </div>
    {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each journeys as journey}
                <div class="bg-white p-6 rounded-xl shadow-sm border border-stone-100 hover:shadow-md transition">
                    <div class={`w-2 h-2 rounded-full mb-4 bg-${journey.theme_color || 'green-500'}`}></div>
                    <h3 class="text-xl font-bold text-stone-800">{journey.title}</h3>
                    <p class="text-sm text-stone-500 mt-2 line-clamp-2">{journey.description}</p>
                    
                    <div class="mt-6 flex justify-between items-center text-sm">
                        <span class="bg-stone-100 px-2 py-1 rounded text-stone-600">ID: {journey.id}</span>
                        <a href={`/journeys/${journey.id}`} class="text-green-600 hover:underline">Manage Stops &rarr;</a>
                    </div>
                </div>
            {/each}
        </div>
    {/if}
</div>