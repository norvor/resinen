<script lang="ts">
    import { api } from '$lib/api';
    import { goto } from '$app/navigation';

    let email = '';
    let password = '';
    let full_name = '';
    let error = '';
    let loading = false;

    async function handleSignup() {
        loading = true;
        error = '';
        try {
            await api.signup({ email, password, full_name });
            // Signup automatically calls login in our API wrapper
            await api.getMe(); 
            goto('/'); 
        } catch (e: any) {
            console.error(e);
            error = e.message || "REGISTRATION FAILED: Email may be in use.";
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
            <h1 class="text-4xl font-black uppercase tracking-tighter text-skin-text">Join The <span class="text-skin-accent underline decoration-4 decoration-skin-accent/30">Corps</span></h1>
            <div class="text-xs font-mono font-bold text-skin-muted tracking-[0.3em] mt-2">NEW OPERATOR ONBOARDING</div>
        </div>

        <div class="bg-skin-surface border-2 border-skin-border shadow-hard">
            
            <div class="flex border-b border-skin-border">
                <div class="flex-1 bg-skin-fill p-3 text-center border-r border-skin-border">
                    <span class="text-xs font-black uppercase text-skin-accent">01. Identity</span>
                </div>
                <div class="flex-1 bg-skin-surface p-3 text-center opacity-50">
                    <span class="text-xs font-black uppercase text-skin-muted">02. Verify</span>
                </div>
            </div>

            <div class="p-8">
                {#if error}
                    <div class="mb-6 bg-red-500/10 border-l-4 border-red-500 p-4">
                        <div class="text-xs font-black uppercase text-red-500 flex items-center gap-2">
                            <span>⚠</span> {error}
                        </div>
                    </div>
                {/if}

                <form on:submit|preventDefault={handleSignup} class="space-y-5">
                    
                    <div class="group">
                        <label class="block text-xs font-black uppercase text-skin-muted mb-1">Designation (Full Name)</label>
                        <input 
                            bind:value={full_name} 
                            type="text" 
                            required 
                            class="w-full bg-skin-fill border border-skin-border p-3 font-mono text-sm focus:outline-none focus:border-skin-accent transition-all" 
                            placeholder="John Doe" 
                        />
                    </div>
                    
                    <div class="group">
                        <label class="block text-xs font-black uppercase text-skin-muted mb-1">Comms ID (Email)</label>
                        <input 
                            bind:value={email} 
                            type="email" 
                            required 
                            class="w-full bg-skin-fill border border-skin-border p-3 font-mono text-sm focus:outline-none focus:border-skin-accent transition-all" 
                            placeholder="agent@resinen.com" 
                        />
                    </div>

                    <div class="group">
                        <label class="block text-xs font-black uppercase text-skin-muted mb-1">Passcode</label>
                        <input 
                            bind:value={password} 
                            type="password" 
                            required 
                            class="w-full bg-skin-fill border border-skin-border p-3 font-mono text-sm focus:outline-none focus:border-skin-accent transition-all" 
                            placeholder="••••••••" 
                        />
                        <div class="text-[10px] text-skin-muted mt-1 text-right">Must be 8+ chars</div>
                    </div>

                    <button 
                        disabled={loading} 
                        class="w-full bg-skin-accent text-white py-4 font-black uppercase tracking-widest hover:bg-opacity-90 transition-all disabled:opacity-50 disabled:cursor-not-allowed mt-8 shadow-lg shadow-skin-accent/20"
                    >
                        {loading ? 'Processing...' : 'Submit Credentials'}
                    </button>
                </form>
            </div>

            <div class="bg-skin-fill border-t border-skin-border p-4 text-center">
                <a href="/login" class="text-xs font-bold font-mono uppercase text-skin-muted hover:text-skin-text transition-colors">
                    [ Already Registered? Login ]
                </a>
            </div>
        </div>
    </div>
</div>