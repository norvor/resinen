<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';

    export let communityId: string;

    let event: any = null;
    let loading = true;
    let rsvpStatus: string | null = null;

    // Fallback Mock
    const MOCK_EVENT = {
        id: 'demo',
        name: 'Midnight Rooftop Mixer',
        location: 'The Quad',
        start_time: new Date(),
        count_going: 42
    };

    onMount(async () => {
        try {
            const events = await api.getEvents(communityId);
            // Get first future event
            event = events.find((e: any) => new Date(e.start_time) > new Date()) || null;
            if (event) rsvpStatus = event.my_rsvp;
        } catch {
            event = null;
        } finally {
            loading = false;
        }
    });

    async function rsvp(status: 'going' | 'not_going') {
        if (!event) return;
        const oldStatus = rsvpStatus;
        rsvpStatus = status; // Optimistic
        
        try {
            await api.rsvpEvent(event.id, status);
        } catch (e) {
            rsvpStatus = oldStatus; // Revert
            alert("RSVP failed.");
        }
    }
</script>

<div class="h-full w-full relative group">
    {#if loading}
        <div class="h-full bg-pink-50 animate-pulse rounded-2xl"></div>
    {:else if event || MOCK_EVENT}
        {@const e = event || MOCK_EVENT}
        
        <div class="h-full bg-pink-500 text-white p-5 flex flex-col justify-between relative overflow-hidden shadow-md transform rotate-1 group-hover:rotate-0 transition-transform duration-300">
            
            <div class="absolute top-2 left-1/2 -translate-x-1/2 w-8 h-2 bg-zinc-400 shadow-sm rounded-full z-20"></div>

            <div class="relative z-10 mt-2">
                <div class="flex justify-between items-start">
                    <span class="text-[9px] font-black uppercase bg-white text-pink-600 px-1.5 py-0.5 transform -rotate-2">
                        Next Event
                    </span>
                    <span class="text-[9px] font-mono font-bold">
                        {new Date(e.start_time).toLocaleDateString(undefined, {month:'short', day:'numeric'})}
                    </span>
                </div>
                
                <h3 class="mt-2 text-2xl font-black uppercase leading-none break-words text-shadow-sm">
                    {e.name}
                </h3>
                <p class="text-[10px] font-bold uppercase mt-1 opacity-90 flex items-center gap-1">
                    <span>📍</span> {e.location}
                </p>
            </div>

            <div class="relative z-10 mt-4 border-t-2 border-white/20 pt-3 flex justify-between items-center">
                <div class="text-[9px] font-black uppercase">
                    {e.count_going} Going
                </div>
                
                <div class="flex gap-2">
                    <button 
                        on:click={() => rsvp('going')}
                        class="px-3 py-1 bg-white text-pink-600 text-[9px] font-black uppercase rounded hover:bg-black hover:text-white transition-colors {rsvpStatus === 'going' ? 'bg-black text-white' : ''}"
                    >
                        I'm In
                    </button>
                    {#if !rsvpStatus}
                        <button 
                            on:click={() => rsvp('not_going')}
                            class="px-2 py-1 border border-white/50 text-white text-[9px] font-black uppercase rounded hover:bg-white/10"
                        >
                            Nah
                        </button>
                    {/if}
                </div>
            </div>

            <div class="absolute bottom-0 left-0 right-0 h-4 bg-[#f0f0f4]" 
                 style="mask-image: radial-gradient(circle 6px at bottom, transparent 4px, black 5px); mask-size: 12px 100%; -webkit-mask-image: radial-gradient(circle 6px at bottom, transparent 4px, black 5px); -webkit-mask-size: 12px 100%;">
            </div>
        </div>
    {:else}
        <div class="h-full bg-zinc-50 rounded-2xl border-2 border-dashed border-zinc-200 flex items-center justify-center flex-col text-zinc-400">
            <span class="text-2xl mb-1">🎉</span>
            <span class="text-[10px] font-bold uppercase">No Parties</span>
        </div>
    {/if}
</div>

<style>
    .text-shadow-sm { text-shadow: 2px 2px 0px rgba(0,0,0,0.1); }
</style>