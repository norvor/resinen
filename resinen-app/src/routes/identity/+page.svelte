<script lang="ts">
    import { user, token, API_URL } from '$lib/api';
    import { get } from 'svelte/store';
    import FileUploader from '$lib/components/FileUploader.svelte';

    let isUpdating = false;

    async function handleUploadSuccess(event: CustomEvent) {
        const newUrl = event.detail.url;
        console.log("Vault URL received:", newUrl);
        
        await updateProfileAvatar(newUrl);
    }

    async function updateProfileAvatar(url: string) {
        isUpdating = true;
        try {
            const authToken = get(token);
            if (!authToken) return;

            // PATCH the user profile in the database
            const res = await fetch(`${API_URL}/users/me`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify({ avatar_url: url })
            });

            if (res.ok) {
                const updatedUser = await res.json();
                // Update the global store so the UI reflects the change instantly
                user.set(updatedUser);
            }
        } catch (err) {
            console.error("Failed to link avatar to profile:", err);
        } finally {
            isUpdating = false;
        }
    }
</script>

<div class="max-w-2xl mx-auto">
    
    <div class="bg-white border-4 border-black p-0 shadow-hard-lg relative overflow-hidden">
        
        <div class="bg-sp-blue p-6 border-b-4 border-black flex justify-between items-center">
            <h1 class="text-white text-2xl font-black uppercase tracking-widest">Citizen ID</h1>
            <div class="w-12 h-12 bg-white/20 rounded-full border-2 border-white/50 flex items-center justify-center">
                <span class="text-2xl">🏔️</span>
            </div>
        </div>

        <div class="p-8 flex flex-col md:flex-row gap-8 items-start">
            
            <div class="flex-shrink-0 flex flex-col gap-4 w-full md:w-auto">
                <div class="w-32 h-32 border-4 border-black shadow-hard overflow-hidden bg-sp-yellow flex items-center justify-center relative">
                    {#if isUpdating}
                        <div class="absolute inset-0 bg-black/50 flex items-center justify-center text-white font-bold text-xs z-10">
                            SAVING...
                        </div>
                    {/if}

                    {#if $user?.avatar_url}
                        <img 
                            src={$user.avatar_url} 
                            alt="Avatar" 
                            class="w-full h-full object-cover"
                        />
                    {:else}
                        <div class="text-5xl font-black">
                            {$user?.full_name?.charAt(0) || '?'}
                        </div>
                    {/if}
                </div>

                <div class="w-32">
                    <FileUploader 
                        label="Update Photo" 
                        uploadingText="..."
                        on:success={handleUploadSuccess} 
                    />
                </div>
            </div>

            <div class="flex-grow space-y-4 w-full">
                <div>
                    <label class="block text-xs font-black text-gray-400 uppercase">Full Name</label>
                    <div class="text-2xl font-black uppercase">{$user?.full_name}</div>
                </div>

                <div>
                    <label class="block text-xs font-black text-gray-400 uppercase">Digital Identity (Email)</label>
                    <div class="text-xl font-bold font-mono">{$user?.email}</div>
                </div>

                <div>
                    <label class="block text-xs font-black text-gray-400 uppercase">User ID</label>
                    <div class="text-sm font-bold font-mono bg-gray-100 p-2 border-2 border-black inline-block break-all">
                        {$user?.id || 'UNREGISTERED'}
                    </div>
                </div>
            </div>
        </div>

        <div class="bg-gray-100 p-4 border-t-4 border-black text-center">
            <p class="text-xs font-bold text-gray-500 uppercase">
                Issued by Resinen Governance Protocol • Valid Forever
            </p>
        </div>
    </div>

</div>