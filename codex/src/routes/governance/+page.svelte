<script lang="ts">
    import { onMount } from 'svelte';
    import { getGovernanceIssues, createGovernanceIssue, user } from '$lib/api';

    let issues: any[] = [];
    let loading = true;
    let showNewModal = false;

    // Form Data
    let newTitle = '';
    let newDesc = '';
    let newKind = 'proposal'; // or 'moderation'

    onMount(async () => {
        try {
            issues = await getGovernanceIssues();
        } catch (e) {
            console.error(e);
        } finally {
            loading = false;
        }
    });

    async function handleSubmit() {
        await createGovernanceIssue({ title: newTitle, description: newDesc, kind: newKind });
        showNewModal = false;
        issues = await getGovernanceIssues(); // Refresh
    }

    // Filter Logic
    // In a real app, the backend should tell us if we have a pending vote.
    // For this UI demo, we'll assume any 'moderation' issue is a Jury Duty case.
    $: juryDutyCases = issues.filter(i => i.kind === 'moderation' && i.status === 'active');
    $: publicProposals = issues.filter(i => i.kind === 'proposal');
</script>

<div class="space-y-8">
    
    <div class="flex flex-col md:flex-row justify-between items-end border-b-4 border-black pb-4 gap-4">
        <div>
            <h1 class="text-4xl font-black uppercase tracking-tight">Governance</h1>
            <p class="font-bold text-gray-600">The Law of the Land.</p>
        </div>
        <button 
            on:click={() => showNewModal = true}
            class="bg-black text-white px-6 py-3 font-black uppercase hover:bg-sp-green transition-colors shadow-hard"
        >
            + New Proposal
        </button>
    </div>

    {#if juryDutyCases.length > 0}
        <div class="bg-sp-red border-4 border-black p-6 shadow-hard animate-pulse">
            <h2 class="text-white text-2xl font-black uppercase mb-2">⚠️ Jury Summons Active</h2>
            <p class="text-white font-bold mb-4">You have been selected to serve on the following cases. Failure to vote will impact your reputation.</p>
            
            <div class="grid gap-4">
                {#each juryDutyCases as issue}
                    <a href="/governance/{issue.id}" class="block bg-white border-4 border-black p-4 hover:translate-x-1 hover:translate-y-1 transition-transform">
                        <div class="flex justify-between items-center">
                            <span class="font-black uppercase">CASE #{issue.id.slice(0,8)}</span>
                            <span class="bg-black text-white text-xs font-bold px-2 py-1">VOTE REQUIRED</span>
                        </div>
                        <p class="font-bold text-gray-800 mt-1">{issue.title}</p>
                    </a>
                {/each}
            </div>
        </div>
    {/if}

    <div>
        <h3 class="font-black text-xl uppercase mb-6 flex items-center gap-2">
            <span>Active Proposals</span>
            <div class="h-1 bg-black/10 flex-grow"></div>
        </h3>

        {#if loading}
            <div class="text-center font-bold text-gray-400 py-12">LOADING DOCKET...</div>
        {:else if publicProposals.length === 0}
            <div class="text-center font-bold text-gray-400 py-12 border-2 border-dashed border-gray-300">
                No active proposals. The community is at peace.
            </div>
        {:else}
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                {#each publicProposals as issue}
                    <a href="/governance/{issue.id}" class="bg-white border-4 border-black p-6 shadow-hard hover:shadow-hard-lg transition-all group">
                        <div class="flex justify-between items-start mb-4">
                            <div class="bg-sp-yellow border-2 border-black w-10 h-10 flex items-center justify-center font-black rounded-full">
                                ?
                            </div>
                            <span class="text-xs font-bold bg-gray-100 px-2 py-1 border border-black">{issue.status}</span>
                        </div>
                        <h4 class="font-black text-lg uppercase mb-2 group-hover:text-sp-blue transition-colors">{issue.title}</h4>
                        <p class="text-sm font-bold text-gray-500 line-clamp-2">{issue.description}</p>
                        
                        <div class="mt-4 pt-4 border-t-2 border-dashed border-gray-200 flex justify-between text-xs font-bold uppercase">
                            <span>Expires in 3 Days</span>
                            <span>{issue.votes?.length || 0} Votes</span>
                        </div>
                    </a>
                {/each}
            </div>
        {/if}
    </div>

</div>

{#if showNewModal}
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
        <div class="bg-white border-4 border-black shadow-hard-lg max-w-lg w-full p-8 relative">
            <button on:click={() => showNewModal = false} class="absolute top-4 right-4 font-black text-xl hover:text-sp-red">X</button>
            
            <h2 class="text-2xl font-black uppercase mb-6">Draft Proposal</h2>
            
            <div class="space-y-4">
                <div>
                    <label class="block text-xs font-black uppercase mb-1">Title</label>
                    <input bind:value={newTitle} class="w-full border-4 border-black p-3 font-bold outline-none focus:bg-sp-paper" placeholder="e.g. Ban Anime Spoilers" />
                </div>
                
                <div>
                    <label class="block text-xs font-black uppercase mb-1">Reasoning</label>
                    <textarea bind:value={newDesc} rows="4" class="w-full border-4 border-black p-3 font-bold outline-none focus:bg-sp-paper" placeholder="Explain why this should be law..."></textarea>
                </div>

                <button on:click={handleSubmit} class="w-full bg-sp-green border-4 border-black py-4 font-black uppercase text-xl shadow-hard hover:translate-y-1 hover:shadow-none transition-all">
                    Submit to Docket
                </button>
            </div>
        </div>
    </div>
{/if}