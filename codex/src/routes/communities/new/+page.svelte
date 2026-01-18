<script lang="ts">
    import { api, type CreateCommunityDTO } from '$lib/api';
    import { goto } from '$app/navigation';

    let name = '';
    let slug = '';
    let description = '';
    let is_private = true;
    let isSubmitting = false;

    // ROOT CAUSE FIX: 
    // This reactive statement forces the slug to be lowercase-kebab-case instantly.
    // It prevents "Resinen" from ever being sent to the DB.
    $: slug = name.toLowerCase()
        .replace(/[^a-z0-9]+/g, '-') // Replace non-alphanumeric with hyphen
        .replace(/(^-|-$)/g, '');    // Remove leading/trailing hyphens

    async function handleSubmit() {
        if (!name || !slug) return;
        isSubmitting = true;

        try {
            const payload: CreateCommunityDTO = {
                name,
                slug, // This is now guaranteed to be clean
                description,
                is_private
            };

            await api.createCommunity(payload);
            goto('/communities');
            
        } catch (e: any) {
            alert(`Error: ${e.message}`);
        } finally {
            isSubmitting = false;
        }
    }
</script>

<div class="max-w-2xl mx-auto p-8">
    <div class="flex justify-between items-center mb-8">
        <h1 class="text-2xl font-bold text-white">Initialize Territory</h1>
        <a href="/communities" class="text-sm text-slate-400 hover:text-white">Cancel</a>
    </div>

    <div class="bg-slate-950 border border-slate-800 rounded-xl p-8 space-y-6">
        
        <div>
            <label class="block text-xs font-bold text-slate-500 uppercase mb-2">Name</label>
            <input 
                bind:value={name}
                type="text" 
                placeholder="e.g. The Iron Fortress" 
                class="w-full bg-slate-900 border border-slate-800 rounded-lg p-4 text-white font-bold focus:border-orange-500 outline-none"
            />
        </div>

        <div>
            <label class="block text-xs font-bold text-slate-500 uppercase mb-2">URL Handle</label>
            <div class="flex items-center bg-slate-900 border border-slate-800 rounded-lg overflow-hidden">
                <span class="pl-4 pr-2 text-slate-500 select-none">resinen.com/communities/</span>
                <input 
                    bind:value={slug}
                    type="text" 
                    readonly
                    class="flex-1 bg-transparent p-4 text-orange-500 font-mono font-bold outline-none cursor-default"
                />
            </div>
            <p class="text-[10px] text-slate-600 mt-2">Auto-generated to ensure URL safety.</p>
        </div>

        <div>
            <label class="block text-xs font-bold text-slate-500 uppercase mb-2">Manifesto</label>
            <textarea 
                bind:value={description}
                rows="3" 
                class="w-full bg-slate-900 border border-slate-800 rounded-lg p-4 text-white focus:border-orange-500 outline-none"
            ></textarea>
        </div>

        <label class="flex items-center justify-between p-4 border border-slate-800 rounded-lg cursor-pointer hover:bg-slate-900 transition-colors">
            <div>
                <span class="block text-white font-bold text-sm">Gatekeeping Protocol</span>
                <span class="block text-xs text-slate-500">Private communities require admin approval.</span>
            </div>
            <input type="checkbox" bind:checked={is_private} class="accent-orange-500 w-5 h-5" />
        </label>

        <button 
            on:click={handleSubmit} 
            disabled={isSubmitting}
            class="w-full bg-orange-600 text-white font-bold py-4 rounded-lg hover:bg-orange-500 transition-all disabled:opacity-50"
        >
            {isSubmitting ? 'Establishing...' : 'Establish Territory'}
        </button>

    </div>
</div>