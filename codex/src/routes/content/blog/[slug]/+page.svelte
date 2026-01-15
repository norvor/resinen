<script lang="ts">
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';
    import { api, type BlogPost } from '$lib/api';
    import { Save, ArrowLeft, Loader } from 'lucide-svelte';

    let loading = false;
    let isNew = false;
    
    // Default State
    let post: BlogPost = {
        slug: "", title: "", summary: "", content: "", 
        cover_image: "", category: "General", published: false
    };

    onMount(async () => {
        const slug = $page.params.slug;
        if (slug === 'new') {
            isNew = true;
        } else {
            try {
                post = await api.getPosts().then(posts => posts.find(p => p.slug === slug) || post);
            } catch(e) {
                console.error("Failed to load post");
            }
        }
    });

    async function save() {
        if (!post.slug) return alert("Slug is required");
        loading = true;
        try {
            await api.savePost(post);
            goto('/content/blog');
        } catch (e) {
            alert("Error saving post.");
        }
        loading = false;
    }
</script>

<div class="p-8 max-w-5xl mx-auto pb-32">
    <div class="flex items-center justify-between mb-8">
        <button on:click={() => goto('/content/blog')} class="flex items-center gap-2 text-gray-500 hover:text-white transition-colors">
            <ArrowLeft size={18} /> Back
        </button>
        <div class="flex gap-4">
            <label class="flex items-center gap-2 bg-gray-900 border border-gray-700 px-4 py-2 rounded cursor-pointer hover:bg-gray-800">
                <input type="checkbox" bind:checked={post.published} class="accent-green-500" />
                <span class="text-sm font-bold text-gray-300">Published</span>
            </label>
            <button on:click={save} class="flex items-center gap-2 bg-pink-600 hover:bg-pink-500 text-white px-6 py-2 rounded font-bold transition-colors">
                {#if loading}<Loader class="animate-spin" size={18}/>{:else}<Save size={18}/>{/if} Save Post
            </button>
        </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div class="lg:col-span-2 space-y-6">
            <input bind:value={post.title} placeholder="Transmission Title" class="w-full bg-transparent border-b border-gray-800 text-4xl font-bold text-white focus:border-pink-500 outline-none py-4 placeholder-gray-700" />
            
            <textarea bind:value={post.content} placeholder="Write your transmission here... (Markdown supported)" rows="20" class="w-full bg-gray-900/50 border border-gray-800 rounded-xl p-6 text-gray-300 focus:border-pink-500 outline-none font-mono leading-relaxed resize-y"></textarea>
        </div>

        <div class="space-y-6">
            <div class="bg-gray-900 border border-gray-800 p-6 rounded-xl space-y-4">
                <h3 class="text-sm font-bold text-white uppercase tracking-widest border-b border-gray-800 pb-2">Meta Data</h3>
                
                <div>
                    <label class="block text-xs text-gray-500 uppercase mb-1">Slug (URL)</label>
                    <input bind:value={post.slug} disabled={!isNew} class="w-full bg-gray-950 border border-gray-700 rounded p-2 text-white disabled:opacity-50" />
                </div>

                <div>
                    <label class="block text-xs text-gray-500 uppercase mb-1">Category</label>
                    <input bind:value={post.category} class="w-full bg-gray-950 border border-gray-700 rounded p-2 text-white" />
                </div>

                <div>
                    <label class="block text-xs text-gray-500 uppercase mb-1">Summary / Excerpt</label>
                    <textarea bind:value={post.summary} rows="4" class="w-full bg-gray-950 border border-gray-700 rounded p-2 text-white text-sm"></textarea>
                </div>

                <div>
                    <label class="block text-xs text-gray-500 uppercase mb-1">Cover Image URL</label>
                    <input bind:value={post.cover_image} class="w-full bg-gray-950 border border-gray-700 rounded p-2 text-white" />
                </div>
            </div>
        </div>
    </div>
</div>