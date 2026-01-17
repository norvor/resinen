<script lang="ts">
    import { api } from '$lib/api';
    import { onMount } from 'svelte';

    let laws: any[] = [];
    let newLaw = { title: '', body: '', severity: 'standard' };

    onMount(async () => {
        laws = await api.getGlobalLaws(); // You'll add this getter to api.ts
    });

    async function addLaw() {
        await api.post('/governance/global', newLaw);
        laws = await api.getGlobalLaws(); // Refresh
        newLaw = { title: '', body: '', severity: 'standard' };
    }
</script>

<div class="max-w-4xl mx-auto text-white p-8">
    <h1 class="text-4xl font-bold mb-2 text-orange-500">The Resinen Constitution</h1>
    <p class="text-slate-400 mb-8">These laws apply to every single user and community on the network.</p>

    <div class="bg-slate-900 p-6 rounded-xl border border-slate-800 mb-8">
        <h3 class="font-bold mb-4">Draft New Article</h3>
        <div class="grid gap-4">
            <input bind:value={newLaw.title} placeholder="Law Title (e.g. No Hate Speech)" class="bg-slate-950 p-3 rounded border border-slate-700 text-white" />
            <textarea bind:value={newLaw.body} placeholder="Legal text..." class="bg-slate-950 p-3 rounded border border-slate-700 text-white" rows="3"></textarea>
            <select bind:value={newLaw.severity} class="bg-slate-950 p-3 rounded border border-slate-700 text-white">
                <option value="standard">Standard Violation (Warning)</option>
                <option value="critical">Critical Violation (Immediate Ban)</option>
            </select>
            <button on:click={addLaw} class="bg-orange-600 hover:bg-orange-500 py-3 rounded font-bold">Ratify Law</button>
        </div>
    </div>

    <div class="space-y-4">
        {#each laws as law}
            <div class="p-6 border-l-4 border-orange-500 bg-slate-900 rounded-r-xl">
                <h4 class="font-bold text-lg">{law.title}</h4>
                <p class="text-slate-400 mt-1">{law.body}</p>
                <span class="text-xs uppercase font-bold mt-2 inline-block px-2 py-1 bg-slate-800 rounded text-orange-400">{law.severity}</span>
            </div>
        {/each}
    </div>
</div>