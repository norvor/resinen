<script lang="ts">
    import { page } from '$app/stores';
    import { onMount } from 'svelte';
    import { api, type Post, type User } from '$lib/api';
    import PostCard from '$lib/components/PostCard.svelte'; 

    // --- STATE ---
    let slug = $page.params.slug; 
    let community: any = null;
    let posts: Post[] = [];
    let currentUser: User | null = null;
    let membership: any = null;
    
    let activeTab = 'town-square'; // Default View
    let newPostContent = "";
    let isPosting = false;
    let loading = true;
    let error = "";

    // --- MOCK DATA (For the "Final Product" feel until backend is ready) ---
    const MOCK_STATS = {
        treasury: "42,000 $RES",
        tax_rate: "5%",
        jury_cases: 3,
        active_quests: 12
    };

    onMount(async () => {
        try {
            // 1. Parallel Data Fetching
            const [userData, commData] = await Promise.all([
                api.getMe(),
                api.getCommunityBySlug(slug)
            ]);
            currentUser = userData;
            community = commData;

            // 2. Fetch Dependent Data
            if (community?.id) {
                // Get my relationship to this land
                // (We try/catch this silently in case user isn't logged in/member)
                try {
                     const memData = await api.request('GET', `/communities/${community.id}/membership_status`);
                     membership = memData;
                } catch(e) {}

                // Get the feed
                posts = await api.getFeed(community.id);
            }

        } catch (e: any) {
            console.error(e);
            error = "Territory Unreachable. Check frequency.";
        } finally {
            loading = false;
        }
    });

    async function handleCreatePost() {
        if (!newPostContent.trim() || !community?.id) return;
        isPosting = true;
        try {
            await api.createPost(community.id, newPostContent);
            newPostContent = "";
            posts = await api.getFeed(community.id); 
        } catch (e) {
            alert("Broadcast failed.");
        } finally {
            isPosting = false;
        }
    }
</script>

