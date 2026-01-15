<script lang="ts">
    import { onMount } from 'svelte';
    import { api, type BlogPost } from '$lib/api';
    import { Plus, PenTool, Trash2, Edit } from 'lucide-svelte';

    let posts: BlogPost[] = [];
    let loading = true;

    async function load() {
        posts = await api.getPosts();
        loading = false;
    }

    async function deletePost(slug: string) {
        if(!confirm('Delete this transmission?')) return;
        await api.deletePost(slug);
        load();
    }

    onMount(load);
</script>

<div class="p-8 max-w-7xl mx-auto">
    <div class="flex justify-between items-center mb-8">
        <div>
            <h1 class="text-3xl font-bold text-white mb-2">Transmissions</h1>
            <p class="text-gray-400">Manage blog posts and intelligence briefings.</p>
        </div>
        <a href="/content/blog/new" class="flex items-center gap-2 bg-pink-600 hover:bg-pink-500 text-white px-4 py-2 rounded font-bold transition-colors">
            <Plus size={18} /> New Transmission
        </a>
    </div>

    {#if loading}
        <div class="text-gray-500">Loading feed...</div>
    {:else if posts.length === 0}
        <div class="p-12 text-center border border-dashed border-gray-800 rounded text-gray-500">
            No transmissions found.
        </div>
    {:else}
        <div class="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
            <table class="w-full text-left">
                <thead class="bg-gray-950 text-gray-500 text-xs uppercase font-mono">
                    <tr>
                        <th class="p-4">Title</th>
                        <th class="p-4">Category</th>
                        <th class="p-4">Status</th>
                        <th class="p-4 text-right">Actions</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-800">
                    {#each posts as post}
                        <tr class="hover:bg-gray-800/50 transition-colors">
                            <td class="p-4">
                                <div class="font-bold text-white">{post.title}</div>
                                <div class="text-xs text-gray-500 font-mono">{post.slug}</div>
                            </td>
                            <td class="p-4 text-sm text-gray-400">{post.category}</td>
                            <td class="p-4">
                                <span class={`px-2 py-1 rounded text-xs font-bold ${post.published ? 'bg-green-900/30 text-green-400' : 'bg-yellow-900/30 text-yellow-400'}`}>
                                    {post.published ? 'PUBLISHED' : 'DRAFT'}
                                </span>
                            </td>
                            <td class="p-4 text-right flex justify-end gap-3">
                                <a href={`/content/blog/${post.slug}`} class="p-2 bg-gray-800 rounded hover:text-white text-gray-400">
                                    <Edit size={16} />
                                </a>
                                <button on:click={() => deletePost(post.slug)} class="p-2 bg-gray-800 rounded hover:text-red-400 text-gray-400">
                                    <Trash2 size={16} />
                                </button>
                            </td>
                        </tr>
                    {/each}
                </tbody>
            </table>
        </div>
    {/if}
</div>