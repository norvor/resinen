<script lang="ts">
    import { onMount } from 'svelte';
    import { api, type WikiNode } from '$lib/api';
    import { fade, scale, slide } from 'svelte/transition';

    export let data;
    $: community = data.community;

    let tree: WikiNode[] = [];
    let loading = true;
    let showCreate = false;
    let editingPage: WikiNode | null = null;
    let pageContentBuffer = "";

    // New Page Form
    let newNode = {
        title: '',
        type: 'page' as 'page' | 'folder',
        parent_id: '' // Optional: ID of parent folder
    };

    onMount(async () => {
        await loadTree();
    });

    async function loadTree() {
        loading = true;
        try {
            const res = await api.getTree(community.id);
            tree = Array.isArray(res) ? res : (res as any).items || [];
        } catch (e) { console.error(e); } 
        finally { loading = false; }
    }

    async function handleCreate() {
        try {
            await api.createPage(community.id, newNode);
            showCreate = false;
            newNode = { title: '', type: 'page', parent_id: '' };
            await loadTree();
        } catch (e) { alert("Failed to create node."); }
    }

    async function openEditor(node: WikiNode) {
        if (node.type === 'folder') return;
        editingPage = node;
        // In a real app, fetch the content first:
        // const page = await api.getPage(node.slug);
        // pageContentBuffer = page.content;
        pageContentBuffer = "# " + node.title + "\n\nWrite your content here...";
    }

    async function saveContent() {
        if (!editingPage) return;
        try {
            await api.updatePage(editingPage.id, pageContentBuffer);
            alert("Saved!");
            editingPage = null;
        } catch (e) { alert("Save failed"); }
    }

    // Recursive component for Tree Items would be ideal, but we'll use a flat list visual for simplicity in this file
    function getAllFolders(nodes: WikiNode[]): WikiNode[] {
        let folders: WikiNode[] = [];
        for (const node of nodes) {
            if (node.type === 'folder') {
                folders.push(node);
                if (node.children) folders = [...folders, ...getAllFolders(node.children)];
            }
        }
        return folders;
    }
</script>

