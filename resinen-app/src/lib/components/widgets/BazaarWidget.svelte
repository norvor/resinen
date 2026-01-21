<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';

    export let communityId: string;

    let item: any = null;
    let loading = true;
    let vouching = false;

    // Fallback Mock
    const MOCK_ITEM = {
        id: 'demo',
        title: 'Gaming Laptop (Used)',
        price: '$450',
        seller_name: 'Alex',
        trust_score: 12
    };

    onMount(async () => {
        try {
            const listings = await api.getListings(communityId);
            item = listings[0] || null;
        } catch {
            item = null;
        } finally {
            loading = false;
        }
    });

    async function handleVouch() {
        if (!item) return;
        vouching = true;
        try {
            await api.vouchListing(item.id);
            item.trust_score += 1;
        } catch (e) {
            alert("Vouch failed.");
        } finally {
            vouching = false;
        }
    }
</script>

<div class="h-full w-full">
    {#if loading}
        <div class="h-full bg-orange-50 animate-pulse rounded-2xl"></div>
    {:else if item || MOCK_ITEM}
        {@const i = item || MOCK_ITEM}
        
        <div class="h-full bg-white border-2 border-orange-200 rounded-2xl p-5 flex flex-col justify-between relative group hover:shadow-lg transition-all duration-300">
            
            <div class="absolute -top-3 left-1/2 -translate-x-1/2 w-4 h-4 bg-white border-2 border-orange-200 rounded-full z-20"></div>
            <div class="absolute -top-10 left-1/2 -translate-x-1/2 w-[2px] h-10 bg-orange-300 z-10"></div>

            <div class="relative z-10 mt-2">
                <div class="flex justify-between items-start">
                    <span class="text-[9px] font-black uppercase text-orange-400 tracking-widest">For Sale</span>
                    <span class="text-lg font-black text-green-600 bg-green-50 px-2 py-0.5 rounded border border-green-200">
                        {i.price}
                    </span>
                </div>
                
                <h3 class="mt-2 text-xl font-bold text-zinc-800 leading-tight line-clamp-2">
                    {i.title}
                </h3>
                
                <div class="mt-2 flex items-center gap-2 text-[10px] text-zinc-400 font-bold uppercase">
                    <span>Seller: {i.seller_name}</span>
                </div>
            </div>

            <div class="relative z-10 pt-4 mt-auto border-t border-dashed border-orange-200 flex justify-between items-center">
                <div class="flex flex-col">
                    <span class="text-[9px] font-bold text-zinc-400 uppercase">Trust Score</span>
                    <span class="text-sm font-black text-zinc-800">🛡️ {i.trust_score}</span>
                </div>
                
                <button 
                    on:click={handleVouch}
                    disabled={vouching}
                    class="px-3 py-1.5 bg-orange-100 text-orange-700 text-[9px] font-black uppercase rounded hover:bg-orange-500 hover:text-white transition-colors"
                >
                    {vouching ? '...' : 'Vouch'}
                </button>
            </div>
            
        </div>
    {:else}
        <div class="h-full bg-zinc-50 rounded-2xl border-2 border-dashed border-zinc-200 flex items-center justify-center flex-col text-zinc-400">
            <span class="text-2xl mb-1">🏷️</span>
            <span class="text-[10px] font-bold uppercase">Sold Out</span>
        </div>
    {/if}
</div>