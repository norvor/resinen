<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    export let community: any;

    let activeTab: 'projects' | 'bounties' = 'projects';
    let projects: any[] = [];
    let bounties: any[] = [];
    let loading = true;

    onMount(async () => {
        try {
            // Load both concurrently
            const [p, b] = await Promise.all([
                api.getProjects(community.id),
                api.getBounties(community.id)
            ]);
            projects = p;
            bounties = b;
        } catch (e) {
            console.error(e);
        } finally {
            loading = false;
        }
    });
</script>

<div class="space-y-6">
    <div class="flex border-b border-skin-border">
        <button 
            on:click={() => activeTab = 'projects'}
            class="px-6 py-3 text-sm font-black uppercase tracking-wide border-b-2 transition-colors
            {activeTab === 'projects' ? 'border-skin-accent text-skin-text' : 'border-transparent text-skin-muted hover:text-skin-text'}"
        >
            Showcase ({projects.length})
        </button>
        <button 
            on:click={() => activeTab = 'bounties'}
            class="px-6 py-3 text-sm font-black uppercase tracking-wide border-b-2 transition-colors
            {activeTab === 'bounties' ? 'border-skin-accent text-skin-text' : 'border-transparent text-skin-muted hover:text-skin-text'}"
        >
            Bounties ({bounties.length})
        </button>
    </div>

    {#if loading}
        <div class="p-12 text-center animate-pulse text-skin-muted font-bold uppercase">Loading Guild Data...</div>
    {:else}
        
        {#if activeTab === 'projects'}
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                {#each projects as p}
                    <div class="skin-card p-6 flex flex-col group hover:border-skin-accent transition-colors">
                        <div class="flex items-start justify-between mb-2">
                            <h3 class="text-xl font-black uppercase text-skin-text">{p.title}</h3>
                            <div class="text-xs font-bold text-skin-muted border border-skin-border px-2 py-0.5 rounded">
                                ♥ {p.likes}
                            </div>
                        </div>
                        
                        <p class="text-sm opacity-70 mb-4 flex-1">{p.description}</p>
                        
                        {#if p.tech_stack}
                            <div class="flex flex-wrap gap-2 mb-4">
                                {#each p.tech_stack.split(',') as tech}
                                    <span class="text-[10px] font-bold uppercase bg-skin-surface text-skin-muted px-2 py-1 rounded">
                                        {tech.trim()}
                                    </span>
                                {/each}
                            </div>
                        {/if}

                        <div class="flex gap-2 mt-auto pt-4 border-t border-skin-border/50">
                            {#if p.repo_url}
                                <a href={p.repo_url} target="_blank" class="flex-1 text-center py-2 border border-skin-border text-xs font-bold uppercase hover:bg-skin-surface">
                                    Code
                                </a>
                            {/if}
                            {#if p.demo_url}
                                <a href={p.demo_url} target="_blank" class="flex-1 text-center py-2 bg-skin-text text-skin-fill text-xs font-bold uppercase hover:opacity-90">
                                    Demo
                                </a>
                            {/if}
                        </div>
                        
                        <div class="mt-3 text-[10px] text-skin-muted flex items-center gap-2">
                            <span>Built by</span>
                            <span class="font-bold text-skin-text">{p.author_name}</span>
                        </div>
                    </div>
                {/each}

                {#if projects.length === 0}
                    <div class="col-span-full py-12 text-center border-2 border-dashed border-skin-border rounded-xl">
                        <div class="text-4xl mb-2">🔨</div>
                        <div class="font-bold text-skin-muted uppercase tracking-widest text-xs">No Projects Shipped Yet</div>
                    </div>
                {/if}
            </div>
        {/if}

        {#if activeTab === 'bounties'}
            <div class="space-y-4">
                {#each bounties as b}
                    <div class="skin-card p-4 flex flex-col md:flex-row gap-6 items-center group">
                        <div class="shrink-0 text-center w-full md:w-32 bg-green-500/10 border border-green-500/30 p-3 rounded-lg">
                            <div class="text-green-600 font-black text-lg leading-none">{b.reward_text}</div>
                            <div class="text-[10px] font-bold text-green-700/70 uppercase mt-1">Reward</div>
                        </div>

                        <div class="flex-1 text-center md:text-left">
                            <h3 class="text-lg font-black uppercase text-skin-text">{b.title}</h3>
                            <p class="text-sm opacity-70 line-clamp-2">{b.description}</p>
                            <div class="flex items-center justify-center md:justify-start gap-4 mt-2 text-xs font-bold text-skin-muted">
                                <span>Posted by {b.author_name}</span>
                                <span>•</span>
                                <span>{new Date(b.created_at).toLocaleDateString()}</span>
                            </div>
                        </div>

                        <div class="shrink-0 w-full md:w-auto">
                            <button class="w-full md:w-auto px-6 py-3 bg-skin-surface border border-skin-border hover:bg-skin-accent hover:text-white hover:border-skin-accent transition-all text-xs font-black uppercase rounded shadow-sm">
                                Apply Now
                            </button>
                            <div class="text-[10px] text-center mt-1 text-skin-muted font-bold">
                                {b.applicant_count} Applicants
                            </div>
                        </div>
                    </div>
                {/each}

                {#if bounties.length === 0}
                    <div class="py-12 text-center border-2 border-dashed border-skin-border rounded-xl">
                        <div class="text-4xl mb-2">💰</div>
                        <div class="font-bold text-skin-muted uppercase tracking-widest text-xs">No Open Bounties</div>
                    </div>
                {/if}
            </div>
        {/if}

    {/if}
</div>