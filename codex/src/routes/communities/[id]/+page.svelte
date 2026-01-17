<script lang="ts">
    import { page } from '$app/stores';
    import { onMount } from 'svelte';
    import { api } from '$lib/api';

    const communityId = $page.params.id;

    let community: any = null;
    let chapters: any[] = [];
    let isLoading = true;

    onMount(async () => {
        try {
            const [c, ch] = await Promise.all([
                api.getCommunity(communityId),
                api.getChapters(communityId)
            ]);
            community = c;
            chapters = ch;
            
            // DEBUG: Open your browser console (F12) to see exactly what the backend sends
            console.log("Backend Chapter Data:", chapters);
            
        } catch (e) {
            console.error(e);
        } finally {
            isLoading = false;
        }
    });
</script>

<div class="max-w-5xl mx-auto">
    <a href="/communities" class="text-slate-500 hover:text-white mb-6 inline-block text-sm">&larr; Back to List</a>

    {#if isLoading}
        <div class="animate-pulse text-slate-500">Loading Control Room...</div>
    {:else if community}
        <div class="bg-slate-950 border border-slate-800 rounded-2xl p-8 mb-8 flex justify-between items-start">
            <div>
                <div class="flex items-center gap-3 mb-2">
                    <h1 class="text-3xl font-bold text-white">{community.name}</h1>
                    <span class="bg-orange-900/30 text-orange-400 text-xs font-mono px-2 py-1 rounded border border-orange-900/50">
                        {community.slug}
                    </span>
                </div>
                <p class="text-slate-400 max-w-2xl">{community.description}</p>
            </div>
            <a href="/communities/{communityId}/edit" class="text-slate-500 hover:text-white transition-colors">
                ⚙ Settings
            </a>
        </div>

        <div class="flex justify-between items-end mb-6">
            <h2 class="text-xl font-bold text-white">Chapters</h2>
            <a href="/communities/{communityId}/chapters/new" class="text-sm bg-slate-800 hover:bg-slate-700 text-white px-4 py-2 rounded-lg transition-colors border border-slate-700">
                + Add Chapter
            </a>
        </div>

        {#if chapters.length === 0}
            <div class="p-8 border border-dashed border-slate-800 rounded-2xl text-center text-slate-500">
                No chapters found. Create the first one.
            </div>
        {:else}
            <div class="bg-slate-950 border border-slate-800 rounded-2xl overflow-hidden">
                <table class="w-full text-left">
                    <thead class="bg-slate-900/50 text-slate-500 text-xs uppercase font-bold">
                        <tr>
                            <th class="p-4">Chapter Name</th>
                            <th class="p-4">Location</th>
                            <th class="p-4 text-right">Action</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-800">
                        {#each chapters as ch}
                            <tr class="hover:bg-slate-900/50 transition-colors">
                               <td class="p-4 font-bold text-white">
                                    <a href="/communities/{communityId}/chapters/{ch.id}" class="hover:underline hover:text-orange-400">
                                        {ch.name}
                                    </a>
                                </td>
                                
                                <td class="p-4 text-slate-400 text-sm">
                                    {ch.location_name || ch.location || ch.description || 'Global'}
                                </td>
                                
                                <td class="p-4 text-right">
                                    <a href="/communities/{communityId}/chapters/{ch.id}/edit" class="text-xs text-orange-500 hover:text-orange-400">
                                        Manage
                                    </a>
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        {/if}

    {:else}
        <div class="text-red-500">Community not found.</div>
    {/if}
</div>