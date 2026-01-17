<script lang="ts">
    import { page } from '$app/stores';
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    import { goto } from '$app/navigation';

    const communityId = $page.params.id;
    let name = '';
    let description = '';
    let isSubmitting = false;

    onMount(async () => {
        const c = await api.getCommunity(communityId);
        if (c) {
            name = c.name;
            description = c.description;
        }
    });

    async function handleUpdate() {
        isSubmitting = true;
        try {
            await api.updateCommunity(communityId, { name, description });
            goto(`/communities/${communityId}`);
        } catch (e) {
            alert('Update failed');
            isSubmitting = false;
        }
    }

    async function handleDelete() {
        if(!confirm("Are you sure? This will delete all chapters and data.")) return;
        try {
            await api.deleteCommunity(communityId);
            goto('/communities');
        } catch (e) {
            alert('Delete failed');
        }
    }
</script>

<div class="max-w-2xl mx-auto mt-8">
    <a href="/communities/{communityId}" class="text-slate-500 hover:text-white mb-6 inline-block">&larr; Back</a>

    <div class="bg-slate-950 border border-slate-800 rounded-2xl p-8">
        <h1 class="text-2xl font-bold text-white mb-6">Community Settings</h1>

        <div class="space-y-6">
            <div>
                <label class="block text-slate-400 text-sm font-bold mb-2">Name</label>
                <input bind:value={name} class="w-full bg-slate-900 border border-slate-800 text-white p-4 rounded-xl"/>
            </div>
            
            <div>
                <label class="block text-slate-400 text-sm font-bold mb-2">Description</label>
                <textarea bind:value={description} rows="4" class="w-full bg-slate-900 border border-slate-800 text-white p-4 rounded-xl"></textarea>
            </div>

            <div class="flex gap-4 pt-4">
                <button on:click={handleUpdate} disabled={isSubmitting} class="flex-1 bg-orange-600 hover:bg-orange-500 text-white font-bold py-4 rounded-xl">
                    {isSubmitting ? 'SAVING...' : 'SAVE CHANGES'}
                </button>
                
                <button on:click={handleDelete} class="px-6 bg-red-900/20 hover:bg-red-900/40 text-red-500 border border-red-900/50 font-bold rounded-xl">
                    DELETE
                </button>
            </div>
        </div>
    </div>
</div>