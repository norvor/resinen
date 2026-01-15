<script lang="ts">
    import { onMount } from 'svelte';
    import { api, type HomePage } from '$lib/api';
    import { Save, Loader, Layout } from 'lucide-svelte';

    let data: HomePage = {
        id: "home",
        hero_title: "", hero_subtitle: "", 
        hero_cta_primary: "", hero_cta_secondary: "",
        featured_insights: [], ticker_items: []
    };
    
    let loading = false;
    let tickerJson = '[]';
    let insightsJson = '[]';

    onMount(async () => {
        data = await api.getHomePage();
        tickerJson = JSON.stringify(data.ticker_items, null, 2);
        insightsJson = JSON.stringify(data.featured_insights, null, 2);
    });

    async function save() {
        loading = true;
        try {
            data.ticker_items = JSON.parse(tickerJson);
            data.featured_insights = JSON.parse(insightsJson);
            await api.updateHomePage(data);
        } catch (e) {
            alert("Error saving. Check JSON syntax.");
        }
        loading = false;
    }
</script>

<div class="p-8 max-w-4xl mx-auto pb-32">
    <div class="flex justify-between items-center mb-8">
        <div class="flex items-center gap-3">
            <div class="p-2 bg-purple-900/30 rounded text-purple-400">
                <Layout size={24} />
            </div>
            <h1 class="text-3xl font-bold text-white">Homepage Configuration</h1>
        </div>
        <button on:click={save} class="flex items-center gap-2 bg-purple-600 hover:bg-purple-500 px-6 py-2 rounded text-white font-bold transition-colors">
            {#if loading}<Loader class="animate-spin" size={18}/>{:else}<Save size={18}/>{/if} Publish Changes
        </button>
    </div>

    <div class="space-y-8">
        <div class="bg-gray-900 border border-gray-800 p-6 rounded-xl space-y-4">
            <h2 class="text-lg font-bold text-white border-b border-gray-800 pb-2 mb-4">Hero Section</h2>
            
            <div>
                <label class="block text-gray-500 text-xs uppercase mb-1">Main Headline</label>
                <textarea bind:value={data.hero_title} rows="2" class="w-full bg-gray-950 border border-gray-700 rounded p-3 text-white text-2xl font-bold"></textarea>
            </div>
            
            <div>
                <label class="block text-gray-500 text-xs uppercase mb-1">Subtitle</label>
                <textarea bind:value={data.hero_subtitle} rows="3" class="w-full bg-gray-950 border border-gray-700 rounded p-3 text-gray-300"></textarea>
            </div>

            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block text-gray-500 text-xs uppercase mb-1">Primary CTA Label</label>
                    <input bind:value={data.hero_cta_primary} class="w-full bg-gray-950 border border-gray-700 rounded p-2 text-white" />
                </div>
                <div>
                    <label class="block text-gray-500 text-xs uppercase mb-1">Secondary CTA Label</label>
                    <input bind:value={data.hero_cta_secondary} class="w-full bg-gray-950 border border-gray-700 rounded p-2 text-white" />
                </div>
            </div>
        </div>

        <div class="bg-gray-900 border border-gray-800 p-6 rounded-xl">
            <div class="flex justify-between mb-2">
                <h2 class="text-lg font-bold text-white">Live Ticker Items</h2>
                <span class="text-xs font-mono text-gray-500">JSON ARRAY</span>
            </div>
            <p class="text-gray-500 text-sm mb-4">Format: <code>[{`{"label": "Yield", "value": "98%"}`}, ...]</code></p>
            <textarea bind:value={tickerJson} rows="6" class="w-full bg-gray-950 border border-gray-700 rounded p-3 text-green-400 font-mono text-sm"></textarea>
        </div>

        <div class="bg-gray-900 border border-gray-800 p-6 rounded-xl">
            <h2 class="text-lg font-bold text-white mb-2">Featured Insights Grid</h2>
            <p class="text-gray-500 text-sm mb-4">List of Insight IDs to display on the homepage.</p>
            <textarea bind:value={insightsJson} rows="4" class="w-full bg-gray-950 border border-gray-700 rounded p-3 text-green-400 font-mono text-sm"></textarea>
        </div>
    </div>
</div>