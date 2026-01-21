<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { api } from '$lib/api';

    // State
    let community: any = null;
    let loading = true;

    // 1. DEFINITIONS: How each engine should look
    const ENGINE_CONFIG: Record<string, { label: string, icon: string, color: string }> = {
        social:  { label: 'Social Feed', icon: '💬', color: 'text-blue-700 bg-blue-50' },
        arena:   { label: 'The Arena',   icon: '🏆', color: 'text-red-700 bg-red-50' },
        guild:   { label: 'The Guild',   icon: '💰', color: 'text-yellow-700 bg-yellow-50' },
        senate:  { label: 'The Senate',  icon: '⚖️', color: 'text-purple-700 bg-purple-50' },
        garden:  { label: 'The Garden',  icon: '🌻', color: 'text-green-700 bg-green-50' },
        library: { label: 'The Library', icon: '📚', color: 'text-orange-700 bg-orange-50' },
        club:    { label: 'The Club',    icon: '🎉', color: 'text-pink-700 bg-pink-50' },
        bunker:  { label: 'The Bunker',  icon: '☢️', color: 'text-green-400 bg-zinc-800' },
        academy: { label: 'Academy',     icon: '🎓', color: 'text-indigo-700 bg-indigo-50' },
        stage:   { label: 'The Stage',   icon: '🎥', color: 'text-rose-700 bg-rose-50' },
        bazaar:  { label: 'Bazaar',      icon: '🛍️', color: 'text-emerald-700 bg-emerald-50' },
    };

    // Reactive: Whenever the ID in the URL changes, fetch data
    $: communityId = $page.params.id;
    $: if (communityId) loadCommunity(communityId);

    async function loadCommunity(id: string) {
        try {
            loading = true;
            community = await api.getCommunity(id);
        } catch (e) {
            console.error("Layout fetch failed:", e);
        } finally {
            loading = false;
        }
    }

    // Helper for active links
    $: isActive = (path: string) => $page.url.pathname.includes(path);
</script>

<div class="min-h-screen bg-gray-50 flex flex-col md:flex-row font-sans text-gray-900">
    
    {#if community}
        <aside class="w-full md:w-64 bg-white border-r border-gray-200 flex-shrink-0 h-auto md:h-screen sticky top-0 overflow-y-auto">
            <div class="p-6 border-b border-gray-100">
                <h1 class="font-black text-xl uppercase tracking-tighter leading-none mb-1">{community.name}</h1>
                <div class="text-xs font-bold text-gray-400 uppercase tracking-widest">Codex Control</div>
            </div>

            <nav class="p-4 space-y-8">
                <div>
                    <div class="px-3 mb-2 text-[10px] font-black uppercase text-gray-400 tracking-widest">General</div>
                    <div class="space-y-1">
                        <a href="/communities/{community.id}" class="block px-3 py-2 rounded-md text-sm font-bold {isActive(`/communities/${community.id}`) && !isActive('/settings') ? 'bg-black text-white' : 'text-gray-600 hover:bg-gray-100'}">Overview</a>
                        <a href="/communities/{community.id}/settings" class="block px-3 py-2 rounded-md text-sm font-bold {isActive('/settings') ? 'bg-black text-white' : 'text-gray-600 hover:bg-gray-100'}">Settings</a>
                    </div>
                </div>
                
                <div>
                    <div class="px-3 mb-2 text-[10px] font-black uppercase text-gray-400 tracking-widest">
                        Installed Engines
                    </div>
                    
                    <div class="space-y-1">
                        {#if community.installed_engines && community.installed_engines.length > 0}
                            {#each community.installed_engines as engineKey}
                                {#if ENGINE_CONFIG[engineKey]}
                                    {@const config = ENGINE_CONFIG[engineKey]}
                                    <a href="/communities/{community.id}/manage/{engineKey}" 
                                    class="flex items-center gap-3 px-3 py-2 rounded-md text-sm font-bold transition-colors 
                                    {isActive(`/manage/${engineKey}`) ? config.color : 'text-gray-600 hover:bg-gray-100'}">
                                        <span>{config.icon}</span> 
                                        {config.label}
                                    </a>
                                {/if}
                            {/each}
                        {:else}
                            <div class="px-3 py-2 text-xs text-gray-400 italic">
                                No engines installed.
                            </div>
                        {/if}
                    </div>
                </div>
            </nav>
        </aside>
    {:else}
        <aside class="w-full md:w-64 bg-white border-r border-gray-200 h-screen p-6">
            <div class="h-8 bg-gray-200 rounded animate-pulse mb-8"></div>
            <div class="space-y-4">
                <div class="h-4 w-1/2 bg-gray-100 rounded animate-pulse"></div>
                <div class="h-10 bg-gray-100 rounded animate-pulse"></div>
            </div>
        </aside>
    {/if}

    <main class="flex-1 p-6 md:p-12 overflow-y-auto">
        <slot />
    </main>

</div>