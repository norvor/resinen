<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    import { scale, fade, fly } from 'svelte/transition';
    import type { Community, User } from '$lib/types';

    export let community: Community;
    export let currentUser: User | null;

    // --- TYPES ---
    interface VideoItem {
        id: string;
        platform: 'youtube' | 'tiktok' | 'instagram' | 'other';
        title: string;
        thumbnail: string;
        url: string; // The video ID or slug
        duration?: string;
    }

    interface VideoCategory {
        category: string;
        items: VideoItem[];
    }

    // --- STATE ---
    let catalog: VideoCategory[] = [];
    let heroVideo: VideoItem | null = null;
    let activeVideo: VideoItem | null = null; // Currently playing
    let hoveredVideoId: string | null = null;
    let loading = true;
    let error: string | null = null;

    onMount(async () => {
        if (!community?.id) return;
        try {
            const res = await api.getStageFeed(community.id);
            // Handle structure: backend might return flat list or categorized
            if (Array.isArray(res)) {
                // Check if it's already categorized or needs grouping
                if (res.length > 0 && 'items' in res[0]) {
                    catalog = res as VideoCategory[];
                } else {
                    // Fallback: Group flat list into one category
                    catalog = [{ category: "Recent Uploads", items: res as VideoItem[] }];
                }
            }
            
            // Set Hero Video
            if (catalog.length > 0 && catalog[0].items.length > 0) {
                heroVideo = catalog[0].items[0];
            }
        } catch (e) {
            console.error("Stage Offline:", e);
            error = "Broadcast signal lost.";
        } finally {
            loading = false;
        }
    });

    // --- HELPERS ---
    function getEmbedSrc(video: VideoItem) {
        if (!video) return '';
        switch (video.platform) {
            case 'youtube':
                return `https://www.youtube.com/embed/${video.url}?autoplay=1&rel=0&modestbranding=1`;
            case 'tiktok':
                return `https://www.tiktok.com/embed/v2/${video.url}`;
            case 'instagram':
                return `https://www.instagram.com/p/${video.url}/embed/captioned`;
            default:
                return '';
        }
    }

    function isVertical(platform: string) {
        return platform === 'tiktok' || platform === 'instagram';
    }
</script>

