<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';

    export let communityId: string;

    let messageCount = 0;
    let latestDrop: any = null;
    let loading = true;

    // Fallback Mock
    const MOCK_DROP = {
        is_anonymous: true,
        ttl_seconds: 3600,
        content: "The exams are being moved to Tuesday..."
    };

    onMount(async () => {
        try {
            const msgs = await api.getBunkerMessages(communityId);
            messageCount = msgs.length;
            latestDrop = msgs[0] || null;
        } catch {
            latestDrop = null;
        } finally {
            loading = false;
        }
    });
</script>

<div class="h-full w-full">
    {#if loading}
        <div class="h-full bg-zinc-800 animate-pulse rounded-2xl"></div>
    {:else if latestDrop || MOCK_DROP}
        {@const d = latestDrop || MOCK_DROP}
        
        <div class="h-full bg-[#111] border border-zinc-700 rounded-2xl p-5 flex flex-col justify-between relative overflow-hidden group hover:border-red-900 transition-colors cursor-pointer">
            
            <div class="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] opacity-20"></div>

            <div class="relative z-10 flex justify-between items-start">
                <span class="text-[9px] font-mono text-red-500 animate-pulse">
                    ● ENCRYPTED_CHANNEL
                </span>
                <span class="text-[9px] font-mono text-zinc-500">
                    TTL: {Math.floor(d.ttl_seconds / 60)}m
                </span>
            </div>

            <div class="relative z-10 mt-2 flex-1 flex flex-col justify-center">
                <div class="space-y-2 select-none group-hover:opacity-80 transition-opacity">
                    <div class="h-3 bg-zinc-800 w-3/4 rounded-sm"></div>
                    <div class="h-3 bg-zinc-800 w-full rounded-sm"></div>
                    <div class="h-3 bg-zinc-800 w-1/2 rounded-sm"></div>
                </div>
                
                <div class="absolute inset-0 flex items-center justify-center opacity-30 group-hover:opacity-10 pointer-events-none transition-opacity">
                    <span class="border-4 border-red-800 text-red-800 font-black text-2xl uppercase p-2 -rotate-12">
                        Classified
                    </span>
                </div>
            </div>

            <div class="relative z-10 pt-3 border-t border-zinc-800 flex justify-between items-center">
                <span class="text-[9px] font-mono text-zinc-500">
                    SENDER: {d.is_anonymous ? 'UNKNOWN' : 'VERIFIED'}
                </span>
                <span class="text-[9px] font-bold text-white uppercase border border-zinc-600 px-2 py-1 rounded hover:bg-white hover:text-black transition-colors">
                    Decrypt
                </span>
            </div>

        </div>
    {:else}
        <div class="h-full bg-zinc-900 rounded-2xl border border-zinc-800 flex items-center justify-center flex-col text-zinc-600">
            <span class="text-2xl mb-1">🔇</span>
            <span class="text-[10px] font-mono uppercase">Channel Silent</span>
        </div>
    {/if}
</div>