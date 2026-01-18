<script lang="ts">
    import { page } from '$app/stores';
    import { onMount } from 'svelte';
    import { api, type User } from '$lib/api';
    import { goto } from '$app/navigation';

    // 1. Get Search Query from URL (e.g. ?q=fortress)
    let query = $page.url.searchParams.get('q') || '';
    
    let communities: any[] = [];
    let loading = true;
    let joiningId: string | null = null;

    onMount(async () => {
        await searchCommunities();
    });

    async function searchCommunities() {
        loading = true;
        try {
            // This calls GET /communities?q=...
            communities = await api.getCommunities(query);
        } catch (e) {
            console.error(e);
        } finally {
            loading = false;
        }
    }

    async function handleJoin(communityId: string, slug: string) {
        joiningId = communityId;
        try {
            // 1. Send Join Request AND wait for the answer
            const response = await api.joinCommunity(communityId);
            
            // 2. CHECK THE STATUS (The Gatekeeper Logic)
            if (response.membership_status === 'pending') {
                // CASE A: Private Community -> Stop here.
                alert("Your application is pending approval from the Gatekeeper.");
                
                // Optional: Refresh list to show "Pending" button state if you want
                await searchCommunities(); 
            } else {
                // CASE B: Open Community -> Enter.
                goto(`/communities/${slug}`);
            }

        } catch (e: any) {
            alert(e.message || "Failed to join territory");
        } finally {
            joiningId = null;
        }
    }

    function handleSearchInput() {
        // Debounce could go here, but simple works for now
        searchCommunities();
    }
</script>

<div class="min-h-screen bg-gray-100 p-4 md:p-8">
    <div class="max-w-6xl mx-auto">
        
        <div class="flex flex-col md:flex-row justify-between items-end mb-8 gap-4">
            <div>
                <h1 class="text-4xl font-black uppercase">World Map</h1>
                <p class="font-bold text-gray-500">Discover sovereign territories.</p>
            </div>
            
            <div class="w-full md:w-96 flex">
                <input 
                    bind:value={query}
                    on:input={handleSearchInput}
                    type="text" 
                    placeholder="Search territories..." 
                    class="w-full border-4 border-black p-3 font-bold outline-none uppercase placeholder:normal-case shadow-hard"
                />
            </div>
        </div>

        {#if loading}
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 animate-pulse">
                {#each Array(3) as _}
                    <div class="h-48 bg-gray-200 border-4 border-black/10"></div>
                {/each}
            </div>
        {:else if communities.length === 0}
            <div class="text-center py-20 border-4 border-dashed border-gray-300">
                <h2 class="text-xl font-black text-gray-400">No Territories Found</h2>
                <p class="text-gray-500 font-bold">The map is blank. Why not <a href="/communities/new" class="text-blue-600 underline">initialize one?</a></p>
            </div>
        {:else}
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {#each communities as comm}
                    <div class="bg-white border-4 border-black shadow-hard flex flex-col h-full group">
                        
                        <div class="h-24 bg-sp-blue relative overflow-hidden">
                            {#if comm.banner_url}
                                <img src={comm.banner_url} alt="Banner" class="w-full h-full object-cover opacity-50 grayscale group-hover:grayscale-0 transition-all" />
                            {/if}
                            <div class="absolute -bottom-6 left-4 w-12 h-12 bg-white border-4 border-black flex items-center justify-center font-black text-xl uppercase z-10">
                                {comm.name[0]}
                            </div>
                        </div>

                        <div class="p-4 pt-8 flex-grow">
                            <h3 class="font-black text-lg uppercase leading-none mb-1">{comm.name}</h3>
                            <div class="text-xs font-mono text-gray-400 mb-4">/{comm.slug}</div>
                            
                            <p class="text-sm font-bold text-gray-600 line-clamp-3 mb-4">
                                {comm.description || "A sovereign territory."}
                            </p>

                            <div class="flex flex-wrap gap-2 text-xs font-black uppercase">
                                <span class="bg-gray-100 px-2 py-1 border border-black/20">{comm.member_count} Citizens</span>
                                {#if comm.is_private}
                                    <span class="bg-yellow-100 px-2 py-1 border border-black/20 text-yellow-800">Private</span>
                                {:else}
                                    <span class="bg-green-100 px-2 py-1 border border-black/20 text-green-800">Open</span>
                                {/if}
                            </div>
                        </div>

                        <div class="p-4 border-t-4 border-black bg-gray-50">
                            <button 
                                on:click={() => handleJoin(comm.id, comm.slug)}
                                disabled={joiningId === comm.id}
                                class="w-full bg-black text-white font-black uppercase py-3 hover:bg-sp-green hover:text-black hover:shadow-none transition-all shadow-hard-sm disabled:opacity-50 disabled:cursor-wait"
                            >
                                {joiningId === comm.id ? 'Processing Visa...' : 'Join Territory'}
                            </button>
                        </div>
                    </div>
                {/each}
            </div>
        {/if}
    </div>
</div>