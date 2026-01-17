<script lang="ts">
    import { page } from '$app/stores';
    import { api, user } from '$lib/api';
    import { onMount } from 'svelte';

    let community: any = null;
    let posts: any[] = [];
    let loading = true;
    let newPostTitle = '';
    let newPostBody = '';

    onMount(async () => {
        // 1. Get Community Info (Branding, Rules)
        community = await api('GET', `/communities/lookup?slug=${$page.params.slug}`);
        
        // 2. Get The Local Feed
        posts = await api('GET', `/social/feed?scope=community&community_id=${community.id}`);
        loading = false;
    });

    async function handlePost() {
        try {
            const post = await api('POST', '/social/posts', {
                community_id: community.id,
                title: newPostTitle,
                body: newPostBody,
                slug: newPostTitle.toLowerCase().replace(/ /g, '-')
            });
            posts = [post, ...posts]; // Optimistic update
            newPostTitle = '';
            newPostBody = '';
        } catch (e: any) {
            alert('LAW VIOLATION: ' + e.message); // Show the Sheriff's error
        }
    }
</script>

{#if loading}
    <div class="p-12 text-center animate-pulse">Entering Territory...</div>
{:else}
    <div class="bg-sp-cyan border-b-4 border-black p-8 relative overflow-hidden">
        <h1 class="text-5xl font-black uppercase text-white drop-shadow-hard relative z-10">
            {community.name}
        </h1>
        <p class="font-bold text-black mt-2 relative z-10 bg-white/50 inline-block px-2">
            {community.description}
        </p>
        
        <div class="absolute top-4 right-4 bg-white border-4 border-black px-4 py-2 font-black rotate-2 shadow-hard">
            {community.member_count} CITIZENS
        </div>
    </div>

    <div class="max-w-4xl mx-auto p-4 grid grid-cols-1 md:grid-cols-3 gap-8 mt-6">
        
        <div class="md:col-span-2 space-y-6">
            
            <div class="bg-white border-4 border-black p-4 shadow-hard">
                <input bind:value={newPostTitle} class="w-full font-black text-xl outline-none mb-2" placeholder="Speak your mind..." />
                <textarea bind:value={newPostBody} class="w-full resize-none outline-none font-medium text-gray-600" rows="2" placeholder="Elaborate..."></textarea>
                <div class="flex justify-between items-center mt-2 pt-2 border-t-2 border-gray-100">
                    <span class="text-xs font-bold text-gray-400 uppercase">遵循 Bylaws</span>
                    <button on:click={handlePost} class="bg-black text-white font-black uppercase px-6 py-2 hover:bg-sp-green hover:text-black transition-colors">
                        Post
                    </button>
                </div>
            </div>

            {#each posts as post}
                <div class="bg-white border-4 border-black p-6 shadow-hard hover:translate-x-1 hover:translate-y-1 transition-transform cursor-pointer">
                    <div class="flex justify-between items-start mb-2">
                        <div class="flex items-center gap-2">
                            <div class="w-8 h-8 bg-gray-200 rounded-full border-2 border-black"></div>
                            <span class="font-black text-sm">{post.author?.full_name || 'Citizen'}</span>
                        </div>
                        <span class="text-xs font-mono text-gray-400">{new Date(post.created_at).toLocaleDateString()}</span>
                    </div>
                    <h3 class="text-2xl font-black uppercase leading-tight">{post.title}</h3>
                    <p class="mt-2 text-gray-800 font-medium line-clamp-3">{post.body}</p>
                    
                    <div class="mt-4 flex gap-4 text-xs font-bold uppercase">
                        <button class="hover:text-sp-blue">Like ({post.likes?.length || 0})</button>
                        <button class="hover:text-sp-blue">Comment ({post.comments?.length || 0})</button>
                    </div>
                </div>
            {/each}
        </div>

        <div class="space-y-6">
            <div class="bg-yellow-300 border-4 border-black p-4 shadow-hard -rotate-1">
                <h3 class="font-black uppercase border-b-4 border-black pb-2 mb-2">Local Bylaws</h3>
                <ul class="list-disc list-inside font-bold text-sm space-y-1">
                    <li>No Hate Speech</li>
                    <li>Respect the Canon</li>
                    <li>English Only</li>
                </ul>
            </div>
            
            <a href="/governance" class="block bg-sp-red border-4 border-black p-4 text-white font-black uppercase text-center hover:scale-105 transition-transform">
                View Court Docket
            </a>
        </div>

    </div>
{/if}