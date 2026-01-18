<script lang="ts">
    import { page } from '$app/stores';
    import { onMount } from 'svelte';
    import { api, type Community, type Post } from '$lib/api';

    // --- STATE ---
    let communityId = $page.params.id;
    let currentUser: any = null;
    
    let community: Community | null = null;
    let posts: Post[] = [];
    
    // Admin Only Data
    let pendingQueue: any[] = [];
    let activeCitizens: any[] = []; // Visible to all, but managed by admin
    
    // Permissions
    let isAdmin = false;
    let isMember = false;

    // UI State
    let loading = true; 
    let processingId: string | null = null;
    let newPostContent = "";
    let isPosting = false;

    onMount(async () => {
        // 1. Get current user first to check permissions
        try {
            currentUser = await api.getMe();
        } catch (e) {
            console.error("Auth check failed", e);
        }
        await loadIntel();
    });

    async function loadIntel() {
        try {
            // 2. Fetch Core Data
            const [commData, feedData, membersData] = await Promise.all([
                api.getCommunity(communityId),
                api.getFeed(communityId),
                api.getMembers(communityId) // We fetch members to check our own status
            ]);

            community = commData;
            posts = feedData;
            
            // 3. Calculate Permissions
            if (currentUser && community) {
                // Am I the Creator?
                isAdmin = community.creator_id === currentUser.id;
                
                // Am I a Member?
                const myMembership = membersData.find((m: any) => m.user_id === currentUser.id);
                isMember = myMembership?.status === 'active';
            }

            // 4. Organize Roster
            // We use the fetched members list to populate the sidebar
            pendingQueue = membersData.filter((m: any) => m.status === 'pending');
            activeCitizens = membersData.filter((m: any) => m.status === 'active');

        } catch (e: any) {
            console.error("Intel Failure:", e);
        } finally {
            loading = false;
        }
    }

    // --- ACTIONS ---

    async function handlePost() {
        if (!newPostContent.trim()) return;
        isPosting = true;
        try {
            await api.createPost({
                community_id: communityId,
                content: newPostContent,
                // No title logic for now - keeping it simple like a tweet
            });
            newPostContent = ""; 
            // Refresh feed only
            posts = await api.getFeed(communityId);
        } catch (e: any) {
            alert("Transmission failed: " + e.message);
        } finally {
            isPosting = false;
        }
    }

    async function handleLike(post: Post) {
        if (post.is_liked) return;
        post.is_liked = true; 
        post.like_count++;
        posts = posts; 
        try {
            await api.likePost(post.id);
        } catch (e) {
            console.error("Like failed", e);
        }
    }

    // Admin Actions
    async function handleDecision(userId: string, action: 'approve' | 'reject') {
        if (!confirm(`Confirm: ${action.toUpperCase()}?`)) return;
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
</script>

<div class="max-w-6xl mx-auto p-4 md:p-8">
    <a href="/communities" class="text-slate-500 hover:text-white mb-6 inline-block text-sm font-mono">&larr; RETURN TO MAP</a>

    {#if loading}
        <div class="p-12 text-center text-slate-500 animate-pulse border border-slate-800 rounded-xl bg-slate-950">
            CONNECTING TO NODE...
        </div>
    {:else if community}
        
        <div class="bg-slate-950 border border-slate-800 rounded-xl p-8 mb-8">
            <div class="flex flex-col md:flex-row justify-between items-start gap-4">
                <div>
                    <h1 class="text-3xl font-bold text-white mb-2">{community.name}</h1>
                    <div class="text-slate-500 font-mono text-sm">/c/{community.slug}</div>
                    <p class="text-slate-400 mt-4 max-w-2xl">{community.description || "No manifesto established."}</p>
                </div>
                
                <div class="flex items-center gap-6">
                    <div class="text-right">
                        <div class="text-3xl font-bold text-white">{activeCitizens.length}</div>
                        <div class="text-xs text-slate-500 uppercase font-bold">Population</div>
                    </div>
                    </div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            <div class="lg:col-span-2 space-y-8">
                
                {#if isMember}
                    <div class="bg-slate-950 border border-slate-800 rounded-xl p-4 md:p-6">
                        <textarea 
                            bind:value={newPostContent}
                            rows="2"
                            placeholder="What is happening in {community.name}?"
                            class="w-full bg-slate-900 border border-slate-800 rounded-lg p-3 text-white text-sm focus:border-orange-500 outline-none resize-none mb-3 transition-all"
                        ></textarea>
                        <div class="flex justify-end">
                            <button 
                                on:click={handlePost}
                                disabled={isPosting || !newPostContent}
                                class="bg-orange-600 hover:bg-orange-500 text-white font-bold py-2 px-6 rounded-lg text-xs uppercase tracking-wider transition-all disabled:opacity-50"
                            >
                                {isPosting ? 'POSTING...' : 'POST'}
                            </button>
                        </div>
                    </div>
                {:else}
                    <div class="p-6 border border-slate-800 bg-slate-900/50 rounded-xl text-center text-slate-400 text-sm">
                        You must be a citizen to transmit signals.
                    </div>
                {/if}

                <div class="space-y-4">
                    {#if posts.length === 0}
                        <div class="text-center py-12 border border-dashed border-slate-800 rounded-xl text-slate-500">
                            No activity recorded. Be the first.
                        </div>
                    {:else}
                        {#each posts as post}
                            <div class="bg-slate-950 border border-slate-800 rounded-xl p-6">
                                <div class="flex justify-between items-start mb-3">
                                    <div class="flex items-center gap-3">
                                        <div class="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center text-xs font-bold text-slate-300">
                                            {post.author_name[0]}
                                        </div>
                                        <div>
                                            <div class="font-bold text-white text-sm">{post.author_name}</div>
                                            <div class="text-xs text-slate-500">{new Date(post.created_at).toLocaleDateString()}</div>
                                        </div>
                                    </div>
                                    {#if post.title}
                                        <span class="bg-slate-900 text-slate-400 text-[10px] px-2 py-1 rounded uppercase font-bold">{post.title}</span>
                                    {/if}
                                </div>
                                
                                <p class="text-slate-300 text-sm leading-relaxed mb-4 whitespace-pre-wrap">{post.content}</p>
                                
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
                
                {#if isAdmin}
                    <div class="space-y-4 border-b border-slate-800 pb-8">
                        <h3 class="text-orange-500 font-bold uppercase text-xs tracking-widest">Pending Applications</h3>
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
                                                <button on:click={() => handleDecision(applicant.user_id, 'approve')} class="text-[10px] bg-green-900/20 text-green-400 px-2 py-1 rounded border border-green-900/50 hover:bg-green-900/40">ACCEPT</button>
                                                <button on:click={() => handleDecision(applicant.user_id, 'reject')} class="text-[10px] bg-red-900/20 text-red-400 px-2 py-1 rounded border border-red-900/50 hover:bg-red-900/40">REJECT</button>
                                            </div>
                                        </div>
                                    {/each}
                                </div>
                            {/if}
                        </div>
                    </div>
                {/if}

                <div class="space-y-4">
                    <h3 class="text-slate-500 font-bold uppercase text-xs tracking-widest">Citizens</h3>
                    <div class="bg-slate-950 border border-slate-800 rounded-xl p-4 max-h-[400px] overflow-y-auto">
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