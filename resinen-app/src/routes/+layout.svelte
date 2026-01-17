<script lang="ts">
    import "../app.css";
    import { page } from '$app/stores';
    import { user, logout } from '$lib/api';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';

    // Protect Routes (Bouncer Logic)
    onMount(() => {
        const unsubscribe = user.subscribe(u => {
            // FIX 1: Allow both /login AND /signup without redirecting
            if (!u && $page.url.pathname !== '/login' && $page.url.pathname !== '/signup') {
                goto('/login');
            }
        });
        return unsubscribe;
    });

    const navItems = [
        { label: "Dashboard", path: "/dashboard", color: "bg-sp-cyan" },
        { label: "My Identity", path: "/identity", color: "bg-sp-yellow" },
        { label: "Governance", path: "/governance", color: "bg-sp-green" },
        { label: "Treasury", path: "/treasury", color: "bg-sp-orange" },
    ];
</script>

{#if $page.url.pathname === '/login' || $page.url.pathname === '/signup'}
    <slot />
{:else}
    <div class="min-h-screen flex flex-col md:flex-row font-sans">
        
        <aside class="w-full md:w-64 bg-sp-blue border-r-4 border-black p-6 flex flex-col gap-6 relative z-20">
            
            <div class="bg-white border-4 border-black p-3 shadow-hard transform -rotate-2 text-center">
                <h1 class="font-black text-2xl uppercase tracking-tighter">RESINEN <span class="text-sp-red">APP</span></h1>
            </div>

            <nav class="flex-1 space-y-4 mt-4">
                {#each navItems as item}
                    <a 
                        href={item.path} 
                        class="block border-4 border-black p-3 shadow-hard font-black uppercase text-sm hover:translate-x-1 hover:translate-y-1 hover:shadow-hard-sm transition-all
                        {$page.url.pathname.startsWith(item.path) ? item.color : 'bg-white'}"
                    >
                        {item.label}
                    </a>
                {/each}
            </nav>

            <div class="mt-auto bg-[#5D3A1F] p-4 border-4 border-black shadow-hard relative group cursor-pointer" on:click={logout}>
                <div class="absolute -top-8 left-1/2 -translate-x-1/2 bg-black text-white text-[10px] font-bold px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                    CLICK TO LOGOUT
                </div>

                <div class="flex items-center gap-3 mb-2">
                    <div class="w-10 h-10 bg-sp-yellow border-2 border-black rounded-full flex items-center justify-center font-black text-xl">
                        {$user?.full_name?.charAt(0) || '?'}
                    </div>
                    
                    <div class="leading-none overflow-hidden">
                        <div class="text-white font-bold text-xs uppercase">Operator</div>
                        <div class="text-[#FFD700] font-black truncate">{$user?.full_name || 'Guest'}</div>
                    </div>
                </div>
            </div>
        </aside>

        <main class="flex-1 p-8 overflow-y-auto relative">
            <div class="absolute inset-0 z-0 opacity-10 pointer-events-none" 
                 style="background-image: radial-gradient(circle, #000 1px, transparent 1px); background-size: 20px 20px;">
            </div>
            
            <div class="relative z-10 max-w-5xl mx-auto">
                <slot />
            </div>
        </main>
    </div>
{/if}