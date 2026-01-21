<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    import { fly, scale, fade } from 'svelte/transition';
    import type { Community, User } from '$lib/types';

    export let community: Community;
    export let currentUser: User | null;

    interface ClubEvent {
        id: string;
        name: string;
        location: string;
        start_time: string;
        image?: string;
        image_url?: string;
        going_count: number;
        my_rsvp: 'going' | 'not_going' | 'maybe' | null;
        description: string;
    }

    // --- STATE ---
    let events: ClubEvent[] = [];
    let loading = true;
    let selectedEvent: ClubEvent | null = null; // For the Ticket View
    let rsvpLoading = false;
    let error: string | null = null;

    onMount(async () => {
        if (!community?.id) return;
        try {
            // Fetch real events
            const res = await api.getEvents(community.id);
            events = Array.isArray(res) ? res : (res as any).items || [];
        } catch (e) {
            console.error("Club Offline:", e);
            error = "Could not load the calendar.";
        } finally {
            loading = false;
        }
    });

    async function handleRSVP(status: 'going' | 'not_going') {
        if (!selectedEvent) return;
        rsvpLoading = true;
        
        // Optimistic State Capture (to revert if needed)
        const previousStatus = selectedEvent.my_rsvp;
        const previousCount = selectedEvent.going_count;

        try {
            // 1. Optimistic Update
            if (status === 'going' && previousStatus !== 'going') {
                selectedEvent.going_count++;
            } else if (status === 'not_going' && previousStatus === 'going') {
                selectedEvent.going_count = Math.max(0, selectedEvent.going_count - 1);
            }
            selectedEvent.my_rsvp = status;
            events = events; // Trigger reactivity

            // 2. API Call
            await api.rsvpEvent(selectedEvent.id, status);

        } catch (e) {
            console.error("RSVP Failed", e);
            // Revert
            if (selectedEvent) {
                selectedEvent.my_rsvp = previousStatus;
                selectedEvent.going_count = previousCount;
                events = events;
            }
            alert("Could not update RSVP.");
        } finally {
            rsvpLoading = false;
        }
    }

    function getDateParts(isoString: string) {
        const d = new Date(isoString);
        return {
            month: d.toLocaleDateString(undefined, { month: 'short' }).toUpperCase(),
            day: d.getDate(),
            time: d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })
        };
    }
</script>

