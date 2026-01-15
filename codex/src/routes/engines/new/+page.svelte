<script lang="ts">
    import { api } from '$lib/api';
    import { goto } from '$app/navigation';
    import { Save, ArrowLeft, AlertCircle } from 'lucide-svelte';

    let loading = false;
    let error = '';

    // --- FIELDS ---
    let id = '';
    let name = '';
    let category = '';
    let description = '';
    let bottomLine = '';

    // --- JSON SCAFFOLDING ---
    let heroJson = JSON.stringify({
        title: "The Problem...",
        subtitle: "The Context...",
        solution: "The Fix..."
    }, null, 2);

    let modulesJson = JSON.stringify([
        {
            title: "Module 1",
            problem: "Current State",
            solution: "Future State",
            detail: "Technical implementation details..."
        }
    ], null, 2);

    let comparisonJson = JSON.stringify({
        intro: "Why we win...",
        analogy: "Think of it like...",
        rows: [
            { feature: "Speed", standard: "Slow", resinen: "Fast" }
        ]
    }, null, 2);

    async function handleSubmit() {
        loading = true;
        error = '';

        try {
            const payload = {
                id, name, category, description, bottomLine,
                hero: JSON.parse(heroJson),
                modules: JSON.parse(modulesJson),
                comparison: JSON.parse(comparisonJson)
            };

            await api.createEngine(payload);
            goto('/engines');
        } catch (e: any) {
            console.error(e);
            error = e instanceof SyntaxError 
                ? "Invalid JSON syntax." 
                : "Failed to create engine. ID might be duplicate.";
        } finally {
            loading = false;
        }
    }
</script>

<div class="p-8 max-w-4xl mx-auto pb-32">
    <button on:click={() => goto('/engines')} class="flex items-center gap-2 text-gray-500 hover:text-white mb-6">
        <ArrowLeft size={16} /> Back to List
    </button>

    <h1 class="text-3xl font-bold text-white mb-8">Initialize New Engine</h1>

    {#if error}
        <div class="mb-6 p-4 bg-red-900/20 border border-red-500/50 text-red-400 rounded flex items-center gap-3">
            <AlertCircle size={20} /> {error}
        </div>
    {/if}

    <form on:submit|preventDefault={handleSubmit} class="space-y-8">
        
        <div class="bg-gray-900 border border-gray-800 p-6 rounded-xl space-y-4">
            <h2 class="text-lg font-bold text-white mb-4 border-b border-gray-800 pb-2">System Metadata</h2>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label class="block text-xs font-mono text-gray-500 uppercase mb-1">Engine ID (Slug)</label>
                    <input bind:value={id} type="text" placeholder="e.g. talent-engine" class="w-full bg-gray-950 border border-gray-700 rounded p-2 text-white focus:border-green-500 outline-none" required />
                </div>
                <div>
                    <label class="block text-xs font-mono text-gray-500 uppercase mb-1">Display Name</label>
                    <input bind:value={name} type="text" placeholder="e.g. The Talent Engine" class="w-full bg-gray-950 border border-gray-700 rounded p-2 text-white focus:border-green-500 outline-none" required />
                </div>
            </div>

            <div>
                <label class="block text-xs font-mono text-gray-500 uppercase mb-1">Category</label>
                <input bind:value={category} type="text" placeholder="e.g. HR / Operations" class="w-full bg-gray-950 border border-gray-700 rounded p-2 text-white focus:border-green-500 outline-none" required />
            </div>

            <div>
                <label class="block text-xs font-mono text-gray-500 uppercase mb-1">Description (Short)</label>
                <textarea bind:value={description} rows="3" class="w-full bg-gray-950 border border-gray-700 rounded p-2 text-white focus:border-green-500 outline-none" required></textarea>
            </div>

             <div>
                <label class="block text-xs font-mono text-gray-500 uppercase mb-1">The Bottom Line (Outcome)</label>
                <input bind:value={bottomLine} type="text" class="w-full bg-gray-950 border border-gray-700 rounded p-2 text-white focus:border-green-500 outline-none" />
            </div>
        </div>

        <div class="bg-gray-900 border border-gray-800 p-6 rounded-xl space-y-6">
            <h2 class="text-lg font-bold text-white mb-4 border-b border-gray-800 pb-2">Architecture (JSON)</h2>

            <div>
                <label class="block text-xs font-mono text-green-500 uppercase mb-1">1. Hero Section</label>
                <textarea bind:value={heroJson} rows="6" class="w-full font-mono text-sm bg-gray-950 border border-gray-700 rounded p-3 text-green-400 focus:border-green-500 outline-none"></textarea>
            </div>

            <div>
                <label class="block text-xs font-mono text-green-500 uppercase mb-1">2. Modules Array</label>
                <textarea bind:value={modulesJson} rows="10" class="w-full font-mono text-sm bg-gray-950 border border-gray-700 rounded p-3 text-green-400 focus:border-green-500 outline-none"></textarea>
            </div>

            <div>
                <label class="block text-xs font-mono text-green-500 uppercase mb-1">3. Comparison Table</label>
                <textarea bind:value={comparisonJson} rows="8" class="w-full font-mono text-sm bg-gray-950 border border-gray-700 rounded p-3 text-green-400 focus:border-green-500 outline-none"></textarea>
            </div>
        </div>

        <div class="fixed bottom-0 left-64 right-0 p-6 bg-gray-900 border-t border-gray-800 flex justify-end gap-4 z-50">
            <button type="button" on:click={() => goto('/engines')} class="px-6 py-3 text-gray-400 hover:text-white font-bold transition-colors">Cancel</button>
            <button type="submit" disabled={loading} class="flex items-center gap-2 bg-green-600 hover:bg-green-500 disabled:opacity-50 text-white px-8 py-3 rounded font-bold transition-all shadow-lg shadow-green-900/20">
                {#if loading} <Loader class="animate-spin" size={18} /> Saving... {:else} <Save size={18} /> Initialize Engine {/if}
            </button>
        </div>

    </form>
</div>