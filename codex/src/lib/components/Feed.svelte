<script lang="ts">
    import { onMount } from 'svelte';
    import { api, type Post } from '$lib/api';

    export let communityId: string;
    export let chapterId: string | undefined = undefined;

    let posts: Post[] = [];
    let newPostContent = '';
    let isPosting = false;

    // Comment State
    let replyingToId: string | null = null;
    let replyContent = '';

    async function loadFeed() {
        try {
            posts = await api.getFeed(communityId, chapterId);
        } catch (e) {
            console.error(e);
        }
    }

    async function handlePost() {
        if (!newPostContent.trim()) return;
        isPosting = true;
        try {
            const post = await api.createPost({
                community_id: communityId,
                chapter_id: chapterId,
                content: newPostContent
            });
            posts = [post, ...posts];
            newPostContent = '';
        } catch (e) {
            alert('Failed to post');
        } finally {
            isPosting = false;
        }
    }

    async function handleReply(post: Post) {
        if (!replyContent.trim()) return;
        try {
            const newComment = await api.createComment(post.id, replyContent);
            const updatedPosts = posts.map(p => {
                if (p.id === post.id) {
                    return { ...p, comments: [...(p.comments || []), newComment] };
                }
                return p;
            });
            posts = updatedPosts;
            replyContent = '';
            replyingToId = null;
        } catch (e) {
            alert('Failed to reply');
        }
    }

    async function handleLike(post: Post) {
        try {
            // Optimistic Update
            const wasLiked = post.is_liked;
            const updatedPosts = posts.map(p => {
                if (p.id === post.id) {
                    return {
                        ...p,
                        is_liked: !wasLiked,
                        like_count: wasLiked ? p.like_count - 1 : p.like_count + 1
                    };
                }
                return p;
            });
            posts = updatedPosts;

            // API Call
            await api.toggleLike(post.id);
        } catch (e) {
            console.error(e);
            // Revert on failure (could implement reload here)
        }
    }

    onMount(loadFeed);
</script>

<div class="space-y-6">
    <div class="bg-slate-900/50 border border-slate-800 rounded-xl p-4 shadow-lg">
        <textarea 
            bind:value={newPostContent}
            rows="3"
            placeholder="Share something with this chapter..."
            class="w-full bg-transparent text-white placeholder-slate-500 outline-none resize-none"
        ></textarea>
        <div class="flex justify-end mt-2">
            <button 
                on:click={handlePost}
                disabled={isPosting || !newPostContent}
                class="bg-orange-600 hover:bg-orange-500 disabled:opacity-50 text-white px-4 py-2 rounded-lg font-bold text-sm transition-all"
            >
                {isPosting ? 'Posting...' : 'Post Update'}
            </button>
        </div>
    </div>

    <div class="space-y-4">
        {#each posts as post (post.id)}
            <div class="bg-slate-950 border border-slate-800 rounded-xl p-6 shadow-md transition-colors hover:border-slate-700">
                <div class="flex items-start gap-3 mb-4">
                    <div class="h-10 w-10 rounded-full bg-gradient-to-br from-orange-600 to-purple-700 flex items-center justify-center text-sm font-bold text-white shadow-lg shrink-0">
                        {post.author_name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                        <div class="flex items-baseline gap-2">
                            <span class="text-sm font-bold text-white">{post.author_name}</span>
                            <span class="text-[10px] text-slate-500 font-mono">{new Date(post.created_at).toLocaleDateString()}</span>
                        </div>
                        <p class="text-slate-200 mt-1 whitespace-pre-wrap text-sm leading-relaxed">{post.content}</p>
                    </div>
                </div>

                <div class="ml-12 flex items-center gap-6 border-t border-slate-900 pt-3 select-none">
                    
                    <button 
                        on:click={() => { replyingToId = replyingToId === post.id ? null : post.id }}
                        class="text-xs text-slate-500 hover:text-white font-bold flex items-center gap-1.5 transition-colors group"
                    >
                        <span class="group-hover:text-blue-400">💬</span> 
                        {post.comments ? post.comments.length : 0} <span class="hidden sm:inline">Comments</span>
                    </button>

                    <button 
                        on:click={() => handleLike(post)}
                        class="text-xs font-bold flex items-center gap-1.5 transition-all group {post.is_liked ? 'text-red-500' : 'text-slate-500 hover:text-white'}"
                    >
                        <span class="transform transition-transform group-active:scale-125 {post.is_liked ? 'scale-110' : ''}">
                            {post.is_liked ? '❤️' : '🤍'}
                        </span> 
                        {post.like_count} <span class="hidden sm:inline">Likes</span>
                    </button>
                </div>

                {#if (post.comments && post.comments.length > 0) || replyingToId === post.id}
                    <div class="ml-12 mt-4 space-y-3 bg-slate-900/20 rounded-lg p-4">
                        {#if post.comments}
                            {#each post.comments as comment}
                                <div class="flex gap-3">
                                    <div class="h-6 w-6 rounded-full bg-slate-800 flex items-center justify-center text-[10px] text-slate-400 shrink-0 border border-slate-700">
                                        {comment.author_name.charAt(0)}
                                    </div>
                                    <div>
                                        <div class="flex items-center gap-2">
                                            <span class="text-xs font-bold text-slate-400">{comment.author_name}</span>
                                            <span class="text-[10px] text-slate-600">{new Date(comment.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                                        </div>
                                        <p class="text-xs text-slate-300 mt-0.5">{comment.content}</p>
                                    </div>
                                </div>
                            {/each}
                        {/if}

                        {#if replyingToId === post.id}
                            <div class="flex gap-2 mt-4 animate-in fade-in slide-in-from-top-2 duration-200">
                                <input 
                                    bind:value={replyContent}
                                    type="text" 
                                    placeholder="Write a reply..." 
                                    class="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:border-orange-500 outline-none"
                                    on:keydown={(e) => e.key === 'Enter' && handleReply(post)}
                                    autoFocus
                                />
                                <button on:click={() => handleReply(post)} class="bg-orange-600 hover:bg-orange-500 text-white px-3 py-2 rounded-lg text-xs font-bold">Send</button>
                            </div>
                        {/if}
                    </div>
                {/if}
            </div>
        {:else}
            <div class="text-center text-slate-600 py-12 bg-slate-950/50 rounded-xl border border-dashed border-slate-800">
                It's quiet here... be the first to speak.
            </div>
        {/each}
    </div>
</div>