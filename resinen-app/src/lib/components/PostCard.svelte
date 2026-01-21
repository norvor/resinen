<script lang="ts">
    import { api } from '$lib/api';
    import type { Post, User, Comment } from '$lib/api'; // Use centralized types
    import { createEventDispatcher } from 'svelte';
    import { slide } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';

    export let post: Post;
    export let currentUser: User | null;

    const dispatch = createEventDispatcher();

    // --- STATE ---
    let showComments = false;
    let comments: Comment[] = [];
    let loadingComments = false;
    let newCommentText = "";
    let isSubmitting = false;
    let likeBounce = false; 

    // --- HELPERS ---
    // Handle specific backend data shape (PostRead.author is a User object)
    $: authorName = post.author?.full_name || 'Unknown';
    $: authorAvatar = post.author?.avatar_url;
    $: authorLevel = post.author?.level || 1;

    // --- ACTIONS ---
    async function toggleComments() {
        showComments = !showComments;
        if (showComments && comments.length === 0) {
            await loadComments();
        }
    }

    async function loadComments() {
        loadingComments = true;
        try {
            // ✅ FIX: Use API Client (points to localhost automatically)
            comments = await api.getComments(post.id);
        } catch (e) {
            console.error("Comment load error", e);
        } finally {
            loadingComments = false;
        }
    }

    async function handlePostComment() {
        if (!newCommentText.trim()) return;
        isSubmitting = true;
        try {
            // ✅ FIX: Use API Client
            const newComment = await api.createComment(post.id, newCommentText);
            
            // Optimistic Update
            // Patch author details immediately for UI since backend might return a fresh object
            if (currentUser && !newComment.author) {
                newComment.author = currentUser;
            }
            
            comments = [...comments, newComment]; 
            post.comment_count++;
            newCommentText = "";
            
        } catch (e) {
            console.error(e);
            alert("Failed to post comment.");
        } finally {
            isSubmitting = false;
        }
    }

    async function handleLikePost() {
        // ✅ FIX: Property name matches Backend Schema (is_liked)
        if (post.is_liked) return;
        
        // Optimistic UI
        post.is_liked = true;
        post.like_count++;
        triggerBounce();

        try {
            await api.likePost(post.id);
        } catch (e) {
            // Revert on failure
            post.is_liked = false;
            post.like_count--;
        }
    }
    
    async function handleLikeComment(comment: Comment) {
        if (comment.is_liked) return;
        
        comment.is_liked = true;
        comment.like_count++;
        comments = comments; // Trigger reactivity

        try {
            await api.likeComment(comment.id);
        } catch (e) {
            comment.is_liked = false;
            comment.like_count--;
            comments = comments;
        }
    }

    function triggerBounce() {
        likeBounce = true;
        setTimeout(() => likeBounce = false, 300);
    }
</script>