<div class="bg-[#141414] min-h-screen text-white overflow-x-hidden font-sans pb-20">

    {#if loading}
        <div class="h-screen flex items-center justify-center flex-col gap-4">
            <div class="w-12 h-12 border-4 border-red-600 border-t-transparent rounded-full animate-spin"></div>
            <div class="text-xs font-black uppercase tracking-widest text-zinc-500">Loading Stage...</div>
        </div>
    
    {:else if error}
        <div class="h-screen flex items-center justify-center flex-col gap-4 text-zinc-500">
            <div class="text-4xl">📡</div>
            <div class="text-xs font-black uppercase tracking-widest">{error}</div>
        </div>

    {:else if !heroVideo}
        <div class="h-screen flex items-center justify-center flex-col gap-4 text-zinc-500">
            <div class="text-4xl">🎬</div>
            <div class="text-xs font-black uppercase tracking-widest">No Content Available</div>
        </div>

    {:else}
        
        <div class="relative h-[70vh] w-full overflow-hidden">
            <div class="absolute inset-0">
                <img src={heroVideo.thumbnail} alt="Hero" class="w-full h-full object-cover opacity-60 mask-image-gradient" />
                <div class="absolute inset-0 bg-gradient-to-t from-[#141414] via-[#141414]/20 to-transparent"></div>
                <div class="absolute inset-0 bg-gradient-to-r from-[#141414] via-[#141414]/40 to-transparent"></div>
            </div>

            <div class="absolute bottom-0 left-0 w-full p-8 md:p-16 z-10 flex flex-col items-start gap-6">
                <div class="flex items-center gap-2">
                    <span class="bg-red-600 text-white text-[10px] font-black uppercase px-2 py-1 tracking-widest rounded-sm">
                        Featured Premiere
                    </span>
                    <span class="text-zinc-400 text-xs font-bold uppercase">• Trending Now</span>
                </div>
                
                <h1 class="text-5xl md:text-7xl font-black uppercase tracking-tighter leading-[0.9] max-w-3xl drop-shadow-2xl">
                    {heroVideo.title}
                </h1>
                
                <div class="flex items-center gap-4 mt-2">
                    <button 
                        on:click={() => activeVideo = heroVideo}
                        class="bg-white text-black px-8 py-3 rounded text-lg font-bold flex items-center gap-2 hover:bg-zinc-200 transition-colors"
                    >
                        <span>▶</span> Play Now
                    </button>
                    <button class="bg-[rgba(109,109,110,0.7)] text-white px-8 py-3 rounded text-lg font-bold flex items-center gap-2 hover:bg-[rgba(109,109,110,0.4)] transition-colors backdrop-blur-sm">
                        <span>ℹ</span> More Info
                    </button>
                </div>
            </div>
        </div>

        <div class="relative z-20 -mt-20 space-y-12 pl-8 md:pl-16 overflow-hidden">
            
            {#each catalog as section}
                <div class="section">
                    <h3 class="text-xl font-bold text-zinc-200 mb-4 flex items-center gap-2 group cursor-pointer">
                        {section.category}
                        <span class="text-xs text-blue-500 opacity-0 group-hover:opacity-100 transition-opacity -translate-x-2 group-hover:translate-x-0">
                            Explore All >
                        </span>
                    </h3>

                    <div class="flex gap-4 overflow-x-auto pb-8 pr-16 scrollbar-hide snap-x">
                        {#each section.items as video}
                            <div 
                                class="relative shrink-0 transition-all duration-300 snap-start cursor-pointer group/card
                                {isVertical(video.platform) ? 'w-[180px] h-[320px]' : 'w-[300px] h-[169px]'}"
                                on:click={() => activeVideo = video}
                                on:mouseenter={() => hoveredVideoId = video.id}
                                on:mouseleave={() => hoveredVideoId = null}
                            >
                                <img 
                                    src={video.thumbnail} 
                                    alt={video.title} 
                                    class="w-full h-full object-cover rounded-md group-hover/card:brightness-110 transition-all" 
                                />

                                <div class="absolute top-2 right-2 z-10">
                                    {#if video.platform === 'youtube'}
                                        <div class="bg-red-600 text-white text-[8px] font-black px-1.5 py-0.5 rounded uppercase">YT</div>
                                    {:else if video.platform === 'tiktok'}
                                        <div class="bg-black text-white border border-zinc-700 text-[8px] font-black px-1.5 py-0.5 rounded uppercase">TikTok</div>
                                    {:else}
                                        <div class="bg-gradient-to-tr from-yellow-400 to-purple-600 text-white text-[8px] font-black px-1.5 py-0.5 rounded uppercase">Reel</div>
                                    {/if}
                                </div>

                                <div class="absolute inset-0 bg-black/60 opacity-0 group-hover/card:opacity-100 transition-opacity duration-200 p-4 flex flex-col justify-end rounded-md">
                                    <div class="flex items-center gap-2 mb-2">
                                        <div class="w-8 h-8 rounded-full bg-white text-black flex items-center justify-center shadow-lg transform group-hover/card:scale-110 transition-transform">
                                            ▶
                                        </div>
                                    </div>
                                    <h4 class="font-bold text-sm leading-tight">{video.title}</h4>
                                    <p class="text-[10px] text-zinc-300 font-mono mt-1">{video.duration || '0:00'} • {video.platform}</p>
                                </div>
                            </div>
                        {/each}
                    </div>
                </div>
            {/each}

        </div>
    {/if}

    {#if activeVideo}
        <div class="fixed inset-0 z-50 bg-black/95 flex items-center justify-center p-4 md:p-10 backdrop-blur-xl" transition:fade>
            
            <div class="relative w-full max-w-6xl bg-black rounded-xl overflow-hidden shadow-2xl border border-zinc-800 flex flex-col h-full md:h-auto md:aspect-video" in:scale={{start: 0.9}}>
                
                <div class="absolute top-0 left-0 right-0 p-4 flex justify-between items-center z-20 bg-gradient-to-b from-black/80 to-transparent pointer-events-none">
                    <h3 class="font-bold text-lg pointer-events-auto">{activeVideo.title}</h3>
                    <button 
                        on:click={() => activeVideo = null} 
                        class="bg-zinc-800/80 hover:bg-zinc-700 text-white w-10 h-10 rounded-full flex items-center justify-center transition-colors pointer-events-auto"
                    >
                        ✕
                    </button>
                </div>

                <div class="flex-1 w-full h-full bg-black relative flex items-center justify-center">
                    {#if isVertical(activeVideo.platform)}
                        <div class="h-full aspect-[9/16] bg-black">
                            <iframe 
                                src={getEmbedSrc(activeVideo)} 
                                title={activeVideo.title}
                                class="w-full h-full border-none"
                                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                allowfullscreen
                            ></iframe>
                        </div>
                    {:else}
                        <iframe 
                            src={getEmbedSrc(activeVideo)} 
                            title={activeVideo.title}
                            class="w-full h-full border-none"
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                            allowfullscreen
                        ></iframe>
                    {/if}
                </div>

            </div>
        </div>
    {/if}

</div>

<style>
    /* Hide scrollbar but keep functionality */
    .scrollbar-hide::-webkit-scrollbar {
        display: none;
    }
    .scrollbar-hide {
        -ms-overflow-style: none;
        scrollbar-width: none;
    }
</style>