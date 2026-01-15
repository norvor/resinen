<script lang="ts">
    import { onMount } from 'svelte';
    import { api, type DoctrinePage } from '$lib/api';
    import { Save, Loader } from 'lucide-svelte';

    let data: DoctrinePage = { id: "doctrine", title: "", subtitle: "", intro_text: "", principles: [], team_members: [] };
    let loading = false;
    
    // JSON Editors
    let principlesJson = '[]';
    let teamJson = '[]';

    onMount(async () => {
        data = await api.getDoctrine();
        principlesJson = JSON.stringify(data.principles, null, 2);
        teamJson = JSON.stringify(data.team_members, null, 2);
    });

    async function save() {
        loading = true;
        try {
            data.principles = JSON.parse(principlesJson);
            data.team_members = JSON.parse(teamJson);
            await api.updateDoctrine(data);
        } catch(e) { alert("Invalid JSON"); }
        loading = false;
    }
</script>

<div class="p-8 max-w-4xl mx-auto pb-32">
    <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold text-white">Doctrine Configuration</h1>
        <button on:click={save} class="bg-yellow-600 hover:bg-yellow-500 text-black font-bold px-6 py-2 rounded flex gap-2">
            {#if loading}<Loader class="animate-spin" size={18}/>{:else}<Save size={18}/>{/if} Save
        </button>
    </div>

    <div class="space-y-6">
        <div class="bg-gray-900 border border-gray-800 p-6 rounded-xl space-y-4">
            <input bind:value={data.title} class="w-full bg-transparent text-2xl font-bold text-white border-b border-gray-700 pb-2 focus:border-yellow-500 outline-none" placeholder="Page Title" />
            <input bind:value={data.subtitle} class="w-full bg-transparent text-gray-400 border-b border-gray-700 pb-2 focus:border-yellow-500 outline-none" placeholder="Subtitle" />
            
            <label class="block text-gray-500 text-xs uppercase pt-2">Manifesto (Introduction)</label>
            <textarea bind:value={data.intro_text} rows="6" class="w-full bg-gray-950 border border-gray-700 rounded p-3 text-white"></textarea>
        </div>

        <div class="bg-gray-900 border border-gray-800 p-6 rounded-xl">
            <label class="block text-yellow-500 text-xs uppercase mb-2">Principles (JSON)</label>
            <textarea bind:value={principlesJson} rows="8" class="w-full bg-gray-950 border border-gray-700 rounded p-3 text-green-400 font-mono text-sm"></textarea>
        </div>

        <div class="bg-gray-900 border border-gray-800 p-6 rounded-xl">
            <label class="block text-yellow-500 text-xs uppercase mb-2">Team Members (JSON)</label>
            <textarea bind:value={teamJson} rows="8" class="w-full bg-gray-950 border border-gray-700 rounded p-3 text-green-400 font-mono text-sm"></textarea>
        </div>
    </div>
</div>