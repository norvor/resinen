<script lang="ts">
    import { onMount } from 'svelte';
    import { api, user } from '$lib/api';

    let myCommunities: any[] = [];
    let loading = true;
    let searchQuery = '';

    onMount(async () => {
        try {
            // Fetch the territories I am a citizen of
            myCommunities = await api('GET', '/users/me/communities');
        } catch (e) {
            console.error(e);
        } finally {
            loading = false;
        }
    });

    function handleSearch() {
        if(searchQuery.trim()) {
            window.location.href = `/communities?q=${searchQuery}`;
        }
    }
</script>

<div class="max-w-6xl mx-auto p-4 md:p-8">
    
    <div class="flex justify-between items-end border-b-4 border-black pb-6 mb-8">
        <div>
            <h1 class="text-4xl md:text-5xl font-black uppercase tracking-tight">Home Base</h1>
            <p class="font-bold text-gray-500">Welcome back, Citizen.</p>
        </div>
        <a href="/communities/new" class="hidden md:block bg-black text-white px-6 py-3 font-black uppercase hover:bg-sp-green hover:text-black transition-colors shadow-hard">
            + Initialize Territory
        </a>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <div class="space-y-8">
            
            <div class="bg-white border-4 border-black p-6 shadow-hard relative overflow-hidden group">
                <div class="absolute top-0 right-0 bg-sp-yellow border-l-4 border-b-4 border-black px-3 py-1 font-black text-xs uppercase">
                    ID: {$user?.id.slice(0,8)}
                </div>

                <div class="flex flex-col items-center text-center mt-4">
                    <div class="w-32 h-32 bg-gray-200 border-4 border-black rounded-full overflow-hidden mb-4 relative">
                        <img src={$user?.avatar_url || 'https://api.dicebear.com/7.x/notionists/svg?seed=' + $user?.email} alt="Avatar" class="w-full h-full object-cover" />
                    </div>
                    
                    <h2 class="text-2xl font-black uppercase leading-none">{$user?.full_name}</h2>
                    <p class="font-mono text-sm text-gray-500 mt-1">{$user?.email}</p>
                    
                    <div class="flex gap-2 mt-4">
                        <span class="bg-black text-white px-3 py-1 font-bold text-xs uppercase">Level {$user?.level || 1}</span>
                        <span class="bg-gray-200 text-black border border-black px-3 py-1 font-bold text-xs uppercase">{$user?.reputation_score || 0} Rep</span>
                    </div>
                </div>

                <div class="mt-8 space-y-2">
                    <a href="/identity/{$user?.id}" class="block w-full text-center border-2 border-black py-2 font-bold uppercase text-xs hover:bg-black hover:text-white transition-colors">
                        View Public Passport
                    </a>
                    <a href="/settings" class="block w-full text-center border-2 border-black py-2 font-bold uppercase text-xs hover:bg-black hover:text-white transition-colors">
                        Edit Biometrics
                    </a>
                </div>
            </div>

            <div class="bg-sp-blue border-4 border-black p-6 shadow-hard text-white">
                <h3 class="font-black uppercase text-lg mb-4 border-b-2 border-white/20 pb-2">Status Report</h3>
                <ul class="space-y-2 text-sm font-bold">
                    <li class="flex justify-between">
                        <span>Jury Summons</span>
                        <span class="bg-white text-black px-2 rounded">0</span>
                    </li>
                    <li class="flex justify-between">
                        <span>Unread Alerts</span>
                        <span class="bg-white text-black px-2 rounded">0</span>
                    </li>
                </ul>
            </div>
        </div>

        <div class="lg:col-span-2">
            
            <div class="bg-white border-4 border-black p-2 shadow-hard mb-8 flex gap-2">
                <input 
                    bind:value={searchQuery}
                    on:keydown={(e) => e.key === 'Enter' && handleSearch()}
                    type="text" 
                    placeholder="Find a new territory to join..." 
                    class="flex-grow p-3 font-bold outline-none uppercase placeholder:normal-case"
                />
                <button on:click={handleSearch} class="bg-sp-orange px-6 font-black uppercase border-l-4 border-black hover:bg-sp-yellow transition-colors">
                    Search
                </button>
            </div>

            <h3 class="font-black text-xl uppercase mb-4 flex items-center gap-2">
                <span>My Territories</span>
                <div class="h-1 bg-black/10 flex-grow"></div>
            </h3>

            {#if loading}
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 animate-pulse">
                    <div class="h-40 bg-gray-200 border-4 border-black/20"></div>
                    <div class="h-40 bg-gray-200 border-4 border-black/20"></div>
                </div>
            {:else if myCommunities.length === 0}
                <div class="bg-gray-50 border-4 border-dashed border-gray-300 p-12 text-center">
                    <h4 class="font-black text-xl text-gray-400 mb-2">No Allegiances Yet</h4>
                    <p class="font-bold text-gray-500 mb-6">You are a nomad. Join a territory to settle down.</p>
                    <a href="/communities" class="inline-block bg-black text-white px-6 py-3 font-black uppercase hover:scale-105 transition-transform">
                        Explore The Map
                    </a>
                </div>
            {:else}
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {#each myCommunities as community}
                        <a href="/communities/{community.slug}" class="bg-white border-4 border-black p-6 shadow-hard hover:translate-x-1 hover:translate-y-1 transition-transform group relative">
                            <div class="absolute top-4 right-4 w-3 h-3 bg-green-500 border-2 border-black rounded-full"></div>

                            <div class="flex items-center gap-4 mb-4">
                                <div class="w-12 h-12 bg-sp-purple border-2 border-black flex items-center justify-center font-black text-white text-xl uppercase">
                                    {community.name.slice(0,1)}
                                </div>
                                <div>
                                    <h4 class="font-black text-lg uppercase leading-none group-hover:text-sp-blue transition-colors">
                                        {community.name}
                                    </h4>
                                    <span class="text-xs font-mono text-gray-400">/{community.slug}</span>
                                </div>
                            </div>
                            
                            <p class="text-sm font-bold text-gray-600 line-clamp-2 mb-4 h-10">
                                {community.description || 'A sovereign territory on the network.'}
                            </p>

                            <div class="flex justify-between items-center pt-4 border-t-2 border-gray-100 text-xs font-black uppercase">
                                <span class="bg-gray-100 px-2 py-1 border border-black">{community.member_count} Citizens</span>
                                <span class="text-sp-blue group-hover:underline">Enter Territory &rarr;</span>
                            </div>
                        </a>
                    {/each}
                </div>
            {/if}

        </div>

    </div>
</div>