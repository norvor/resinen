<script lang="ts">
    import { onMount } from 'svelte';
    import { api, type SiteConfig } from '$lib/api';
    import { Save, Loader } from 'lucide-svelte';

    let config: SiteConfig = {
        id: "global", brand_name: "", logo_url: "", contact_email: "", footer_text: "",
        social_links: {}, navigation: []
    };
    let loading = false;

    // Helper for JSON fields
    let socialJson = '{}';
    let navJson = '[]';

    onMount(async () => {
        config = await api.getConfig();
        socialJson = JSON.stringify(config.social_links, null, 2);
        navJson = JSON.stringify(config.navigation, null, 2);
    });

    async function save() {
        loading = true;
        config.social_links = JSON.parse(socialJson);
        config.navigation = JSON.parse(navJson);
        await api.updateConfig(config);
        loading = false;
    }
</script>

<div class="p-8 max-w-4xl mx-auto">
    <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold text-white">Global Identity</h1>
        <button on:click={save} class="flex items-center gap-2 bg-cyan-600 px-6 py-2 rounded text-white font-bold hover:bg-cyan-500">
            {#if loading}<Loader class="animate-spin" size={18}/>{:else}<Save size={18}/>{/if} Save Changes
        </button>
    </div>

    <div class="space-y-6">
        <div class="bg-gray-900 p-6 rounded-xl border border-gray-800">
            <label class="block text-gray-500 text-xs uppercase mb-1">Brand Name</label>
            <input bind:value={config.brand_name} class="w-full bg-gray-950 border border-gray-700 rounded p-2 text-white" />
        </div>
        
        <div class="bg-gray-900 p-6 rounded-xl border border-gray-800 grid grid-cols-2 gap-4">
            <div>
                <label class="block text-gray-500 text-xs uppercase mb-1">Logo URL</label>
                <input bind:value={config.logo_url} class="w-full bg-gray-950 border border-gray-700 rounded p-2 text-white" />
            </div>
            <div>
                <label class="block text-gray-500 text-xs uppercase mb-1">Contact Email</label>
                <input bind:value={config.contact_email} class="w-full bg-gray-950 border border-gray-700 rounded p-2 text-white" />
            </div>
        </div>

        <div class="bg-gray-900 p-6 rounded-xl border border-gray-800">
            <label class="block text-gray-500 text-xs uppercase mb-1">Navigation Menu (JSON)</label>
            <textarea bind:value={navJson} rows="5" class="w-full bg-gray-950 border border-gray-700 rounded p-2 text-green-400 font-mono text-sm"></textarea>
        </div>
        
        <div class="bg-gray-900 p-6 rounded-xl border border-gray-800">
            <label class="block text-gray-500 text-xs uppercase mb-1">Social Links (JSON)</label>
            <textarea bind:value={socialJson} rows="5" class="w-full bg-gray-950 border border-gray-700 rounded p-2 text-green-400 font-mono text-sm"></textarea>
        </div>
    </div>
</div>