<script lang="ts">
    import { onMount } from 'svelte';
    import { api, type Post } from '$lib/api';
    import { fade } from 'svelte/transition';

    export let data;
    $: community = data.community;

    let posts: Post[] = [];
    let loading = true;

    onMount(async () => {
        await loadFeed();
    });

    async function loadFeed() {
        loading = true;
        try {
            const res = await api.getFeed(community.id);
            posts = Array.isArray(res) ? res : [];
        } catch (e) { console.error(e); } 
        finally { loading = false; }
    }

    async function togglePin(post: Post) {
        // Optimistic update
        post.is_pinned = !post.is_pinned;
        posts = posts;
        try {
            await api.pinPost(post.id);
        } catch (e) { alert("Action failed"); }
    }

    async function handleDelete(postId: string) {
        if (!confirm("Permanently delete this post?")) return;
        try {
            await api.deletePost(postId);
            posts = posts.filter(p => p.id !== postId);
        } catch (e) { alert("Delete failed"); }
    }
</script>

<div class="space-y-8 animate-fade-in-up">
    
    <div class="flex items-end justify-between border-b-4 border-black pb-6">
        <div>
            <div class="text-xs font-black uppercase text-blue-600 tracking-widest mb-1 flex items-center gap-2">
                <span>💬</span> Social Engine
            </div>
            <h1 class="text-4xl font-black uppercase tracking-tighter">
                Feed Moderation
            </h1>
        </div>
        <div class="flex gap-2">
            <button class="px-4 py-2 bg-gray-100 text-gray-500 font-bold rounded text-xs uppercase cursor-not-allowed">
                View Reports (0)
            </button>
            <button 
                on:click={loadFeed}
                class="px-4 py-2 bg-black text-white font-bold rounded text-xs uppercase hover:bg-gray-800 transition-colors"
            >
                Refresh Feed
            </button>
        </div>
    </div>

    {#if loading}
        <div class="p-12 text-center text-gray-400 font-bold animate-pulse">Scanning Frequency...</div>
    {:else if posts.length === 0}
        <div class="p-20 text-center border-4 border-dashed border-gray-200 rounded-xl text-gray-400">
            <span class="text-4xl block mb-2">📡</span>
            <span class="font-bold uppercase tracking-widest">Feed is Silent</span>
        </div>
    {:else}
        <div class="space-y-4">
            {#each posts as post (post.id)}
                <div class="bg-white border-2 border-gray-200 p-6 rounded-xl flex gap-6 hover:border-black transition-colors group">
                    
                    <div class="w-10 h-10 rounded-full bg-gray-100 flex-shrink-0 flex items-center justify-center font-bold text-gray-400">
                        {post.author_name ? post.author_name[0] : '?'}
                    </div>

                    <div class="flex-1">
                        <div class="flex justify-between items-start mb-2">
                            <div>
                                <span class="font-black text-sm">{post.author_name}</span>
                                <span class="text-xs text-gray-400 font-bold ml-2">{new Date(post.created_at).toLocaleDateString()}</span>
                                {#if post.is_pinned}
                                    <span class="ml-2 px-2 py-0.5 bg-yellow-100 text-yellow-700 text-[9px] font-black uppercase rounded">Pinned</span>
                                {/if}
                            </div>
                            <div class="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                <button 
                                    on:click={() => togglePin(post)}
                                    class="text-[10px] font-bold uppercase hover:underline {post.is_pinned ? 'text-gray-400' : 'text-blue-600'}"
                                >
                                    {post.is_pinned ? 'Unpin' : 'Pin to Top'}
                                </button>
                                <button 
                                    on:click={() => handleDelete(post.id)}
                                    class="text-[10px] font-bold uppercase text-red-500 hover:text-red-700 hover:underline"
                                >
                                    Delete
                                </button>
                            </div>
                        </div>

                        {#if post.title}
                            <h3 class="font-bold text-lg mb-2">{post.title}</h3>
                        {/if}
                        
                        <p class="text-gray-600 text-sm leading-relaxed whitespace-pre-wrap">{post.content}</p>

                        {#if post.image_url}
                            <img src={post.image_url} alt="Post attachment" class="mt-4 rounded-lg border border-gray-100 max-h-64 object-cover" />
                        {/if}

                        <div class="mt-4 flex gap-4 text-xs font-bold text-gray-400">
                            <span>♥ {post.like_count} Likes</span>
                            <span>💬 {post.comment_count} Comments</span>
                        </div>
                    </div>

                </div>
            {/each}
        </div>
    {/if}

</div>