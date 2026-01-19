<script lang="ts">
    import { api } from '$lib/api';
    import { goto } from '$app/navigation';

    let email = '';
    let password = '';
    let error = '';
    let loading = false;

    async function handleLogin() {
        loading = true;
        error = '';
        try {
            const formData = new FormData();
            formData.append('username', email);
            formData.append('password', password);
            
            await api.login(formData);
            await api.getMe(); // Load user profile into store
            goto('/');
        } catch (e: any) {
            console.error(e);
            error = "ACCESS DENIED: Invalid credentials.";
        } finally {
            loading = false;
        }
    }
</script>

<div class="min-h-screen bg-skin-fill flex flex-col items-center justify-center p-4 relative overflow-hidden">
    <div class="absolute inset-0 opacity-[0.03]" 
         style="background-image: linear-gradient(#000 1px, transparent 1px), linear-gradient(90deg, #000 1px, transparent 1px); background-size: 40px 40px;">
    </div>

    <div class="w-full max-w-md relative z-10">
        <div class="mb-8 text-center">
            <div class="text-6xl mb-4">▣</div>
            <h1 class="text-4xl font-black uppercase tracking-tighter text-skin-text">Resinen<span class="text-skin-accent">OS</span></h1>
            <div class="text-xs font-mono font-bold text-skin-muted tracking-[0.3em] mt-2">SECURE GATEWAY v3.0</div>
        </div>

        <div class="bg-skin-surface border-2 border-skin-border shadow-hard">
            <div class="border-b border-skin-border p-2 flex justify-between items-center bg-skin-fill">
                <div class="flex gap-2">
                    <div class="w-2 h-2 rounded-full bg-red-500 animate-pulse"></div>
                    <div class="w-2 h-2 rounded-full bg-yellow-500"></div>
                    <div class="w-2 h-2 rounded-full bg-green-500"></div>
                </div>
                <div class="text-[10px] font-mono font-bold text-skin-muted uppercase">Auth_Required</div>
            </div>

            <div class="p-8">
                {#if error}
                    <div class="mb-6 bg-red-500/10 border-l-4 border-red-500 p-4">
                        <div class="text-xs font-black uppercase text-red-500 flex items-center gap-2">
                            <span>🚫</span> {error}
                        </div>
                    </div>
                {/if}

                <form on:submit|preventDefault={handleLogin} class="space-y-6">
                    <div class="group">
                        <label class="block text-xs font-black uppercase text-skin-muted mb-2 group-focus-within:text-skin-accent transition-colors">
                            Operator ID (Email)
                        </label>
                        <input 
                            bind:value={email} 
                            type="email" 
                            required 
                            class="w-full bg-skin-fill border border-skin-border p-4 font-mono text-sm text-skin-text focus:outline-none focus:border-skin-accent focus:ring-1 focus:ring-skin-accent transition-all placeholder-skin-muted/30" 
                            placeholder="user@resinen.com" 
                        />
                    </div>

                    <div class="group">
                        <label class="block text-xs font-black uppercase text-skin-muted mb-2 group-focus-within:text-skin-accent transition-colors">
                            Access Key (Password)
                        </label>
                        <input 
                            bind:value={password} 
                            type="password" 
                            required 
                            class="w-full bg-skin-fill border border-skin-border p-4 font-mono text-sm text-skin-text focus:outline-none focus:border-skin-accent focus:ring-1 focus:ring-skin-accent transition-all placeholder-skin-muted/30" 
                            placeholder="••••••••" 
                        />
                    </div>

                    <button 
                        disabled={loading} 
                        class="w-full bg-skin-text text-skin-fill py-4 font-black uppercase tracking-widest hover:bg-skin-accent hover:text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 mt-8 group"
                    >
                        {#if loading}
                            <span class="animate-spin">⟳</span> Authenticating...
                        {:else}
                            <span>Initialize Session</span> <span class="group-hover:translate-x-1 transition-transform">→</span>
                        {/if}
                    </button>
                </form>
            </div>
            
            <div class="bg-skin-fill border-t border-skin-border p-4 text-center">
                <a href="/signup" class="text-xs font-bold font-mono uppercase text-skin-muted hover:text-skin-accent transition-colors">
                    [ No ID Found? Request Access ]
                </a>
            </div>
        </div>
        
        <div class="mt-8 text-center text-[10px] text-skin-muted font-mono opacity-50">
            ENCRYPTED CONNECTION // NODE_ID: {Math.floor(Math.random() * 9999)}
        </div>
    </div>
</div>