<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    import { fly, fade, scale } from 'svelte/transition';
    import type { Community, User } from '$lib/types';

    export let community: Community;
    export let currentUser: User | null;

    // Define local interface for strict typing
    interface Listing {
        id: string;
        title: string;
        brand: string;
        price: string;
        image?: string;     // Handle variations in API naming
        image_url?: string; 
        link: string;
        vouches: number;
        verified: boolean;
        description: string;
    }

    // --- STATE ---
    let items: Listing[] = [];
    let loading = true;
    let wishlist = new Set<string>(); 
    let view: 'all' | 'wishlist' = 'all';
    let selectedItem: Listing | null = null;
    let error: string | null = null;

    onMount(async () => {
        if (!community?.id) return;

        try {
            // Fetch real listings from the backend
            const res = await api.getListings(community.id);
            // Handle array vs pagination wrapper
            items = Array.isArray(res) ? res : (res as any).items || [];
        } catch (e) {
            console.error("Bazaar Load Failed:", e);
            error = "Marketplace offline.";
        } finally {
            loading = false;
        }
    });

    function toggleWishlist(e: Event, id: string) {
        e.stopPropagation();
        if (wishlist.has(id)) wishlist.delete(id);
        else wishlist.add(id);
        wishlist = wishlist; // Trigger reactivity
    }

    async function handleVouch(e: Event, item: Listing) {
        e.stopPropagation();
        
        // Optimistic UI update
        item.vouches += 1;
        items = items; // Trigger reactivity

        try {
            await api.vouchListing(item.id);
        } catch (e) {
            console.error(e);
            // Revert on failure
            item.vouches -= 1;
            items = items;
        }
    }
</script>

