<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    export let community: any;

    let items: any[] = [];
    let loading = true;
    
    onMount(async () => {
        try {
            items = await api.getListings(community.id);
        } catch (e) {
            console.error(e);
        } finally {
            loading = false;
        }
    });

    async function vouch(id: string) {
        try {
            await api.vouchListing(id);
            // Optimistic update: increment count locally
            items = items.map(i => i.id === id ? {...i, vouch_count: i.vouch_count + 1} : i);
        } catch (e) {
            alert("Could not vouch. Try again.");
        }
    }
</script>

{#if loading}
    <div class="p-8 text-center animate-pulse text-skin-muted font-bold uppercase">Loading Market...</div>
{:else}
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        {#each items as item}
            <div class="skin-card p-4 flex gap-4 hover:border-skin-accent transition-colors group">
                <div class="w-24 h-24 bg-skin-surface border border-skin-border flex items-center justify-center shrink-0 overflow-hidden">
                    {#if item.image_url}
                        <img src={item.image_url} alt="Item" class="w-full h-full object-cover"/>
                    {:else}
                        <span class="text-2xl opacity-50">📦</span>
                    {/if}
                </div>
                
                <div class="flex-1 min-w-0 flex flex-col justify-between">
                    <div>
                        <div class="flex justify-between items-start">
                            <h3 class="font-bold truncate pr-2 text-skin-text">{item.title}</h3>
                            <span class="text-skin-accent font-black text-sm whitespace-nowrap">{item.price_display}</span>
                        </div>
                        <div class="text-[10px] uppercase font-bold text-skin-muted mb-1 truncate tracking-wider">{item.domain}</div>
                        <p class="text-xs opacity-70 line-clamp-2 leading-relaxed">{item.description}</p>
                    </div>
                    
                    <div class="flex gap-2 mt-3">
                        <a href={item.link_url} target="_blank" class="flex-1 text-center text-xs bg-skin-text text-skin-fill px-3 py-2 font-black uppercase hover:opacity-90 transition-opacity">
                            View Deal
                        </a>
                        <button on:click={() => vouch(item.id)} class="text-xs border border-skin-border px-3 py-2 font-bold uppercase hover:bg-skin-surface flex items-center gap-1 transition-colors">
                            <span class="text-skin-accent">▲</span> {item.vouch_count}
                        </button>
                    </div>
                </div>
            </div>
        {/each}
        
        {#if items.length === 0}
            <div class="col-span-full py-12 text-center border-2 border-dashed border-skin-border rounded-xl">
                <div class="text-4xl mb-2">🛍️</div>
                <div class="font-bold text-skin-muted uppercase tracking-widest text-xs">Market is Empty</div>
            </div>
        {/if}
    </div>
{/if}