<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { api } from '$lib/api';
    import { fade, fly } from 'svelte/transition';
    import type { Community, User } from '$lib/types';

    export let community: Community;
    export let currentUser: User | null;

    // --- TYPES ---
    interface BunkerMessage {
        id: string;
        content: string;
        created_at: string;
        ttl_seconds: number; // Remaining time
        is_anonymous: boolean;
        color?: string; // UI only property
    }

    // --- STATE ---
    let messages: BunkerMessage[] = [];
    let loading = true;
    let newMessage = "";
    let isPosting = false;
    let interval: any;
    let selectedTTL = 3600; // Default 1 hour
    let error: string | null = null;

    onMount(async () => {
        if (!community?.id) return;
        try {
            // Fetch real messages
            const res = await api.getBunkerMessages(community.id);
            // Handle array vs pagination wrapper
            messages = Array.isArray(res) ? res : (res as any).items || [];
        } catch (e) {
            console.error("Bunker Encrypted/Offline:", e);
            error = "Connection Refused by Host.";
        } finally {
            loading = false;
        }

        // Countdown Timer Logic
        // Decrement TTL locally every second to simulate "Self-Destruct"
        interval = setInterval(() => {
            messages = messages.map(m => ({
                ...m,
                ttl_seconds: m.ttl_seconds > 0 ? m.ttl_seconds - 1 : 0
            })).filter(m => m.ttl_seconds > 0); // Remove dead messages from UI
        }, 1000);
    });

    onDestroy(() => {
        if (interval) clearInterval(interval);
    });

    async function handlePost() {
        if (!newMessage.trim()) return;
        isPosting = true;
        
        // Prepare payload
        const content = newMessage;
        const ttl = selectedTTL;
        
        try {
            // 1. Send to Backend
            await api.postBunkerMessage(community.id, content, true, ttl);

            // 2. Optimistic Add
            // We create a temporary ID. In a real app with WebSockets, we'd wait for the echo.
            const tempMsg: BunkerMessage = {
                id: 'temp-' + Date.now(),
                content: content,
                created_at: new Date().toISOString(),
                ttl_seconds: ttl,
                is_anonymous: true,
                color: 'text-white'
            };

            messages = [tempMsg, ...messages];
            newMessage = "";

        } catch (e) {
            console.error("Transmission Failed", e);
            alert("Upload Failed: Encryption Error");
        } finally {
            isPosting = false;
        }
    }

    function formatTime(seconds: number) {
        if (seconds < 0) return "00:00:00";
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = Math.floor(seconds % 60);
        return `${h.toString().padStart(2,'0')}:${m.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}`;
    }

    // "Matrix" Text Scramble Effect
    function scramble(node: HTMLElement, { duration = 1000 }) {
        const text = node.textContent || '';
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()';
        return {
            duration,
            tick: (t: number) => {
                if (t === 1) {
                    node.textContent = text;
                    return;
                }
                const progress = Math.floor(text.length * t);
                let scrambled = text.slice(0, progress);
                for (let i = progress; i < text.length; i++) {
                    scrambled += chars[Math.floor(Math.random() * chars.length)];
                }
                node.textContent = scrambled;
            }
        };
    }
</script>

