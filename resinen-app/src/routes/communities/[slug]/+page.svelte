<script lang="ts">
    import { getContext } from 'svelte';
    import { type Writable } from 'svelte/store';
    import { api, currentUser } from '$lib/api';
    import type { Community, Membership } from '$lib/types';
    import { 
        FEATURE_REGISTRY, 
        resolveFeatures, 
        getPrimaryArchetypeName, 
        getPrimaryArchetypeFocus 
    } from '$lib/config/archetypes';
    import { fly } from 'svelte/transition';

    // --- CONTEXT ---
    // We grab the stores provided by the +layout.svelte "Airlock"
    const communityStore = getContext<Writable<Community | null>>('community');
    const membershipStore = getContext<Writable<Membership | null>>('membership');

    // --- STATE ---
    // Reactive variables that auto-update when the stores change
    $: community = $communityStore;
    $: membership = $membershipStore;
    $: user = $currentUser;

    let activeFeatureId: string = '';
    let availableFeatures: string[] = [];
    let archetypeMeta: any = null;
    let joining = false;
    let error = "";
    let rotation = 'rotate-1'; // Visual fluff

    // --- LOGIC ---
    // When the community loads (or changes), calculate the active engines
    $: if (community) {
        initCommunity(community);
    }

    function initCommunity(c: Community) {
        rotation = Math.random() > 0.5 ? 'rotate-1' : '-rotate-1';

        // 🚨 FIX: Read 'installed_engines' from the backend response
        // The backend sends ['social', 'arena', 'listings'], NOT 'archetypes'
        const engines = (c as any).installed_engines || [];

        // 1. Resolve features using the correct list
        availableFeatures = resolveFeatures(engines);
        
        archetypeMeta = {
            name: getPrimaryArchetypeName(engines),
            focus: getPrimaryArchetypeFocus(engines)
        };

        // 2. Open first tab
        if (!activeFeatureId && availableFeatures.length > 0) {
            activeFeatureId = availableFeatures[0];
        }
    }

    async function handleJoin() {
        if (!community) return;
        joining = true;
        try {
            await api.joinCommunity(community.id);
            
            // Refresh membership status and update the store
            // This will instantly flip the UI from "Join" to "Citizen"
            const newStatus = await api.getMembershipStatus(community.id);
            membershipStore.set(newStatus);
            
        } catch (e) {
            console.error("Join failed", e);
            alert("Application Rejected: System Error.");
        } finally {
            joining = false;
        }
    }

    function getTabColor(isActive: boolean) {
        return isActive 
            ? 'bg-white text-black border-b-white translate-y-[2px] z-20' 
            : 'bg-gray-100 text-gray-500 hover:bg-gray-50 hover:text-black z-10';
    }
</script>

