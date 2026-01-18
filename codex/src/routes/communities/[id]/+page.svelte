<script lang="ts">
    import { page } from '$app/stores';
    import { onMount } from 'svelte';
    import { api, type Community, type Post } from '$lib/api';

    // 1. DATA STATE
    let communityId = $page.params.id;
    let community: Community | null = null;
    let allMembers: any[] = [];
    let posts: Post[] = [];
    
    // Lists derived from members
    let pendingQueue: any[] = [];
    let activeCitizens: any[] = [];
    
    // UI State
    let loading = true; 
    let processingId: string | null = null;
    
    // Posting State
    let newPostContent = "";
    let isPosting = false;

    onMount(async () => {
        await loadIntel();
    });

    async function loadIntel() {
        try {
            // Load Community, Members, and Feed all at once
            const [commData, membersData, feedData] = await Promise.all([
                api.getCommunity(communityId),
                api.getMembers(communityId),
                api.getFeed(communityId)
            ]);

            community = commData;
            allMembers = membersData;
            posts = feedData;

            // Sort members
            pendingQueue = allMembers.filter(m => m.status.toLowerCase() === 'pending');
            activeCitizens = allMembers.filter(m => m.status.toLowerCase() === 'active');
            
            if (community) community.member_count = activeCitizens.length;

        } catch (e: any) {
            console.error("Intel Failure:", e);
        } finally {
            loading = false;
        }
    }

    async function handleDecision(userId: string, action: 'approve' | 'reject') {
        if (!confirm(`Confirm: ${action.toUpperCase()} this applicant?`)) return;
        processingId = userId;
        try {
            await api.processMembership(communityId, userId, action);
            await loadIntel(); 
        } catch (e: any) {
            alert('Command failed: ' + e.message);
        } finally {
            processingId = null;
        }
    }

    async function handlePost() {
        if (!newPostContent.trim()) return;
        isPosting = true;
        try {
            await api.createPost({
                community_id: communityId,
                content: newPostContent,
                title: "Admin Announcement"
            });
            newPostContent = ""; 
            await loadIntel(); // Refresh feed
        } catch (e: any) {
            alert("Broadcast failed: " + e.message);
        } finally {
            isPosting = false;
        }
    }

    async function handleLike(post: Post) {
        if (post.is_liked) return; // Prevent double liking visually for now
        post.is_liked = true; 
        post.like_count++;
        posts = posts; // Trigger Svelte update
        try {
            await api.likePost(post.id);
        } catch (e) {
            console.error("Like failed", e);
        }
    }
</script>

