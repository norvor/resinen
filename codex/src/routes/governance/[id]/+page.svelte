<script lang="ts">
    import { page } from '$app/stores';
    import { castVote } from '$lib/api';
    
    // In a real app, you'd fetch the specific issue details here using $page.params.id
    // For this template, we'll mock the data to show the UI state
    let issueId = $page.params.id;
    let voteReason = '';
    let hasVoted = false;

    async function handleVote(decision: string) {
        try {
            await castVote(issueId, decision, voteReason);
            hasVoted = true;
            alert('Vote Cast! Thank you for your service.');
        } catch (e) {
            alert('Failed to cast vote.');
        }
    }
</script>

<div class="max-w-4xl mx-auto">
    
    <a href="/governance" class="inline-block font-black uppercase text-xs mb-6 hover:underline">← Back to Docket</a>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        
        <div class="md:col-span-2 space-y-8">
            <div class="bg-white border-4 border-black p-8 shadow-hard relative overflow-hidden">
                <div class="absolute top-0 right-0 bg-sp-yellow border-l-4 border-b-4 border-black px-4 py-2 font-black uppercase text-sm">
                    Open for Voting
                </div>

                <h1 class="text-3xl md:text-5xl font-black uppercase mb-6 leading-none">Proposal #{issueId.slice(0,4)}</h1>
                
                <div class="prose font-bold text-gray-800">
                    <p class="text-lg">Allow "Meme Fridays" in the General Channel.</p>
                    <p class="text-gray-500 text-sm">Submitted by: Citizen #4921</p>
                </div>
                
                <div class="mt-8 p-6 bg-gray-100 border-2 border-dashed border-black">
                    <h3 class="font-black uppercase text-sm mb-2 text-gray-500">Evidence / Description</h3>
                    <p>Current morale is low. Allowing memes on Fridays has been shown to increase engagement by 40% in other chapters.</p>
                </div>
            </div>
        </div>

        <div>
            <div class="bg-sp-blue p-6 border-4 border-black shadow-hard text-white sticky top-6">
                <h2 class="text-2xl font-black uppercase mb-4 border-b-4 border-black pb-2">Cast Vote</h2>
                
                {#if hasVoted}
                    <div class="bg-sp-green text-black p-4 font-black text-center border-4 border-black">
                        VOTE RECORDED
                    </div>
                {:else}
                    <div class="space-y-4">
                        <textarea 
                            bind:value={voteReason}
                            class="w-full bg-black/20 border-2 border-white/30 p-3 text-white placeholder-white/50 font-bold text-sm outline-none focus:border-white"
                            rows="3"
                            placeholder="Optional: Why are you voting this way?"
                        ></textarea>

                        <div class="grid grid-cols-2 gap-4">
                            <button 
                                on:click={() => handleVote('approve')}
                                class="bg-sp-green text-black py-4 font-black uppercase border-4 border-black hover:scale-105 transition-transform"
                            >
                                YES
                            </button>
                            <button 
                                on:click={() => handleVote('reject')}
                                class="bg-sp-red text-black py-4 font-black uppercase border-4 border-black hover:scale-105 transition-transform"
                            >
                                NO
                            </button>
                        </div>
                        <button class="w-full text-xs font-bold uppercase hover:underline opacity-60">Abstain</button>
                    </div>
                {/if}
            </div>
        </div>

    </div>
</div>