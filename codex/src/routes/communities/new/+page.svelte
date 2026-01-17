<script lang="ts">
    import { api } from '$lib/api';
    import type { Community } from '$lib/api';

    let name = '';
    let slug = '';
    let description = '';
    let isLoading = false;
    let message = '';
    let isSuccess = false;

    // Auto-generate slug from name
    function updateSlug() {
        slug = name.toLowerCase()
            .replace(/ /g, '-')
            .replace(/[^\w-]+/g, '');
    }

    async function handleSubmit() {
        isLoading = true;
        message = '';
        
        const payload: Community = {
            name,
            slug,
            description,
            settings: { theme: 'default', privacy: 'public' }
        };

        try {
            await api.createCommunity(payload);
            isSuccess = true;
            message = `Protocol Initialized: "${name}" is now active.`;
            // Reset form
            name = ''; slug = ''; description = '';
        } catch (e: any) {
            isSuccess = false;
            message = `System Error: ${e.message}`;
        } finally {
            isLoading = false;
        }
    }
</script>

<div class="max-w-4xl mx-auto animate-in fade-in duration-500">
    <header class="mb-8 border-b border-slate-800 pb-6">
        <h2 class="text-3xl font-black text-white tracking-tighter">GENESIS PROTOCOL</h2>
        <p class="text-slate-400 font-mono text-sm mt-1">INITIALIZE NEW COMMUNITY STRUCTURE</p>
    </header>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <div class="lg:col-span-2 space-y-6">
            <div class="p-8 rounded-2xl bg-slate-950 border border-slate-800 shadow-xl">
                
                <div class="mb-6">
                    <label class="block text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">
                        Community Designation
                    </label>
                    <input 
                        bind:value={name}
                        on:input={updateSlug}
                        type="text" 
                        placeholder="e.g. The Legal Guild"
                        class="w-full bg-slate-900 border border-slate-800 text-white p-4 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none transition-all placeholder-slate-600 font-bold"
                    />
                </div>

                <div class="mb-6">
                    <label class="block text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">
                        Network Identifier (Slug)
                    </label>
                    <div class="flex items-center">
                        <span class="bg-slate-800 text-slate-400 px-4 py-4 rounded-l-xl font-mono text-sm border-y border-l border-slate-700">
                            resinen.com/
                        </span>
                        <input 
                            bind:value={slug}
                            type="text" 
                            class="flex-1 bg-slate-900 border border-slate-800 text-orange-500 p-4 rounded-r-xl focus:ring-2 focus:ring-orange-500 outline-none font-mono text-sm"
                        />
                    </div>
                </div>

                <div class="mb-8">
                    <label class="block text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">
                        Manifesto
                    </label>
                    <textarea 
                        bind:value={description}
                        rows="4" 
                        class="w-full bg-slate-900 border border-slate-800 text-slate-300 p-4 rounded-xl focus:ring-2 focus:ring-orange-500 outline-none transition-all"
                    ></textarea>
                </div>

                <button 
                    on:click={handleSubmit}
                    disabled={isLoading}
                    class="w-full py-4 bg-orange-600 hover:bg-orange-500 text-white font-black tracking-widest uppercase rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                    {#if isLoading}
                        <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        Initializing...
                    {:else}
                        Initialize System
                    {/if}
                </button>

                {#if message}
                    <div class={`mt-6 p-4 rounded-lg border text-sm font-mono ${isSuccess ? 'bg-green-900/20 border-green-800 text-green-400' : 'bg-red-900/20 border-red-800 text-red-400'}`}>
                        > {message}
                    </div>
                {/if}

            </div>
        </div>

        <div class="space-y-6">
            <div class="p-6 rounded-2xl bg-slate-900 border border-slate-800">
                <h3 class="text-orange-500 font-bold mb-2">System Note</h3>
                <p class="text-slate-400 text-sm leading-relaxed">
                    Creating a community establishes a root node in the Resinen database. 
                    <br><br>
                    Once initialized, you must proceed to <strong>Chapter Allocation</strong> to assign physical nodes (e.g., London, Mumbai).
                </p>
            </div>
        </div>
    </div>
</div>