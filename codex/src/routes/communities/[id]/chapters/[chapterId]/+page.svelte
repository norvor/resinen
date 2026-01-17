<script lang="ts">
    import { page } from '$app/stores';
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    import Feed from '$lib/components/Feed.svelte'; // Import the component

    const communityId = $page.params.id;
    const chapterId = $page.params.chapterId;
    let chapter: any = null;

    onMount(async () => {
        chapter = await api.getChapter(chapterId);
    });
</script>

<div class="max-w-4xl mx-auto">
    <div class="mb-6 flex justify-between items-center">
        <a href="/communities/{communityId}" class="text-slate-500 hover:text-white text-sm">&larr; Back to HQ</a>
        
        {#if chapter}
            <a href="/communities/{communityId}/chapters/{chapterId}/edit" class="text-slate-500 hover:text-orange-500 text-sm">
                ⚙ Manage Chapter
            </a>
        {/if}
    </div>

    {#if chapter}
        <div class="mb-8">
            <h1 class="text-3xl font-bold text-white">{chapter.name}</h1>
            <p class="text-slate-400">Location: {chapter.location}</p>
        </div>

        <Feed {communityId} {chapterId} />

    {:else}
        <div class="text-slate-500">Loading Channel...</div>
    {/if}
</div>