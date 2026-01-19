<script lang="ts">
    import { onMount } from 'svelte';
    import { api, type Post } from '$lib/api';
    import PostCard from '$lib/components/PostCard.svelte';

    // --- STANDARD PROPS ---
    export let community: any;
    export let currentUser: any = null;
    export let membership: any = null;

    // --- STATE ---
    let posts: Post[] = [];
    let loading = true;
    let newPostContent = "";
    let isPosting = false;

    // --- LOAD DATA ---
    onMount(async () => {
        try {
            posts = await api.getFeed(community.id);
        } catch (e) {
            console.error("Feed Load Failed:", e);
        } finally {
            loading = false;
        }
    });

    // --- ACTIONS ---
    async function handleCreatePost() {
        if (!newPostContent.trim()) return;
        isPosting = true;
        try {
            await api.createPost(community.id, newPostContent);
            newPostContent = "";
            posts = await api.getFeed(community.id); // Refresh feed
        } catch (e) {
            alert("Broadcast failed.");
        } finally {
            isPosting = false;
        }
    }
</script>

<div class="space-y-6">
    
    {#if membership?.status === 'active'}
        <div class="bg-white border-4 border-black p-4 shadow-hard relative z-10">
            <div class="flex gap-4">
                <div class="w-12 h-12 bg-black shrink-0 flex items-center justify-center text-white font-black text-xl">
                    {currentUser?.full_name?.[0] || '?'}
                </div>
                
                <textarea 
                    bind:value={newPostContent}
                    placeholder="Start a discussion..."
                    class="w-full bg-transparent border-none focus:ring-0 text-lg font-bold resize-none h-24 placeholder:text-gray-300 placeholder:uppercase"
                ></textarea>
            </div>
            
            <div class="flex justify-between items-center mt-2 pt-4 border-t-2 border-gray-100">
                <div class="text-xs font-bold text-gray-400 uppercase">Markdown Supported</div>
                <button 
                    on:click={handleCreatePost}
                    disabled={!newPostContent || isPosting}
                    class="bg-black text-white font-black uppercase py-2 px-6 hover:bg-sp-blue hover:text-white transition-colors disabled:opacity-50"
                >
                    {isPosting ? 'Posting...' : 'Post'}
                </button>
            </div>
        </div>
    {:else}
        <div class="bg-gray-100 border-2 border-dashed border-gray-300 p-6 text-center">
            <p class="font-bold text-gray-500">Join {community.name} to contribute to the discussion.</p>
        </div>
    {/if}

    {#if loading}
        <div class="text-center py-12 animate-pulse font-bold text-gray-400">LOADING TRANSMISSIONS...</div>
    {:else}
        <div class="space-y-6">
            {#each posts as post (post.id)}
                <PostCard {post} {currentUser} />
            {:else}
                <div class="text-center py-12">
                    <div class="text-4xl mb-4">🔇</div>
                    <h3 class="font-black uppercase text-gray-400">Radio Silence</h3>
                    <p class="text-gray-500">No discussions yet.</p>
                </div>
            {/each}
        </div>
    {/if}

</div>