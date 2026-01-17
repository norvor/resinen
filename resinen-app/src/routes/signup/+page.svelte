<script lang="ts">
    import { goto } from '$app/navigation';
    import { loginUser } from '$lib/api';

    let fullName = '';
    let email = '';
    let password = '';
    let confirmPassword = '';
    let error = '';
    let isLoading = false;

    async function handleSignup() {
        if (password !== confirmPassword) {
            error = "Passkeys do not match.";
            return;
        }

        isLoading = true;
        error = '';

        try {
            // 1. Create the User (Hit your FastAPI Backend)
            // Adjust endpoint '/users/open' depending on your exact backend route
            const registerRes = await fetch('https://api.resinen.com/api/v1/users/open', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: email,
                    password: password,
                    full_name: fullName
                })
            });

            if (!registerRes.ok) {
                const errData = await registerRes.json();
                throw new Error(errData.detail || 'Registration failed.');
            }

            // 2. Auto-Login (Get Token immediately after signup)
            const formData = new URLSearchParams();
            formData.append('username', email);
            formData.append('password', password);

            const loginRes = await fetch('https://api.resinen.com/api/v1/login/access-token', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData
            });

            if (!loginRes.ok) throw new Error('Auto-login failed. Please sign in manually.');
            const tokenData = await loginRes.json();

            // 3. Get User Profile & Store Session
            const userRes = await fetch('https://api.resinen.com/api/v1/users/me', {
                headers: { 'Authorization': `Bearer ${tokenData.access_token}` }
            });
            const userData = await userRes.json();

            loginUser(tokenData.access_token, userData);
            goto('/dashboard');

        } catch (e: any) {
            error = e.message;
        } finally {
            isLoading = false;
        }
    }
</script>

<div class="min-h-screen bg-sp-orange flex items-center justify-center p-4">
    
    <div class="bg-white border-4 border-black p-8 max-w-md w-full shadow-hard-lg transform -rotate-1 relative">
        
        <div class="absolute -top-6 -right-6 bg-sp-yellow border-4 border-black p-3 rounded-full shadow-hard transform rotate-12">
            <span class="text-2xl">👋</span>
        </div>

        <h1 class="text-3xl font-black mb-2 uppercase text-center mt-2">Join The Network</h1>
        <p class="text-center font-bold text-gray-500 mb-8 text-sm">Create your sovereign identity.</p>
        
        {#if error}
            <div class="bg-sp-red text-white p-3 border-2 border-black font-bold text-sm mb-4 shadow-hard-sm">
                ⚠️ {error}
            </div>
        {/if}

        <form on:submit|preventDefault={handleSignup} class="space-y-4">
            <div>
                <label class="block font-bold text-sm mb-1 uppercase">Full Name</label>
                <input 
                    bind:value={fullName}
                    type="text" 
                    required
                    class="w-full border-4 border-black p-3 bg-sp-paper focus:bg-white outline-none font-bold transition-all focus:shadow-hard-sm" 
                    placeholder="Stan Marsh"
                />
            </div>

            <div>
                <label class="block font-bold text-sm mb-1 uppercase">Email Identity</label>
                <input 
                    bind:value={email}
                    type="email" 
                    required
                    class="w-full border-4 border-black p-3 bg-sp-paper focus:bg-white outline-none font-bold transition-all focus:shadow-hard-sm" 
                    placeholder="stan@resinen.com"
                />
            </div>

            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block font-bold text-sm mb-1 uppercase">Passkey</label>
                    <input 
                        bind:value={password}
                        type="password" 
                        required
                        class="w-full border-4 border-black p-3 bg-sp-paper focus:bg-white outline-none font-bold transition-all focus:shadow-hard-sm" 
                        placeholder="••••••"
                    />
                </div>
                <div>
                    <label class="block font-bold text-sm mb-1 uppercase">Confirm</label>
                    <input 
                        bind:value={confirmPassword}
                        type="password" 
                        required
                        class="w-full border-4 border-black p-3 bg-sp-paper focus:bg-white outline-none font-bold transition-all focus:shadow-hard-sm" 
                        placeholder="••••••"
                    />
                </div>
            </div>
            
            <button 
                disabled={isLoading}
                class="w-full bg-sp-cyan text-black font-black py-4 border-4 border-black shadow-hard hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-none transition-all uppercase disabled:opacity-50 disabled:cursor-not-allowed mt-4"
            >
                {isLoading ? 'Minting Identity...' : 'Initialize Account'}
            </button>
        </form>
        
        <div class="mt-8 pt-6 border-t-2 border-dashed border-black text-center">
            <p class="text-sm font-bold text-gray-500">
                Already have an identity? 
                <a href="/login" class="text-sp-blue underline decoration-2 underline-offset-2 hover:bg-sp-yellow">Login here</a>
            </p>
        </div>
    </div>
</div>