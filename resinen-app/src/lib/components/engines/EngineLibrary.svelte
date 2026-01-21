<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    import { slide, fade, fly } from 'svelte/transition';
    import type { Community, User } from '$lib/types';

    export let community: Community;
    export let currentUser: User | null;

    // --- TYPES ---
    interface LibraryNode {
        id: string;
        title: string;
        type: 'folder' | 'page';
        slug?: string;
        children?: LibraryNode[];
        updated_at?: string;
        author?: string; // Optional metadata from tree
    }

    interface PageContent extends LibraryNode {
        content: string; // The markdown or HTML body
        last_edit?: string;
    }

    // --- STATE ---
    let tree: LibraryNode[] = [];
    let activePage: PageContent | null = null;
    let searchQuery = "";
    let loading = true;
    let pageLoading = false;
    let readingMode = false; // Toggles full-screen reading
    let error: string | null = null;

    // --- INITIALIZATION ---
    onMount(async () => {
        if (!community?.id) return;
        try {
            // Fetch the directory structure
            const data = await api.getPageTree(community.id);
            // Handle wrapper if exists
            tree = Array.isArray(data) ? data : (data as any).items || [];
            
            // Auto-select first page if available
            const firstPage = findFirstPage(tree);
            if (firstPage) {
                selectPage(firstPage);
            }
        } catch (e) {
            console.error("Library Offline:", e);
            error = "Archive inaccessible.";
        } finally {
            loading = false;
        }
    });

    // Helper to find the first readable page in the tree
    function findFirstPage(nodes: LibraryNode[]): LibraryNode | null {
        for (const node of nodes) {
            if (node.type === 'page') return node;
            if (node.children) {
                const found = findFirstPage(node.children);
                if (found) return found;
            }
        }
        return null;
    }

    // --- ACTIONS ---
    async function selectPage(node: LibraryNode) {
        if (node.type === 'folder') {
            // In a real implementation, you might toggle an 'expanded' boolean on the node here
            return;
        }

        if (!node.slug) return;

        pageLoading = true;
        try {
            // Fetch full content
            const pageData = await api.getPage(community.id, node.slug);
            
            activePage = { 
                ...node, 
                content: pageData.content || pageData.html || "No content available.",
                author: pageData.author_name || 'System',
                last_edit: pageData.updated_at ? new Date(pageData.updated_at).toLocaleDateString() : 'Unknown'
            };
        } catch (e) {
            console.error("Page Load Failed", e);
            activePage = { ...node, content: "Error: Could not retrieve document content." };
        } finally {
            pageLoading = false;
        }
    }

    // Flatten tree for search
    function getAllNodes(nodes: LibraryNode[]): LibraryNode[] {
        let all: LibraryNode[] = [];
        for (const node of nodes) {
            all.push(node);
            if (node.children) all = all.concat(getAllNodes(node.children));
        }
        return all;
    }

    // Reactive Search Filter
    $: filteredTree = searchQuery 
        ? getAllNodes(tree).filter(n => n.title.toLowerCase().includes(searchQuery.toLowerCase()) && n.type === 'page')
        : tree;

</script>