<div class="relative w-full h-full min-h-screen bg-zinc-50">

    <div class="absolute top-6 right-6 z-40 flex flex-col items-end gap-2">
        <div class="bg-white/80 backdrop-blur-md border border-white/20 shadow-xl rounded-full p-1.5 flex gap-1 transition-all hover:scale-105 hover:bg-white">
            
            <button 
                on:click={() => view = 'all'}
                class="px-5 py-2.5 rounded-full text-xs font-black uppercase transition-all flex items-center gap-2 {view === 'all' ? 'bg-zinc-900 text-white shadow-lg' : 'text-zinc-500 hover:bg-zinc-100 hover:text-black'}"
            >
                <span>Discovery</span>
            </button>
            
            <button 
                on:click={() => view = 'wishlist'}
                class="px-5 py-2.5 rounded-full text-xs font-black uppercase transition-all flex items-center gap-2 {view === 'wishlist' ? 'bg-red-500 text-white shadow-lg' : 'text-zinc-500 hover:bg-red-50 hover:text-red-500'}"
            >
                <span>Wishlist</span>
                {#if wishlist.size > 0}
                    <span class="bg-white/20 px-1.5 rounded-full text-[9px]">{wishlist.size}</span>
                {/if}
            </button>

        </div>
    </div>

    {#if loading}
        <div class="w-full h-screen flex items-center justify-center">
            <div class="animate-pulse font-black text-zinc-300 tracking-[0.5em] text-2xl">LOADING ASSETS</div>
        </div>
    
    {:else if error}
        <div class="w-full h-[50vh] flex flex-col items-center justify-center">
            <div class="text-4xl mb-4">⚠️</div>
            <div class="font-black uppercase text-red-400">{error}</div>
        </div>

    {:else}
        
        {@const visibleItems = view === 'wishlist' ? items.filter(i => wishlist.has(i.id)) : items}

        {#if visibleItems.length === 0}
            <div class="w-full h-[80vh] flex flex-col items-center justify-center opacity-40">
                <div class="text-8xl mb-6 grayscale">
                    {view === 'wishlist' ? '🔖' : '📦'}
                </div>
                <h3 class="font-black uppercase text-2xl text-zinc-400">
                    {view === 'wishlist' ? 'Wishlist Empty' : 'Inventory Empty'}
                </h3>
                <p class="text-zinc-500 font-bold mt-2">
                    {view === 'wishlist' ? 'Save items from the Discovery feed.' : 'No items listed in this territory.'}
                </p>
            </div>
        {:else}
            <div class="w-full p-4 columns-1 sm:columns-2 md:columns-3 lg:columns-4 xl:columns-5 gap-4 space-y-4">
                
                {#each visibleItems as item (item.id)}
                    <div 
                        class="break-inside-avoid relative group rounded-xl overflow-hidden cursor-pointer bg-white transition-all duration-300 hover:shadow-2xl hover:-translate-y-1"
                        on:click={() => selectedItem = item}
                    >
                        <div class="relative bg-white overflow-hidden">
                            <img 
                                src={item.image_url || item.image || '/placeholder_product.png'} 
                                alt={item.title} 
                                class="w-full h-auto object-cover transition-transform duration-700 group-hover:scale-105" 
                            />
                            
                            <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
                                <span class="bg-white/20 backdrop-blur text-white px-4 py-2 rounded-full font-black uppercase text-xs border border-white/40 transform scale-90 group-hover:scale-100 transition-transform">
                                    View Item
                                </span>
                            </div>

                            <div class="absolute top-3 right-3 flex flex-col gap-2 translate-x-10 group-hover:translate-x-0 transition-transform duration-300 opacity-0 group-hover:opacity-100">
                                <button 
                                    on:click={(e) => toggleWishlist(e, item.id)}
                                    class="w-8 h-8 rounded-full flex items-center justify-center shadow-md transition-colors {wishlist.has(item.id) ? 'bg-red-500 text-white' : 'bg-white text-zinc-900 hover:bg-zinc-100'}"
                                >
                                    <span class="text-sm">{wishlist.has(item.id) ? '★' : '☆'}</span>
                                </button>
                                <a 
                                    href={item.link} 
                                    target="_blank"
                                    on:click|stopPropagation
                                    class="w-8 h-8 rounded-full bg-white flex items-center justify-center shadow-md text-zinc-900 hover:bg-blue-500 hover:text-white transition-colors"
                                >
                                    ↗
                                </a>
                            </div>

                            {#if item.verified}
                                <div class="absolute top-3 left-3 bg-blue-600/90 backdrop-blur px-2 py-0.5 rounded text-[9px] font-black uppercase text-white shadow-sm">
                                    Verified
                                </div>
                            {/if}
                        </div>

                        <div class="p-4">
                            <div class="flex justify-between items-start">
                                <div>
                                    <h3 class="text-sm font-bold text-zinc-900 leading-tight group-hover:text-blue-600 transition-colors">
                                        {item.title}
                                    </h3>
                                    <p class="text-[10px] font-bold text-zinc-400 uppercase mt-0.5">{item.brand}</p>
                                </div>
                                <span class="text-xs font-mono font-black text-zinc-800 bg-zinc-100 px-1.5 py-0.5 rounded ml-2">
                                    {item.price}
                                </span>
                            </div>
                            
                            <div class="flex items-center justify-between mt-3 pt-3 border-t border-zinc-50">
                                <button 
                                    on:click={(e) => handleVouch(e, item)}
                                    class="flex items-center gap-1.5 text-[10px] font-bold text-zinc-400 hover:text-green-600 transition-colors"
                                >
                                    <span class="text-xs">▲</span> {item.vouches}
                                </button>
                                <span class="w-1 h-1 bg-zinc-200 rounded-full"></span>
                                <span class="text-[9px] text-zinc-300 font-bold uppercase">Curated</span>
                            </div>
                        </div>
                    </div>
                {/each}
            </div>
        {/if}
    {/if}


    {#if selectedItem}
        <div class="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-zinc-900/80 backdrop-blur-sm" transition:fade>
            <div 
                class="bg-white w-full max-w-4xl rounded-2xl shadow-2xl overflow-hidden flex flex-col md:flex-row h-auto max-h-[85vh]"
                in:scale={{ start: 0.95, duration: 250 }}
            >
                <div class="w-full md:w-1/2 bg-zinc-50 flex items-center justify-center p-8 relative">
                    <img src={selectedItem.image_url || selectedItem.image} alt={selectedItem.title} class="max-w-full max-h-[300px] md:max-h-full object-contain mix-blend-multiply" />
                    {#if selectedItem.verified}
                         <div class="absolute top-6 left-6 flex items-center gap-2">
                             <span class="bg-blue-600 text-white w-6 h-6 flex items-center justify-center rounded-full text-xs shadow-lg">✓</span>
                         </div>
                    {/if}
                </div>

                <div class="w-full md:w-1/2 p-8 md:p-10 flex flex-col overflow-y-auto bg-white relative">
                    <button on:click={() => selectedItem = null} class="absolute top-6 right-6 w-8 h-8 flex items-center justify-center bg-zinc-100 rounded-full hover:bg-zinc-200 transition-colors">✕</button>

                    <div class="mb-8">
                        <div class="text-xs font-black text-zinc-400 uppercase tracking-widest mb-2">{selectedItem.brand}</div>
                        <h2 class="text-4xl font-black text-zinc-900 leading-tight mb-3">{selectedItem.title}</h2>
                        <div class="inline-block bg-blue-50 text-blue-700 px-3 py-1 rounded text-xl font-mono font-bold">
                            {selectedItem.price}
                        </div>
                    </div>

                    <p class="text-zinc-600 leading-relaxed mb-8">
                        {selectedItem.description}
                    </p>

                    <div class="mt-auto space-y-3">
                        <a 
                            href={selectedItem.link} 
                            target="_blank"
                            class="flex items-center justify-center gap-2 w-full py-4 bg-black text-white rounded-xl font-black uppercase hover:bg-zinc-800 hover:scale-[1.01] transition-all shadow-lg"
                        >
                            <span>Buy on Store</span>
                            <span class="text-xs">↗</span>
                        </a>
                        
                        <button 
                            on:click={(e) => toggleWishlist(e, selectedItem!.id)}
                            class="w-full py-4 border-2 border-zinc-100 text-zinc-900 rounded-xl font-bold uppercase hover:border-zinc-300 transition-colors flex items-center justify-center gap-2"
                        >
                            <span class="text-lg">{wishlist.has(selectedItem.id) ? '★' : '☆'}</span>
                            <span>{wishlist.has(selectedItem.id) ? 'Saved to Wishlist' : 'Add to Wishlist'}</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    {/if}

</div>