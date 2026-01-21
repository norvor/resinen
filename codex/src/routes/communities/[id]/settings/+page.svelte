<script lang="ts">
    import { api } from '$lib/api';
    export let data;
    
    let { community } = data;
    let loading = false;
    let success = false;

    async function handleSave() {
        loading = true;
        try {
            await api.updateCommunity(community.id, {
                name: community.name,
                description: community.description,
                slug: community.slug,
                is_private: community.is_private
            });
            success = true;
            setTimeout(() => success = false, 3000);
        } catch (e) {
            alert("Failed to save changes.");
        } finally {
            loading = false;
        }
    }
</script>

<div class="max-w-3xl space-y-8 animate-fade-in-up">
    
    <div class="border-b-4 border-black pb-6">
        <h1 class="text-4xl font-black uppercase tracking-tighter">Settings</h1>
        <p class="text-gray-500 font-bold mt-2">Manage global configuration for {community.name}.</p>
    </div>

    <div class="bg-white border-2 border-gray-200 rounded-xl p-8 space-y-6">
        <div class="grid gap-6">
            
            <div>
                <label class="block text-xs font-black uppercase text-gray-500 mb-2">Community Name</label>
                <input bind:value={community.name} class="w-full text-xl font-bold border-b-2 border-gray-200 focus:border-black outline-none py-2 transition-colors bg-transparent" />
            </div>

            <div>
                <label class="block text-xs font-black uppercase text-gray-500 mb-2">URL Slug</label>
                <div class="flex items-center">
                    <span class="text-gray-400 font-bold mr-1">resinen.com/c/</span>
                    <input bind:value={community.slug} class="flex-1 font-mono font-bold text-gray-600 border-b-2 border-gray-200 focus:border-black outline-none py-2 transition-colors bg-transparent" />
                </div>
            </div>

            <div>
                <label class="block text-xs font-black uppercase text-gray-500 mb-2">Description</label>
                <textarea bind:value={community.description} class="w-full font-bold text-gray-600 border-2 border-gray-200 rounded-lg p-4 focus:border-black outline-none transition-colors h-32 resize-none"></textarea>
            </div>

            <div class="flex items-center justify-between py-4 border-t border-gray-100">
                <div>
                    <div class="font-bold text-gray-900">Private Community</div>
                    <div class="text-xs text-gray-500">Only approved members can view content.</div>
                </div>
                <label class="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" bind:checked={community.is_private} class="sr-only peer">
                    <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-black"></div>
                </label>
            </div>

        </div>

        <div class="flex justify-end pt-6">
            <button 
                on:click={handleSave} 
                disabled={loading}
                class="px-8 py-3 bg-black text-white font-black uppercase text-xs rounded shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all disabled:opacity-50 disabled:translate-y-0"
            >
                {loading ? 'Saving...' : success ? 'Saved!' : 'Save Changes'}
            </button>
        </div>
    </div>

    <div class="bg-red-50 border-2 border-red-100 rounded-xl p-8 mt-12">
        <h3 class="font-black text-red-700 uppercase mb-2">Danger Zone</h3>
        <p class="text-xs text-red-600 font-bold mb-6">Once you delete a community, there is no going back. Please be certain.</p>
        
        <button class="px-6 py-2 border-2 border-red-200 text-red-600 font-black uppercase text-xs rounded hover:bg-red-600 hover:text-white transition-colors">
            Delete Community
        </button>
    </div>

</div>