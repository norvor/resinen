<script lang="ts">
    import { page } from '$app/stores';
    import { api } from '$lib/api';
    import { resolveTheme } from '$lib/config/themes';
    import { setContext } from 'svelte';
    import { writable } from 'svelte/store';
    import type { Community, Membership } from '$lib/types';

    // --- STATE STORES ---
    // We create stores to share data with all child pages (The Engines)
    // This allows deep components to access the current community without prop drilling.
    const communityStore = writable<Community | null>(null);
    const membershipStore = writable<Membership | null>(null);

    // Make them available via getContext('community') and getContext('membership')
    setContext('community', communityStore);
    setContext('membership', membershipStore);

    let themeClass = '';
    let loading = true;

    // --- REACTIVITY ---
    // When the URL slug changes (e.g. switching communities), reload the context
    $: loadContext($page.params.slug);

    async function loadContext(slug: string) {
        if (!slug) return;
        loading = true;
        
        try {
            // 1. Fetch the Community Details
            const c = await api.getCommunityBySlug(slug);
            communityStore.set(c);

            // 2. Set the Visual Theme (Archetypes)
            if (c && (c as any).archetypes) {
                themeClass = resolveTheme((c as any).archetypes);
            }

            // 3. Check Membership (Are we a Member, Admin, or Guest?)
            // We need the ID from the community object to check membership status
            if (c && c.id) {
                try {
                    const m = await api.getMembershipStatus(c.id);
                    membershipStore.set(m);
                } catch (err) {
                    // 404 or 401 usually means "Not a member yet" or "Guest"
                    membershipStore.set(null); 
                }
            }
        } catch (e) {
            console.error("Territory Load Failed:", e);
            communityStore.set(null);
        } finally {
            loading = false;
        }
    }
</script>

<div class="min-h-screen bg-skin-fill text-skin-text font-header transition-colors duration-300 {themeClass}">
    {#if loading}
        <div class="fixed top-0 left-0 w-full h-1 bg-zinc-200 z-50">
            <div class="h-full bg-black animate-progress-indeterminate"></div>
         </div>
    {/if}
    <slot />
</div>

<style>
    /* Cinematic indeterminate loader */
    @keyframes progress-indeterminate {
        0% { left: 0%; width: 0%; }
        50% { left: 25%; width: 50%; }
        100% { left: 100%; width: 0%; }
    }
    .animate-progress-indeterminate {
        position: relative;
        animation: progress-indeterminate 1.5s infinite linear;
    }
</style>