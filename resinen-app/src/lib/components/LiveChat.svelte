<script lang="ts">
    import { onMount, onDestroy, afterUpdate } from 'svelte';
    import { user } from '$lib/api';
    import { messages, isConnected, connectToCommunity, disconnect, sendMessage } from '$lib/socket';

    export let communityId: string;

    let inputMessage = "";
    let chatContainer: HTMLElement;

    // 1. Connect when the component mounts
    onMount(() => {
        if (communityId) {
            connectToCommunity(communityId);
        }
    });

    // 2. Disconnect when the user leaves the page
    onDestroy(() => {
        disconnect();
    });

    // 3. Auto-scroll to bottom when new messages arrive
    afterUpdate(() => {
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    });

    function handleSend() {
        if (!inputMessage.trim()) return;
        
        // We need user details to send a message
        if (!$user) {
            console.error("Cannot chat: Not logged in");
            return;
        }

        sendMessage(
            inputMessage, 
            $user.full_name, 
            $user.avatar_url || ""
        );
        
        inputMessage = ""; // Clear input
    }

    function handleKeydown(e: KeyboardEvent) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    }
</script>

<div class="flex flex-col h-[600px] bg-white border-4 border-black shadow-hard">
    
    <div class="bg-black text-white p-3 flex justify-between items-center select-none">
        <div class="font-black uppercase tracking-widest flex items-center gap-2">
            <span class="w-3 h-3 rounded-full {$isConnected ? 'bg-green-500' : 'bg-red-500'} animate-pulse"></span>
            Live Frequency
        </div>
        <div class="text-xs font-mono text-gray-400">
            WS://{communityId.substring(0,8)}...
        </div>
    </div>

    <div 
        bind:this={chatContainer}
        class="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50"
    >
        {#if $messages.length === 0}
            <div class="h-full flex flex-col items-center justify-center text-gray-400 opacity-50">
                <div class="text-4xl mb-2">📡</div>
                <div class="text-sm font-bold uppercase">Signal Established</div>
                <div class="text-xs">Waiting for transmission...</div>
            </div>
        {/if}

        {#each $messages as msg}
            <div class="flex gap-3 {msg.user_id === $user?.id ? 'flex-row-reverse' : ''}">
                <div class="flex-shrink-0">
                    {#if msg.avatar_url}
                        <img src={msg.avatar_url} alt="av" class="w-10 h-10 border-2 border-black rounded bg-gray-200 object-cover" />
                    {:else}
                        <div class="w-10 h-10 border-2 border-black rounded bg-sp-yellow flex items-center justify-center font-bold text-xs">
                            {msg.username.charAt(0)}
                        </div>
                    {/if}
                </div>

                <div class="max-w-[80%]">
                    <div class="text-[10px] font-bold uppercase mb-1 text-gray-500 {msg.user_id === $user?.id ? 'text-right' : ''}">
                        {msg.username}
                    </div>
                    <div class="
                        p-3 text-sm font-medium border-2 border-black shadow-sm
                        {msg.user_id === $user?.id ? 'bg-sp-blue text-white' : 'bg-white text-black'}
                    ">
                        {msg.content}
                    </div>
                </div>
            </div>
        {/each}
    </div>

    <div class="p-3 bg-white border-t-4 border-black">
        <div class="flex gap-2">
            <input 
                type="text" 
                bind:value={inputMessage}
                on:keydown={handleKeydown}
                placeholder="Broadcast a message..."
                class="flex-1 p-2 border-2 border-black font-mono text-sm focus:outline-none focus:bg-yellow-50"
                disabled={!$isConnected}
            />
            <button 
                on:click={handleSend}
                disabled={!$isConnected}
                class="bg-black text-white px-6 font-bold uppercase hover:bg-gray-800 disabled:opacity-50"
            >
                TX
            </button>
        </div>
    </div>
</div>