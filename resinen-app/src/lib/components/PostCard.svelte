<script lang="ts">
    import { api, type Post, type Comment, type User } from '$lib/api';
    import { createEventDispatcher } from 'svelte';

    export let post: Post;
    export let currentUser: User | null;

    const dispatch = createEventDispatcher();

    // --- COMMENT STATE ---
    let showComments = false;
    let comments: Comment[] = [];
    let loadingComments = false;
    let newCommentText = "";
    let isSubmitting = false;

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
            comments = await api.getComments(post.id);
        } catch (e) {
            console.error(e);
        } finally {
            loadingComments = false;
        }
    }

    async function handlePostComment() {
        if (!newCommentText.trim()) return;
        isSubmitting = true;
        try {
            const newComment = await api.createComment(post.id, newCommentText);
            comments = [...comments, newComment]; // Add to list
            post.comment_count++; // Update UI counter instantly
            newCommentText = "";
        } catch (e) {
            console.error(e);
            alert("Failed to post comment.");
        } finally {
            isSubmitting = false;
        }
    }

    async function handleLikePost() {
        if (post.is_liked) return;
        // Optimistic UI Update
        post.is_liked = true;
        post.like_count++;
        try {
            await api.likePost(post.id);
        } catch (e) {
            console.error(e);
            post.is_liked = false; // Revert if failed
            post.like_count--;
        }
    }

    async function handleLikeComment(comment: Comment) {
        if (comment.is_liked) return;
        
        // Optimistic UI Update
        comment.is_liked = true;
        comment.like_count++;
        comments = comments; // Trigger reactivity

        try {
            await api.likeComment(comment.id);
        } catch (e) {
            console.error(e);
        }
    }
</script>

<div class="bg-white md:rounded-xl shadow-sm border border-gray-200 overflow-hidden mb-4">
    
    <div class="p-4 flex items-center gap-3">
        <div class="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold shrink-0 shadow-inner">
            {#if post.author_avatar}
                <img src={post.author_avatar} alt={post.author_name} class="w-full h-full rounded-full object-cover" />
            {:else}
                {post.author_name[0]}
            {/if}
        </div>
        <div>
            <div class="flex items-center gap-2">
                <span class="font-bold text-gray-900 text-sm">{post.author_name}</span>
                {#if post.author_level > 1}
                    <span class="bg-black text-white text-[10px] px-1.5 py-0.5 font-bold uppercase rounded">LVL {post.author_level}</span>
                {/if}
            </div>
            <div class="text-xs text-gray-500">{new Date(post.created_at).toLocaleDateString()}</div>
        </div>
    </div>

    <div class="px-4 pb-2">
        <p class="text-gray-800 text-base leading-relaxed whitespace-pre-wrap">{post.content}</p>
    </div>

    <div class="px-4 py-2 flex items-center justify-between text-xs text-gray-500 border-b border-gray-100">
        <div class="font-bold">{post.like_count} Likes</div>
        <div class="font-bold">{post.comment_count} Comments</div>
    </div>

    <div class="flex items-center border-b border-gray-100 bg-gray-50/50">
        <button 
            on:click={handleLikePost}
            class="flex-1 py-3 hover:bg-gray-100 flex items-center justify-center gap-2 transition-colors {post.is_liked ? 'text-sp-blue font-black' : 'text-gray-600 font-bold'}"
        >
            <span class="text-lg">{post.is_liked ? '★' : '☆'}</span>
            Like
        </button>
        
        <button 
            on:click={toggleComments}
            class="flex-1 py-3 hover:bg-gray-100 flex items-center justify-center gap-2 text-gray-600 font-bold transition-colors"
        >
            <span>💬</span>
            Comment
        </button>
    </div>

    {#if showComments}
        <div class="bg-gray-50 p-4 border-t border-gray-200">
            
            {#if loadingComments}
                <div class="text-center py-4 text-gray-400 text-sm font-bold animate-pulse">Loading discourse...</div>
            {:else if comments.length === 0}
                <div class="text-center py-4 text-gray-400 text-sm">No comments yet. Be the first.</div>
            {:else}
                <div class="space-y-4 mb-6">
                    {#each comments as comment}
                        <div class="flex gap-3">
                            <div class="w-8 h-8 rounded-full bg-gray-300 shrink-0 flex items-center justify-center text-xs font-bold text-gray-600">
                                {comment.author_name[0]}
                            </div>
                            
                            <div class="flex-grow">
                                <div class="bg-white p-3 rounded-lg border border-gray-200 shadow-sm">
                                    <div class="flex justify-between items-start mb-1">
                                        <span class="font-black text-xs uppercase">{comment.author_name}</span>
                                        <span class="text-[10px] text-gray-400">{new Date(comment.created_at).toLocaleDateString()}</span>
                                    </div>
                                    <p class="text-sm text-gray-800 leading-snug">{comment.content}</p>
                                </div>
                                
                                <div class="flex items-center gap-4 mt-1 ml-1">
                                    <button 
                                        on:click={() => handleLikeComment(comment)}
                                        class="text-xs font-bold flex items-center gap-1 {comment.is_liked ? 'text-blue-600' : 'text-gray-500 hover:text-black'}"
                                    >
                                        <span>{comment.is_liked ? '▲' : '△'}</span>
                                        {comment.like_count || 0}
                                    </button>
                                    <button class="text-xs font-bold text-gray-500 hover:text-black">Reply</button>
                                </div>
                            </div>
                        </div>
                    {/each}
                </div>
            {/if}

            <div class="flex gap-2 mt-4">
                <div class="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xs shrink-0">
                    {currentUser?.full_name ? currentUser.full_name[0] : '?'}
                </div>
                <div class="flex-grow relative">
                    <input 
                        bind:value={newCommentText}
                        on:keydown={(e) => e.key === 'Enter' && handlePostComment()}
                        type="text" 
                        placeholder="Add to the discussion..." 
                        class="w-full border-2 border-gray-300 rounded-lg py-2 px-3 text-sm font-bold outline-none focus:border-black focus:ring-0 transition-colors"
                        disabled={isSubmitting}
                    />
                    <button 
                        on:click={handlePostComment}
                        disabled={!newCommentText.trim() || isSubmitting}
                        class="absolute right-2 top-1.5 text-blue-600 font-black text-xs uppercase hover:underline disabled:opacity-50"
                    >
                        Post
                    </button>
                </div>
            </div>

        </div>
    {/if}
</div>