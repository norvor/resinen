<script lang="ts">
    import { goto } from '$app/navigation';
    import { api } from '$lib/api'; // We only need 'api'

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
            // 1. Create User
            // The api.signup function handles the JSON structure for you
            await api.signup(email, password, fullName);

            // 2. Auto-Login
            // The api.login function handles the FormData and Token Storage automatically
            await api.login(email, password);

            // 3. Get Profile
            // The api.getMe function handles fetching and updating the User store
            await api.getMe();

            // 4. Success -> Redirect
            goto('/dashboard');

        } catch (e: any) {
            console.error(e);
            // Handle specific API error messages
            error = e.message || e.detail || 'Registration failed';
            
            // Clean up if something half-worked
            localStorage.removeItem('token'); 
        } finally {
            isLoading = false;
        }
    }
</script>

<div class="min-h-screen bg-sp-orange flex items-center justify-center p-4">
    <div class="bg-white border-4 border-black p-8 max-w-md w-full shadow-hard-lg transform -rotate-1 relative">
        <h1 class="text-3xl font-black mb-2 uppercase text-center mt-2">Join The Network</h1>
        <p class="text-center font-bold text-gray-500 mb-8 text-sm">Create your sovereign identity.</p>
        
        {#if error}
            <div class="bg-sp-red text-white p-3 border-2 border-black font-bold text-sm mb-4">
                ⚠️ {error}
            </div>
        {/if}

        <form on:submit|preventDefault={handleSignup} class="space-y-4">
            <div>
                <label class="block font-bold text-sm mb-1 uppercase">Full Name</label>
                <input bind:value={fullName} type="text" required class="w-full border-4 border-black p-3 font-bold outline-none" placeholder="Stan Marsh" />
            </div>

            <div>
                <label class="block font-bold text-sm mb-1 uppercase">Email Identity</label>
                <input bind:value={email} type="email" required class="w-full border-4 border-black p-3 font-bold outline-none" placeholder="stan@resinen.com" />
            </div>

            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block font-bold text-sm mb-1 uppercase">Passkey</label>
                    <input bind:value={password} type="password" required class="w-full border-4 border-black p-3 font-bold outline-none" placeholder="••••••" />
                </div>
                <div>
                    <label class="block font-bold text-sm mb-1 uppercase">Confirm</label>
                    <input bind:value={confirmPassword} type="password" required class="w-full border-4 border-black p-3 font-bold outline-none" placeholder="••••••" />
                </div>
            </div>
            
            <button disabled={isLoading} class="w-full bg-sp-cyan text-black font-black py-4 border-4 border-black shadow-hard hover:shadow-none transition-all uppercase disabled:opacity-50 mt-4">
                {isLoading ? 'Minting Identity...' : 'Initialize Account'}
            </button>
        </form>
        
        <div class="mt-8 pt-6 border-t-2 border-dashed border-black text-center">
            <p class="text-sm font-bold text-gray-500">
                Already have an identity?
                <a href="/login" class="text-sp-blue underline hover:bg-sp-yellow">Login here</a>
            </p>
        </div>
    </div>
</div>