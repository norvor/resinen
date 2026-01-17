<script lang="ts">
    import { page } from '$app/stores';
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    import { goto } from '$app/navigation';

    const communityId = $page.params.id;
    const chapterId = $page.params.chapterId;

    let name = '';
    let location = '';
    let isSubmitting = false;

    onMount(async () => {
        const ch = await api.getChapter(chapterId);
        name = ch.name;
        location = ch.location;
    });

    async function handleUpdate() {
        isSubmitting = true;
        try {
            await api.updateChapter(chapterId, { name, location });
            goto(`/communities/${communityId}`);
        } catch (e) {
            alert('Update failed');
            isSubmitting = false;
        }
    }

    async function handleDelete() {
        if(!confirm("Delete this chapter?")) return;
        await api.deleteChapter(chapterId);
        goto(`/communities/${communityId}`);
    }
</script>

<div class="max-w-xl mx-auto mt-12">
    <a href="/communities/{communityId}" class="text-slate-500 hover:text-white mb-6 inline-block">&larr; Cancel</a>

    <div class="bg-slate-950 border border-slate-800 rounded-2xl p-8">
        <h1 class="text-2xl font-bold text-white mb-6">Edit Chapter</h1>

        <div class="space-y-6">
            <div>
                <label class="block text-slate-400 text-sm font-bold mb-2">Name</label>
                <input bind:value={name} class="w-full bg-slate-900 border border-slate-800 text-white p-4 rounded-xl"/>
            </div>

            <div>
                <label class="block text-slate-400 text-sm font-bold mb-2">Location</label>
                <input bind:value={location} class="w-full bg-slate-900 border border-slate-800 text-white p-4 rounded-xl"/>
            </div>

            <div class="flex gap-4">
                <button on:click={handleUpdate} class="flex-1 bg-orange-600 hover:bg-orange-500 text-white font-bold py-4 rounded-xl">
                    SAVE
                </button>
                <button on:click={handleDelete} class="px-6 bg-red-900/20 text-red-500 border border-red-900/50 font-bold rounded-xl">
                    DELETE
                </button>
            </div>
        </div>
    </div>
</div>