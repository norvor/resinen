<script lang="ts">
    import { page } from '$app/stores';
    import { api } from '$lib/api';
    import { goto } from '$app/navigation';

    const communityId = $page.params.id;
    
    let name = '';
    let location = ''; // <--- CHANGED VARIABLE
    let isSubmitting = false;

    async function handleSubmit() {
        if (!name || !location) return;
        isSubmitting = true;
        
        try {
            await api.createChapter({ 
                community_id: communityId, 
                name, 
                location // <--- SENDS 'location'
            });
            goto(`/communities/${communityId}`);
        } catch (e) {
            alert('Failed to create chapter.');
            console.error(e);
            isSubmitting = false;
        }
    }
</script>

<div class="max-w-xl mx-auto mt-12">
    <div class="bg-slate-950 border border-slate-800 rounded-2xl p-8 shadow-2xl">
        <h1 class="text-2xl font-bold text-white mb-6">Add New Chapter</h1>
        <div class="space-y-6">
            <div>
                <label class="block text-slate-400 text-sm font-bold mb-2">Chapter Name</label>
                <input bind:value={name} type="text" class="w-full bg-slate-900 border border-slate-800 text-white p-4 rounded-xl focus:ring-1 focus:ring-orange-500 outline-none" />
            </div>

            <div>
                <label class="block text-slate-400 text-sm font-bold mb-2">Location</label>
                <input 
                    bind:value={location} 
                    type="text"
                    placeholder="e.g. London" 
                    class="w-full bg-slate-900 border border-slate-800 text-white p-4 rounded-xl focus:ring-1 focus:ring-orange-500 outline-none"
                />
            </div>

            <button on:click={handleSubmit} disabled={isSubmitting} class="w-full bg-orange-600 hover:bg-orange-500 text-white font-bold py-4 rounded-xl transition-all">
                {isSubmitting ? 'CREATING...' : 'CREATE CHAPTER'}
            </button>
        </div>
    </div>
</div>