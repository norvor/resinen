<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';

    export let communityId: string;

    // The widget displays a single "Highlight"
    let highlight: any = null;
    let type: 'bounty' | 'project' | 'empty' = 'empty';
    let loading = true;

    onMount(async () => {
        try {
            // 1. Try to fetch Bounties first (Priority: Actionable)
            const bounties = await api.getBounties(communityId);
            
            if (bounties && bounties.length > 0) {
                highlight = bounties[0];
                type = 'bounty';
            } else {
                // 2. If no bounties, fetch Projects (Priority: Showcase)
                const projects = await api.getProjects(communityId);
                if (projects && projects.length > 0) {
                    // Sort by likes if available, or just take the first
                    highlight = projects.sort((a: any, b: any) => (b.likes || 0) - (a.likes || 0))[0];
                    type = 'project';
                }
            }
        } catch (e) {
            console.error(e);
        } finally {
            loading = false;
        }
    });
</script>

<div class="h-full w-full">
    {#if loading}
        <div class="h-full bg-yellow-50/50 animate-pulse rounded-2xl border border-yellow-100"></div>
    {:else if type === 'bounty'}
        <a href="/communities/{communityId}?tab=guild" class="block h-full bg-[#fffdf0] border-2 border-yellow-400 rounded-2xl p-5 flex flex-col justify-between relative group hover:-translate-y-1 hover:shadow-[4px_4px_0px_#eab308] transition-all duration-200">
            
            <div class="absolute -top-3 left-1/2 -translate-x-1/2 w-4 h-4 bg-red-500 rounded-full border border-black/20 shadow-sm z-20"></div>

            <div class="relative z-10">
                <div class="flex justify-between items-start">
                    <span class="text-[9px] font-black uppercase text-yellow-800 tracking-widest border-b-2 border-yellow-200">
                        Help Wanted
                    </span>
                    <span class="text-xs font-black bg-black text-white px-2 py-1 transform rotate-2 shadow-sm">
                        {highlight.reward_text}
                    </span>
                </div>
                
                <h3 class="mt-3 text-lg font-black text-zinc-900 leading-tight line-clamp-2 uppercase">
                    {highlight.title}
                </h3>
                
                <p class="text-[10px] text-zinc-500 font-medium mt-2 line-clamp-2">
                    {highlight.description}
                </p>
            </div>

            <div class="relative z-10 pt-4 mt-auto flex justify-between items-end">
                <div class="flex flex-col">
                    <span class="text-[9px] font-bold text-zinc-400 uppercase">Applicants</span>
                    <span class="text-xs font-black text-zinc-800">👤 {highlight.applicant_count || 0}</span>
                </div>
                
                <div class="px-3 py-1.5 bg-yellow-400 text-black text-[9px] font-black uppercase rounded border border-black/10 group-hover:bg-yellow-300">
                    Apply ->
                </div>
            </div>
        </a>

    {:else if type === 'project'}
        <a href="/communities/{communityId}?tab=guild" class="block h-full bg-white border border-zinc-200 rounded-2xl p-1 shadow-sm group hover:border-blue-400 hover:shadow-md transition-all">
            <div class="h-full w-full bg-zinc-50 rounded-xl p-4 flex flex-col justify-between relative overflow-hidden">
                
                <div class="absolute -right-4 -top-4 text-9xl opacity-5 grayscale group-hover:grayscale-0 transition-all">
                    🔨
                </div>

                <div class="relative z-10">
                    <div class="flex justify-between items-center mb-2">
                        <span class="text-[9px] font-bold uppercase text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
                            Featured Build
                        </span>
                        <div class="text-[10px] font-bold text-zinc-400 border border-zinc-200 px-1.5 rounded bg-white">
                            ♥ {highlight.likes || 0}
                        </div>
                    </div>
                    <h3 class="text-xl font-black uppercase text-zinc-800 leading-none">
                        {highlight.title}
                    </h3>
                </div>

                <div class="relative z-10 mt-auto">
                    <div class="flex gap-1 flex-wrap mb-3">
                        {#if highlight.tech_stack}
                            {#each highlight.tech_stack.split(',').slice(0, 2) as tech}
                                <span class="text-[8px] font-bold uppercase border border-zinc-300 text-zinc-500 px-1 rounded">
                                    {tech}
                                </span>
                            {/each}
                        {/if}
                    </div>
                    <div class="text-[10px] font-bold text-zinc-500">
                        By <span class="text-black">{highlight.author_name}</span>
                    </div>
                </div>
            </div>
        </a>

    {:else}
        <div class="h-full bg-zinc-50 rounded-2xl border-2 border-dashed border-zinc-200 flex items-center justify-center flex-col text-zinc-400">
            <span class="text-2xl mb-1">⚒️</span>
            <span class="text-[10px] font-bold uppercase">Guild Quiet</span>
        </div>
    {/if}
</div>