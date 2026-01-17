<script lang="ts">
    import { page } from '$app/stores';
    import { api } from '$lib/api';
    import { onMount } from 'svelte';

    let communityId = ''; // You'd fetch this from the slug
    let applicants: any[] = [];
    let loading = true;

    onMount(async () => {
        // Mocking ID fetch for brevity
        const community = await api('GET', `/communities/lookup?slug=${$page.params.slug}`);
        communityId = community.id;
        
        // Fetch the queue
        applicants = await api('GET', `/memberships/pending/${communityId}`);
        loading = false;
    });

    async function judge(membershipId: string, verdict: 'approve' | 'reject') {
        await api('POST', `/memberships/${membershipId}/decide`, { decision: verdict });
        // Remove from UI
        applicants = applicants.filter(a => a.id !== membershipId);
    }
</script>

<div class="max-w-5xl mx-auto">
    <div class="bg-black text-white p-6 border-b-4 border-sp-red mb-8">
        <h1 class="text-3xl font-black uppercase">Border Control</h1>
        <p class="font-mono text-sm opacity-80">Approving entry for: <span class="text-sp-yellow">{$page.params.slug}</span></p>
    </div>

    {#if loading}
        <div class="p-8 text-center font-bold animate-pulse">Loading Manifest...</div>
    {:else if applicants.length === 0}
        <div class="p-12 border-4 border-dashed border-gray-300 text-center text-gray-400 font-bold">
            No one is waiting at the gates.
        </div>
    {:else}
        <div class="grid gap-4">
            {#each applicants as app}
                <div class="bg-white border-4 border-black p-6 shadow-hard flex flex-col md:flex-row justify-between items-center">
                    <div>
                        <h3 class="font-black text-xl uppercase">Candidate #{app.user_id.slice(0,4)}</h3>
                        <p class="text-sm font-bold text-gray-500">Applied: {new Date(app.joined_at).toLocaleDateString()}</p>
                    </div>
                    
                    <div class="flex gap-4 mt-4 md:mt-0">
                        <button 
                            on:click={() => judge(app.id, 'reject')}
                            class="px-6 py-2 border-2 border-black font-black uppercase hover:bg-sp-red hover:text-white transition-colors"
                        >
                            Deny Entry
                        </button>
                        <button 
                            on:click={() => judge(app.id, 'approve')}
                            class="px-6 py-2 bg-sp-green border-2 border-black font-black uppercase shadow-hard-sm hover:translate-y-1 hover:shadow-none transition-all"
                        >
                            Approve
                        </button>
                    </div>
                </div>
            {/each}
        </div>
    {/if}
</div>