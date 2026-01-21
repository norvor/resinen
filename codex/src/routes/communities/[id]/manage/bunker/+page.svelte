<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    
    export let data;
    $: community = data.community;

    let logs: any[] = [];
    let loading = true;
    let nuking = false;

    onMount(async () => {
        await loadLogs();
    });

    async function loadLogs() {
        loading = true;
        try {
            // Fetch admin logs (bypasses TTL filtering)
            const res = await api.getBunkerLogs(community.id);
            logs = Array.isArray(res) ? res : [];
        } catch (e) { console.error(e); } 
        finally { loading = false; }
    }

    async function handleNuke() {
        const confirmText = "NUKE";
        const input = prompt(`WARNING: This will permanently delete ALL messages in the Bunker.\n\nType "${confirmText}" to confirm.`);
        
        if (input !== confirmText) return;

        nuking = true;
        try {
            await api.nukeBunker(community.id);
            logs = [];
            alert("Channel wiped successfully.");
        } catch (e) {
            alert("Nuke failed. Systems unresponsive.");
        } finally {
            nuking = false;
        }
    }
</script>

<div class="space-y-8 animate-fade-in-up">
    
    <div class="flex items-end justify-between border-b-4 border-black pb-6">
        <div>
            <div class="text-xs font-black uppercase text-green-700 tracking-widest mb-1 flex items-center gap-2">
                <span>☢️</span> Bunker Engine
            </div>
            <h1 class="text-4xl font-black uppercase tracking-tighter">
                Secure Comms
            </h1>
        </div>
        <button 
            on:click={handleNuke}
            disabled={nuking}
            class="px-6 py-3 bg-red-600 text-white font-black rounded uppercase text-xs shadow-[4px_4px_0px_black] hover:-translate-y-1 hover:shadow-[6px_6px_0px_black] transition-all disabled:opacity-50 disabled:translate-y-0 disabled:shadow-none"
        >
            {nuking ? 'Wiping Data...' : '☢️ Nuke Channel'}
        </button>
    </div>

    <div class="bg-black rounded-xl overflow-hidden border-4 border-zinc-800 shadow-2xl">
        <div class="bg-zinc-900 px-4 py-2 border-b border-zinc-800 flex justify-between items-center">
            <span class="text-[10px] font-mono font-bold text-green-500 uppercase">System Logs // Admin Access</span>
            <span class="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
        </div>
        
        <div class="h-[500px] overflow-y-auto p-4 font-mono text-xs space-y-2 bg-black text-green-400">
            {#if loading}
                <div class="animate-pulse">DECRYPTING_PACKETS...</div>
            {:else if logs.length === 0}
                <div class="text-zinc-600">No signals detected. Channel is clean.</div>
            {:else}
                {#each logs as msg}
                    <div class="flex gap-4 hover:bg-white/5 p-1 rounded">
                        <span class="text-zinc-500 shrink-0 select-none">{new Date(msg.created_at).toLocaleTimeString()}</span>
                        <span class="font-bold text-zinc-300 shrink-0 select-none">[{msg.id.substring(0,4)}]</span>
                        <span class="break-all">{msg.content}</span>
                    </div>
                {/each}
            {/if}
        </div>
    </div>

</div>