<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { api } from '$lib/api';
    export let community: any;

    let messages: any[] = [];
    let loading = true;
    let newMessage = '';
    let isAnon = false;
    let ttl = 3600; // 1 Hour Default
    let interval: any;

    async function loadFeed() {
        try {
            messages = await api.getBunkerMessages(community.id);
        } catch (e) {
            console.error(e);
        } finally {
            loading = false;
        }
    }

    onMount(() => {
        loadFeed();
        // Auto-refresh every 10s to clear expired items
        interval = setInterval(loadFeed, 10000); 
    });

    onDestroy(() => {
        if (interval) clearInterval(interval);
    });

    async function send() {
        if (!newMessage.trim()) return;
        try {
            await api.postBunkerMessage(community.id, newMessage, isAnon, ttl);
            newMessage = '';
            await loadFeed();
        } catch (e) {
            alert("Transmission failed.");
        }
    }

    function getTimeLeft(expiry: string) {
        const diff = new Date(expiry).getTime() - new Date().getTime();
        if (diff <= 0) return "EXPIRED";
        const mins = Math.floor(diff / 60000);
        return mins < 1 ? "<1m" : `${mins}m`;
    }
</script>

<div class="max-w-3xl mx-auto space-y-8">
    
    <div class="bg-black border border-green-900/50 p-4 rounded-lg shadow-lg relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-green-500/50 to-transparent opacity-50"></div>
        
        <textarea 
            bind:value={newMessage}
            placeholder="Enter encrypted transmission..." 
            class="w-full bg-transparent text-green-500 font-mono text-sm placeholder-green-900 focus:outline-none resize-none h-20 mb-4"
        ></textarea>
        
        <div class="flex justify-between items-center border-t border-green-900/30 pt-4">
            <div class="flex gap-4">
                <label class="flex items-center gap-2 cursor-pointer select-none">
                    <input type="checkbox" bind:checked={isAnon} class="accent-green-500" />
                    <span class="text-xs font-mono font-bold uppercase text-green-700 {isAnon ? 'text-green-400' : ''}">
                        {isAnon ? '🕵️ ANONYMOUS' : '👤 PUBLIC ID'}
                    </span>
                </label>

                <select bind:value={ttl} class="bg-black text-green-700 text-xs font-mono border border-green-900 focus:outline-none px-2 rounded">
                    <option value={60}>1 Min (Burn)</option>
                    <option value={3600}>1 Hour</option>
                    <option value={86400}>24 Hours</option>
                </select>
            </div>

            <button on:click={send} class="px-6 py-1 bg-green-900/20 text-green-500 border border-green-500/50 font-mono text-xs uppercase hover:bg-green-500 hover:text-black transition-colors">
                Transinit
            </button>
        </div>
    </div>

    {#if loading}
        <div class="text-center font-mono text-xs text-green-900 animate-pulse">ESTABLISHING UPLINK...</div>
    {:else}
        <div class="space-y-4">
            {#each messages as msg}
                <div class="bg-black/80 border-l-2 border-green-900/50 p-4 font-mono relative group hover:border-green-500/50 transition-colors">
                    
                    <div class="flex justify-between items-start mb-2 text-[10px] uppercase tracking-wider text-green-800">
                        <div class="flex items-center gap-2">
                            {#if msg.author_name === 'Redacted'}
                                <span class="bg-green-900 text-black px-1">██████</span>
                            {:else}
                                <span class="text-green-600">{msg.author_name}</span>
                            {/if}
                            <span class="opacity-50">:: {new Date(msg.created_at).toLocaleTimeString()}</span>
                        </div>
                        <div class="text-red-900 font-bold group-hover:text-red-500 transition-colors">
                            T-MINUS {getTimeLeft(msg.expires_at)}
                        </div>
                    </div>

                    <div class="text-green-500 text-sm leading-relaxed whitespace-pre-wrap break-words opacity-90">
                        {msg.content}
                    </div>

                </div>
            {/each}

            {#if messages.length === 0}
                <div class="text-center py-12 opacity-30">
                    <div class="text-4xl mb-2">📡</div>
                    <div class="font-mono text-xs text-green-500">NO ACTIVE SIGNALS</div>
                </div>
            {/if}
        </div>
    {/if}
</div>