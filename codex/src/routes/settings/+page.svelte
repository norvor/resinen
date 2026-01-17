<script lang="ts">
    import { onMount } from 'svelte';
    import { api, type User } from '$lib/api';

    let user: Partial<User> = {};
    let isSaving = false;
    let message = '';

    onMount(async () => {
        try {
            user = await api.getMe();
        } catch (e) {
            console.error(e);
        }
    });

    async function handleSave() {
        isSaving = true;
        message = '';
        try {
            // Filter out read-only fields like 'id', 'email', 'xp' if needed, 
            // but the backend handles it via Pydantic schemas anyway.
            await api.updateProfile({
                full_name: user.full_name,
                headline: user.headline,
                bio: user.bio,
                location: user.location,
                website: user.website,
                linkedin: user.linkedin,
                twitter: user.twitter,
                github: user.github
            });
            message = 'Profile updated successfully!';
        } catch (e) {
            message = 'Failed to update profile.';
        } finally {
            isSaving = false;
        }
    }
</script>

<div class="max-w-3xl mx-auto mt-12">
    <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold text-white">Your Profile</h1>
        <a href="/communities" class="text-slate-500 hover:text-white text-sm">Cancel</a>
    </div>

    {#if message}
        <div class="mb-6 p-4 rounded-xl {message.includes('success') ? 'bg-green-900/20 text-green-400 border border-green-900' : 'bg-red-900/20 text-red-400 border border-red-900'}">
            {message}
        </div>
    {/if}

    <div class="bg-slate-950 border border-slate-800 rounded-2xl p-8 space-y-8">
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
                <label class="block text-slate-400 text-sm font-bold mb-2">Full Name</label>
                <input bind:value={user.full_name} type="text" class="w-full bg-slate-900 border border-slate-800 text-white p-3 rounded-xl focus:ring-1 focus:ring-orange-500 outline-none" />
            </div>
            <div>
                <label class="block text-slate-400 text-sm font-bold mb-2">Headline</label>
                <input bind:value={user.headline} type="text" placeholder="e.g. Software Engineer" class="w-full bg-slate-900 border border-slate-800 text-white p-3 rounded-xl focus:ring-1 focus:ring-orange-500 outline-none" />
            </div>
        </div>

        <div>
            <label class="block text-slate-400 text-sm font-bold mb-2">Location</label>
            <input bind:value={user.location} type="text" placeholder="e.g. Paris, France" class="w-full bg-slate-900 border border-slate-800 text-white p-3 rounded-xl focus:ring-1 focus:ring-orange-500 outline-none" />
        </div>

        <div>
            <label class="block text-slate-400 text-sm font-bold mb-2">Bio</label>
            <textarea bind:value={user.bio} rows="4" placeholder="Tell us about yourself..." class="w-full bg-slate-900 border border-slate-800 text-white p-3 rounded-xl focus:ring-1 focus:ring-orange-500 outline-none"></textarea>
        </div>

        <div class="pt-6 border-t border-slate-900">
            <h3 class="text-lg font-bold text-white mb-4">Social Links</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <label class="block text-slate-400 text-xs font-bold mb-2 uppercase">Website</label>
                    <input bind:value={user.website} type="text" placeholder="https://" class="w-full bg-slate-900 border border-slate-800 text-white p-3 rounded-xl outline-none" />
                </div>
                <div>
                    <label class="block text-slate-400 text-xs font-bold mb-2 uppercase">LinkedIn</label>
                    <input bind:value={user.linkedin} type="text" placeholder="https://linkedin.com/in/..." class="w-full bg-slate-900 border border-slate-800 text-white p-3 rounded-xl outline-none" />
                </div>
                <div>
                    <label class="block text-slate-400 text-xs font-bold mb-2 uppercase">Twitter / X</label>
                    <input bind:value={user.twitter} type="text" placeholder="https://x.com/..." class="w-full bg-slate-900 border border-slate-800 text-white p-3 rounded-xl outline-none" />
                </div>
                <div>
                    <label class="block text-slate-400 text-xs font-bold mb-2 uppercase">GitHub</label>
                    <input bind:value={user.github} type="text" placeholder="https://github.com/..." class="w-full bg-slate-900 border border-slate-800 text-white p-3 rounded-xl outline-none" />
                </div>
            </div>
        </div>

        <div class="pt-6">
            <button 
                on:click={handleSave}
                disabled={isSaving}
                class="w-full bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-500 hover:to-red-500 text-white font-bold py-4 rounded-xl transition-all shadow-lg"
            >
                {isSaving ? 'SAVING PROFILE...' : 'SAVE CHANGES'}
            </button>
        </div>
    </div>
</div>