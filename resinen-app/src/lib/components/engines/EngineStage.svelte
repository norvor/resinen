<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    export let community: any;

    let videos: any[] = [];
    let loading = true;
    let activeVideoId: string | null = null;

    onMount(async () => {
        try {
            videos = await api.getStageFeed(community.id);
        } catch (e) {
            console.error(e);
        } finally {
            loading = false;
        }
    });

    function playVideo(id: string) {
        activeVideoId = id;
        // In a real app, this would trigger the HTML video play() method
    }
</script>

{#if loading}
    <div class="p-8 text-center animate-pulse text-skin-muted font-bold uppercase">Loading Stage...</div>
{:else}
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {#each videos as v}
            <div class="relative aspect-[9/16] bg-black rounded-xl overflow-hidden group shadow-lg border border-skin-border/50">
                
                {#if activeVideoId === v.id}
                    <video 
                        src={v.video_url} 
                        autoplay 
                        controls 
                        loop 
                        class="w-full h-full object-cover"
                    ></video>
                {:else}
                    <img src={v.thumbnail_url} alt="Thumbnail" class="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity duration-500" />
                    
                    <button 
                        on:click={() => playVideo(v.id)}
                        class="absolute inset-0 flex items-center justify-center bg-black/20 group-hover:bg-black/0 transition-all"
                    >
                        <div class="w-12 h-12 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center border border-white/40 group-hover:scale-110 transition-transform">
                            <span class="text-white text-xl ml-1">▶</span>
                        </div>
                    </button>
                {/if}

                <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 via-black/50 to-transparent pt-12 pb-4 px-4 pointer-events-none">
                    <h3 class="text-white font-bold text-sm leading-tight mb-1 shadow-black drop-shadow-md">{v.title || 'Untitled'}</h3>
                    
                    <div class="flex items-center gap-2 mb-2">
                        {#if v.author_avatar}
                            <img src={v.author_avatar} alt="Avatar" class="w-5 h-5 rounded-full border border-white/50" />
                        {/if}
                        <span class="text-xs text-white/90 font-medium shadow-black drop-shadow-sm">{v.author_name}</span>
                    </div>

                    <div class="flex items-center justify-between text-xs text-white/80 font-bold font-mono">
                        <div class="flex items-center gap-1">
                            <span>👁</span> {v.view_count}
                        </div>
                        <div class="flex items-center gap-1">
                            <span>♥</span> {v.like_count}
                        </div>
                    </div>
                </div>

            </div>
        {/each}

        {#if videos.length === 0}
            <div class="col-span-full py-20 text-center border-2 border-dashed border-skin-border rounded-xl">
                <div class="text-4xl mb-2">🎬</div>
                <div class="font-bold text-skin-muted uppercase tracking-widest text-xs">Stage is Empty</div>
            </div>
        {/if}
    </div>
{/if}