<div class="h-[calc(100vh-100px)] flex flex-col md:flex-row bg-[#fdfbf7] text-zinc-900 font-serif border-4 border-zinc-900 rounded-xl overflow-hidden shadow-2xl relative">

    <div class="w-full md:w-1/3 lg:w-1/4 bg-[#fdfbf7] flex flex-col border-r-4 border-zinc-900 z-10 {readingMode ? 'hidden md:flex' : 'flex'}">
        
        <div class="p-4 border-b-4 border-zinc-900 bg-zinc-900 text-white">
            <h2 class="text-xs font-black uppercase tracking-[0.2em] mb-3 text-zinc-400">The Index</h2>
            <div class="relative">
                <input 
                    bind:value={searchQuery}
                    type="text" 
                    placeholder="Search the archives..." 
                    class="w-full bg-zinc-800 border border-zinc-700 text-white px-3 py-2 text-sm font-sans focus:outline-none focus:border-white transition-colors placeholder:text-zinc-600 uppercase font-bold"
                />
                <span class="absolute right-3 top-2.5 text-xs text-zinc-500">⌘K</span>
            </div>
        </div>

        {#if error}
             <div class="p-8 text-center text-red-600 font-sans font-bold text-xs uppercase">{error}</div>
        {/if}

        <div class="flex-1 overflow-y-auto p-2 space-y-1 scrollbar-hide">
            {#if loading}
                <div class="p-4 text-xs font-sans font-bold text-zinc-400 animate-pulse uppercase">Scanning Shelves...</div>
            {:else}
                {#each filteredTree as node}
                    {#if node.type === 'folder'}
                        <div class="px-3 py-4 mt-4 mb-2 border-b-2 border-zinc-200">
                            <h3 class="font-black uppercase text-xs tracking-widest text-zinc-400">{node.title}</h3>
                        </div>
                        {#if node.children}
                            {#each node.children as child}
                                <button 
                                    on:click={() => selectPage(child)}
                                    class="w-full text-left px-4 py-3 text-sm font-bold border-l-4 transition-all hover:bg-zinc-100 group flex justify-between items-center
                                    {activePage?.id === child.id ? 'border-orange-600 bg-orange-50 text-orange-900' : 'border-transparent text-zinc-600'}"
                                >
                                    <span>{child.title}</span>
                                    {#if activePage?.id === child.id}
                                        <span class="text-[10px] uppercase tracking-widest font-sans">Reading</span>
                                    {/if}
                                </button>
                            {/each}
                        {/if}
                    {:else}
                        <button 
                            on:click={() => selectPage(node)}
                            class="w-full text-left px-4 py-4 font-bold border-b border-zinc-100 hover:bg-zinc-100 transition-all flex flex-col gap-1
                            {activePage?.id === node.id ? 'bg-zinc-900 text-white hover:bg-zinc-800' : 'text-zinc-900'}"
                        >
                            <span class="text-lg leading-none font-serif italic">{node.title}</span>
                            <span class="text-[10px] font-sans font-black uppercase opacity-50 tracking-wide">
                                {node.updated_at ? new Date(node.updated_at).toLocaleDateString() : 'DOC'}
                            </span>
                        </button>
                    {/if}
                {/each}

                {#if filteredTree.length === 0 && !loading}
                    <div class="p-8 text-center opacity-50">
                        <div class="text-4xl mb-2">🕸️</div>
                        <div class="text-xs font-black uppercase font-sans">No records found</div>
                    </div>
                {/if}
            {/if}
        </div>

        <div class="p-4 border-t-4 border-zinc-900 bg-[#f0eee9] text-[10px] font-sans font-black uppercase text-zinc-400 flex justify-between">
            <span>Vol. {community.id.substring(0,4)}</span>
            <span>Total Entries: {getAllNodes(tree).length}</span>
        </div>
    </div>

    <div class="flex-1 bg-white relative flex flex-col h-full overflow-hidden">
        
        {#if activePage}
            <div class="h-16 border-b border-zinc-100 flex items-center justify-between px-6 shrink-0 bg-white/80 backdrop-blur z-20">
                <div class="flex items-center gap-2 text-xs font-sans font-bold text-zinc-400 uppercase">
                    <span>Archives</span>
                    <span>/</span>
                    <span class="text-zinc-900">{activePage.title}</span>
                </div>
                
                <div class="flex gap-2">
                    <button on:click={() => readingMode = !readingMode} class="w-8 h-8 flex items-center justify-center hover:bg-zinc-100 rounded text-zinc-400 transition-colors" title="Toggle Focus">
                        {readingMode ? '⇲' : '⛶'}
                    </button>
                    <button class="px-3 py-1 bg-zinc-100 hover:bg-zinc-200 text-zinc-600 text-[10px] font-black uppercase rounded transition-colors">
                        Edit
                    </button>
                </div>
            </div>

            <div class="flex-1 overflow-y-auto p-8 md:p-12 lg:p-20 relative">
                
                {#if pageLoading}
                    <div class="absolute inset-0 flex items-center justify-center bg-white/50 backdrop-blur-sm z-30">
                        <div class="animate-pulse font-sans font-black uppercase text-zinc-300">Deciphering...</div>
                    </div>
                {/if}

                <header class="mb-12 border-b-2 border-zinc-900 pb-8">
                    <h1 class="text-5xl md:text-6xl font-black text-zinc-900 mb-6 font-serif tracking-tight leading-[0.9]">
                        {activePage.title}
                    </h1>
                    
                    <div class="flex items-center gap-6 text-xs font-sans font-bold uppercase tracking-widest text-zinc-400">
                        <div class="flex items-center gap-2">
                            <div class="w-6 h-6 bg-zinc-200 rounded-full flex items-center justify-center text-[10px] text-zinc-500">
                                {activePage.author?.[0] || 'S'}
                            </div>
                            <span>{activePage.author || 'System'}</span>
                        </div>
                        <div class="w-px h-4 bg-zinc-200"></div>
                        <span>Updated {activePage.last_edit}</span>
                    </div>
                </header>

                <article class="prose prose-xl prose-zinc prose-headings:font-serif prose-headings:font-bold prose-p:text-zinc-600 prose-p:leading-loose max-w-3xl">
                   <div class="whitespace-pre-wrap font-serif text-lg text-zinc-800">
                       {activePage.content}
                   </div>
                </article>

                <div class="mt-20 pt-10 border-t border-zinc-100 text-zinc-400 font-mono text-xs flex flex-col gap-2">
                    <div class="uppercase font-bold tracking-widest">Citation Metadata</div>
                    <div>UUID: {activePage.id}</div>
                </div>

            </div>
        
        {:else}
            <div class="flex-1 flex flex-col items-center justify-center text-zinc-300 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')]">
                <div class="text-8xl mb-4 opacity-20">📖</div>
                <h3 class="font-black uppercase tracking-widest">Select a Tome</h3>
                <p class="font-serif italic opacity-60 mt-2">Knowledge awaits in the stacks.</p>
            </div>
        {/if}

    </div>

</div>