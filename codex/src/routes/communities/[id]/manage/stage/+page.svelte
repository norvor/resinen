<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api'; // Ensure you add stage methods to api.ts if missing
    import { fade, scale } from 'svelte/transition';

    export let data;
    $: community = data.community;

    let videos: any[] = [];
    let loading = true;
    let showAdd = false;

    // Form
    let newVideo = {
        title: '',
        platform: 'youtube', // youtube | tiktok | instagram
        url: '', // The Video ID
        thumbnail: '',
        category: 'Main Stage'
    };

    onMount(async () => {
        await loadStage();
    });

    async function loadStage() {
        loading = true;
        try {
            // Assuming the API returns a flat list or we flatten the categories
            const res = await api.getStageFeed(community.id);
            // Flatten logic if API returns categories
            if (Array.isArray(res) && res.length > 0 && 'items' in res[0]) {
                videos = res.flatMap((cat: any) => cat.items);
            } else {
                videos = Array.isArray(res) ? res : [];
            }
        } catch (e) { console.error(e); } 
        finally { loading = false; }
    }

    async function handleAdd() {
        try {
            // In a real app: api.addToStage(community.id, newVideo)
            // For now, we simulate the call or use a generic endpoint
            const res = await fetch(`${api.API_URL}/stage/${community.id}/items`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('codex_token')}`
                },
                body: JSON.stringify(newVideo)
            });
            
            if (!res.ok) throw new Error();
            
            showAdd = false;
            newVideo = { title: '', platform: 'youtube', url: '', thumbnail: '', category: 'Main Stage' };
            await loadStage();
        } catch (e) { 
            alert("Failed to add video. Ensure ID is correct."); 
        }
    }

    async function handleDelete(id: string) {
        if(!confirm("Remove this video from the stage?")) return;
        // Mock delete
        videos = videos.filter(v => v.id !== id);
    }
</script>

<div class="space-y-8 animate-fade-in-up">
    
    <div class="flex items-end justify-between border-b-4 border-black pb-6">
        <div>
            <div class="text-xs font-black uppercase text-indigo-600 tracking-widest mb-1 flex items-center gap-2">
                <span>🎬</span> Stage Engine
            </div>
            <h1 class="text-4xl font-black uppercase tracking-tighter">
                Broadcast Control
            </h1>
        </div>
        <button 
            on:click={() => showAdd = true}
            class="px-6 py-3 bg-indigo-600 text-white font-black rounded uppercase text-xs shadow-[4px_4px_0px_black] hover:-translate-y-1 hover:shadow-[6px_6px_0px_black] transition-all"
        >
            + Add Content
        </button>
    </div>

    {#if loading}
        <div class="p-12 text-center text-gray-400 font-bold animate-pulse">Calibrating Projectors...</div>
    {:else if videos.length === 0}
        <div class="p-20 text-center border-4 border-dashed border-gray-200 rounded-xl text-gray-400">
            <span class="text-4xl block mb-2">📺</span>
            <span class="font-bold uppercase tracking-widest">No Active Broadcasts</span>
        </div>
    {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each videos as video}
                <div class="bg-white border-2 border-gray-200 rounded-xl overflow-hidden relative group hover:border-black transition-colors">
                    
                    <div class="aspect-video bg-black relative">
                        <img src={video.thumbnail} alt={video.title} class="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity" />
                        <div class="absolute top-2 right-2 bg-black/80 text-white text-[10px] font-bold px-2 py-1 rounded uppercase">
                            {video.platform}
                        </div>
                    </div>

                    <div class="p-4">
                        <h3 class="font-bold text-lg leading-tight mb-1 line-clamp-1">{video.title}</h3>
                        <div class="text-xs text-gray-400 font-mono mb-4">{video.url}</div>
                        
                        <div class="flex gap-2">
                            <button class="flex-1 py-2 bg-gray-100 text-xs font-bold uppercase rounded hover:bg-black hover:text-white transition-colors">
                                Edit
                            </button>
                            <button 
                                on:click={() => handleDelete(video.id)}
                                class="px-3 py-2 border-2 border-red-100 text-red-500 text-xs font-bold uppercase rounded hover:bg-red-500 hover:text-white transition-colors"
                            >
                                Delete
                            </button>
                        </div>
                    </div>

                </div>
            {/each}
        </div>
    {/if}

    {#if showAdd}
        <div class="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4 backdrop-blur-sm" transition:fade>
            <div class="bg-white w-full max-w-lg rounded-xl p-8 shadow-2xl" in:scale>
                <h2 class="font-black text-2xl uppercase mb-6">Add to Stage</h2>
                
                <div class="space-y-4">
                    <div>
                        <label class="block text-xs font-bold uppercase text-gray-500 mb-1">Title</label>
                        <input bind:value={newVideo.title} class="w-full border-2 border-gray-200 p-3 rounded font-bold focus:border-black outline-none" placeholder="e.g. Graduation Ceremony" />
                    </div>

                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs font-bold uppercase text-gray-500 mb-1">Platform</label>
                            <select bind:value={newVideo.platform} class="w-full border-2 border-gray-200 p-3 rounded font-bold focus:border-black outline-none bg-white">
                                <option value="youtube">YouTube</option>
                                <option value="tiktok">TikTok</option>
                                <option value="instagram">Instagram</option>
                                <option value="twitch">Twitch</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs font-bold uppercase text-gray-500 mb-1">Video ID / Slug</label>
                            <input bind:value={newVideo.url} class="w-full border-2 border-gray-200 p-3 rounded font-bold focus:border-black outline-none" placeholder="dQw4w9WgXcQ" />
                        </div>
                    </div>

                    <div>
                        <label class="block text-xs font-bold uppercase text-gray-500 mb-1">Thumbnail URL</label>
                        <input bind:value={newVideo.thumbnail} class="w-full border-2 border-gray-200 p-3 rounded font-bold focus:border-black outline-none" placeholder="https://..." />
                    </div>
                </div>

                <div class="flex gap-2 mt-8">
                    <button on:click={() => showAdd = false} class="flex-1 py-3 text-gray-500 font-bold hover:bg-gray-100 rounded">Cancel</button>
                    <button on:click={handleAdd} class="flex-1 py-3 bg-indigo-600 text-white font-bold uppercase rounded">Broadcast</button>
                </div>
            </div>
        </div>
    {/if}

</div>