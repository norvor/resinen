<script lang="ts">
    import '../app.css'; 
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    import { browser } from '$app/environment';
    import { fade } from 'svelte/transition';

    let loading = true;

    onMount(async () => {
        if (browser) {
            const token = localStorage.getItem('access_token');
            if (token) {
                try {
                    // Verify token validity with backend
                    await api.getMe();
                    console.log("✅ SYSTEM: User Identity Verified");
                } catch (e) {
                    console.warn("⚠️ SYSTEM: Session Expired or Invalid");
                    localStorage.removeItem('access_token');
                }
            }
        }
        // Artificial delay for cinematic effect (optional, can remove setTimeout)
        setTimeout(() => {
            loading = false;
        }, 500);
    });
</script>

<div class="min-h-screen bg-zinc-50 text-zinc-900 font-sans selection:bg-yellow-200">
    {#if loading}
        <div class="fixed inset-0 flex flex-col items-center justify-center bg-zinc-900 z-50 text-white" out:fade={{ duration: 200 }}>
            <div class="w-12 h-12 border-4 border-zinc-700 border-t-white rounded-full animate-spin mb-6"></div>
            <div class="font-mono text-xs uppercase tracking-[0.2em] animate-pulse text-zinc-400">
                Initializing Resinen OS...
            </div>
        </div>
    {:else}
        <slot />
    {/if}
</div>