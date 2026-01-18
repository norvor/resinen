<script lang="ts">
    import { api } from '$lib/api'; // We only need the api object
    import { goto } from '$app/navigation';

    let email = '';
    let password = '';
    let error = '';
    let isLoading = false;

    async function handleLogin() {
        isLoading = true;
        error = '';

        try {
            // 1. The api.login function already handles FormData and hits /auth/login
            await api.login(email, password);

            // 2. The api.getMe function already fetches the user and updates the store
            await api.getMe();

            // 3. Redirect
            goto('/dashboard');

        } catch (e: any) {
            console.error(e);
            // Handle specific error messages from your FastAPI backend
            error = e.detail || e.message || 'Login failed';
        } finally {
            isLoading = false;
        }
    }
</script>

<div class="min-h-screen bg-sp-blue flex items-center justify-center p-4">
    <div class="bg-white border-4 border-black p-8 max-w-md w-full shadow-hard-lg transform rotate-1 relative">
        <h1 class="text-3xl font-black mb-2 uppercase text-center mt-4">Security Check</h1>
        <p class="text-center font-bold text-gray-500 mb-8 text-sm">Production Server Connection</p>
        
        {#if error}
            <div class="bg-sp-red text-white p-3 border-2 border-black font-bold text-sm mb-4">
                ⚠️ {error}
            </div>
        {/if}

        <form on:submit|preventDefault={handleLogin} class="space-y-4">
            <div>
                <label class="block font-bold text-sm mb-1 uppercase">Email Identity</label>
                <input bind:value={email} type="email" class="w-full border-4 border-black p-3 font-bold outline-none" placeholder="citizen@resinen.com" />
            </div>
            <div>
                <label class="block font-bold text-sm mb-1 uppercase">Passkey</label>
                <input bind:value={password} type="password" class="w-full border-4 border-black p-3 font-bold outline-none" placeholder="••••••••" />
            </div>
            
            <button disabled={isLoading} class="w-full bg-sp-green text-white font-black py-4 border-4 border-black shadow-hard hover:shadow-none transition-all uppercase disabled:opacity-50">
                {isLoading ? 'Verifying...' : 'Authenticate'}
            </button>
        </form>
    </div>
</div>