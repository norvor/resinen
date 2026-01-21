<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';

    export let communityId: string;

    let video: any = null;
    let loading = true;

    // Fallback Mock
    const MOCK_VIDEO = {
        title: 'Campus Tour 2026',
        author_name: 'Media Team',
        thumbnail_url: null // Will fallback to gradient
    };

    onMount(async () => {
        try {
            const feed = await api.getStageFeed(communityId);
            video = feed[0] || null;
        } catch {
            video = null;
        } finally {
            loading = false;
        }
    });
</script>

<div class="h-full w-full">
    {#if loading}
        <div class="h-full bg-black animate-pulse rounded-2xl"></div>
    {:else if video || MOCK_VIDEO}
        {@const v = video || MOCK_VIDEO}
        
        <div class="h-full bg-black rounded-2xl border border-zinc-800 relative overflow-hidden group cursor-pointer">
            
            {#if v.thumbnail_url}
                <img src={v.thumbnail_url} alt="Cover" class="absolute inset-0 w-full h-full object-cover opacity-60 group-hover:opacity-80 transition-opacity" />
            {:else}
                <div class="absolute inset-0 bg-gradient-to-br from-purple-900 to-blue-900 opacity-60"></div>
            {/if}

            <div class="absolute inset-0 bg-gradient-to-t from-black via-transparent to-black/50"></div>

            <div class="absolute top-4 left-4 flex items-center gap-2 z-20">
                <span class="w-2 h-2 bg-red-600 rounded-full animate-pulse"></span>
                <span class="text-[9px] font-black text-white uppercase tracking-widest">
                    Stage
                </span>
            </div>

            <div class="absolute inset-0 flex items-center justify-center z-20 opacity-0 group-hover:opacity-100 transition-all duration-300 transform scale-50 group-hover:scale-100">
                <div class="w-12 h-12 bg-white rounded-full flex items-center justify-center shadow-lg">
                    <div class="w-0 h-0 border-t-[6px] border-t-transparent border-l-[10px] border-l-black border-b-[6px] border-b-transparent ml-1"></div>
                </div>
            </div>

            <div class="absolute bottom-4 left-4 right-4 z-20">
                <p class="text-[9px] font-bold text-zinc-400 uppercase mb-1">Now Playing</p>
                <h3 class="text-white font-bold leading-tight line-clamp-2 text-sm">
                    {v.title}
                </h3>
            </div>

            <div class="absolute inset-0 pointer-events-none opacity-10 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] z-10 background-size-[100%_2px,3px_100%]"></div>
        </div>
    {:else}
        <div class="h-full bg-zinc-900 rounded-2xl border border-zinc-800 flex items-center justify-center flex-col text-zinc-600">
            <span class="text-2xl mb-1">📺</span>
            <span class="text-[10px] font-mono uppercase">Off Air</span>
        </div>
    {/if}
</div>