<script lang="ts">
    import { api } from '$lib/api';
    import { goto } from '$app/navigation';

    let name = '';
    let slug = '';
    let description = '';
    
    // GOVERNANCE CONTROLS (The missing pieces)
    let isPrivate = true; // Default to Gatekeeping ON
    let allowPolitics = false; // Default to Politics OFF

    let isSubmitting = false;

    // Auto-generate slug
    $: slug = name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');

    async function handleSubmit() {
        if (!name || !slug) return;
        isSubmitting = true;

        try {
            // 1. Create the Territory (Community)
            const community = await api.createCommunity({ 
                name, 
                slug, 
                description,
                is_private: isPrivate, // Send the Gatekeeping setting
                rules: JSON.stringify({ allow_politics: allowPolitics }) // Store simple laws in rules for now
            });

            // If you implemented the full Bylaws table, you would make a second API call here.
            // For now, saving it to the 'rules' column is a perfect quick start.

            goto('/communities');
        } catch (e) {
            alert('Failed to initialize territory. Slug might be taken.');
            console.error(e);
        } finally {
            isSubmitting = false;
        }
    }
</script>

<div class="max-w-2xl mx-auto">
    <a href="/communities" class="text-slate-500 hover:text-white mb-6 inline-block text-sm">&larr; Back to Dashboard</a>
    
    <div class="bg-slate-950 border border-slate-800 rounded-2xl p-8 shadow-2xl">
        <h1 class="text-2xl font-bold text-white mb-2">Initialize Territory</h1>
        <p class="text-slate-500 mb-6 text-sm">Deploy a new sovereign community node.</p>

        <div class="space-y-6">
            
            <div class="space-y-4 border-b border-slate-800 pb-6">
                <div>
                    <label class="block text-slate-400 text-xs uppercase font-bold mb-2">Territory Name</label>
                    <input 
                        bind:value={name}
                        type="text" 
                        placeholder="e.g. The Iron Fortress" 
                        class="w-full bg-slate-900 border border-slate-800 text-white p-4 rounded-xl focus:ring-1 focus:ring-orange-500 outline-none transition-all font-bold"
                    />
                </div>

                <div>
                    <label class="block text-slate-400 text-xs uppercase font-bold mb-2">URL Slug</label>
                    <div class="flex">
                        <span class="bg-slate-900 border border-slate-800 border-r-0 text-slate-500 p-4 rounded-l-xl select-none font-mono text-sm flex items-center">resinen.com/</span>
                        <input 
                            bind:value={slug}
                            type="text" 
                            class="w-full bg-slate-900 border border-slate-800 text-orange-400 p-4 rounded-r-xl focus:ring-1 focus:ring-orange-500 outline-none font-mono font-bold"
                        />
                    </div>
                </div>

                <div>
                    <label class="block text-slate-400 text-xs uppercase font-bold mb-2">Manifesto</label>
                    <textarea 
                        bind:value={description}
                        rows="3"
                        placeholder="State the purpose of this territory..."
                        class="w-full bg-slate-900 border border-slate-800 text-white p-4 rounded-xl focus:ring-1 focus:ring-orange-500 outline-none transition-all"
                    ></textarea>
                </div>
            </div>

            <div>
                <h3 class="text-orange-500 font-bold uppercase text-xs mb-4 tracking-widest">Constitution & Laws</h3>
                
                <div class="grid grid-cols-1 gap-4">
                    
                    <label class="flex items-center justify-between p-4 bg-slate-900 rounded-xl border border-slate-800 cursor-pointer hover:border-slate-600 transition-colors">
                        <div>
                            <div class="font-bold text-white flex items-center gap-2">
                                🔒 Gatekeeping Protocol
                                {#if isPrivate}<span class="text-[10px] bg-orange-600 text-white px-2 py-0.5 rounded-full uppercase">Active</span>{/if}
                            </div>
                            <div class="text-xs text-slate-500 mt-1">If active, new citizens must be manually approved by Admin.</div>
                        </div>
                        <input type="checkbox" bind:checked={isPrivate} class="w-6 h-6 rounded accent-orange-500" />
                    </label>

                    <label class="flex items-center justify-between p-4 bg-slate-900 rounded-xl border border-slate-800 cursor-pointer hover:border-slate-600 transition-colors">
                        <div>
                            <div class="font-bold text-white flex items-center gap-2">
                                📢 Political Discourse
                                {#if allowPolitics}<span class="text-[10px] bg-red-600 text-white px-2 py-0.5 rounded-full uppercase">Allowed</span>{/if}
                            </div>
                            <div class="text-xs text-slate-500 mt-1">Allow posts regarding elections and political ideology.</div>
                        </div>
                        <input type="checkbox" bind:checked={allowPolitics} class="w-6 h-6 rounded accent-orange-500" />
                    </label>

                </div>
            </div>

            <button 
                on:click={handleSubmit}
                disabled={isSubmitting}
                class="w-full bg-orange-600 hover:bg-orange-500 text-white font-bold py-4 rounded-xl transition-all shadow-lg shadow-orange-900/20 mt-4"
            >
                {isSubmitting ? 'ESTABLISHING...' : 'ESTABLISH TERRITORY'}
            </button>
        </div>
    </div>
</div>