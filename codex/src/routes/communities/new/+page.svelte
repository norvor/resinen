<script lang="ts">
    import { api, type CreateCommunityDTO } from '$lib/api';
    import { goto } from '$app/navigation';

    // 1. Form State
    let name = '';
    let slug = '';
    let description = '';
    let isGatekept = true; 
    let isSubmitting = false;

    // 2. Archetype State
    let selectedArchetypes: string[] = [];

    // Archetype Definitions (The Menu)
    const ARCHETYPES = [
        { id: 'arena', label: 'The Arena', icon: '🏆', desc: 'Sports & Competition' },
        { id: 'stage', label: 'The Stage', icon: '🎤', desc: 'Visuals & Performance' },
        { id: 'sanctuary', label: 'The Sanctuary', icon: '🙏', desc: 'Faith & Spirit' },
        { id: 'library', label: 'The Library', icon: '📚', desc: 'Wiki & Knowledge' },
        { id: 'guild', label: 'The Guild', icon: '⚒️', desc: 'Building & Code' },
        { id: 'bazaar', label: 'The Bazaar', icon: '🏷️', desc: 'Commerce & Trade' },
        { id: 'senate', label: 'The Senate', icon: '⚖️', desc: 'Politics & Voting' },
        { id: 'academy', label: 'The Academy', icon: '🎓', desc: 'Education & Growth' },
        { id: 'club', label: 'The Club', icon: '🥂', desc: 'Nightlife & Events' },
        { id: 'bunker', label: 'The Bunker', icon: '🕵️', desc: 'Privacy & Anon' },
        { id: 'lounge', label: 'The Lounge', icon: '🛋️', desc: 'Social & Casual' },
    ];

    function toggleArchetype(id: string) {
        if (selectedArchetypes.includes(id)) {
            selectedArchetypes = selectedArchetypes.filter(a => a !== id);
        } else {
            selectedArchetypes = [...selectedArchetypes, id];
        }
    }

    // Auto-generate slug
    $: slug = name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');

    async function handleSubmit() {
        if (!name || !slug) return;
        isSubmitting = true;

        try {
            // Default to 'lounge' if nothing selected
            const finalArchetypes = selectedArchetypes.length > 0 ? selectedArchetypes : ['lounge'];

            const payload: CreateCommunityDTO = {
                name,
                slug,
                description,
                is_private: isGatekept,
                archetypes: finalArchetypes // 🚨 SENDING ARRAY
            };

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

<div class="max-w-3xl mx-auto p-8">
    <a href="/communities" class="text-slate-500 hover:text-white mb-6 inline-block text-sm font-mono">&larr; ABORT OPERATION</a>
    
    <div class="bg-slate-950 border border-slate-800 rounded-2xl p-8 shadow-2xl">
        <h1 class="text-2xl font-bold text-white mb-2">Initialize Territory</h1>
        <p class="text-slate-500 mb-8 text-sm">Deploy a new sovereign community node.</p>

        <div class="space-y-8">
            
            <div class="space-y-4">
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-slate-400 text-xs uppercase font-bold mb-2">Designation</label>
                        <input bind:value={name} type="text" placeholder="e.g. Neo Tokyo" 
                            class="w-full bg-slate-900 border border-slate-800 text-white p-4 rounded-xl focus:border-orange-500 outline-none font-bold transition-all" />
                    </div>
                    <div>
                        <label class="block text-slate-400 text-xs uppercase font-bold mb-2">Network Handle</label>
                        <div class="flex">
                            <span class="bg-slate-900 border border-slate-800 border-r-0 text-slate-500 p-4 rounded-l-xl select-none font-mono text-sm flex items-center">/c/</span>
                            <input bind:value={slug} type="text" 
                                class="w-full bg-slate-900 border border-slate-800 text-orange-500 p-4 rounded-r-xl focus:border-orange-500 outline-none font-mono font-bold transition-all" />
                        </div>
                    </div>
                </div>

                <div>
                    <label class="block text-slate-400 text-xs uppercase font-bold mb-2">Manifesto</label>
                    <textarea bind:value={description} rows="2" placeholder="State the purpose..." 
                        class="w-full bg-slate-900 border border-slate-800 text-white p-4 rounded-xl focus:border-orange-500 outline-none transition-all"></textarea>
                </div>
            </div>

            <div>
                <h3 class="text-orange-500 font-bold uppercase text-xs mb-4 tracking-widest">Select Modules (Archetypes)</h3>
                <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {#each ARCHETYPES as type}
                        <button 
                            on:click={() => toggleArchetype(type.id)}
                            class="p-3 rounded-xl border text-left transition-all relative flex flex-col gap-1
                            {selectedArchetypes.includes(type.id) 
                                ? 'bg-orange-900/20 border-orange-500 text-orange-100' 
                                : 'bg-slate-900 border-slate-800 text-slate-400 hover:border-slate-600 hover:text-white'}"
                        >
                            <div class="flex justify-between items-start">
                                <span class="text-xl">{type.icon}</span>
                                {#if selectedArchetypes.includes(type.id)}
                                    <span class="w-2 h-2 rounded-full bg-orange-500 shadow-[0_0_10px_rgba(249,115,22,0.5)]"></span>
                                {/if}
                            </div>
                            <div class="font-bold text-xs uppercase mt-1">{type.label}</div>
                            <div class="text-[10px] opacity-60 leading-tight">{type.desc}</div>
                        </button>
                    {:else}
                        <p class="text-white">Loading Archetypes...</p>
                    {/each}
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
                class="w-full bg-orange-600 hover:bg-orange-500 text-white font-bold py-4 rounded-xl transition-all shadow-lg shadow-orange-900/20 disabled:opacity-50 disabled:cursor-not-allowed"
            >
                {isSubmitting ? 'ESTABLISHING...' : 'ESTABLISH TERRITORY'}
            </button>
        </div>
    </div>
</div>