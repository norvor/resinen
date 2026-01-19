<script lang="ts">
    import { page } from '$app/stores';
    import { onMount } from 'svelte';
    import { api, type User, type Community } from '$lib/api';
    import { 
        FEATURE_REGISTRY, 
        resolveFeatures, 
        ARCHETYPES, 
        getPrimaryArchetypeName, 
        getPrimaryArchetypeFocus 
    } from '$lib/config/archetypes';

    // State
    let slug = $page.params.slug;
    let community: Community | null = null;
    let currentUser: User | null = null;
    let membership: any = null;
    
    let activeFeatureId: string = '';
    let availableFeatures: string[] = [];
    let archetypeMeta: any = null;
    let loading = true;
    let error = "";

    onMount(async () => {
        try {
            const [userData, commData] = await Promise.all([
                api.getMe(),
                api.getCommunityBySlug(slug)
            ]);
            currentUser = userData;
            community = commData;

            if (community?.id) {
                try { membership = await api.getMembershipStatus(community.id); } catch(e) {}

                availableFeatures = resolveFeatures(community.archetypes);
                
                archetypeMeta = {
                    name: getPrimaryArchetypeName(community.archetypes),
                    focus: getPrimaryArchetypeFocus(community.archetypes)
                };

                if (availableFeatures.length > 0) activeFeatureId = availableFeatures[0];
            }
        } catch (e) {
            console.error(e);
            error = "Territory Unreachable.";
        } finally {
            loading = false;
        }
    });
</script>

