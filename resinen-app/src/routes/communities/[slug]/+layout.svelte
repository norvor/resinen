<script lang="ts">
    import { page } from '$app/stores';
    import { api } from '$lib/api';
    import { resolveTheme } from '$lib/config/themes';
    
    // We need to fetch the community data here to determine the theme
    // BEFORE the page renders fully.
    let themeClass = '';
    
    // Reactive statement: When the slug changes, update the theme
    $: loadTheme($page.params.slug);

    async function loadTheme(slug: string) {
        if (!slug) return;
        try {
            const community = await api.getCommunityBySlug(slug);
            if (community && community.archetypes) {
                themeClass = resolveTheme(community.archetypes);
            }
        } catch (e) {
            console.error("Theme load failed", e);
        }
    }
</script>

<div class="min-h-screen bg-skin-fill text-skin-text font-header transition-colors duration-300 {themeClass}">
    <slot />
</div>