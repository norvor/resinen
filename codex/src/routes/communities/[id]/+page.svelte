<script lang="ts">
    import { page } from '$app/stores';
    import { onMount } from 'svelte';
    import { api, type Community } from '$lib/api';

    // 1. Get ID
    let communityId = $page.params.id;

    // 2. Data State
    let community: Community | null = null;
    let allMembers: any[] = [];
    let pendingQueue: any[] = [];
    let activeCitizens: any[] = [];
    
    // FIX: The script uses 'loading'
    let loading = true; 
    let processingId: string | null = null;

    onMount(async () => {
        await loadIntel();
    });

    async function loadIntel() {
        try {
            community = await api.getCommunity(communityId);
            allMembers = await api.getMembers(communityId);

            // Sort members
            pendingQueue = allMembers.filter(m => m.status.toLowerCase() === 'pending');
            activeCitizens = allMembers.filter(m => m.status.toLowerCase() === 'active');

            if (community) {
                community.member_count = activeCitizens.length;
            }

        } catch (e: any) {
            console.error("Intel Failure:", e);
        } finally {
            loading = false;
        }
    }

    async function handleDecision(userId: string, action: 'approve' | 'reject') {
        if (!confirm(`Confirm: ${action.toUpperCase()} this applicant?`)) return;
        processingId = userId;

        try {
            await api.processMembership(communityId, userId, action);
            await loadIntel(); 
        } catch (e: any) {
            alert('Command failed: ' + e.message);
        } finally {
            processingId = null;
        }
    }
</script>

<div class="max-w-6xl mx-auto p-8">
    <a href="/communities" class="text-slate-500 hover:text-white mb-6 inline-block text-sm font-mono">&larr; RETURN TO MAP</a>

    {#if loading}
        <div class="p-12 text-center text-slate-500 animate-pulse border border-slate-800 rounded-xl bg-slate-950">
            LOADING INTEL...
        </div>
    {:else if community}
        
        <div class="bg-slate-950 border border-slate-800 rounded-xl p-8 mb-8 flex justify-between items-start">
            <div>
                <h1 class="text-3xl font-bold text-white mb-2">{community.name}</h1>
                <div class="text-slate-500 font-mono text-sm">{community.slug}</div>
            </div>
            <div class="text-right">
                <div class="text-4xl font-bold text-white">{activeCitizens.length}</div>
                <div class="text-xs text-slate-500 uppercase font-bold">Citizens</div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            
            <div class="space-y-4">
                <h3 class="text-orange-500 font-bold uppercase text-xs tracking-widest flex items-center gap-2">
                    Pending Applications
                    {#if pendingQueue.length > 0}
                        <span class="bg-orange-600 text-white text-[10px] px-2 rounded-full">{pendingQueue.length}</span>
                    {/if}
                </h3>

                <div class="bg-slate-950 border border-slate-800 rounded-xl min-h-[200px]">
                    {#if pendingQueue.length === 0}
                        <div class="h-full flex flex-col items-center justify-center p-8 text-slate-600">
                            <div class="text-2xl mb-2">✓</div>
                            <div class="text-sm font-bold">All Clear</div>
                            <div class="text-xs">No pending applications.</div>
                        </div>
                    {:else}
                        <div class="divide-y divide-slate-800">
                            {#each pendingQueue as applicant}
                                <div class="p-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 hover:bg-slate-900/30 transition-colors">
                                    
                                    <div class="flex items-center gap-3">
                                        <div class="w-10 h-10 rounded-full bg-slate-900 border border-slate-700 flex items-center justify-center text-white font-bold text-sm uppercase">
                                            {(applicant.user?.full_name || applicant.user?.email || '?')[0]}
                                        </div>
                                        
                                        <div>
                                            <div class="font-bold text-white text-sm">
                                                {applicant.user?.full_name || 'Unknown User'}
                                            </div>
                                            <div class="text-xs text-slate-500 font-mono">
                                                {applicant.user?.email || applicant.user_id}
                                            </div>
                                            <div class="text-[10px] text-orange-500 mt-0.5 font-bold uppercase tracking-wider">
                                                Awaiting Entry
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div class="flex gap-2 w-full sm:w-auto">
                                        <button 
                                            on:click={() => handleDecision(applicant.user_id, 'reject')}
                                            disabled={processingId === applicant.user_id}
                                            class="flex-1 sm:flex-none px-4 py-2 text-xs font-bold text-red-400 border border-red-900/30 bg-red-900/10 rounded-lg hover:bg-red-900/20 hover:border-red-500/50 transition-all disabled:opacity-50"
                                        >
                                            REJECT
                                        </button>
                                        <button 
                                            on:click={() => handleDecision(applicant.user_id, 'approve')}
                                            disabled={processingId === applicant.user_id}
                                            class="flex-1 sm:flex-none px-4 py-2 text-xs font-bold text-green-400 border border-green-900/30 bg-green-900/10 rounded-lg hover:bg-green-900/20 hover:border-green-500/50 transition-all disabled:opacity-50 shadow-[0_0_10px_rgba(74,222,128,0.05)]"
                                        >
                                            {processingId === applicant.user_id ? 'PROCESSING...' : 'APPROVE'}
                                        </button>
                                    </div>
                                </div>
                            {/each}
                        </div>
                    {/if}
                </div>
            </div>

            <div class="space-y-4">
                <h3 class="text-slate-500 font-bold uppercase text-xs tracking-widest">Active Roster</h3>
                
                <div class="bg-slate-950 border border-slate-800 rounded-xl p-4 min-h-[200px]">
                    {#if activeCitizens.length === 0}
                        <div class="text-slate-600 text-sm italic w-full text-center mt-8">No active citizens.</div>
                    {:else}
                        <div class="space-y-2">
                            {#each activeCitizens as citizen}
                                <div class="flex items-center justify-between bg-slate-900 border border-slate-800 p-3 rounded-lg hover:border-slate-700 transition-colors">
                                    
                                    <div class="flex items-center gap-3">
                                        <div class="w-8 h-8 rounded-full bg-orange-900/20 text-orange-500 flex items-center justify-center font-bold text-xs border border-orange-900/50">
                                            {citizen.user?.full_name ? citizen.user.full_name[0] : '?'}
                                        </div>
                                        
                                        <div>
                                            <div class="text-sm font-bold text-white">
                                                {citizen.user?.full_name || 'Unknown Citizen'}
                                            </div>
                                            <div class="text-xs text-slate-500 font-mono">
                                                {citizen.user?.email || citizen.user_id}
                                            </div>
                                        </div>
                                    </div>

                                    <span class="text-[10px] uppercase font-bold bg-slate-950 text-slate-400 px-2 py-1 rounded border border-slate-800">
                                        {citizen.role}
                                    </span>
                                </div>
                            {/each}
                        </div>
                    {/if}
                </div>
            </div>

        </div>

    {:else}
        <div class="p-12 text-center text-red-500 border border-red-900/50 bg-red-900/10 rounded-xl">
            DATA LINK SEVERED (404)
        </div>
    {/if}
</div>