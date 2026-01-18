<script lang="ts">
    import { api, type CreateCommunityDTO } from '$lib/api';
    import { goto } from '$app/navigation';

    // 1. Form State (Mutable by User)
    let name = '';
    let slug = '';
    let description = '';
    
    // Default to true for safety, but USER can change this via checkbox
    let isGatekept = true; 
    
    let isSubmitting = false;

    // Auto-generate URL handle (slug) as user types name
    $: slug = name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');

    async function handleSubmit() {
        if (!name || !slug) return;
        isSubmitting = true;

        try {
            // 2. Dynamic Payload Construction
            // We map the live UI variable 'isGatekept' to the backend field 'is_private'
            const payload: CreateCommunityDTO = {
                name: name,
                slug: slug,
                description: description,
                is_private: isGatekept // <--- REAL VALUE FROM CHECKBOX
            };

            // Debug: Check your console to see exactly what is being sent
            console.log("Transmitting Payload:", payload); 

            await api.createCommunity(payload);
            goto('/communities');
            
        } catch (e: any) {
            console.error(e);
            alert(`Protocol Failure: ${e.message}`);
        } finally {
            isSubmitting = false;
        }
    }
</script>

<div class="max-w-2xl mx-auto p-8">
    <a href="/communities" class="text-slate-500 hover:text-white mb-6 inline-block text-sm font-mono">&larr; ABORT OPERATION</a>
    
    <div class="bg-slate-950 border border-slate-800 rounded-2xl p-8 shadow-2xl">
        <h1 class="text-2xl font-bold text-white mb-2">Initialize Territory</h1>
        <p class="text-slate-500 mb-6 text-sm">Deploy a new sovereign community node.</p>

        <div class="space-y-6">
            
            <div class="space-y-4 border-b border-slate-800 pb-6">
                <div>
                    <label class="block text-slate-400 text-xs uppercase font-bold mb-2">Designation</label>
                    <input 
                        bind:value={name}
                        type="text" 
                        placeholder="e.g. Area 51" 
                        class="w-full bg-slate-900 border border-slate-800 text-white p-4 rounded-xl focus:border-orange-500 outline-none font-bold transition-all"
                    />
                </div>

                <div>
                    <label class="block text-slate-400 text-xs uppercase font-bold mb-2">Network Handle</label>
                    <div class="flex">
                        <span class="bg-slate-900 border border-slate-800 border-r-0 text-slate-500 p-4 rounded-l-xl select-none font-mono text-sm flex items-center">/c/</span>
                        <input 
                            bind:value={slug}
                            type="text" 
                            class="w-full bg-slate-900 border border-slate-800 text-orange-500 p-4 rounded-r-xl focus:border-orange-500 outline-none font-mono font-bold transition-all"
                        />
                    </div>
                </div>

                <div>
                    <label class="block text-slate-400 text-xs uppercase font-bold mb-2">Manifesto</label>
                    <textarea 
                        bind:value={description}
                        rows="3"
                        placeholder="State the purpose of this territory..."
                        class="w-full bg-slate-900 border border-slate-800 text-white p-4 rounded-xl focus:border-orange-500 outline-none transition-all"
                    ></textarea>
                </div>
            </div>

            <div>
                <h3 class="text-orange-500 font-bold uppercase text-xs mb-4 tracking-widest">Protocols</h3>
                
                <label class="flex items-center justify-between p-4 bg-slate-900 rounded-xl border border-slate-800 cursor-pointer hover:border-slate-600 transition-colors group">
                    <div>
                        <div class="font-bold text-white flex items-center gap-2">
                            🔒 Gatekeeping Protocol
                            {#if isGatekept}
                                <span class="text-[10px] bg-orange-600 text-white px-2 py-0.5 rounded-full uppercase">Active</span>
                            {/if}
                        </div>
                        <div class="text-xs text-slate-500 mt-1 group-hover:text-slate-400 transition-colors">
                            Requires admin approval for new citizens.
                        </div>
                    </div>
                    <input type="checkbox" bind:checked={isGatekept} class="w-6 h-6 rounded accent-orange-500" />
                </label>
            </div>

            <button 
                on:click={handleSubmit}
                disabled={isSubmitting}
                class="w-full bg-orange-600 hover:bg-orange-500 text-white font-bold py-4 rounded-xl transition-all shadow-lg shadow-orange-900/20 mt-4 disabled:opacity-50 disabled:cursor-not-allowed"
            >
                {isSubmitting ? 'ESTABLISHING...' : 'ESTABLISH TERRITORY'}
            </button>
        </div>
    </div>
</div>