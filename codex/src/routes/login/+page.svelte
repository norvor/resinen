<script lang="ts">
    import { api } from '$lib/api';
    import { goto } from '$app/navigation';

    let email = '';
    let password = '';
    let isLoading = false;
    let error = '';

    // Toggle between Login and Signup (Hidden feature for you)
    let isSignup = false; 
    let fullName = 'Super Admin'; 

    async function handleAuth() {
        isLoading = true;
        error = '';

        try {
            if (isSignup) {
                // First time setup only
                await api.signup(email, password, fullName);
                // Then login automatically
                await api.login(email, password);
            } else {
                await api.login(email, password);
            }
            
            // Redirect to Dashboard
            goto('/');
            
        } catch (e) {
            error = isSignup ? "Signup Failed. Email taken?" : "Access Denied.";
        } finally {
            isLoading = false;
        }
    }
</script>

<div class="min-h-screen flex items-center justify-center bg-slate-950 p-4">
    <div class="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl">
        <div class="text-center mb-8">
            <h1 class="text-3xl font-black text-orange-500 tracking-tighter">CODEX // ACCESS</h1>
            <p class="text-slate-500 text-sm font-mono mt-2">RESTRICTED ENVIRONMENT</p>
        </div>

        <div class="space-y-4">
            {#if isSignup}
            <div>
                <input 
                    bind:value={fullName}
                    type="text" 
                    placeholder="Operator Name" 
                    class="w-full bg-slate-950 border border-slate-800 text-white p-3 rounded-lg focus:ring-1 focus:ring-orange-500 outline-none"
                />
            </div>
            {/if}

            <div>
                <input 
                    bind:value={email}
                    type="email" 
                    placeholder="Identity (Email)" 
                    class="w-full bg-slate-950 border border-slate-800 text-white p-3 rounded-lg focus:ring-1 focus:ring-orange-500 outline-none"
                />
            </div>
            <div>
                <input 
                    bind:value={password}
                    type="password" 
                    placeholder="Passcode" 
                    class="w-full bg-slate-950 border border-slate-800 text-white p-3 rounded-lg focus:ring-1 focus:ring-orange-500 outline-none"
                />
            </div>

            <button 
                on:click={handleAuth}
                disabled={isLoading}
                class="w-full py-3 bg-orange-600 hover:bg-orange-500 text-white font-bold rounded-lg transition-all flex justify-center"
            >
                {#if isLoading}
                    <span class="animate-pulse">AUTHENTICATING...</span>
                {:else}
                    {isSignup ? 'INITIALIZE ADMIN' : 'ESTABLISH LINK'}
                {/if}
            </button>

            {#if error}
                <div class="p-3 bg-red-900/20 text-red-400 text-center text-xs font-mono rounded border border-red-900/50">
                    ERROR: {error}
                </div>
            {/if}
            
            <div class="text-center pt-4">
                <button on:click={() => isSignup = !isSignup} class="text-xs text-slate-600 hover:text-orange-500 transition-colors">
                    {isSignup ? 'Switch to Login' : '[ Create Genesis Account ]'}
                </button>
            </div>
        </div>
    </div>
</div>