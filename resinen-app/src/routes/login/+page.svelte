<script lang="ts">
    import { api, loginUser } from '$lib/api';
    import { goto } from '$app/navigation';

    let email = '';
    let password = '';
    let error = '';
    let isLoading = false;

    async function handleLogin() {
        isLoading = true;
        error = '';
        
        try {
            // 1. Get Token (FastAPI expects form-data usually, but let's try JSON first or standard OAuth flow)
            // Note: FastAPI's OAuth2PasswordRequestForm expects form-data. 
            // We'll construct a URLSearchParams body for compatibility.
            
            const formData = new URLSearchParams();
            formData.append('username', email); // FastAPI uses 'username' for email
            formData.append('password', password);

            const res = await fetch('https://api.resinen.com/api/v1/login/access-token', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData
            });

            if (!res.ok) throw new Error('Invalid Identity Credentials');
            const data = await res.json();

            // 2. Get User Details (Now that we have the token)
            // We manually fetch "me" to get the user's name/avatar
            const userRes = await fetch('https://api.resinen.com//api/v1/users/me', {
                headers: { 'Authorization': `Bearer ${data.access_token}` }
            });
            const userData = await userRes.json();

            // 3. Save & Redirect
            loginUser(data.access_token, userData);
            goto('/dashboard');

        } catch (e: any) {
            error = e.message;
        } finally {
            isLoading = false;
        }
    }
</script>

<div class="min-h-screen bg-sp-blue flex items-center justify-center p-4">
    
    <div class="bg-white border-4 border-black p-8 max-w-md w-full shadow-hard-lg transform rotate-1 relative">
        
        <div class="absolute -top-4 left-1/2 -translate-x-1/2 w-32 h-8 bg-sp-yellow/50 border-l-2 border-r-2 border-white/20 transform -rotate-2"></div>

        <h1 class="text-3xl font-black mb-2 uppercase text-center mt-4">Security Check</h1>
        <p class="text-center font-bold text-gray-500 mb-8 text-sm">Verify your identity to enter.</p>
        
        {#if error}
            <div class="bg-sp-red text-white p-3 border-2 border-black font-bold text-sm mb-4 shadow-hard-sm">
                ⚠️ {error}
            </div>
        {/if}

        <form on:submit|preventDefault={handleLogin} class="space-y-4">
            <div>
                <label class="block font-bold text-sm mb-1 uppercase">Email Identity</label>
                <input 
                    bind:value={email}
                    type="email" 
                    class="w-full border-4 border-black p-3 bg-sp-paper focus:bg-white outline-none font-bold transition-all focus:shadow-hard-sm" 
                    placeholder="citizen@resinen.com"
                />
            </div>
            <div>
                <label class="block font-bold text-sm mb-1 uppercase">Passkey</label>
                <input 
                    bind:value={password}
                    type="password" 
                    class="w-full border-4 border-black p-3 bg-sp-paper focus:bg-white outline-none font-bold transition-all focus:shadow-hard-sm" 
                    placeholder="••••••••"
                />
            </div>
            
            <button 
                disabled={isLoading}
                class="w-full bg-sp-green text-white font-black py-4 border-4 border-black shadow-hard hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-none transition-all uppercase disabled:opacity-50 disabled:cursor-not-allowed"
            >
                {isLoading ? 'Verifying...' : 'Authenticate'}
            </button>
        </form>
        
        <div class="mt-8 pt-6 border-t-2 border-dashed border-black text-center">
            <p class="text-xs font-bold text-gray-400 uppercase tracking-widest">Resinen OS v1.0</p>
        </div>
    </div>

</div>