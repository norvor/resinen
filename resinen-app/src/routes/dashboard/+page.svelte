<script lang="ts">
    import { onMount } from 'svelte';
    import { api, user } from '$lib/api';

    let engines: any[] = [];
    let loading = true;

    // GAMIFICATION MATH
    $: currentXp = $user?.xp || 0;
    $: currentLevel = $user?.level || 1;
    // Reverse the formula: XP needed = (Level / 0.1)^2
    $: nextLevelXp = Math.pow((currentLevel) / 0.1, 2); 
    $: prevLevelXp = Math.pow((currentLevel - 1) / 0.1, 2);
    // Calculate percentage for the bar
    $: progressPercent = ((currentXp - prevLevelXp) / (nextLevelXp - prevLevelXp)) * 100;

    onMount(async () => {
        try {
            // Get available engines (Academic, Social, etc.)
            engines = await api('GET', '/engines/my-installed');
        } catch (e) {
            console.error(e);
        } finally {
            loading = false;
        }
    });
</script>

<div class="max-w-4xl mx-auto space-y-8">
    
    <div class="flex justify-between items-center border-b-4 border-black pb-4">
        <div>
            <h1 class="text-4xl font-black uppercase tracking-tight">Command Center</h1>
            <p class="font-mono text-sm text-gray-500">System: <span class="text-green-600 font-bold">ONLINE</span></p>
        </div>
        <div class="bg-black text-white px-4 py-2 font-black rotate-2 shadow-hard">
            v1.0.0
        </div>
    </div>

    <div class="bg-white border-4 border-black p-6 shadow-hard flex flex-col md:flex-row gap-6 items-center">
        
        <div class="relative">
            <div class="w-24 h-24 bg-gray-200 border-4 border-black rounded-full overflow-hidden">
                <img src={$user?.avatar_url || 'https://api.dicebear.com/7.x/notionists/svg'} alt="Profile" />
            </div>
            <div class="absolute -bottom-2 -right-2 bg-sp-yellow border-4 border-black w-10 h-10 flex items-center justify-center font-black text-xl rounded-full shadow-sm z-10">
                {currentLevel}
            </div>
        </div>

        <div class="flex-grow w-full">
            <h2 class="text-3xl font-black uppercase">{$user?.full_name || 'Anonymous User'}</h2>
            <p class="font-mono text-gray-500 mb-4 uppercase">Citizen ID: {$user?.id?.slice(0,8) || 'Unknown'}</p>
            
            <div class="w-full bg-gray-200 border-4 border-black h-8 relative mt-2">
                <div 
                    class="bg-sp-green h-full border-r-4 border-black transition-all duration-500" 
                    style="width: {Math.max(progressPercent, 5)}%"
                ></div>
                <div class="absolute inset-0 flex items-center justify-center font-bold text-xs uppercase tracking-widest z-10 pointer-events-none">
                    {currentXp} / {Math.round(nextLevelXp)} XP
                </div>
            </div>
        </div>

        <div class="flex flex-col gap-2 w-full md:w-auto">
            <a href="/identity" class="bg-black text-white px-6 py-3 font-black uppercase text-center hover:bg-sp-cyan hover:text-black transition-colors border-2 border-transparent hover:border-black">
                View Passport
            </a>
            <div class="text-xs text-center font-bold text-gray-400">
                Reputation Score: {$user?.reputation_score}
            </div>
        </div>
    </div>

    <div>
        <h3 class="font-black text-xl uppercase mb-6 flex items-center gap-2">
            <span>Active Modules</span>
            <div class="h-1 bg-black/10 flex-grow"></div>
        </h3>

        {#if loading}
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 animate-pulse">
                <div class="h-32 bg-gray-200 border-4 border-black/20"></div>
                <div class="h-32 bg-gray-200 border-4 border-black/20"></div>
                <div class="h-32 bg-gray-200 border-4 border-black/20"></div>
            </div>
        {:else}
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <a href="/academy" class="bg-white border-4 border-black p-6 shadow-hard hover:translate-x-1 hover:translate-y-1 transition-transform group">
                    <div class="w-10 h-10 bg-sp-blue border-2 border-black mb-4 group-hover:bg-sp-yellow transition-colors"></div>
                    <h4 class="font-black text-lg uppercase">Academic Center</h4>
                    <p class="text-sm font-bold text-gray-500">Access Courses</p>
                </a>

                <a href="/governance" class="bg-white border-4 border-black p-6 shadow-hard hover:translate-x-1 hover:translate-y-1 transition-transform group">
                    <div class="w-10 h-10 bg-sp-red border-2 border-black mb-4 group-hover:bg-sp-yellow transition-colors"></div>
                    <h4 class="font-black text-lg uppercase">Governance</h4>
                    <p class="text-sm font-bold text-gray-500">Voting & Jury Duty</p>
                </a>

                <a href="/communities/my-feed" class="bg-white border-4 border-black p-6 shadow-hard hover:translate-x-1 hover:translate-y-1 transition-transform group">
                    <div class="w-10 h-10 bg-sp-cyan border-2 border-black mb-4 group-hover:bg-sp-yellow transition-colors"></div>
                    <h4 class="font-black text-lg uppercase">Town Square</h4>
                    <p class="text-sm font-bold text-gray-500">Global Feed</p>
                </a>
            </div>
        {/if}
    </div>
</div>