<div class="min-h-screen bg-gray-100 pb-20">
    
    {#if loading}
        <div class="h-screen flex flex-col items-center justify-center text-center">
            <div class="text-4xl font-black uppercase animate-pulse mb-4">Establishing Uplink...</div>
            <div class="font-mono text-sm text-gray-500">Decrypting Territory Data</div>
        </div>

    {:else if error}
        <div class="pt-20 text-center text-red-600 font-black uppercase text-xl">{error}</div>

    {:else if community}

        <div class="relative bg-black text-white">
            <div class="h-64 w-full relative overflow-hidden opacity-60">
                <img 
                    src={community.banner_url || "https://images.unsplash.com/photo-1531297461136-82lw.jpg?q=80&w=2607&auto=format&fit=crop"} 
                    alt="Territory Banner" 
                    class="w-full h-full object-cover"
                />
                <div class="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent"></div>
            </div>

            <div class="absolute -bottom-12 left-0 right-0 px-4 md:px-8 max-w-7xl mx-auto flex items-end justify-between">
                <div class="flex items-end gap-6">
                    <div class="w-32 h-32 bg-sp-blue border-4 border-black shadow-hard flex items-center justify-center text-4xl font-black uppercase text-white shrink-0">
                        {community.name[0]}
                    </div>
                    
                    <div class="mb-4 text-shadow">
                        <h1 class="text-4xl md:text-6xl font-black uppercase leading-none tracking-tighter mb-1">
                            {community.name}
                        </h1>
                        <div class="flex items-center gap-3 text-sm font-bold uppercase tracking-widest text-gray-300">
                            <span>/{community.slug}</span>
                            <span class="w-1 h-1 bg-gray-500 rounded-full"></span>
                            <span>{community.member_count} Citizens</span>
                            <span class="w-1 h-1 bg-gray-500 rounded-full"></span>
                            <span class="text-green-400">Online</span>
                        </div>
                    </div>
                </div>

                <div class="hidden md:block mb-6">
                    {#if membership?.status === 'active'}
                        <button class="bg-white text-black font-black uppercase py-3 px-8 border-4 border-black shadow-hard hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-none transition-all">
                            Manage Citizenship
                        </button>
                    {:else if membership?.status === 'pending'}
                        <button disabled class="bg-gray-300 text-gray-500 font-black uppercase py-3 px-8 border-4 border-black cursor-not-allowed">
                            Visa Pending
                        </button>
                    {:else}
                         <button class="bg-sp-green text-black font-black uppercase py-3 px-8 border-4 border-black shadow-hard hover:bg-white transition-colors">
                            Apply For Visa
                        </button>
                    {/if}
                </div>
            </div>
        </div>

        <div class="h-16 bg-white border-b-4 border-black mb-8"></div>

        <div class="max-w-7xl mx-auto px-4 md:px-8 grid grid-cols-1 lg:grid-cols-4 gap-8">
            
            <div class="space-y-6">
                
                <div class="bg-white border-4 border-black p-6 shadow-hard">
                    <h3 class="font-black uppercase text-lg mb-2">Manifesto</h3>
                    <p class="text-sm font-bold text-gray-600 leading-relaxed mb-4">
                        {community.description || "No description provided for this sovereign territory."}
                    </p>
                    <div class="flex flex-wrap gap-2">
                        <span class="bg-gray-100 text-xs font-black uppercase px-2 py-1 border border-black">
                            {community.is_private ? 'Restricted Access' : 'Public Domain'}
                        </span>
                        <span class="bg-gray-100 text-xs font-black uppercase px-2 py-1 border border-black">
                            Est. {new Date(community.created_at).getFullYear()}
                        </span>
                    </div>
                </div>

                <div class="bg-sp-yellow border-4 border-black p-6 shadow-hard">
                    <h3 class="font-black uppercase text-lg mb-4 border-b-2 border-black pb-2">Territory Stats</h3>
                    <ul class="space-y-3 font-bold text-sm">
                        <li class="flex justify-between">
                            <span>Treasury</span>
                            <span class="font-mono">{MOCK_STATS.treasury}</span>
                        </li>
                        <li class="flex justify-between">
                            <span>Tax Rate</span>
                            <span class="font-mono">{MOCK_STATS.tax_rate}</span>
                        </li>
                        <li class="flex justify-between">
                            <span>Open Cases</span>
                            <span class="bg-black text-white px-2 rounded-full text-xs flex items-center">{MOCK_STATS.jury_cases}</span>
                        </li>
                    </ul>
                </div>

                <div>
                    <h3 class="font-black uppercase text-sm text-gray-400 mb-2">Gatekeepers</h3>
                    <div class="flex gap-2">
                        <div class="w-10 h-10 bg-black border-2 border-white outline outline-2 outline-black"></div>
                        <div class="w-10 h-10 bg-gray-300 border-2 border-white outline outline-2 outline-black"></div>
                        <div class="w-10 h-10 bg-gray-300 border-2 border-white outline outline-2 outline-black"></div>
                    </div>
                </div>

            </div>

            <div class="lg:col-span-3">
                
                <div class="flex overflow-x-auto gap-4 border-b-4 border-gray-200 mb-6 pb-2 scrollbar-hide">
                    <button 
                        on:click={() => activeTab = 'town-square'}
                        class="whitespace-nowrap font-black uppercase text-sm px-4 py-2 transition-colors {activeTab === 'town-square' ? 'text-black bg-sp-cyan border-4 border-black shadow-hard-sm' : 'text-gray-400 hover:text-black'}"
                    >
                        Town Square
                    </button>
                    <button 
                        on:click={() => activeTab = 'academy'}
                        class="whitespace-nowrap font-black uppercase text-sm px-4 py-2 transition-colors {activeTab === 'academy' ? 'text-black bg-sp-purple border-4 border-black shadow-hard-sm' : 'text-gray-400 hover:text-black'}"
                    >
                        Academy (3)
                    </button>
                    <button 
                        class="whitespace-nowrap font-black uppercase text-sm px-4 py-2 text-gray-300 cursor-not-allowed flex items-center gap-2"
                    >
                        Governance 🔒
                    </button>
                    <button 
                        class="whitespace-nowrap font-black uppercase text-sm px-4 py-2 text-gray-300 cursor-not-allowed flex items-center gap-2"
                    >
                        Treasury 🔒
                    </button>
                </div>

                {#if activeTab === 'town-square'}
                    
                    {#if membership?.status === 'active'}
                        <div class="bg-white border-4 border-black p-4 mb-8 shadow-hard relative z-10">
                            <div class="flex gap-4">
                                <div class="w-12 h-12 bg-black shrink-0">
                                    <div class="w-full h-full flex items-center justify-center text-white font-black text-xl">
                                        {currentUser?.full_name[0] || '?'}
                                    </div>
                                </div>
                                <textarea 
                                    bind:value={newPostContent}
                                    placeholder="Broadcast to the {community.name} network..."
                                    class="w-full bg-transparent border-none focus:ring-0 text-lg font-bold resize-none h-24 placeholder:text-gray-300 placeholder:uppercase"
                                ></textarea>
                            </div>
                            <div class="flex justify-between items-center mt-2 pt-4 border-t-2 border-gray-100">
                                <div class="text-xs font-bold text-gray-400 uppercase">Markdown Supported</div>
                                <button 
                                    on:click={handleCreatePost}
                                    disabled={!newPostContent || isPosting}
                                    class="bg-black text-white font-black uppercase py-2 px-6 hover:bg-sp-blue hover:text-white transition-colors disabled:opacity-50"
                                >
                                    {isPosting ? 'Transmitting...' : 'Broadcast'}
                                </button>
                            </div>
                        </div>
                    {:else}
                         <div class="bg-gray-100 border-2 border-dashed border-gray-300 p-6 text-center mb-8">
                            <p class="font-bold text-gray-500">You must be a citizen to broadcast in the Town Square.</p>
                         </div>
                    {/if}

                    <div class="space-y-6">
                        {#each posts as post (post.id)}
                            <PostCard {post} {currentUser} />
                        {:else}
                            <div class="text-center py-12">
                                <div class="text-4xl mb-4">🔇</div>
                                <h3 class="font-black uppercase text-gray-400">Radio Silence</h3>
                                <p class="text-gray-500">No broadcasts yet. Be the first voice.</p>
                            </div>
                        {/each}
                    </div>

                {/if}

                {#if activeTab === 'academy'}
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div class="bg-white border-4 border-black p-6 shadow-hard group hover:-translate-y-1 transition-transform cursor-pointer">
                            <div class="text-xs font-black text-sp-purple uppercase mb-2">Initiation • Level 1</div>
                            <h3 class="text-xl font-black uppercase mb-2">The Founding Principles</h3>
                            <p class="text-sm text-gray-600 font-bold mb-4">Learn the core laws of {community.name} to earn your Citizenship Badge.</p>
                            <div class="w-full bg-gray-200 h-2 border-2 border-black">
                                <div class="bg-sp-purple h-full w-0"></div>
                            </div>
                            <div class="mt-4 text-right">
                                <span class="bg-black text-white text-xs font-black uppercase px-3 py-1"><a href="/communities/{slug}/journey/1">Start Journey &rarr;</a></span>
                            </div>
                        </div>
                        
                         <div class="bg-gray-100 border-4 border-gray-300 p-6 flex items-center justify-center text-center">
                            <div>
                                <h3 class="text-lg font-black uppercase text-gray-400">Advanced Economics</h3>
                                <p class="text-xs font-bold text-gray-400 uppercase mt-1">Locked (Req. Level 5)</p>
                            </div>
                        </div>
                    </div>
                {/if}

            </div>
        </div>

    {:else}
        <div class="pt-20 text-center font-bold">Signal Lost.</div>
    {/if}
</div>