<div class="bg-white border-2 border-zinc-200 rounded-xl overflow-hidden mb-6 transition-all duration-300 hover:border-zinc-400 hover:shadow-md group relative">
    
    <div class="px-5 py-4 flex items-start justify-between border-b border-zinc-100 bg-zinc-50/50">
        <div class="flex items-center gap-3">
            <div class="relative">
                <div class="w-10 h-10 rounded-lg bg-zinc-900 flex items-center justify-center overflow-hidden shadow-sm border border-zinc-200">
                    {#if authorAvatar}
                        <img src={authorAvatar} alt={authorName} class="w-full h-full object-cover" />
                    {:else}
                        <span class="text-sm font-black text-white select-none">{authorName[0]}</span>
                    {/if}
                </div>
                <div class="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></div>
            </div>

            <div>
                <div class="flex items-center gap-2">
                    <span class="font-bold text-zinc-900 text-sm">{authorName}</span>
                    <span class="px-1.5 py-0.5 rounded bg-zinc-200 text-[9px] font-black text-zinc-500 uppercase">
                        LVL {authorLevel}
                    </span>
                </div>
                <div class="text-[10px] font-mono font-medium text-zinc-400 flex items-center gap-2">
                    <span>{new Date(post.created_at).toLocaleDateString()}</span>
                    <span class="text-zinc-300">•</span>
                    <span>{new Date(post.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                </div>
            </div>
        </div>

        <button class="text-zinc-300 hover:text-zinc-600 font-black tracking-widest text-xs transition-colors">
            •••
        </button>
    </div>

    <div class="p-5">
        <p class="text-zinc-800 text-[15px] leading-relaxed whitespace-pre-wrap font-medium">
            {post.content}
        </p>
        
        {#if post.image_url}
             <div class="mt-4 rounded-lg overflow-hidden border border-zinc-200 shadow-sm relative group/img">
                 <div class="absolute inset-0 bg-black/0 group-hover/img:bg-black/5 transition-colors"></div>
                 <img src={post.image_url} alt="Attachment" class="w-full h-auto object-cover max-h-[500px]" />
             </div>
        {/if}
    </div>

    <div class="px-5 py-3 flex items-center justify-between border-t border-zinc-100 bg-zinc-50">
        
        <div class="flex items-center gap-1">
            <button 
                on:click={handleLikePost}
                class="flex items-center gap-2 px-3 py-2 rounded-lg transition-all group/btn active:scale-95 hover:bg-white hover:shadow-sm border border-transparent hover:border-zinc-200"
            >
                <span class="text-lg transition-transform duration-300 {likeBounce ? 'scale-150' : 'group-hover/btn:scale-110'} {post.is_liked ? 'grayscale-0' : 'grayscale opacity-50'}">
                    ❤️
                </span>
                <span class="text-xs font-bold {post.is_liked ? 'text-zinc-900' : 'text-zinc-500'}">
                    {post.like_count}
                </span>
            </button>

            <button 
                on:click={toggleComments}
                class="flex items-center gap-2 px-3 py-2 rounded-lg transition-all group/btn active:scale-95 hover:bg-white hover:shadow-sm border border-transparent hover:border-zinc-200"
            >
                <span class="text-lg grayscale opacity-50 group-hover/btn:grayscale-0 group-hover/btn:opacity-100 group-hover/btn:scale-110 transition-all">💬</span>
                <span class="text-xs font-bold text-zinc-500 group-hover/btn:text-zinc-900">
                    {post.comment_count}
                </span>
            </button>
        </div>

        <button class="text-zinc-400 hover:text-zinc-900 transition-colors">
            <span class="text-xs font-black uppercase tracking-widest">Share</span>
        </button>
    </div>

    {#if showComments}
        <div transition:slide={{ duration: 300, easing: quintOut }} class="bg-zinc-50 border-t border-zinc-200">
            
            <div class="p-5 space-y-6">
                {#if loadingComments}
                      <div class="flex justify-center py-4">
                          <div class="w-6 h-6 border-2 border-zinc-300 border-t-zinc-900 rounded-full animate-spin"></div>
                      </div>
                {:else if comments.length === 0}
                    <div class="text-center py-8 opacity-50">
                        <div class="text-2xl mb-1">💭</div>
                        <div class="text-xs font-bold uppercase text-zinc-400">Quiet in here</div>
                    </div>
                {:else}
                    {#each comments as comment}
                        <div class="flex gap-3 group/comment relative">
                            <div class="absolute top-8 left-[14px] bottom-[-24px] w-[2px] bg-zinc-200 group-last/comment:hidden"></div>

                            <div class="relative z-10">
                                <div class="w-7 h-7 rounded bg-white border border-zinc-300 flex items-center justify-center text-[10px] font-black text-zinc-500 shadow-sm">
                                    {(comment.author?.full_name || 'U')[0]}
                                </div>
                            </div>

                            <div class="flex-1">
                                <div class="flex items-baseline justify-between">
                                    <div class="flex items-center gap-2">
                                        <span class="text-xs font-bold text-zinc-900">{comment.author?.full_name || 'Unknown'}</span>
                                        <span class="text-[9px] font-mono text-zinc-400">{new Date(comment.created_at).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}</span>
                                    </div>
                                    
                                    <button 
                                        on:click={() => handleLikeComment(comment)}
                                        class="text-[9px] font-bold flex items-center gap-1 hover:text-red-500 transition-colors {comment.is_liked ? 'text-red-500' : 'text-zinc-300'}"
                                    >
                                        {comment.is_liked ? '❤️' : '♡'} {comment.like_count || ''}
                                    </button>
                                </div>
                                <p class="text-xs text-zinc-700 mt-1 leading-relaxed">{comment.content}</p>
                            </div>
                        </div>
                    {/each}
                {/if}
            </div>

            <div class="p-4 bg-white border-t border-zinc-200 flex gap-3 items-end">
                <div class="w-8 h-8 rounded bg-zinc-100 flex items-center justify-center text-xs font-bold text-zinc-400 shrink-0">
                    {currentUser?.full_name ? currentUser.full_name[0] : '?'}
                </div>
                
                <div class="flex-grow relative group/input">
                    <textarea 
                        bind:value={newCommentText}
                        on:keydown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handlePostComment())}
                        placeholder="Write a reply..." 
                        rows="1"
                        class="w-full bg-zinc-100 border-2 border-transparent focus:border-zinc-300 rounded-xl px-3 py-2 text-sm text-zinc-800 placeholder-zinc-400 focus:outline-none focus:bg-white transition-all resize-none overflow-hidden min-h-[40px]"
                        disabled={isSubmitting}
                    ></textarea>
                </div>

                <button 
                    on:click={handlePostComment}
                    disabled={!newCommentText.trim() || isSubmitting}
                    class="h-10 w-10 flex items-center justify-center rounded-xl bg-zinc-900 text-white hover:bg-blue-600 disabled:opacity-50 disabled:bg-zinc-300 transition-all active:scale-95 shadow-sm"
                >
                    <span class="text-xs">➤</span>
                </button>
            </div>

        </div>
    {/if}
</div>