<div class="min-h-screen pb-40 p-4 md:p-8 overflow-x-hidden">
    
    {#if !community}
        <div class="h-[60vh] flex flex-col items-center justify-center text-center">
            <div class="w-20 h-24 bg-white border-2 border-black shadow-[4px_4px_0px_black] animate-[spin_3s_linear_infinite] mb-8 relative">
                <div class="absolute inset-0 flex items-center justify-center font-black text-2xl">?</div>
            </div>
            <div class="text-2xl font-black uppercase animate-bounce text-gray-400">Unlocking Door...</div>
        </div>

    {:else}

        <div class="relative mb-12 mt-4 max-w-5xl mx-auto" in:fly={{ y: -20, duration: 800 }}>
            <div class="bg-blue-600 text-white p-8 md:p-12 border-4 border-black shadow-[8px_8px_0px_rgba(0,0,0,0.2)] transform {rotation} relative overflow-hidden group">
                
                <div class="absolute -top-6 left-1/4 w-12 h-20 bg-white/30 rotate-3 border-x-2 border-white/20 shadow-sm backdrop-blur-sm z-20"></div>
                <div class="absolute -top-6 right-1/4 w-12 h-20 bg-white/30 -rotate-2 border-x-2 border-white/20 shadow-sm backdrop-blur-sm z-20"></div>

                <div class="relative z-10 flex flex-col md:flex-row items-start md:items-end justify-between gap-6">
                    <div>
                        <div class="flex items-center gap-3 mb-2">
                            <span class="bg-black text-white text-[10px] font-black uppercase px-2 py-1 transform -rotate-2 border border-white/20">
                                {archetypeMeta?.name || 'Community'}
                            </span>
                            <span class="text-xs font-bold uppercase tracking-widest text-blue-200">
                                Est. 2026
                            </span>
                        </div>
                        <h1 class="text-5xl md:text-7xl font-black uppercase leading-none tracking-tighter text-shadow-sm">
                            {community.name}
                        </h1>
                    </div>

                    <div class="shrink-0">
                        {#if membership?.status === 'active' || membership?.role === 'admin' || membership?.role === 'owner'}
                            <div class="w-24 h-24 bg-green-400 rounded-full border-4 border-black flex items-center justify-center transform rotate-12 shadow-sm group-hover:rotate-[360deg] transition-transform duration-700">
                                <span class="font-black text-black uppercase -rotate-12 text-sm">Citizen</span>
                            </div>
                        {:else if membership?.status === 'pending'}
                            <div class="w-24 h-24 bg-yellow-400 rounded-full border-4 border-black flex items-center justify-center transform -rotate-6 shadow-sm">
                                <span class="font-black text-black uppercase rotate-6 text-sm text-center leading-none">Under<br>Review</span>
                            </div>
                        {:else}
                             <button 
                                on:click={handleJoin}
                                disabled={joining}
                                class="bg-white text-black text-sm font-black uppercase px-8 py-4 border-4 border-black shadow-[4px_4px_0px_black] hover:translate-y-1 hover:shadow-[2px_2px_0px_black] transition-all hover:bg-yellow-300 disabled:opacity-50 disabled:cursor-not-allowed">
                                {#if joining}
                                    Stamping...
                                {:else}
                                    Join Club
                                {/if}
                            </button>
                        {/if}
                    </div>
                </div>

                <div class="absolute inset-0 opacity-10 pointer-events-none" 
                     style="background-image: radial-gradient(#000 2px, transparent 2px); background-size: 10px 10px;">
                </div>
            </div>
        </div>

        <div class="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-4 gap-8 items-start">
            
            <div class="lg:col-span-1 space-y-8" in:fly={{ x: -20, duration: 800, delay: 200 }}>
                <div class="bg-yellow-100 border-2 border-black p-6 shadow-[4px_4px_0px_rgba(0,0,0,0.1)] relative transform -rotate-1 hover:rotate-0 transition-transform">
                    <div class="absolute -top-3 left-1/2 -translate-x-1/2 w-4 h-4 rounded-full bg-red-500 border-2 border-black shadow-sm z-20">
                        <div class="absolute top-1 left-1 w-1 h-1 bg-white opacity-40 rounded-full"></div>
                    </div>
                    
                    <h3 class="font-black uppercase text-sm mb-4 border-b-2 border-black pb-2 text-center tracking-widest">Manifesto</h3>
                    
                    <p class="font-mono text-xs font-bold text-gray-800 leading-relaxed whitespace-pre-wrap">
                        {community.description || "1. Have fun.\n2. Be cool.\n3. No running in the halls."}
                    </p>

                    <div class="mt-4 pt-4 border-t-2 border-dashed border-black/20 flex justify-between items-center text-[10px] font-black uppercase text-gray-500">
                        <span>Pop: {(community as any).member_count ?? (community as any)._count?.members ?? 0}</span>
                        <span>{(community as any).creator_id ? 'Architect' : 'Anon'}</span>
                    </div>
                </div>
            </div>

            <div class="lg:col-span-3" in:fly={{ x: 20, duration: 800, delay: 400 }}>
                
                <div class="flex flex-wrap gap-1 px-4 relative z-10 -mb-[2px]">
                    {#each availableFeatures as featureKey}
                        {@const feature = FEATURE_REGISTRY[featureKey]}
                        {#if feature}
                            <button 
                                on:click={() => activeFeatureId = featureKey}
                                class="px-6 py-3 font-black uppercase text-xs border-2 border-black rounded-t-lg transition-all relative {getTabColor(activeFeatureId === featureKey)}"
                            >
                                <span class="mr-2">{feature.icon}</span>
                                {feature.label}
                            </button>
                        {/if}
                    {/each}
                </div>

                <div class="bg-white border-2 border-black p-0 min-h-[500px] shadow-[8px_8px_0px_rgba(0,0,0,0.1)] relative z-0 rounded-b-xl rounded-tr-xl overflow-hidden">
                    
                    {#if activeFeatureId && FEATURE_REGISTRY[activeFeatureId]}
                        {@const FeatureDef = FEATURE_REGISTRY[activeFeatureId]}
                        
                        <div class="p-6 md:p-8">
                            <svelte:component 
                                this={FeatureDef.component} 
                                {community} 
                                currentUser={user} 
                                {membership}
                                label={FeatureDef.label} 
                            />
                        </div>

                    {:else}
                         <div class="h-full flex flex-col items-center justify-center p-20 opacity-50">
                            <div class="text-4xl mb-4">📂</div>
                            <div class="font-black uppercase text-gray-400">Select a File</div>
                         </div>
                    {/if}

                </div>

            </div>
        </div>

    {/if}
</div>