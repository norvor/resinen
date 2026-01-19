<script lang="ts">
    import '../app.css';
    import { onMount } from 'svelte';
    import { api, user } from '$lib/api';
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';

    let checkingAuth = true;
    let communities = [];

    onMount(async () => {
        const token = localStorage.getItem('token');
        const isAuthPage = $page.url.pathname === '/login' || $page.url.pathname === '/signup';

        if (!token) {
            checkingAuth = false;
            if (!isAuthPage) goto('/login');
            return;
        }

        try {
            if (!$user) {
                await api.getMe();
            }
            // Fetch the sidebar communities
            communities = await api.getCommunities();
            
            if (isAuthPage) goto('/');
        } catch (err) {
            localStorage.removeItem('token');
            if (!isAuthPage) goto('/login');
        } finally {
            checkingAuth = false;
        }
    });

    function logout() {
        localStorage.removeItem('token');
        user.set(null);
        goto('/login');
    }
</script>

{#if checkingAuth}
    <div class="min-h-screen bg-black flex items-center justify-center font-mono text-green-500">
        <span class="animate-pulse">LOADING_SYSTEM_RESOURCES...</span>
    </div>
{:else if $page.url.pathname === '/login' || $page.url.pathname === '/signup'}
    <slot />
{:else}
    <div class="flex h-screen bg-skin-fill text-skin-text overflow-hidden">
        <aside class="w-20 md:w-64 border-r border-skin-border flex flex-col bg-skin-surface">
            <div class="p-4 border-b border-skin-border flex items-center gap-3">
                <div class="w-8 h-8 bg-skin-accent flex items-center justify-center font-black text-white">R</div>
                <span class="font-black uppercase tracking-tighter hidden md:block">Resinen</span>
            </div>
            
            <nav class="flex-1 overflow-y-auto p-2 space-y-2">
                <a href="/" class="flex items-center gap-3 p-3 rounded hover:bg-skin-fill transition-colors {$page.url.pathname === '/' ? 'bg-skin-fill border border-skin-border' : ''}">
                    <span class="text-xl">🏠</span>
                    <span class="text-xs font-bold uppercase hidden md:block">Command Center</span>
                </a>
                
                <div class="mt-6 mb-2 px-3 text-[10px] font-black text-skin-muted uppercase tracking-widest hidden md:block">Territories</div>
                
                {#each communities as c}
                    <a href="/c/{c.slug}" class="flex items-center gap-3 p-3 rounded hover:bg-skin-fill transition-colors group">
                        <div class="w-8 h-8 rounded bg-skin-border flex items-center justify-center group-hover:border-skin-accent border border-transparent transition-all">
                            {c.name[0]}
                        </div>
                        <div class="hidden md:block min-w-0">
                            <div class="text-xs font-bold truncate">{c.name}</div>
                            <div class="text-[9px] text-skin-muted uppercase">{c.archetypes[0]}</div>
                        </div>
                    </a>
                {/each}
            </nav>

            <div class="p-4 border-t border-skin-border">
                <button on:click={logout} class="w-full text-left text-[10px] font-bold uppercase text-skin-muted hover:text-red-500 transition-colors flex items-center gap-2">
                    <span>⏻</span> <span class="hidden md:block">Terminate Session</span>
                </button>
            </div>
        </aside>

        <main class="flex-1 flex flex-col min-w-0 overflow-hidden">
            <header class="h-16 border-b border-skin-border flex items-center justify-between px-6 bg-skin-surface/50 backdrop-blur-md">
                <div class="flex items-center gap-4">
                    <h2 class="font-black uppercase tracking-widest text-sm">
                        {$page.url.pathname === '/' ? 'Home' : 'Territory_View'}
                    </h2>
                </div>
                
                <div class="flex items-center gap-4">
                    <div class="text-right hidden sm:block">
                        <div class="text-[10px] font-black text-skin-accent uppercase leading-none">Level {$user?.level || 1}</div>
                        <div class="text-xs font-bold">{$user?.full_name}</div>
                    </div>
                    <div class="w-10 h-10 rounded-full border-2 border-skin-accent p-0.5">
                        <div class="w-full h-full bg-skin-border rounded-full flex items-center justify-center font-bold">
                            {$user?.full_name?.[0]}
                        </div>
                    </div>
                </div>
            </header>

            <div class="flex-1 overflow-y-auto p-6 md:p-10">
                <slot />
            </div>
        </main>
    </div>
{/if}