<div class="pb-20">
    
    {#if loading}
        <div class="h-screen flex flex-col items-center justify-center text-center">
            <div class="text-4xl font-black uppercase animate-pulse mb-4 text-skin-accent">Loading Territory...</div>
        </div>

    {:else if community}

        <div class="relative bg-black text-white"> 
            <div class="h-64 w-full relative overflow-hidden opacity-60">
                <img 
                    src={community.banner_url || "https://images.unsplash.com/photo-1531297461136-82lw.jpg?q=80&w=2607&auto=format&fit=crop"} 
                    alt="Banner" 
                    class="w-full h-full object-cover"
                />
                <div class="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent"></div>
            </div>

            <div class="absolute -bottom-12 left-0 right-0 px-4 md:px-8 max-w-7xl mx-auto flex items-end justify-between">
                <div class="flex items-end gap-6">
                    <div class="w-32 h-32 bg-skin-accent border-4 border-skin-border shadow-hard flex items-center justify-center text-4xl font-black uppercase text-skin-fill shrink-0">
                        {community.name[0]}
                    </div>
                    
                    <div class="mb-4 text-shadow">
                        <h1 class="text-4xl md:text-6xl font-black uppercase leading-none tracking-tighter mb-1 text-white">
                            {community.name}
                        </h1>
                        <div class="flex items-center gap-3 text-sm font-bold uppercase tracking-widest text-gray-300">
                            <span class="text-skin-accent">{archetypeMeta?.name}</span>
                            <span class="w-1 h-1 bg-gray-500 rounded-full"></span>
                            <span>{community.member_count} Citizens</span>
                        </div>
                    </div>
                </div>

                <div class="hidden md:block mb-6">
                    {#if membership?.status === 'active'}
                        <button class="skin-btn-primary">
                            Manage Citizenship
                        </button>
                    {:else}
                         <button class="skin-btn-primary">
                            Apply For Visa
                        </button>
                    {/if}
                </div>
            </div>
        </div>

        <div class="h-16 bg-skin-surface border-b border-skin-border mb-8"></div>

        <div class="max-w-7xl mx-auto px-4 md:px-8 grid grid-cols-1 lg:grid-cols-4 gap-8">
            
            <div class="space-y-6">
                
                <div class="relative bg-skin-surface border-2 border-skin-border rounded-xl overflow-hidden shadow-hard group hover:-translate-y-1 transition-transform duration-300">
                    
                    <div class="h-2 w-full bg-skin-accent flex items-center px-2 gap-1">
                        <div class="w-1 h-1 bg-white rounded-full opacity-50"></div>
                        <div class="w-1 h-1 bg-white rounded-full opacity-50"></div>
                        <div class="w-10 h-1 bg-white rounded-full opacity-20 ml-auto"></div>
                    </div>

                    <div class="p-6 relative">
                        <div class="absolute inset-0 opacity-[0.03] pointer-events-none" 
                             style="background-image: radial-gradient(#000 1px, transparent 1px); background-size: 20px 20px;">
                        </div>

                        <div class="flex items-center justify-between mb-4 border-b border-skin-border/20 pb-4">
                            <h3 class="font-black uppercase text-sm tracking-widest text-skin-accent flex items-center gap-2">
                                <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                                Manifesto
                            </h3>
                            <span class="text-[10px] font-mono opacity-40">SYS.V.1.0</span>
                        </div>

                        <p class="text-sm font-medium text-skin-text leading-relaxed opacity-90 relative z-10">
                            {community.description || "No description provided."}
                        </p>

                        <div class="mt-6 grid grid-cols-2 gap-2">
                            <div class="bg-skin-muted/30 p-2 rounded border border-skin-border/10">
                                <div class="text-[10px] uppercase font-bold text-skin-accent opacity-70">Focus</div>
                                <div class="font-black text-xs">{archetypeMeta?.focus}</div>
                            </div>
                            <div class="bg-skin-muted/30 p-2 rounded border border-skin-border/10">
                                <div class="text-[10px] uppercase font-bold text-skin-accent opacity-70">Est.</div>
                                <div class="font-black text-xs">2026</div>
                            </div>
                        </div>
                    </div>

                    <div class="absolute bottom-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-skin-accent to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                </div>

                <div class="bg-skin-fill border border-skin-border rounded-lg p-4 flex items-center gap-4 opacity-80 hover:opacity-100 transition-opacity">
                    <div class="w-10 h-10 bg-skin-muted rounded-full flex items-center justify-center font-black text-skin-text text-xs">
                        OP
                    </div>
                    <div>
                        <div class="text-[10px] uppercase font-bold text-skin-accent">System Operator</div>
                        <div class="text-xs font-bold">{community.creator_id ? 'Architect' : 'Unknown'}</div>
                    </div>
                </div>

            </div>

            <div class="lg:col-span-3">
                
                <div class="flex overflow-x-auto gap-4 border-b border-skin-border mb-6 pb-2 scrollbar-hide">
                    {#each availableFeatures as featureKey}
                        {@const feature = FEATURE_REGISTRY[featureKey]}
                        {#if feature}
                            <button 
                                on:click={() => activeFeatureId = featureKey}
                                class="whitespace-nowrap font-black uppercase text-sm px-4 py-2 transition-colors border-2 
                                {activeFeatureId === featureKey 
                                    ? 'bg-skin-text text-skin-fill border-skin-text shadow-hard' 
                                    : 'bg-transparent text-skin-muted border-transparent hover:text-skin-text hover:bg-skin-surface/10'}"
                            >
                                <span class="mr-2">{feature.icon}</span>
                                {feature.label}
                            </button>
                        {/if}
                    {/each}
                </div>

                {#if activeFeatureId && FEATURE_REGISTRY[activeFeatureId]}
                    {@const FeatureDef = FEATURE_REGISTRY[activeFeatureId]}
                    <div class="min-h-[400px]">
                        <svelte:component 
                            this={FeatureDef.component} 
                            {community} 
                            {currentUser} 
                            {membership}
                            label={FeatureDef.label} 
                        />
                    </div>
                {/if}

            </div>
        </div>

    {:else}
        <div class="pt-20 text-center font-bold text-skin-accent">Signal Lost.</div>
    {/if}
</div>