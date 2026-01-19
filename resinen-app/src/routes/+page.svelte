<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';

    let communities = [];
    let loading = true;

    onMount(async () => {
        try {
            communities = await api.getCommunities();
        } finally {
            loading = false;
        }
    });
</script>

<div class="max-w-6xl mx-auto">
    <div class="mb-12">
        <h1 class="text-5xl font-black uppercase tracking-tighter mb-2 italic">Dashboard</h1>
        <p class="text-skin-muted font-mono text-sm tracking-tight">Welcome back, Operator. Select a territory to begin deployment.</p>
    </div>

    {#if loading}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each Array(6) as _}
                <div class="h-48 bg-skin-surface animate-pulse border border-skin-border"></div>
            {/each}
        </div>
    {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each communities as c}
                <a href="/c/{c.slug}" class="skin-card p-6 flex flex-col justify-between group hover:-translate-y-1 transition-all">
                    <div>
                        <div class="flex justify-between items-start mb-4">
                            <div class="px-2 py-1 bg-skin-accent/10 text-skin-accent text-[10px] font-black uppercase tracking-widest border border-skin-accent/20">
                                {c.archetypes[0]}
                            </div>
                            <span class="text-xs font-bold text-skin-muted">👥 {c.member_count}</span>
                        </div>
                        <h2 class="text-2xl font-black uppercase leading-none mb-2 group-hover:text-skin-accent transition-colors">
                            {c.name}
                        </h2>
                        <p class="text-sm text-skin-muted line-clamp-2 leading-relaxed">{c.description}</p>
                    </div>
                    
                    <div class="mt-6 flex items-center justify-between">
                        <span class="text-[10px] font-mono font-bold uppercase text-skin-muted">STATUS: ACTIVE</span>
                        <span class="text-xs font-black uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-opacity">Enter →</span>
                    </div>
                </a>
            {/each}
        </div>
    {/if}
</div>