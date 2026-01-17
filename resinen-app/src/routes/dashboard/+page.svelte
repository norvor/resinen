<script lang="ts">
    import { onMount } from 'svelte';
    import { user, getEngines } from '$lib/api';

    // State for Dynamic Data
    let engines: any[] = [];
    let loading = true;

    onMount(async () => {
        engines = await getEngines();
        loading = false;
    });
</script>

<div class="flex flex-col md:flex-row justify-between items-end mb-12 border-b-4 border-black pb-4 gap-4">
    <div>
        <h2 class="text-4xl font-black uppercase">Command Center</h2>
        <p class="font-bold text-gray-600">
            Welcome back, <span class="text-sp-blue">{$user?.full_name || 'Operator'}</span>.
        </p>
    </div>
    
    <div class="bg-black text-white px-4 py-2 font-mono font-bold text-xs uppercase tracking-widest rounded">
        System: <span class="text-sp-green">ONLINE</span>
    </div>
</div>

<div class="grid grid-cols-1 md:grid-cols-3 gap-8">
    
    <div class="bg-white p-6 border-4 border-black shadow-hard transform rotate-1 h-fit">
        <h3 class="font-black text-xl uppercase mb-4 border-b-2 border-black pb-2">My Identity</h3>
        <div class="space-y-6">
            <div class="text-center">
                <div class="w-20 h-20 bg-sp-yellow border-4 border-black rounded-full mx-auto flex items-center justify-center text-3xl font-black mb-2">
                    {$user?.full_name?.charAt(0)}
                </div>
                <div class="font-bold text-sm text-gray-500 uppercase">{$user?.email}</div>
            </div>

            <div class="space-y-2">
                <div class="flex justify-between items-center text-sm font-bold">
                    <span>Reputation</span>
                    <span>Level 1</span>
                </div>
                <div class="w-full bg-gray-200 h-3 border-2 border-black rounded-full overflow-hidden">
                    <div class="bg-sp-cyan h-full w-[25%]"></div>
                </div>
            </div>
        </div>
    </div>

    <div class="md:col-span-2 space-y-6">
        <h3 class="font-black text-xl uppercase text-gray-500 flex items-center gap-2">
            <span>Installed Modules</span>
            <div class="flex-grow h-1 bg-black/10"></div>
        </h3>

        {#if loading}
            <div class="p-12 border-4 border-dashed border-black/20 text-center font-bold text-gray-400 animate-pulse">
                SYNCING WITH CODEX...
            </div>
        {:else if engines.length > 0}
            <div class="grid grid-cols-1 gap-6">
                {#each engines as engine}
                    <div class="bg-sp-paper border-4 border-black p-6 shadow-hard hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-hard-sm transition-all group cursor-pointer relative overflow-hidden">
                        
                        <div class="absolute left-0 top-0 bottom-0 w-4 border-r-4 border-black
                            {engine.id.includes('talent') ? 'bg-sp-red' : 
                             engine.id.includes('governance') ? 'bg-sp-green' : 'bg-sp-orange'}">
                        </div>

                        <div class="ml-6">
                            <div class="flex justify-between items-start mb-2">
                                <h4 class="text-2xl font-black uppercase">{engine.name}</h4>
                                <span class="text-xs font-black bg-black text-white px-2 py-1 uppercase">{engine.category}</span>
                            </div>
                            
                            <p class="font-bold text-gray-600 mb-4 line-clamp-2">
                                {engine.description}
                            </p>

                            <div class="grid grid-cols-2 gap-2 mt-4">
                                {#each engine.modules as mod}
                                    <div class="bg-white border-2 border-black p-2 text-xs font-bold uppercase flex items-center gap-2">
                                        <div class="w-2 h-2 bg-black rounded-full"></div>
                                        {mod.title}
                                    </div>
                                {/each}
                            </div>
                        </div>
                    </div>
                {/each}
            </div>
        {:else}
            <div class="bg-sp-red text-white p-6 border-4 border-black shadow-hard">
                <h3 class="font-black text-xl">CONNECTION LOST</h3>
                <p class="font-bold">Could not fetch engines from Codex. Is the backend running?</p>
            </div>
        {/if}
    </div>

</div>