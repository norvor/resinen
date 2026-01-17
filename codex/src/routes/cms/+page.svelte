<script lang="ts">
    import { onMount } from 'svelte';
    import { api, type ContentBlock } from '$lib/api';

    let section = 'home'; // Default section to edit
    let blocks: ContentBlock[] = [];
    let editingBlock: Partial<ContentBlock> | null = null;
    let isSaving = false;

    // Load blocks when section changes
    $: if(section) loadBlocks();

    async function loadBlocks() {
        try {
            blocks = await api.getSectionBlocks(section);
        } catch (e) {
            console.error(e);
        }
    }

    function startEdit(block: ContentBlock) {
        editingBlock = { ...block };
    }

    function startNew() {
        editingBlock = {
            slug: '',
            section: section,
            title: '',
            body: '',
            is_active: true
        };
    }

    async function handleSave() {
        if (!editingBlock || !editingBlock.slug) return;
        isSaving = true;
        try {
            // Check if it's an update or new
            const exists = blocks.find(b => b.slug === editingBlock!.slug);
            
            if (exists && editingBlock.id) {
                await api.updateContentBlock(editingBlock.slug, editingBlock);
            } else {
                await api.createContentBlock(editingBlock);
            }
            
            await loadBlocks();
            editingBlock = null;
        } catch (e) {
            alert('Failed to save block. Slug must be unique.');
        } finally {
            isSaving = false;
        }
    }
</script>

<div class="max-w-6xl mx-auto mt-8 px-4">
    <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold text-white">Website CMS</h1>
        
        <div class="flex bg-slate-900 rounded-lg p-1 border border-slate-800">
            {#each ['home', 'pricing', 'about', 'footer'] as s}
                <button 
                    on:click={() => section = s}
                    class="px-4 py-2 rounded-md text-sm font-bold transition-all {section === s ? 'bg-slate-800 text-white shadow' : 'text-slate-500 hover:text-slate-300'}"
                >
                    {s.toUpperCase()}
                </button>
            {/each}
        </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div class="lg:col-span-1 space-y-4">
            <button on:click={startNew} class="w-full py-3 border-2 border-dashed border-slate-800 text-slate-500 hover:border-orange-500 hover:text-orange-500 rounded-xl font-bold transition-all">
                + Create New Block
            </button>

            {#each blocks as block}
                <div 
                    on:click={() => startEdit(block)}
                    class="p-4 bg-slate-950 border border-slate-800 rounded-xl cursor-pointer hover:border-slate-600 transition-all {editingBlock?.slug === block.slug ? 'ring-1 ring-orange-500 border-orange-500' : ''}"
                >
                    <div class="flex justify-between items-start mb-2">
                        <span class="text-xs font-mono text-orange-400 bg-orange-900/20 px-2 py-0.5 rounded">{block.slug}</span>
                        <div class="h-2 w-2 rounded-full {block.is_active ? 'bg-green-500' : 'bg-red-500'}"></div>
                    </div>
                    <h3 class="font-bold text-white truncate">{block.title || 'Untitled Block'}</h3>
                    <p class="text-xs text-slate-500 truncate mt-1">{block.body}</p>
                </div>
            {/each}
        </div>

        <div class="lg:col-span-2">
            {#if editingBlock}
                <div class="bg-slate-950 border border-slate-800 rounded-2xl p-8 sticky top-8">
                    <div class="flex justify-between mb-6">
                        <h2 class="text-xl font-bold text-white">
                            {editingBlock.id ? 'Edit Block' : 'New Block'}
                        </h2>
                        <button on:click={() => editingBlock = null} class="text-slate-500 hover:text-white">Close</button>
                    </div>

                    <div class="space-y-6">
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <label class="block text-slate-500 text-xs font-bold mb-2 uppercase">Slug (ID)</label>
                                <input bind:value={editingBlock.slug} disabled={!!editingBlock.id} type="text" placeholder="e.g. home_hero_title" class="w-full bg-slate-900 border border-slate-800 text-white p-3 rounded-xl focus:border-orange-500 outline-none disabled:opacity-50" />
                            </div>
                            <div>
                                <label class="block text-slate-500 text-xs font-bold mb-2 uppercase">Section</label>
                                <input bind:value={editingBlock.section} type="text" class="w-full bg-slate-900 border border-slate-800 text-white p-3 rounded-xl focus:border-orange-500 outline-none" />
                            </div>
                        </div>

                        <div>
                            <label class="block text-slate-500 text-xs font-bold mb-2 uppercase">Title / Heading</label>
                            <input bind:value={editingBlock.title} type="text" class="w-full bg-slate-900 border border-slate-800 text-white p-3 rounded-xl focus:border-orange-500 outline-none" />
                        </div>

                        <div>
                            <label class="block text-slate-500 text-xs font-bold mb-2 uppercase">Body Text / HTML</label>
                            <textarea bind:value={editingBlock.body} rows="6" class="w-full bg-slate-900 border border-slate-800 text-white p-3 rounded-xl focus:border-orange-500 outline-none font-mono text-sm"></textarea>
                        </div>

                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <label class="block text-slate-500 text-xs font-bold mb-2 uppercase">Button Text</label>
                                <input bind:value={editingBlock.link_text} type="text" class="w-full bg-slate-900 border border-slate-800 text-white p-3 rounded-xl focus:border-orange-500 outline-none" />
                            </div>
                            <div>
                                <label class="block text-slate-500 text-xs font-bold mb-2 uppercase">Button URL</label>
                                <input bind:value={editingBlock.link_url} type="text" class="w-full bg-slate-900 border border-slate-800 text-white p-3 rounded-xl focus:border-orange-500 outline-none" />
                            </div>
                        </div>

                        <div class="flex items-center gap-3 pt-4 border-t border-slate-900">
                             <button 
                                on:click={handleSave}
                                disabled={isSaving}
                                class="bg-orange-600 hover:bg-orange-500 text-white font-bold py-3 px-8 rounded-xl transition-all"
                            >
                                {isSaving ? 'Saving...' : 'Save Block'}
                            </button>
                            <label class="flex items-center gap-2 cursor-pointer select-none">
                                <input type="checkbox" bind:checked={editingBlock.is_active} class="w-4 h-4 rounded bg-slate-800 border-slate-700 text-orange-600 focus:ring-0" />
                                <span class="text-slate-400 text-sm">Active / Visible</span>
                            </label>
                        </div>
                    </div>
                </div>
            {:else}
                <div class="h-full flex items-center justify-center border-2 border-dashed border-slate-900 rounded-2xl p-12 text-slate-600">
                    Select a block to edit or create a new one.
                </div>
            {/if}
        </div>
    </div>
</div>