<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    import type { Community, Membership, User, Post } from '$lib/api'; // Ensure Post type is exported in api.ts
    import { fly, slide, fade } from 'svelte/transition';
    import PostCard from '$lib/components/PostCard.svelte'; 

    // --- PROPS ---
    export let community: Community;
    export let currentUser: User | null = null;
    export let membership: Membership | null = null;

    // --- STATE ---
    let posts: Post[] = [];
    let loading = true;
    let newPostContent = "";
    let isPosting = false;
    let focused = false;
    let error: string | null = null;

    // --- LOAD DATA ---
    onMount(async () => {
        if (!community?.id) return;
        
        try {
            // ✅ UPDATED: Calls api.getFeed(communityId)
            posts = await api.getFeed(community.id);
        } catch (e) {
            console.error("Feed Load Failed:", e);
            error = "Signal Lost: Could not retrieve frequency.";
        } finally {
            loading = false;
        }
    });

    // --- ACTIONS ---
    async function handleCreatePost() {
        if (!newPostContent.trim()) return;
        isPosting = true;
        error = null;
        
        try {
            // 1. Send to Backend
            // ✅ UPDATED: Calls api.createPost({ community_id, content })
            const newPost = await api.createPost({
                community_id: community.id,
                content: newPostContent
            });

            // 2. Optimistic Update (UI Polish)
            // The backend might not return the full Author object immediately (depending on implementation),
            // so we patch it with 'currentUser' to ensure the avatar/name shows up instantly.
            if (currentUser && !newPost.author) {
                newPost.author = currentUser;
                // Patch legacy fields if PostCard uses them
                (newPost as any).author_name = currentUser.full_name;
                (newPost as any).author_avatar = currentUser.avatar_url;
            }
            
            // Add to top of list
            posts = [newPost, ...posts]; 

            // 3. Reset Form
            newPostContent = "";
            focused = false;
            
        } catch (e: any) {
            console.error(e);
            error = "Transmission Failed: " + (e.message || "Unknown Error");
        } finally {
            isPosting = false;
        }
    }

    // Permission Check
    $: canPost = membership?.status === 'active' || membership?.role === 'admin' || membership?.role === 'owner';
</script>

<div class="max-w-3xl mx-auto pb-20">

    {#if error}
        <div class="bg-red-50 border-2 border-red-500 text-red-700 p-4 rounded mb-8 text-center font-bold font-mono text-sm shadow-sm" transition:slide>
            [SYSTEM FAILURE]: {error}
        </div>
    {/if}

    {#if canPost}
        <div class="relative mb-12 group z-20">
            <div class="absolute -top-4 left-1/2 -translate-x-1/2 w-32 h-12 bg-yellow-200/80 rotate-1 backdrop-blur-sm shadow-sm z-30 pointer-events-none border-x-2 border-white/40"></div>

            <div class="bg-white border-2 border-zinc-900 shadow-[8px_8px_0px_rgba(0,0,0,1)] relative transition-transform duration-200 {focused ? '-translate-y-1 shadow-[12px_12px_0px_rgba(0,0,0,1)]' : ''}">
                
                <div class="p-6">
                    <div class="flex gap-4 items-start">
                        <div class="w-12 h-12 bg-zinc-900 shrink-0 flex items-center justify-center text-white font-black text-xl rounded-sm -rotate-2 border-2 border-white shadow-sm overflow-hidden">
                            {#if currentUser?.avatar_url}
                                <img src={currentUser.avatar_url} alt="User" class="w-full h-full object-cover" />
                            {:else}
                                {currentUser?.full_name?.[0] || '?'}
                            {/if}
                        </div>
                        
                        <div class="flex-1 relative">
                            <textarea 
                                bind:value={newPostContent}
                                on:focus={() => focused = true}
                                on:blur={() => focused = (newPostContent.length > 0)}
                                placeholder="Broadcast to the campus..."
                                class="w-full bg-transparent border-none focus:ring-0 text-lg font-medium text-zinc-800 resize-none placeholder:text-zinc-300 placeholder:uppercase placeholder:font-black leading-[32px]"
                                style="background-image: linear-gradient(transparent 31px, #e4e4e7 32px); background-size: 100% 32px; min-height: 128px;"
                            ></textarea>
                        </div>
                    </div>
                </div>

                {#if focused || newPostContent}
                    <div class="bg-zinc-50 border-t-2 border-zinc-900 p-3 flex justify-between items-center" transition:slide>
                        <div class="flex gap-2">
                             <button class="w-8 h-8 flex items-center justify-center rounded hover:bg-zinc-200 text-zinc-500 transition-colors" title="Attach Image">📷</button>
                            <button class="w-8 h-8 flex items-center justify-center rounded hover:bg-zinc-200 text-zinc-500 transition-colors" title="Create Poll">📊</button>
                        </div>
                        
                        <div class="flex items-center gap-4">
                            {#if newPostContent.length > 0}
                                <span class="text-[10px] font-bold text-zinc-400 uppercase tracking-widest" transition:fade>
                                    {newPostContent.length} chars
                                </span>
                            {/if}
                            <button 
                                on:click={handleCreatePost}
                                disabled={!newPostContent || isPosting}
                                class="bg-blue-600 text-white font-black uppercase text-xs py-2 px-6 hover:bg-blue-700 hover:shadow-lg transition-all disabled:opacity-50 disabled:shadow-none transform active:scale-95 border-2 border-transparent hover:border-black"
                            >
                                {isPosting ? 'Transmitting...' : 'Broadcast ->'}
                            </button>
                        </div>
                    </div>
                {/if}
            </div>
        </div>
    {:else}
        <div class="bg-zinc-100 border-2 border-dashed border-zinc-300 p-8 text-center rounded-xl mb-12">
            <span class="text-4xl block mb-2">🔒</span>
            <p class="font-bold text-zinc-500 uppercase tracking-widest text-xs">
                {#if !currentUser}
                    Log in to transmit.
                {:else}
                    Join {community.name} to transmit signals.
                {/if}
            </p>
        </div>
    {/if}

    <div class="relative">
        <div class="absolute left-6 top-0 bottom-0 w-[2px] bg-zinc-200 z-0"></div>

        {#if loading}
            <div class="ml-16 py-12 animate-pulse font-black text-zinc-200 text-4xl uppercase tracking-tighter">
                Decoding Signal...
            </div>
        {:else}
            <div class="space-y-8">
                {#each posts as post, i (post.id)}
                    <div class="relative pl-16 group" in:fly={{ y: 20, delay: i * 50 }}>
                        <div class="absolute left-[21px] top-8 w-4 h-4 bg-white border-4 border-zinc-300 rounded-full z-10 group-hover:border-blue-500 group-hover:scale-125 transition-all"></div>
                        
                        <div class="relative hover:-translate-y-1 transition-transform duration-300">
                             <PostCard {post} {currentUser} />
                        </div>
                    </div>
                {:else}
                    <div class="ml-16 py-12 text-center border-2 border-dashed border-zinc-200 rounded-xl bg-zinc-50">
                        <div class="text-4xl mb-4 grayscale opacity-50">📡</div>
                        <h3 class="font-black uppercase text-zinc-400">Radio Silence</h3>
                        <p class="text-zinc-400 text-xs mt-1">Be the first to broadcast on this frequency.</p>
                    </div>
                {/each}
            </div>
        {/if}
    </div>
</div>