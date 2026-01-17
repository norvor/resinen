<script lang="ts">
    import '../app.css';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';

    onMount(() => {
        const token = localStorage.getItem('access_token');
        // If no token AND we are not already on the login page, kick them out
        if (!token && $page.url.pathname !== '/login') {
            goto('/login');
        }
    });
</script>

{#if $page.url.pathname === '/login'}
    <div class="min-h-screen bg-slate-950 text-white">
        <slot />
    </div>

{:else}
    <div class="flex h-screen bg-slate-900 text-white font-sans">
        <aside class="w-64 border-r border-slate-800 bg-slate-950 flex flex-col shrink-0">
            <div class="p-6 border-b border-slate-800">
                <h1 class="font-bold text-xl tracking-tight text-orange-500">CODEX</h1>
                <p class="text-xs text-slate-400">Resinen Admin Panel</p>
            </div>

            <nav class="...">
               <a href="/settings" class="flex items-center gap-3 px-4 py-3 text-slate-400 hover:text-white hover:bg-slate-800 rounded-xl transition-all font-bold text-sm">
                    <span>⚙️ Settings</span>
                </a>
               
                <a href="/communities" class="... flex items-center gap-3 ...">
                    <span>🏰 Communities</span>
                </a>

                <a href="/cms" class="flex items-center gap-3 px-4 py-3 text-slate-400 hover:text-white hover:bg-slate-800 rounded-xl transition-all font-bold text-sm">
                    <span>📝 Website CMS</span>
                </a>
            </nav>

            <div class="p-4 border-t border-slate-800">
                <button 
                    on:click={() => {
                        localStorage.removeItem('access_token');
                        goto('/login');
                    }}
                    class="flex items-center gap-2 text-xs text-slate-500 hover:text-red-400 transition-colors"
                >
                    <span>⚠</span> TERMINATE SESSION
                </button>
            </div>
        </aside>

        <main class="flex-1 overflow-y-auto bg-slate-900 p-8">
            <slot />
        </main>
    </div>
{/if}