<div class="max-w-6xl mx-auto p-8">
    <a href="/communities" class="text-slate-500 hover:text-white mb-6 inline-block text-sm font-mono">&larr; RETURN TO MAP</a>

    {#if loading}
        <div class="p-12 text-center text-slate-500 animate-pulse border border-slate-800 rounded-xl bg-slate-950">
            LOADING INTEL...
        </div>
    {:else if community}
        
        <div class="bg-slate-950 border border-slate-800 rounded-xl p-8 mb-8 flex justify-between items-start">
            <div>
                <h1 class="text-3xl font-bold text-white mb-2">{community.name}</h1>
                <div class="text-slate-500 font-mono text-sm">{community.slug}</div>
            </div>
            <div class="text-right">
                <div class="text-4xl font-bold text-white">{activeCitizens.length}</div>
                <div class="text-xs text-slate-500 uppercase font-bold">Citizens</div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            <div class="lg:col-span-2 space-y-8">
                
                <div class="bg-slate-950 border border-slate-800 rounded-xl p-6">
                    <h4 class="text-white font-bold mb-4 flex items-center gap-2">
                        <span class="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                        Broadcast Signal
                    </h4>
                    <textarea 
                        bind:value={newPostContent}
                        rows="3"
                        placeholder="Transmit message to all citizens..."
                        class="w-full bg-slate-900 border border-slate-800 rounded-lg p-3 text-white text-sm focus:border-orange-500 outline-none resize-none mb-3"
                    ></textarea>
                    <button 
                        on:click={handlePost}
                        disabled={isPosting || !newPostContent}
                        class="w-full bg-orange-600 hover:bg-orange-500 text-white font-bold py-3 rounded-lg text-xs uppercase tracking-wider transition-all disabled:opacity-50"
                    >
                        {isPosting ? 'TRANSMITTING...' : 'SEND BROADCAST'}
                    </button>
                </div>

                <div class="space-y-4">
                    <h3 class="text-slate-500 font-bold uppercase text-xs tracking-widest">Live Transmissions</h3>
                    {#if posts.length === 0}
                        <div class="text-center py-12 border border-dashed border-slate-800 rounded-xl text-slate-500">
                            No signals detected.
                        </div>
                    {:else}
                        {#each posts as post}
                            <div class="bg-slate-950 border border-slate-800 rounded-xl p-6">
                                <div class="flex justify-between items-start mb-3">
                                    <div class="flex items-center gap-3">
                                        <div class="font-bold text-white text-sm">{post.author_name}</div>
                                        <div class="text-xs text-slate-500">{new Date(post.created_at).toLocaleDateString()}</div>
                                    </div>
                                    {#if post.title}
                                        <span class="bg-slate-900 text-slate-400 text-[10px] px-2 py-1 rounded uppercase font-bold">{post.title}</span>
                                    {/if}
                                </div>
                                <p class="text-slate-300 text-sm leading-relaxed mb-4">{post.content}</p>
                                <div class="flex items-center gap-4 text-xs font-bold text-slate-500 border-t border-slate-900 pt-3">
                                    <button 
                                        on:click={() => handleLike(post)}
                                        class="flex items-center gap-2 hover:text-white transition-colors {post.is_liked ? 'text-red-500' : ''}"
                                    >
                                        <span>{post.is_liked ? '❤️' : '♡'}</span> {post.like_count}
                                    </button>
                                    <div class="flex items-center gap-2"><span>💬</span> {post.comment_count}</div>
                                </div>
                            </div>
                        {/each}
                    {/if}
                </div>
            </div>

            <div class="space-y-8">
                
                <div class="space-y-4">
                    <h3 class="text-orange-500 font-bold uppercase text-xs tracking-widest">Pending ({pendingQueue.length})</h3>
                    <div class="bg-slate-950 border border-slate-800 rounded-xl min-h-[100px] p-2">
                        {#if pendingQueue.length === 0}
                            <div class="p-6 text-center text-slate-600 text-xs">Queue Empty</div>
                        {:else}
                            <div class="divide-y divide-slate-800">
                                {#each pendingQueue as applicant}
                                    <div class="p-3">
                                        <div class="font-bold text-white text-xs mb-1">
                                            {applicant.user?.full_name || 'Unknown'}
                                        </div>
                                        <div class="flex gap-2 mt-2">
                                            <button on:click={() => handleDecision(applicant.user_id, 'approve')} class="text-[10px] bg-green-900/20 text-green-400 px-2 py-1 rounded border border-green-900/50">APPROVE</button>
                                            <button on:click={() => handleDecision(applicant.user_id, 'reject')} class="text-[10px] bg-red-900/20 text-red-400 px-2 py-1 rounded border border-red-900/50">REJECT</button>
                                        </div>
                                    </div>
                                {/each}
                            </div>
                        {/if}
                    </div>
                </div>

                <div class="space-y-4">
                    <h3 class="text-slate-500 font-bold uppercase text-xs tracking-widest">Active Roster</h3>
                    <div class="bg-slate-950 border border-slate-800 rounded-xl p-4">
                        {#if activeCitizens.length === 0}
                            <div class="text-slate-600 text-sm italic text-center">No active citizens.</div>
                        {:else}
                            <div class="space-y-2">
                                {#each activeCitizens as citizen}
                                    <div class="flex items-center justify-between p-2 bg-slate-900 rounded border border-slate-800">
                                        <div class="flex items-center gap-3">
                                            <div class="w-6 h-6 rounded-full bg-slate-800 text-slate-400 flex items-center justify-center text-[10px] font-bold">
                                                {(citizen.user?.full_name || '?')[0]}
                                            </div>
                                            <div class="text-xs font-bold text-white">
                                                {citizen.user?.full_name || 'Unknown'}
                                            </div>
                                        </div>
                                    </div>
                                {/each}
                            </div>
                        {/if}
                    </div>
                </div>

            </div>
        </div>

    {:else}
        <div class="p-12 text-center text-red-500 border border-red-900/50 bg-red-900/10 rounded-xl">
            DATA LINK SEVERED (404)
        </div>
    {/if}
</div>