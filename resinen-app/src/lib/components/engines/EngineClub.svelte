<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    export let community: any;

    let events: any[] = [];
    let loading = true;

    async function loadEvents() {
        try {
            events = await api.getEvents(community.id);
        } catch (e) {
            console.error(e);
        } finally {
            loading = false;
        }
    }

    onMount(loadEvents);

    async function rsvp(eventId: string, status: 'going' | 'not_going') {
        try {
            const res = await api.rsvpEvent(eventId, status);
            // Optimistic update
            events = events.map(e => e.id === eventId ? {
                ...e, 
                my_rsvp: status,
                count_going: res.going // API returns updated count
            } : e);
        } catch (e) {
            alert("RSVP failed.");
        }
    }
</script>

{#if loading}
    <div class="p-8 text-center animate-pulse text-skin-muted font-bold uppercase">Loading Events...</div>
{:else}
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        {#each events as e}
            <div class="skin-card group flex flex-col h-full overflow-hidden hover:-translate-y-1 transition-transform duration-300">
                
                <div class="h-32 bg-skin-surface relative">
                    {#if e.cover_image_url}
                        <img src={e.cover_image_url} alt="Cover" class="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity"/>
                    {:else}
                        <div class="w-full h-full flex items-center justify-center text-4xl opacity-20 bg-gradient-to-tr from-skin-accent to-purple-900">
                            🎟️
                        </div>
                    {/if}
                    
                    <div class="absolute top-4 left-4 bg-skin-fill border border-skin-border shadow-hard px-3 py-1 text-center">
                        <div class="text-xs font-bold text-red-500 uppercase">{new Date(e.start_time).toLocaleString('default', { month: 'short' })}</div>
                        <div class="text-xl font-black leading-none text-skin-text">{new Date(e.start_time).getDate()}</div>
                    </div>
                </div>

                <div class="p-5 flex-1 flex flex-col">
                    <div class="text-xs font-bold text-skin-muted uppercase mb-1 tracking-wider">{e.location_name}</div>
                    <h3 class="text-lg font-black uppercase text-skin-text mb-2 leading-tight">{e.title}</h3>
                    <p class="text-sm opacity-70 mb-4 line-clamp-3 flex-1">{e.description}</p>
                    
                    <div class="flex items-center justify-between border-t border-skin-border pt-4 mt-auto">
                        <div class="text-xs font-bold text-skin-muted">
                            <span class="text-skin-accent">{e.count_going}</span> Going
                        </div>

                        <div class="flex gap-2">
                            {#if e.my_rsvp === 'going'}
                                <button on:click={() => rsvp(e.id, 'not_going')} class="px-4 py-1.5 bg-green-500 text-white font-bold uppercase text-[10px] rounded shadow-sm hover:bg-green-600 transition-colors">
                                    ✓ Going
                                </button>
                            {:else}
                                <button on:click={() => rsvp(e.id, 'going')} class="px-4 py-1.5 border border-skin-border text-skin-text font-bold uppercase text-[10px] rounded hover:bg-skin-accent hover:text-white transition-colors">
                                    RSVP
                                </button>
                            {/if}
                        </div>
                    </div>
                </div>
            </div>
        {/each}

        {#if events.length === 0}
            <div class="col-span-full p-12 text-center border-2 border-dashed border-skin-border rounded-xl">
                <div class="text-4xl mb-2">📅</div>
                <div class="font-bold text-skin-muted uppercase tracking-widest text-xs">No Upcoming Events</div>
            </div>
        {/if}
    </div>
{/if}