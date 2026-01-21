<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { api } from '$lib/api';

    // State
    let community: any = null;
    let stats: any[] = [];
    let loading = true;

    // Reactive Fetch
    $: communityId = $page.params.id;
    $: if (communityId) initPage(communityId);

    async function initPage(id: string) {
        loading = true;
        try {
            // 1. Fetch Identity
            community = await api.getCommunity(id);
            
            // 2. Set Default Stats
            stats = [
                { label: 'Total Members', value: community.member_count, trend: '...', color: 'text-blue-600' },
                { label: 'Daily Active', value: '-', trend: '...', color: 'text-green-600' },
                { label: 'Posts Today', value: '-', trend: '...', color: 'text-orange-600' },
            ];

            // 3. Fetch Live Stats (Non-blocking)
            const liveData = await api.getCommunityStats(id);
            stats = [
                { label: 'Total Members', value: liveData.member_count, trend: '+1%', color: 'text-blue-600' },
                { label: 'Daily Active', value: liveData.daily_active, trend: '~', color: 'text-green-600' },
                { label: 'Posts Today', value: liveData.posts_today, trend: 'Live', color: 'text-orange-600' },
                { label: 'Pending Approvals', value: liveData.pending_reports, trend: 'Action Req', color: 'text-red-600' },
            ];
            
        } catch (e) {
            console.error("Dashboard fetch error:", e);
        } finally {
            loading = false;
        }
    }
</script>

{#if !loading && community}
<div class="space-y-8 animate-fade-in-up">
    
    <div class="flex items-end justify-between border-b-4 border-black pb-6">
        <div>
            <div class="text-xs font-black uppercase text-gray-400 tracking-widest mb-1">Dashboard</div>
            <h1 class="text-5xl font-black uppercase tracking-tighter">Overview</h1>
        </div>
        <a href="https://resinen.com/c/{community.slug}" target="_blank" class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-900 font-bold rounded text-xs uppercase transition-colors">
            View Public Site ↗
        </a>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {#each stats as stat}
            <div class="bg-white p-6 rounded-xl border-2 border-gray-100 shadow-sm hover:border-gray-300 transition-colors">
                <div class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">{stat.label}</div>
                <div class="flex items-end gap-2">
                    <div class="text-4xl font-black text-gray-900">{stat.value}</div>
                    <div class="text-xs font-bold {stat.color} mb-1.5">{stat.trend}</div>
                </div>
            </div>
        {/each}
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div class="lg:col-span-2 space-y-6">
            <div class="bg-white border-2 border-gray-200 rounded-xl p-6 h-64 flex items-center justify-center text-gray-400 font-bold">
                AUDIT LOG COMPONENT HERE
            </div>
        </div>
        <div class="space-y-6">
            <div class="bg-gradient-to-br from-gray-900 to-black text-white rounded-xl p-6 shadow-xl">
                <h3 class="font-black uppercase text-lg mb-2">System Status</h3>
                <div class="flex items-center gap-2 mb-4">
                    <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                    <span class="text-xs font-bold text-green-400 uppercase">Operational</span>
                </div>
            </div>
        </div>
    </div>

</div>
{:else}
    <div class="flex items-center justify-center h-96">
        <div class="text-2xl font-black text-gray-300 animate-pulse">LOADING DASHBOARD...</div>
    </div>
{/if}