<div class="max-w-7xl mx-auto pb-20 px-4 space-y-12">

    <div class="relative py-12 flex flex-col items-center justify-center text-center overflow-hidden rounded-3xl bg-black">
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[120%] h-[120%] bg-gradient-to-tr from-purple-900 via-black to-pink-900 opacity-50 blur-3xl"></div>
        
        <div class="relative z-10">
            <h2 class="text-6xl md:text-8xl font-black uppercase tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 animate-pulse-slow">
                Nightlife
            </h2>
            <p class="text-zinc-400 font-mono font-bold uppercase tracking-[0.5em] mt-2">
                Upcoming Socials
            </p>
        </div>
    </div>

    {#if loading}
        <div class="flex justify-center py-20 animate-pulse text-zinc-300 font-black tracking-widest text-xl">
            PRINTING TICKETS...
        </div>
    {:else if error}
         <div class="flex justify-center py-20 text-red-400 font-black tracking-widest text-xl uppercase">
            {error}
        </div>
    {:else if events.length === 0}
         <div class="text-center py-20 border-2 border-dashed border-zinc-200 rounded-3xl text-zinc-400">
            <span class="text-6xl block mb-4">🗓️</span>
            <span class="font-bold uppercase tracking-widest">No Events Scheduled</span>
        </div>
    {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {#each events as event, i}
                {@const date = getDateParts(event.start_time)}
                
                <div 
                    class="group relative bg-white rounded-2xl overflow-hidden shadow-xl cursor-pointer hover:-translate-y-2 transition-transform duration-300"
                    in:fly={{ y: 50, delay: i * 100 }}
                    on:click={() => selectedEvent = event}
                >
                    <div class="h-64 relative overflow-hidden">
                        <img 
                            src={event.image_url || event.image || '/placeholder_event.jpg'} 
                            alt={event.name} 
                            class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700 filter group-hover:brightness-110" 
                        />
                        <div class="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent"></div>
                        
                        <div class="absolute top-4 left-4 bg-white/10 backdrop-blur-md border border-white/20 rounded-lg p-2 text-center min-w-[60px]">
                            <div class="text-[10px] font-black text-white uppercase tracking-widest">{date.month}</div>
                            <div class="text-2xl font-black text-white leading-none">{date.day}</div>
                        </div>

                        <div class="absolute top-4 right-4 bg-black/60 backdrop-blur-md text-white px-3 py-1 rounded-full text-xs font-bold flex items-center gap-2">
                            <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                            {event.going_count} Going
                        </div>

                        {#if event.my_rsvp === 'going'}
                            <div class="absolute bottom-4 right-4 rotate-[-10deg] bg-green-500 text-black border-2 border-black font-black uppercase text-sm px-4 py-1 shadow-[4px_4px_0px_black]">
                                I'm In!
                            </div>
                        {/if}
                    </div>

                    <div class="p-6 relative">
                        <div class="absolute -top-3 left-0 right-0 h-6 bg-[url('https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Dotted_line.svg/2000px-Dotted_line.svg.png')] bg-repeat-x opacity-20 bg-contain"></div>

                        <h3 class="text-2xl font-black uppercase leading-tight mb-2 group-hover:text-pink-600 transition-colors">
                            {event.name}
                        </h3>
                        <div class="flex items-center gap-2 text-sm font-bold text-zinc-500 mb-4">
                            <span>📍 {event.location}</span>
                            <span>•</span>
                            <span>{date.time}</span>
                        </div>
                        
                        <div class="w-full py-3 bg-zinc-100 text-zinc-400 font-black uppercase text-center rounded-xl group-hover:bg-black group-hover:text-white transition-colors tracking-widest text-xs">
                            View Ticket
                        </div>
                    </div>
                </div>
            {/each}
        </div>
    {/if}

    {#if selectedEvent}
        {@const d = getDateParts(selectedEvent.start_time)}
        
        <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/90 backdrop-blur-sm" transition:fade>
            
            <div 
                class="bg-[#f0f0f0] w-full max-w-md rounded-3xl overflow-hidden shadow-2xl relative flex flex-col md:flex-row"
                in:scale={{ start: 0.9, duration: 300 }}
            >
                <button on:click={() => selectedEvent = null} class="absolute top-4 right-4 z-20 w-8 h-8 bg-black/10 rounded-full flex items-center justify-center hover:bg-black hover:text-white transition-colors">✕</button>

                <div class="relative w-full md:w-2/3 bg-white p-8 border-r-2 border-dashed border-zinc-300">
                    <div class="absolute -top-4 right-[-10px] w-6 h-6 bg-black rounded-full z-10"></div>
                    <div class="absolute -bottom-4 right-[-10px] w-6 h-6 bg-black rounded-full z-10"></div>

                    <div class="flex justify-between items-start mb-8">
                        <div>
                            <div class="text-[10px] font-black uppercase text-zinc-400 tracking-widest">Admit One</div>
                            <h2 class="text-3xl font-black uppercase text-black leading-none mt-2">{selectedEvent.name}</h2>
                        </div>
                    </div>

                    <div class="space-y-4 font-mono text-sm">
                        <div class="flex justify-between border-b border-zinc-100 pb-2">
                            <span class="text-zinc-400">Date</span>
                            <span class="font-bold">{d.month} {d.day}</span>
                        </div>
                        <div class="flex justify-between border-b border-zinc-100 pb-2">
                            <span class="text-zinc-400">Time</span>
                            <span class="font-bold">{d.time}</span>
                        </div>
                        <div class="flex justify-between border-b border-zinc-100 pb-2">
                            <span class="text-zinc-400">Venue</span>
                            <span class="font-bold">{selectedEvent.location}</span>
                        </div>
                    </div>

                    <div class="mt-8 flex gap-3">
                        <button 
                            on:click={() => handleRSVP('going')}
                            disabled={rsvpLoading}
                            class="flex-1 py-3 rounded-xl font-black uppercase text-sm border-2 border-black shadow-[4px_4px_0px_black] active:translate-y-1 active:shadow-none transition-all
                            {selectedEvent.my_rsvp === 'going' ? 'bg-green-400 text-black' : 'bg-white hover:bg-black hover:text-white'}"
                        >
                            {selectedEvent.my_rsvp === 'going' ? 'Going' : 'RSVP Yes'}
                        </button>
                        
                        {#if selectedEvent.my_rsvp !== 'going'}
                            <button 
                                on:click={() => handleRSVP('not_going')}
                                class="px-4 py-3 rounded-xl font-bold uppercase text-sm border-2 border-zinc-200 text-zinc-400 hover:text-black hover:border-black transition-colors"
                            >
                                No
                            </button>
                        {/if}
                    </div>
                </div>

                <div class="relative w-full md:w-1/3 bg-zinc-100 p-6 flex flex-col items-center justify-center text-center">
                    <div class="text-[10px] font-black text-zinc-400 uppercase tracking-widest mb-4 rotate-90 md:rotate-0">
                        Scan for Entry
                    </div>
                    
                    <div class="w-24 h-24 bg-white p-2 rounded-lg shadow-sm">
                        <div class="w-full h-full bg-[url('https://upload.wikimedia.org/wikipedia/commons/d/d0/QR_code_for_mobile_English_Wikipedia.svg')] bg-cover opacity-80 mix-blend-multiply"></div>
                    </div>

                    <div class="mt-4 text-[9px] font-mono text-zinc-400">
                        ID: {selectedEvent.id}-{currentUser?.id.substring(0,4) || 'GUEST'}
                    </div>
                </div>

            </div>
        </div>
    {/if}

</div>

<style>
    @keyframes pulse-slow {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    .animate-pulse-slow {
        animation: pulse-slow 3s ease-in-out infinite;
    }
</style>