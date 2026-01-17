<script lang="ts">
    import { api } from '$lib/api';
    import { goto } from '$app/navigation';

    let name = '';
    let slug = '';
    let description = '';
    let isSubmitting = false;

    // Auto-generate slug from name
    $: slug = name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');

    async function handleSubmit() {
        if (!name || !slug) return;
        isSubmitting = true;
        
        try {
            await api.createCommunity({ name, slug, description });
            goto('/communities');
        } catch (e) {
            alert('Failed to create community. Slug might be taken.');
            isSubmitting = false;
        }
    }
</script>

<div class="max-w-2xl mx-auto">
    <a href="/communities" class="text-slate-500 hover:text-white mb-6 inline-block text-sm">&larr; Back to Dashboard</a>
    
    <div class="bg-slate-950 border border-slate-800 rounded-2xl p-8 shadow-2xl">
        <h1 class="text-2xl font-bold text-white mb-6">Initialize Community</h1>

        <div class="space-y-6">
            <div>
                <label class="block text-slate-400 text-sm font-bold mb-2">Community Name</label>
                <input 
                    bind:value={name}
                    type="text" 
                    placeholder="e.g. The Architects Guild" 
                    class="w-full bg-slate-900 border border-slate-800 text-white p-4 rounded-xl focus:ring-1 focus:ring-orange-500 outline-none transition-all"
                />
            </div>

            <div>
                <label class="block text-slate-400 text-sm font-bold mb-2">URL Slug (Unique ID)</label>
                <div class="flex">
                    <span class="bg-slate-900 border border-slate-800 border-r-0 text-slate-500 p-4 rounded-l-xl select-none">resinen.com/</span>
                    <input 
                        bind:value={slug}
                        type="text" 
                        class="w-full bg-slate-900 border border-slate-800 text-orange-400 p-4 rounded-r-xl focus:ring-1 focus:ring-orange-500 outline-none font-mono"
                    />
                </div>
            </div>

            <div>
                <label class="block text-slate-400 text-sm font-bold mb-2">Manifesto / Description</label>
                <textarea 
                    bind:value={description}
                    rows="4"
                    placeholder="What is this community about?" 
                    class="w-full bg-slate-900 border border-slate-800 text-white p-4 rounded-xl focus:ring-1 focus:ring-orange-500 outline-none transition-all"
                ></textarea>
            </div>

            <button 
                on:click={handleSubmit}
                disabled={isSubmitting}
                class="w-full bg-orange-600 hover:bg-orange-500 text-white font-bold py-4 rounded-xl transition-all shadow-lg shadow-orange-900/20"
            >
                {isSubmitting ? 'INITIALIZING...' : 'LAUNCH COMMUNITY'}
            </button>
        </div>
    </div>
</div>