<script lang="ts">
    import { api } from '$lib/api';
    import { goto } from '$app/navigation';
    import { Save, ArrowLeft, AlertCircle } from 'lucide-svelte';

    let loading = false;
    let error = '';

    // --- TOP LEVEL FIELDS ---
    let id = '';
    let name = '';
    let subject = '';
    let description = '';

    // --- COMPLEX FIELDS (JSON STRINGS) ---
    // We initialize these with "Scaffolding" so it's easy to fill out.
    let summaryJson = JSON.stringify({
        p1: "Paragraph 1...",
        p2: "Paragraph 2...",
        directive: "The core directive..."
    }, null, 2);

    let nodesJson = JSON.stringify([
        {
            id: "A",
            name: "Node Name",
            function: "What it does",
            logic: "The logic model",
            input: "Data needed",
            output: "Result produced",
            failureState: "What happens if it fails"
        }
    ], null, 2);

    let solutionJson = JSON.stringify({
        intro: "Why this path works...",
        path: ["A", "B", "C"],
        reasons: [{ title: "Step 1", description: "Reason..." }]
    }, null, 2);

    // (Simplified for brevity - you can add Isomorphism/Formulas later or leave empty object)
    let isomorphismJson = '{}';
    let formulasJson = '{}';
    let protocolJson = '{}';
    let valuesJson = '{}';

    async function handleSubmit() {
        loading = true;
        error = '';

        try {
            // 1. Parse JSON fields to ensure they are valid
            const payload = {
                id, name, subject, description,
                summary: JSON.parse(summaryJson),
                nodes: JSON.parse(nodesJson),
                solution: JSON.parse(solutionJson),
                isomorphism: JSON.parse(isomorphismJson),
                formulas: JSON.parse(formulasJson),
                protocol: JSON.parse(protocolJson),
                values: JSON.parse(valuesJson)
            };

            // 2. Send to API
            await api.createFramework(payload);
            
            // 3. Redirect back to list
            goto('/frameworks');

        } catch (e: any) {
            console.error(e);
            if (e instanceof SyntaxError) {
                error = "Invalid JSON in one of the fields. Please check your syntax.";
            } else {
                error = "Failed to create framework. Ensure ID is unique.";
            }
        } finally {
            loading = false;
        }
    }
</script>

<div class="p-8 max-w-4xl mx-auto pb-32">
    <button on:click={() => goto('/frameworks')} class="flex items-center gap-2 text-gray-500 hover:text-white mb-6">
        <ArrowLeft size={16} /> Back to List
    </button>

    <h1 class="text-3xl font-bold text-white mb-8">Create New Framework</h1>

    {#if error}
        <div class="mb-6 p-4 bg-red-900/20 border border-red-500/50 text-red-400 rounded flex items-center gap-3">
            <AlertCircle size={20} />
            {error}
        </div>
    {/if}

    <form on:submit|preventDefault={handleSubmit} class="space-y-8">
        
        <div class="bg-gray-900 border border-gray-800 p-6 rounded-xl space-y-4">
            <h2 class="text-lg font-bold text-white mb-4 border-b border-gray-800 pb-2">Core Metadata</h2>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label class="block text-xs font-mono text-gray-500 uppercase mb-1">Framework ID (Slug)</label>
                    <input bind:value={id} type="text" placeholder="e.g. alpine-quant-yield" class="w-full bg-gray-950 border border-gray-700 rounded p-2 text-white focus:border-cyan-500 outline-none" required />
                </div>
                <div>
                    <label class="block text-xs font-mono text-gray-500 uppercase mb-1">Display Name</label>
                    <input bind:value={name} type="text" placeholder="e.g. Alpine Quant-Yield" class="w-full bg-gray-950 border border-gray-700 rounded p-2 text-white focus:border-cyan-500 outline-none" required />
                </div>
            </div>

            <div>
                <label class="block text-xs font-mono text-gray-500 uppercase mb-1">Subject / Category</label>
                <input bind:value={subject} type="text" placeholder="e.g. SEO Optimization" class="w-full bg-gray-950 border border-gray-700 rounded p-2 text-white focus:border-cyan-500 outline-none" required />
            </div>

            <div>
                <label class="block text-xs font-mono text-gray-500 uppercase mb-1">Description (Hero Text)</label>
                <textarea bind:value={description} rows="3" class="w-full bg-gray-950 border border-gray-700 rounded p-2 text-white focus:border-cyan-500 outline-none" required></textarea>
            </div>
        </div>

        <div class="bg-gray-900 border border-gray-800 p-6 rounded-xl space-y-6">
            <h2 class="text-lg font-bold text-white mb-4 border-b border-gray-800 pb-2">Deep Structure (JSON)</h2>
            <p class="text-sm text-gray-500">Edit the raw data structure below. Be careful with commas and brackets.</p>

            <div>
                <label class="block text-xs font-mono text-cyan-500 uppercase mb-1">1. Summary Object</label>
                <textarea bind:value={summaryJson} rows="6" class="w-full font-mono text-sm bg-gray-950 border border-gray-700 rounded p-3 text-green-400 focus:border-cyan-500 outline-none"></textarea>
            </div>

            <div>
                <label class="block text-xs font-mono text-cyan-500 uppercase mb-1">2. Nodes Array (The Graph)</label>
                <textarea bind:value={nodesJson} rows="10" class="w-full font-mono text-sm bg-gray-950 border border-gray-700 rounded p-3 text-green-400 focus:border-cyan-500 outline-none"></textarea>
            </div>

            <div>
                <label class="block text-xs font-mono text-cyan-500 uppercase mb-1">3. Solution Object (The Path)</label>
                <textarea bind:value={solutionJson} rows="8" class="w-full font-mono text-sm bg-gray-950 border border-gray-700 rounded p-3 text-green-400 focus:border-cyan-500 outline-none"></textarea>
            </div>
        </div>

        <div class="fixed bottom-0 left-64 right-0 p-6 bg-gray-900 border-t border-gray-800 flex justify-end gap-4 z-50">
            <button type="button" on:click={() => goto('/frameworks')} class="px-6 py-3 text-gray-400 hover:text-white font-bold transition-colors">
                Cancel
            </button>
            <button type="submit" disabled={loading} class="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white px-8 py-3 rounded font-bold transition-all shadow-lg shadow-cyan-900/20">
                {#if loading}
                    <Loader class="animate-spin" size={18} /> Saving...
                {:else}
                    <Save size={18} /> Create Framework
                {/if}
            </button>
        </div>

    </form>
</div>