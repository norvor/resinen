<script lang="ts">
    import { page } from '$app/stores';
    import { onMount } from 'svelte';
    import { api } from '$lib/api';

    let slug = $page.params.slug;
    let community: any = null;
    let membership: any = { status: 'none' }; // default to outsider
    let loading = true;
    let isJoining = false;

    onMount(async () => {
        try {
            // 1. Fetch Community Info
            community = await api('GET', `/communities/by-slug/${slug}`);
            // 2. Check if I am already a member
            membership = await api('GET', `/communities/${community.id}/membership_status`);
        } catch (e) {
            console.error(e);
        } finally {
            loading = false;
        }
    });

    async function handleJoin() {
        isJoining = true;
        try {
            // 3. Send Join Request
            const res = await api('POST', `/communities/${community.id}/join`);
            
            if (res.status === 'active') {
                alert('Welcome inside!');
                membership.status = 'active';
            } else {
                // This is the flow we are testing
                alert('Application Submitted. Please wait for approval.');
                membership.status = 'pending';
            }
        } catch (e) {
            alert('Error joining.');
        } finally {
            isJoining = false;
        }
    }
</script>

{#if loading}
    <div class="p-12 text-center font-bold uppercase">Loading Territory...</div>
{:else if community}
    <div class="min-h-screen bg-white">
        
        <div class="bg-black text-white p-12 text-center">
            <h1 class="text-5xl font-black uppercase mb-4">{community.name}</h1>
            <p class="text-gray-400 max-w-xl mx-auto">{community.description || "A Sovereign Territory."}</p>
            
            <div class="mt-8">
                {#if membership.status === 'active'}
                    <div class="text-green-500 font-bold text-xl uppercase">✓ Citizenship Verified</div>
                
                {:else if membership.status === 'pending'}
                    <div class="bg-yellow-500 text-black inline-block px-8 py-4 font-black uppercase tracking-widest">
                        ⏳ Application Pending
                    </div>
                    <p class="text-xs text-gray-500 mt-2">The Architect must approve you on Codex.</p>
                
                {:else}
                    <button 
                        on:click={handleJoin} 
                        disabled={isJoining}
                        class="bg-orange-600 hover:bg-orange-500 text-white px-8 py-4 font-black uppercase tracking-widest shadow-white transition-transform hover:scale-105"
                    >
                        {#if community.is_private}
                            Apply for Citizenship
                        {:else}
                            Join Territory
                        {/if}
                    </button>
                    {#if community.is_private}
                        <p class="text-xs text-gray-500 mt-2">🔒 This territory is gated.</p>
                    {/if}
                {/if}
            </div>
        </div>

    </div>
{:else}
    <div class="p-12 text-center text-red-600 font-bold">Community Not Found</div>
{/if}