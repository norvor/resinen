<script lang="ts">
    import { api } from '$lib/api';
    import { goto } from '$app/navigation';
    import { fly } from 'svelte/transition';

    let email = '';
    let password = '';
    let error = '';
    let loading = false;
    let success = false;

    async function handleLogin() {
        loading = true;
        error = '';
        try {
            const formData = new FormData();
            formData.append('username', email);
            formData.append('password', password);
            
            // The new api.login automatically fetches the user profile (getMe)
            // and sets the token in localStorage.
            await api.login(formData);
            
            success = true;
            // Redirect to the Dashboard (The Engine Room)
            setTimeout(() => goto('/dashboard'), 800);
        } catch (e: any) {
            console.error(e);
            // Handle specific API errors if available
            error = e.message || "Invalid Credentials";
            loading = false;
        }
    }
</script>

<div class="min-h-screen bg-orange-50 relative flex items-center justify-center p-4 overflow-hidden" 
     style="--bg-world: #fff7ed; --color-accent: #ea580c; --color-accent-fg: #fff;">
    
    <div class="absolute inset-0 pattern-grid pointer-events-none"></div>
    
    <div class="absolute top-10 left-10 w-24 h-24 bg-yellow-400 rounded-full border-2 border-black shadow-[4px_4px_0px_black] animate-bounce hidden md:block"></div>
    <div class="absolute bottom-20 right-20 w-32 h-32 bg-blue-400 rotate-12 border-2 border-black shadow-[4px_4px_0px_black] hidden md:block"></div>

    {#if !success}
        <div in:fly={{ y: 50, duration: 600 }} class="relative w-full max-w-md">
            
            <div class="absolute -top-6 left-1/2 -translate-x-1/2 w-32 h-10 bg-white/50 backdrop-blur border border-black/10 rotate-[-2deg] z-20 shadow-sm"></div>

            <div class="paper-card p-8 md:p-12 relative bg-white transform rotate-1 transition-transform hover:rotate-0 duration-300">
                
                <div class="text-center mb-10">
                    <div class="inline-block px-4 py-1 bg-black text-white text-xs font-black uppercase tracking-widest mb-4 rotate-[-3deg]">
                        Resinen University
                    </div>
                    <h1 class="text-4xl font-black text-black tracking-tight uppercase">
                        Student<br>Portal
                    </h1>
                </div>

                {#if error}
                    <div class="mb-6 p-4 bg-red-100 border-2 border-red-500 text-red-600 font-bold uppercase text-center rotate-1 shadow-[4px_4px_0px_#ef4444]">
                        ⚠ {error}
                    </div>
                {/if}

                <form on:submit|preventDefault={handleLogin} class="space-y-6">
                    
                    <div class="space-y-2">
                        <label class="block text-xs font-black uppercase text-gray-500 ml-1">Student ID (Email)</label>
                        <input 
                            bind:value={email} 
                            type="email" 
                            required 
                            class="paper-input"
                            placeholder="student@resinen.edu" 
                        />
                    </div>

                    <div class="space-y-2">
                        <label class="block text-xs font-black uppercase text-gray-500 ml-1">Pin Code</label>
                        <input 
                            bind:value={password} 
                            type="password" 
                            required 
                            class="paper-input"
                            placeholder="••••••••" 
                        />
                    </div>

                    <button 
                        disabled={loading} 
                        class="paper-btn w-full mt-4 text-sm"
                    >
                        {#if loading}
                            Processing...
                        {:else}
                            Stamp & Enter
                        {/if}
                    </button>
                </form>

                <div class="mt-8 text-center border-t-2 border-dashed border-gray-200 pt-6">
                    <a href="/signup" class="text-xs font-black uppercase text-gray-400 hover:text-orange-600 hover:underline transition-colors">
                        New Applicant? Fill out Form 1A
                    </a>
                </div>
            </div>
        </div>
    {/if}

    {#if success}
        <div class="fixed inset-0 z-50 flex items-center justify-center bg-orange-600 transition-all duration-500">
            <div class="text-center text-white transform scale-150 animate-pulse">
                <div class="text-6xl mb-4">✅</div>
                <h1 class="text-4xl font-black uppercase tracking-tighter">Authorized</h1>
            </div>
        </div>
    {/if}
</div>