<div class="bg-black min-h-screen font-mono text-green-500 p-4 md:p-8 relative overflow-hidden">
    
    <div class="fixed inset-0 pointer-events-none z-50 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[length:100%_2px,3px_100%] opacity-20"></div>
    <div class="fixed inset-0 pointer-events-none z-50 animate-flicker bg-white/5 opacity-[0.02]"></div>

    <div class="max-w-4xl mx-auto border-b border-green-900/50 pb-6 mb-8 flex justify-between items-end">
        <div>
            <div class="text-[10px] font-bold text-green-800 uppercase tracking-widest mb-1">
                SECURE_CONNECTION_ESTABLISHED::V.2.0.4
            </div>
            <h1 class="text-4xl md:text-5xl font-black uppercase tracking-tighter text-white glitch-text" data-text="THE_BUNKER">
                THE_BUNKER
            </h1>
        </div>
        <div class="text-right hidden md:block">
            <div class="text-xs text-green-600">ENCRYPTION: AES-256</div>
            <div class="text-xs text-green-600">NODE: {community.id.split('-')[0]}</div>
        </div>
    </div>

    <div class="max-w-4xl mx-auto space-y-12 relative z-10">

        <div class="border border-green-800 bg-[#050a05] p-6 rounded-sm shadow-[0_0_20px_rgba(0,255,0,0.1)] relative group">
            <div class="absolute top-0 left-0 bg-green-900 text-[#050a05] text-[9px] font-bold px-2 py-0.5">
                INPUT_STREAM
            </div>
            
            <div class="flex gap-3 mt-4">
                <span class="text-green-500 animate-pulse text-xl">></span>
                <textarea 
                    bind:value={newMessage}
                    placeholder="Drop a secret. It will self-destruct."
                    class="w-full bg-transparent border-none text-green-400 focus:ring-0 placeholder:text-green-900 resize-none h-24 text-lg font-bold uppercase caret-green-500"
                ></textarea>
            </div>

            <div class="flex justify-between items-center mt-4 pt-4 border-t border-green-900/30">
                <div class="flex gap-2">
                    {#each [60, 3600, 86400] as time}
                        <button 
                            on:click={() => selectedTTL = time}
                            class="px-3 py-1 text-[10px] font-bold border border-green-900 uppercase hover:bg-green-900 hover:text-white transition-colors
                            {selectedTTL === time ? 'bg-green-900 text-white' : 'text-green-700'}"
                        >
                            {time === 60 ? '1 MIN' : time === 3600 ? '1 HR' : '24 HR'}
                        </button>
                    {/each}
                </div>

                <button 
                    on:click={handlePost}
                    disabled={!newMessage || isPosting}
                    class="bg-green-700 text-black font-black uppercase px-6 py-2 hover:bg-green-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {isPosting ? 'ENCRYPTING...' : 'TRANSMIT'}
                </button>
            </div>
        </div>

        {#if loading}
            <div class="text-center py-20 text-green-900 font-black text-xl animate-pulse">
                DECRYPTING_PACKETS...
            </div>
        {:else if error}
            <div class="text-center py-20 border border-dashed border-red-900/30 text-red-900">
                <span class="text-4xl block mb-2">⚠</span>
                {error}
            </div>
        {:else if messages.length === 0}
             <div class="text-center py-20 border border-dashed border-green-900/30 text-green-900">
                <span class="text-4xl block mb-2">∅</span>
                NO_SIGNALS_DETECTED
            </div>
        {:else}
            <div class="grid grid-cols-1 gap-4">
                {#each messages as msg (msg.id)}
                    <div 
                        class="bg-[#0a0a0a] border border-green-900/50 p-6 relative overflow-hidden hover:border-green-500/50 transition-colors group"
                        in:fly={{ y: 20 }}
                        out:fade
                    >
                        <div class="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/diagmonds-light.png')] opacity-5 pointer-events-none"></div>

                        <div class="flex justify-between items-start mb-4 border-b border-green-900/30 pb-2">
                            <div class="flex gap-2 items-center">
                                <span class="w-2 h-2 bg-green-500 rounded-full animate-ping"></span>
                                <span class="text-[10px] font-bold text-green-700 uppercase">ANONYMOUS_USER_{msg.id.substring(0,4)}</span>
                            </div>
                            <div class="font-mono font-bold text-red-500 text-sm">
                                T-MINUS {formatTime(msg.ttl_seconds)}
                            </div>
                        </div>

                        <p 
                            class="text-lg md:text-xl font-bold text-green-300 leading-relaxed uppercase break-words"
                            use:scramble
                        >
                            {msg.content}
                        </p>

                        <div class="mt-4 flex justify-end opacity-0 group-hover:opacity-100 transition-opacity">
                            <button class="text-[10px] text-green-800 hover:text-green-500 font-bold uppercase cursor-not-allowed">
                                [ REPLIES DISABLED ]
                            </button>
                        </div>

                        <div class="absolute top-0 left-0 w-full h-[2px] bg-green-500/20 animate-scan pointer-events-none"></div>
                    </div>
                {/each}
            </div>
        {/if}

    </div>
</div>

<style>
    .glitch-text {
        position: relative;
    }
    .glitch-text::before, .glitch-text::after {
        content: attr(data-text);
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: black;
    }
    .glitch-text::before {
        left: 2px;
        text-shadow: -1px 0 red;
        clip: rect(24px, 550px, 90px, 0);
        animation: glitch-anim-1 2.5s infinite linear alternate-reverse;
    }
    .glitch-text::after {
        left: -2px;
        text-shadow: -1px 0 blue;
        clip: rect(85px, 550px, 140px, 0);
        animation: glitch-anim-2 3s infinite linear alternate-reverse;
    }

    @keyframes glitch-anim-1 {
        0% { clip: rect(20px, 9999px, 15px, 0); }
        100% { clip: rect(65px, 9999px, 80px, 0); }
    }
    @keyframes glitch-anim-2 {
        0% { clip: rect(80px, 9999px, 10px, 0); }
        100% { clip: rect(10px, 9999px, 100px, 0); }
    }

    @keyframes scan {
        0% { top: 0%; opacity: 0; }
        50% { opacity: 1; }
        100% { top: 100%; opacity: 0; }
    }
    .animate-scan {
        animation: scan 4s linear infinite;
    }

    @keyframes flicker {
        0% { opacity: 0.02; }
        5% { opacity: 0.05; }
        10% { opacity: 0.02; }
        15% { opacity: 0.06; }
        20% { opacity: 0.02; }
        100% { opacity: 0.02; }
    }
    .animate-flicker {
        animation: flicker 2s infinite;
    }
</style>