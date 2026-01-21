<script lang="ts">
    import { api } from '$lib/api';
    import { goto } from '$app/navigation';
    import { fly } from 'svelte/transition';

    let email = '';
    let password = '';
    let full_name = '';
    let error = '';
    let loading = false;
    let success = false;

    async function handleSignup() {
        loading = true;
        error = '';
        try {
            await api.signup({ email, password, full_name });
            // Auto-login or fetch user would happen here in a real flow, 
            // but for the UI we just show the success state
            await api.getMe();
            
            success = true;
            setTimeout(() => goto('/'), 1500);
        } catch (e: any) {
            console.error(e);
            error = "Application Rejected: Email taken or invalid.";
            loading = false;
        }
    }
</script>

<div class="min-h-screen bg-orange-50 relative flex items-center justify-center p-4 overflow-hidden" 
     style="--bg-world: #fff7ed; --color-accent: #16a34a; --color-accent-fg: #fff;">
    
    <div class="absolute inset-0 pattern-grid pointer-events-none opacity-50"></div>
    
    <div class="absolute top-20 right-20 w-16 h-16 bg-red-400 rounded-full border-2 border-black shadow-[4px_4px_0px_black] animate-bounce delay-700 hidden md:block"></div>
    <div class="absolute bottom-10 left-10 w-24 h-24 bg-blue-400 rotate-[-12deg] border-2 border-black shadow-[4px_4px_0px_black] hidden md:block"></div>

    {#if success}
        <div class="fixed inset-0 z-50 flex flex-col items-center justify-center bg-green-500 transition-all duration-500">
            <div class="bg-white p-8 border-4 border-black shadow-[8px_8px_0px_rgba(0,0,0,0.2)] transform rotate-2 animate-[bounce_0.5s_ease-out]">
                <div class="text-6xl text-center mb-4">🎉</div>
                <h1 class="text-4xl font-black uppercase tracking-tighter text-black mb-2">You're In!</h1>
                <p class="text-center font-bold text-gray-500 font-mono">CLASS OF 2026</p>
            </div>
            <div class="mt-8 font-black text-white uppercase tracking-widest animate-pulse">Redirecting to Campus...</div>
        </div>
    {/if}

    {#if !success}
        <div in:fly={{ y: 50, duration: 600 }} class="relative w-full max-w-lg">
            
            <div class="absolute -top-12 left-1/2 -translate-x-1/2 w-40 h-16 bg-gray-800 rounded-t-lg z-0 border-2 border-b-0 border-black flex items-center justify-center">
                <div class="w-24 h-4 bg-gray-300 rounded-full border-2 border-black"></div>
            </div>

            <div class="paper-card p-8 md:p-12 relative bg-white z-10 mt-4">
                
                <div class="absolute top-4 right-4 w-20 h-20 border-4 border-red-500 rounded-full flex items-center justify-center opacity-20 rotate-[-20deg] pointer-events-none">
                    <span class="text-[10px] font-black text-red-500 uppercase">Form 1A</span>
                </div>

                <div class="text-center mb-8 border-b-2 border-black border-dashed pb-6">
                    <h1 class="text-3xl font-black text-black uppercase tracking-tight">New Student<br>Enrollment</h1>
                    <p class="text-xs font-bold text-gray-400 mt-2 uppercase tracking-widest">Please print clearly in block letters</p>
                </div>

                {#if error}
                    <div class="mb-6 p-4 bg-red-100 border-2 border-red-500 text-red-600 font-bold text-xs uppercase shadow-[4px_4px_0px_#ef4444]">
                        🚨 {error}
                    </div>
                {/if}

                <form on:submit|preventDefault={handleSignup} class="space-y-5">
                    
                    <div class="space-y-1">
                        <label class="block text-xs font-black uppercase text-gray-500">Legal Name</label>
                        <input 
                            bind:value={full_name} 
                            type="text" 
                            required 
                            class="paper-input bg-blue-50/30 focus:bg-white"
                            placeholder="e.g. ERIC CARTMAN" 
                        />
                    </div>

                    <div class="space-y-1">
                        <label class="block text-xs font-black uppercase text-gray-500">Student Email</label>
                        <input 
                            bind:value={email} 
                            type="email" 
                            required 
                            class="paper-input bg-blue-50/30 focus:bg-white"
                            placeholder="student@resinen.edu" 
                        />
                    </div>

                    <div class="space-y-1">
                        <label class="block text-xs font-black uppercase text-gray-500">Create Pin</label>
                        <input 
                            bind:value={password} 
                            type="password" 
                            required 
                            class="paper-input bg-blue-50/30 focus:bg-white"
                            placeholder="••••••••" 
                        />
                        <div class="text-[10px] font-bold text-gray-400 text-right">Min. 8 Characters</div>
                    </div>

                    <div class="pt-4">
                        <button 
                            disabled={loading} 
                            class="paper-btn w-full bg-green-500 hover:bg-green-400 text-white border-black"
                        >
                            {#if loading}
                                Reviewing...
                            {:else}
                                Submit Application
                            {/if}
                        </button>
                    </div>

                    <div class="text-center text-[10px] text-gray-400 font-mono mt-4">
                        By signing, you agree to the Honor Code.
                    </div>
                </form>
            </div>

            <div class="mt-8 text-center">
                <a href="/login" class="inline-block px-4 py-2 bg-yellow-400 border-2 border-black font-black text-xs uppercase shadow-[4px_4px_0px_black] hover:-translate-y-1 hover:shadow-[6px_6px_0px_black] transition-all">
                    ← Back to Login
                </a>
            </div>

        </div>
    {/if}
</div>