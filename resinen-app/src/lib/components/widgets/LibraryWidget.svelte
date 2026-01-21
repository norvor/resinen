<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';

    export let communityId: string;

    let page: any = null;
    let loading = true;

    // Fallback Mock
    const MOCK_PAGE = {
        title: 'The History of 2024',
        slug: 'history-2024',
        updated_at: new Date(),
        read_time: '5 min'
    };

    onMount(async () => {
        try {
            // Get the tree and pick a random or first page
            const tree = await api.getPageTree(communityId);
            if (tree.length > 0) {
                // Flatten tree slightly to find a leaf node if possible, for now just take root
                page = tree[0]; 
            }
        } catch {
            page = null;
        } finally {
            loading = false;
        }
    });
</script>

<div class="h-full w-full">
    {#if loading}
        <div class="h-full bg-[#fdfbf7] animate-pulse rounded-2xl border border-stone-200"></div>
    {:else if page || MOCK_PAGE}
        {@const p = page || MOCK_PAGE}
        
        <div class="h-full bg-[#fdfbf7] border border-stone-300 rounded-2xl p-6 flex flex-col justify-between relative shadow-sm group hover:-translate-y-1 hover:shadow-md transition-all duration-300">
            
            <div class="absolute bottom-4 left-1/2 -translate-x-1/2 w-3 h-3 bg-stone-200 rounded-full shadow-inner border border-stone-300"></div>

            <div class="relative z-10 border-b-2 border-red-100 pb-2 mb-2">
                <div class="flex justify-between items-end">
                    <span class="text-[9px] font-serif font-bold text-stone-500 italic">
                        Ref. {Math.floor(Math.random() * 900) + 100}.{Math.floor(Math.random() * 99)}
                    </span>
                    <span class="text-[9px] font-black uppercase text-stone-400">
                        Library
                    </span>
                </div>
            </div>

            <div class="relative z-10 flex-1">
                <h3 class="text-xl font-serif font-bold text-stone-900 leading-tight">
                    {p.title}
                </h3>
                <p class="text-[10px] text-stone-500 mt-2 font-mono">
                    Last access: {new Date().toLocaleDateString()}
                </p>
            </div>

            <div class="relative z-10 mt-4 flex justify-end">
                <button class="text-[10px] font-black uppercase border-b border-black hover:text-red-600 hover:border-red-600 transition-colors">
                    Read Entry ->
                </button>
            </div>

            <div class="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cardboard-flat.png')] opacity-10 pointer-events-none rounded-2xl"></div>
        </div>
    {:else}
        <div class="h-full bg-stone-50 rounded-2xl border-2 border-dashed border-stone-200 flex items-center justify-center flex-col text-stone-400">
            <span class="text-2xl mb-1">📚</span>
            <span class="text-[10px] font-bold uppercase">Archive Empty</span>
        </div>
    {/if}
</div>