<div class="space-y-8 animate-fade-in-up h-[calc(100vh-100px)] flex flex-col">
    
    <div class="flex items-end justify-between border-b-4 border-black pb-6 shrink-0">
        <div>
            <div class="text-xs font-black uppercase text-orange-600 tracking-widest mb-1 flex items-center gap-2">
                <span>📚</span> Library Engine
            </div>
            <h1 class="text-4xl font-black uppercase tracking-tighter">
                Archives
            </h1>
        </div>
        <button 
            on:click={() => showCreate = true}
            class="px-6 py-3 bg-orange-500 text-white font-black rounded uppercase text-xs shadow-[4px_4px_0px_black] hover:-translate-y-1 hover:shadow-[6px_6px_0px_black] transition-all"
        >
            + New Page
        </button>
    </div>

    <div class="flex-1 flex gap-8 overflow-hidden">
        
        <div class="w-1/3 border-r border-gray-200 pr-8 overflow-y-auto">
            {#if loading}
                <div class="text-center py-10 text-gray-400 font-bold animate-pulse">Scanning Index...</div>
            {:else if tree.length === 0}
                <div class="p-8 text-center border-2 border-dashed border-gray-200 rounded text-gray-400">
                    Empty Archive
                </div>
            {:else}
                <div class="space-y-2">
                    {#each tree as node}
                        <div class="group">
                            <div 
                                class="flex items-center gap-2 p-2 rounded cursor-pointer hover:bg-gray-100 {editingPage?.id === node.id ? 'bg-orange-50 text-orange-700' : ''}"
                                on:click={() => openEditor(node)}
                            >
                                <span class="text-lg">{node.type === 'folder' ? '📁' : '📄'}</span>
                                <span class="text-sm font-bold uppercase">{node.title}</span>
                            </div>

                            {#if node.children}
                                <div class="ml-6 border-l-2 border-gray-100 pl-2 mt-1 space-y-1">
                                    {#each node.children as child}
                                        <div 
                                            class="flex items-center gap-2 p-2 rounded cursor-pointer hover:bg-gray-100 {editingPage?.id === child.id ? 'bg-orange-50 text-orange-700' : ''}"
                                            on:click={() => openEditor(child)}
                                        >
                                            <span class="text-lg">{child.type === 'folder' ? '📁' : '📄'}</span>
                                            <span class="text-sm font-bold">{child.title}</span>
                                        </div>
                                    {/each}
                                </div>
                            {/if}
                        </div>
                    {/each}
                </div>
            {/if}
        </div>

        <div class="flex-1 bg-gray-50 rounded-xl border-2 border-gray-200 relative overflow-hidden flex flex-col">
            {#if editingPage}
                <div class="bg-white border-b border-gray-200 p-4 flex justify-between items-center">
                    <div>
                        <div class="text-[10px] font-black uppercase text-gray-400">Editing</div>
                        <div class="font-bold text-lg">{editingPage.title}</div>
                    </div>
                    <button on:click={saveContent} class="px-4 py-2 bg-black text-white text-xs font-bold uppercase rounded hover:bg-gray-800">
                        Save Changes
                    </button>
                </div>
                <textarea 
                    bind:value={pageContentBuffer}
                    class="flex-1 w-full p-8 resize-none outline-none font-mono text-sm bg-transparent"
                    placeholder="Type markdown here..."
                ></textarea>
            {:else}
                <div class="flex-1 flex flex-col items-center justify-center text-gray-300">
                    <div class="text-6xl mb-4">✍️</div>
                    <div class="font-black uppercase tracking-widest">Select a page to edit</div>
                </div>
            {/if}
        </div>

    </div>

    {#if showCreate}
        <div class="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4 backdrop-blur-sm" transition:fade>
            <div class="bg-white w-full max-w-md rounded-xl p-8 shadow-2xl" in:scale>
                <h2 class="font-black text-2xl uppercase mb-6">Create Node</h2>
                
                <div class="space-y-4">
                    <div>
                        <label class="block text-xs font-bold uppercase text-gray-500 mb-1">Title</label>
                        <input bind:value={newNode.title} class="w-full border-2 border-gray-200 p-2 rounded font-bold focus:border-black outline-none" />
                    </div>

                    <div>
                        <label class="block text-xs font-bold uppercase text-gray-500 mb-1">Type</label>
                        <div class="flex gap-4">
                            <label class="flex items-center gap-2 cursor-pointer">
                                <input type="radio" bind:group={newNode.type} value="page" class="accent-orange-500" />
                                <span class="text-sm font-bold">Page</span>
                            </label>
                            <label class="flex items-center gap-2 cursor-pointer">
                                <input type="radio" bind:group={newNode.type} value="folder" class="accent-orange-500" />
                                <span class="text-sm font-bold">Folder</span>
                            </label>
                        </div>
                    </div>

                    <div>
                        <label class="block text-xs font-bold uppercase text-gray-500 mb-1">Parent Folder (Optional)</label>
                        <select bind:value={newNode.parent_id} class="w-full border-2 border-gray-200 p-2 rounded font-bold focus:border-black outline-none bg-white">
                            <option value="">(Root)</option>
                            {#each getAllFolders(tree) as folder}
                                <option value={folder.id}>{folder.title}</option>
                            {/each}
                        </select>
                    </div>
                </div>

                <div class="flex gap-2 mt-8">
                    <button on:click={() => showCreate = false} class="flex-1 py-3 text-gray-500 font-bold hover:bg-gray-100 rounded">Cancel</button>
                    <button on:click={handleCreate} class="flex-1 py-3 bg-black text-white font-bold uppercase rounded">Create</button>
                </div>
            </div>
        </div>
    {/if}

</div>