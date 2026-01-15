<script lang="ts">
    import { onMount } from 'svelte';
    import { api, type ContactPage } from '$lib/api';
    import { Save, Loader } from 'lucide-svelte';

    let data: ContactPage = { id: "contact", title: "", subtitle: "", locations: [], form_success_message: "", support_email: "" };
    let loading = false;
    let locJson = '[]';

    onMount(async () => {
        data = await api.getContact();
        locJson = JSON.stringify(data.locations, null, 2);
    });

    async function save() {
        loading = true;
        try {
            data.locations = JSON.parse(locJson);
            await api.updateContact(data);
        } catch(e) { alert("Invalid JSON"); }
        loading = false;
    }
</script>

<div class="p-8 max-w-4xl mx-auto pb-32">
    <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold text-white">Contact Page Settings</h1>
        <button on:click={save} class="bg-blue-600 hover:bg-blue-500 text-white font-bold px-6 py-2 rounded flex gap-2">
            {#if loading}<Loader class="animate-spin" size={18}/>{:else}<Save size={18}/>{/if} Save
        </button>
    </div>

    <div class="space-y-6">
        <div class="bg-gray-900 border border-gray-800 p-6 rounded-xl grid grid-cols-2 gap-4">
            <div class="col-span-2">
                <label class="block text-gray-500 text-xs uppercase mb-1">Page Title</label>
                <input bind:value={data.title} class="w-full bg-gray-950 border border-gray-700 rounded p-2 text-white" />
            </div>
            <div class="col-span-2">
                <label class="block text-gray-500 text-xs uppercase mb-1">Subtitle</label>
                <input bind:value={data.subtitle} class="w-full bg-gray-950 border border-gray-700 rounded p-2 text-white" />
            </div>
            <div>
                <label class="block text-gray-500 text-xs uppercase mb-1">Support Email</label>
                <input bind:value={data.support_email} class="w-full bg-gray-950 border border-gray-700 rounded p-2 text-white" />
            </div>
            <div>
                <label class="block text-gray-500 text-xs uppercase mb-1">Success Message</label>
                <input bind:value={data.form_success_message} class="w-full bg-gray-950 border border-gray-700 rounded p-2 text-white" />
            </div>
        </div>

        <div class="bg-gray-900 border border-gray-800 p-6 rounded-xl">
            <label class="block text-blue-500 text-xs uppercase mb-2">Office Locations (JSON)</label>
            <p class="text-xs text-gray-500 mb-2">Format: <code>[{`{"city": "Zurich", "address": "..."}`}, ...]</code></p>
            <textarea bind:value={locJson} rows="8" class="w-full bg-gray-950 border border-gray-700 rounded p-3 text-green-400 font-mono text-sm"></textarea>
        </div>
    </div>
</div>