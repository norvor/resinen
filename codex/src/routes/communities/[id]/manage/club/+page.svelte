<script lang="ts">
    import { onMount } from 'svelte';
    import { api, type Event } from '$lib/api';
    import { fade, scale } from 'svelte/transition';

    export let data;
    $: community = data.community;

    let events: Event[] = [];
    let loading = true;
    let showCreate = false;

    let newEvent = {
        title: '',
        location: '',
        start_time: '',
        description: ''
    };

    onMount(async () => {
        await loadClub();
    });

    async function loadClub() {
        loading = true;
        try {
            const res = await api.getEvents(community.id);
            events = Array.isArray(res) ? res : [];
        } catch (e) { console.error(e); } 
        finally { loading = false; }
    }

    async function handleCreate() {
        try {
            await api.createEvent(community.id, newEvent);
            showCreate = false;
            newEvent = { title: '', location: '', start_time: '', description: '' };
            await loadClub();
        } catch (e) { alert("Failed to book venue."); }
    }
</script>

<div class="space-y-8 animate-fade-in-up">
    
    <div class="flex items-end justify-between border-b-4 border-black pb-6">
        <div>
            <div class="text-xs font-black uppercase text-pink-600 tracking-widest mb-1 flex items-center gap-2">
                <span>🎉</span> Club Engine
            </div>
            <h1 class="text-4xl font-black uppercase tracking-tighter">
                Event Calendar
            </h1>
        </div>
        <button 
            on:click={() => showCreate = true}
            class="px-6 py-3 bg-pink-600 text-white font-black rounded uppercase text-xs shadow-[4px_4px_0px_black] hover:-translate-y-1 hover:shadow-[6px_6px_0px_black] transition-all"
        >
            + Create Event
        </button>
    </div>

    {#if loading}
        <div class="p-12 text-center text-gray-400 font-bold animate-pulse">Checking Guestlist...</div>
    {:else if events.length === 0}
        <div class="p-20 text-center border-4 border-dashed border-gray-200 rounded-xl text-gray-400">
            <span class="text-4xl block mb-2">🗓️</span>
            <span class="font-bold uppercase tracking-widest">Calendar Empty</span>
        </div>
    {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each events as event}
                <div class="bg-white border-2 border-gray-200 p-6 rounded-xl relative group hover:border-black transition-colors flex flex-col">
                    <div class="text-xs font-black uppercase text-pink-500 mb-2">
                        {new Date(event.start_time).toLocaleDateString()} @ {new Date(event.start_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                    </div>
                    <h3 class="text-2xl font-black uppercase leading-none mb-1">{event.title}</h3>
                    <div class="text-xs font-bold text-gray-400 mb-4 uppercase">📍 {event.location}</div>
                    
                    <div class="mt-auto pt-4 border-t border-gray-100 flex justify-between items-center">
                        <div class="flex -space-x-2">
                            {#each [1,2,3] as _}
                                <div class="w-6 h-6 rounded-full bg-gray-200 border-2 border-white"></div>
                            {/each}
                        </div>
                        <button class="text-[10px] font-black uppercase text-gray-400 hover:text-black">
                            Edit Details
                        </button>
                    </div>
                </div>
            {/each}
        </div>
    {/if}

    {#if showCreate}
        <div class="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4 backdrop-blur-sm" transition:fade>
            <div class="bg-white w-full max-w-lg rounded-xl p-8 shadow-2xl" in:scale>
                <h2 class="font-black text-2xl uppercase mb-6">Host New Event</h2>
                
                <div class="space-y-4">
                    <div>
                        <label class="block text-xs font-bold uppercase text-gray-500 mb-1">Event Name</label>
                        <input bind:value={newEvent.title} class="w-full border-2 border-gray-200 p-3 rounded font-bold focus:border-black outline-none" />
                    </div>
                    <div>
                        <label class="block text-xs font-bold uppercase text-gray-500 mb-1">Location</label>
                        <input bind:value={newEvent.location} class="w-full border-2 border-gray-200 p-3 rounded font-bold focus:border-black outline-none" placeholder="e.g. Rooftop Bar" />
                    </div>
                    <div>
                        <label class="block text-xs font-bold uppercase text-gray-500 mb-1">Date & Time</label>
                        <input type="datetime-local" bind:value={newEvent.start_time} class="w-full border-2 border-gray-200 p-3 rounded font-bold focus:border-black outline-none" />
                    </div>
                    <div>
                        <label class="block text-xs font-bold uppercase text-gray-500 mb-1">Description</label>
                        <textarea bind:value={newEvent.description} class="w-full border-2 border-gray-200 p-3 rounded font-bold focus:border-black outline-none resize-none h-24"></textarea>
                    </div>
                </div>

                <div class="flex gap-2 mt-8">
                    <button on:click={() => showCreate = false} class="flex-1 py-3 text-gray-500 font-bold hover:bg-gray-100 rounded">Cancel</button>
                    <button on:click={handleCreate} class="flex-1 py-3 bg-pink-600 text-white font-bold uppercase rounded">Publish Event</button>
                </div>
            </div>
        </div>
    {/if}

</div>