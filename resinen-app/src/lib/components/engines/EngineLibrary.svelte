<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    export let community: any;

    let tree: any[] = [];
    let activePage: any = null;
    let loading = true;
    let pageLoading = false;

    onMount(async () => {
        try {
            tree = await api.getPageTree(community.id);
            // Auto-load first page if exists
            if (tree.length > 0) {
                await loadPage(tree[0].slug);
            }
        } catch (e) {
            console.error(e);
        } finally {
            loading = false;
        }
    });

    async function loadPage(slug: string) {
        pageLoading = true;
        try {
            activePage = await api.getPage(community.id, slug);
        } catch (e) {
            console.error(e);
        } finally {
            pageLoading = false;
        }
    }
</script>

{#if loading}
    <div class="p-8 text-center animate-pulse text-skin-muted font-bold uppercase">Loading Archive...</div>
{:else}
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-8 h-[600px]">
        
        <div class="lg:col-span-1 border-r border-skin-border pr-4 overflow-y-auto">
            <div class="text-xs font-black uppercase text-skin-muted mb-4 tracking-widest">Table of Contents</div>
            
            <div class="space-y-1">
                {#each tree as item}
                    <button 
                        on:click={() => loadPage(item.slug)}
                        class="w-full text-left px-3 py-2 rounded text-sm font-bold transition-colors truncate
                        {activePage?.slug === item.slug 
                            ? 'bg-skin-accent text-white shadow-md' 
                            : 'text-skin-muted hover:bg-skin-surface hover:text-skin-text'}"
                    >
                        {item.title}
                    </button>
                    
                    {#if item.children && item.children.length > 0}
                        <div class="ml-4 border-l-2 border-skin-border pl-2 my-1 space-y-1">
                            {#each item.children as child}
                                <button 
                                    on:click={() => loadPage(child.slug)}
                                    class="w-full text-left px-2 py-1 text-xs font-medium transition-colors truncate
                                    {activePage?.slug === child.slug ? 'text-skin-accent' : 'text-skin-muted hover:text-skin-text'}"
                                >
                                    {child.title}
                                </button>
                            {/each}
                        </div>
                    {/if}
                {/each}

                {#if tree.length === 0}
                    <div class="text-xs italic opacity-50">No documents found.</div>
                {/if}
            </div>
        </div>

        <div class="lg:col-span-3 overflow-y-auto bg-skin-surface/30 rounded-xl border border-skin-border/50 p-8">
            {#if pageLoading}
                <div class="h-full flex items-center justify-center opacity-50">
                    <div class="animate-spin text-2xl">⏳</div>
                </div>
            {:else if activePage}
                <article class="prose prose-invert prose-sm max-w-none">
                    <div class="mb-6 pb-6 border-b border-skin-border/30">
                        <h1 class="text-3xl font-black uppercase tracking-tight text-skin-text mb-2">{activePage.title}</h1>
                        <div class="flex items-center gap-4 text-xs font-mono text-skin-muted">
                            <span>LAST UPDATED: {new Date(activePage.updated_at).toLocaleDateString()}</span>
                            <span>•</span>
                            <span>AUTHOR: {activePage.author_name || 'System'}</span>
                        </div>
                    </div>
                    
                    <div class="whitespace-pre-wrap leading-relaxed opacity-90 text-skin-text">
                        {activePage.content}
                    </div>
                </article>
            {:else}
                <div class="h-full flex flex-col items-center justify-center text-skin-muted">
                    <div class="text-4xl mb-2 opacity-50">📜</div>
                    <div class="font-bold text-xs uppercase tracking-widest">Select a document</div>
                </div>
            {/if}
        </div>
    </div>
{/if}