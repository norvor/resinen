<script lang="ts">
    import { page } from '$app/stores';
    import { onMount } from 'svelte';
    import { api, user } from '$lib/api';

    // State
    let slug = $page.params.slug;
    let community: any = null;
    let membership: any = { status: 'none' };
    let posts: any[] = [];
    
    let loading = true;
    let isJoining = false;

    // Composer
    let postTitle = '';
    let postBody = '';

    onMount(async () => {
        await loadTerritory();
    });

    async function loadTerritory() {
        try {
            // 1. Get Community Details
            community = await api('GET', `/communities/by-slug/${slug}`);
            
            // 2. Check My Status
            membership = await api('GET', `/communities/${community.id}/membership_status`);

            // 3. If Active, Load the Feed
            if (membership.status === 'active') {
                posts = await api('GET', `/social/feed?scope=community&community_id=${community.id}`);
            }
        } catch (e) {
            console.error(e);
        } finally {
            loading = false;
        }
    }

    async function handleJoin() {
        isJoining = true;
        try {
            const res = await api('POST', `/communities/${community.id}/join`);
            if (res.status === 'active') {
                alert('Welcome, Citizen. You have entered the territory.');
                await loadTerritory(); // Reload to show feed
            } else {
                alert('Application Submitted. Waiting for Admin approval.');
                membership.status = 'pending';
            }
        } catch (e) {
            alert('Failed to join.');
        } finally {
            isJoining = false;
        }
    }

    async function handlePost() {
        if (!postTitle || !postBody) return;
        try {
            await api('POST', '/social/posts', {
                community_id: community.id,
                title: postTitle,
                body: postBody,
                slug: postTitle.toLowerCase().replace(/ /g, '-')
            });
            // Refresh Feed
            posts = await api('GET', `/social/feed?scope=community&community_id=${community.id}`);
            postTitle = ''; postBody = '';
        } catch (e: any) {
            alert('VIOLATION: ' + e.message);
        }
    }
</script>

{#if loading}
    <div class="flex items-center justify-center h-screen bg-gray-100">
        <div class="text-2xl font-black uppercase animate-pulse">Entering Territory...</div>
    </div>
{:else if community}
    <div class="min-h-screen bg-gray-50 pb-12">
        
        <div class="bg-slate-900 text-white border-b-4 border-black relative overflow-hidden">
            <div class="max-w-6xl mx-auto p-8 relative z-10">
                <div class="flex flex-col md:flex-row justify-between items-end gap-6">
                    <div>
                        <div class="text-xs font-mono text-orange-500 mb-2 uppercase tracking-widest">Sovereign Territory</div>
                        <h1 class="text-5xl md:text-6xl font-black uppercase tracking-tighter">{community.name}</h1>
                        <p class="text-xl text-slate-400 font-medium max-w-2xl mt-4">{community.description}</p>
                    </div>
                    
                    <div class="bg-white/10 p-6 rounded-lg backdrop-blur-sm border border-white/20">
                        <div class="text-center mb-2">
                            <span class="block text-3xl font-black">{community.member_count}</span>
                            <span class="text-xs uppercase font-bold text-slate-400">Citizens</span>
                        </div>

                        {#if membership.status === 'active'}
                            <button class="w-full bg-green-500 text-black font-black uppercase py-3 px-8 shadow-hard" disabled>
                                ✓ Citizen
                            </button>
                        {:else if membership.status === 'pending'}
                            <button class="w-full bg-yellow-400 text-black font-black uppercase py-3 px-8 shadow-hard opacity-80" disabled>
                                ⏳ Pending Review
                            </button>
                        {:else}
                            <button 
                                on:click={handleJoin} 
                                disabled={isJoining}
                                class="w-full bg-orange-600 hover:bg-orange-500 text-white font-black uppercase py-3 px-8 shadow-hard transition-all"
                            >
                                {isJoining ? 'Signing...' : 'Apply for Citizenship'}
                            </button>
                        {/if}
                    </div>
                </div>
            </div>
            <div class="absolute -right-20 -bottom-20 w-96 h-96 bg-orange-600/20 rounded-full blur-3xl"></div>
        </div>

        <div class="max-w-6xl mx-auto p-4 md:p-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            <div class="space-y-6">
                <div class="bg-white border-4 border-black p-6 shadow-hard">
                    <h3 class="font-black uppercase text-lg mb-4 border-b-2 border-black pb-2">Constitution</h3>
                    <ul class="space-y-2 text-sm font-bold text-gray-700">
                        <li class="flex items-start gap-2">
                            <span class="text-orange-600">§1</span>
                            <span>Respect the hierarchy.</span>
                        </li>
                        <li class="flex items-start gap-2">
                            <span class="text-orange-600">§2</span>
                            <span>{community.is_private ? 'Closed Borders (Approval Required)' : 'Open Borders'}</span>
                        </li>
                    </ul>
                </div>

                <a href="/governance" class="block bg-sp-blue text-white border-4 border-black p-4 font-black uppercase text-center hover:bg-sp-purple transition-colors">
                    View Court Docket
                </a>
            </div>

            <div class="lg:col-span-2">
                
                {#if membership.status === 'active'}
                    <div class="bg-white border-4 border-black p-4 shadow-hard mb-8">
                        <input bind:value={postTitle} class="w-full font-black text-xl outline-none mb-2 placeholder:text-gray-300" placeholder="Title of your decree..." />
                        <textarea bind:value={postBody} class="w-full resize-none outline-none font-medium text-gray-600 placeholder:text-gray-300" rows="3" placeholder="Speak to the citizens..."></textarea>
                        <div class="flex justify-between items-center mt-2 pt-2 border-t-2 border-gray-100">
                            <span class="text-xs font-bold text-gray-400 uppercase">Public Record</span>
                            <button on:click={handlePost} class="bg-black text-white font-black uppercase px-6 py-2 hover:bg-orange-600 transition-colors">
                                Publish
                            </button>
                        </div>
                    </div>

                    <div class="space-y-6">
                        {#each posts as post}
                            <div class="bg-white border-4 border-black p-6 shadow-hard hover:translate-x-1 hover:translate-y-1 transition-transform">
                                <div class="flex justify-between items-start mb-2">
                                    <div class="flex items-center gap-3">
                                        <div class="w-8 h-8 bg-gray-200 rounded-full border-2 border-black overflow-hidden">
                                            <img src={`https://api.dicebear.com/7.x/notionists/svg?seed=${post.author_id}`} alt="avatar" />
                                        </div>
                                        <span class="font-black text-sm">{post.author?.full_name || 'Citizen'}</span>
                                    </div>
                                    <span class="text-xs font-mono text-gray-400">{new Date(post.created_at).toLocaleDateString()}</span>
                                </div>
                                <h3 class="text-xl font-black uppercase leading-tight mb-2">{post.title}</h3>
                                <p class="text-gray-800 font-medium">{post.body}</p>
                            </div>
                        {/each}
                    </div>
                {:else}
                    <div class="bg-gray-200 border-4 border-dashed border-gray-400 p-12 text-center">
                        <div class="text-6xl mb-4">🔒</div>
                        <h2 class="text-2xl font-black uppercase text-gray-500 mb-2">Restricted Access</h2>
                        <p class="font-bold text-gray-600">You must be a citizen of {community.name} to view or participate in the town square.</p>
                    </div>
                {/if}

            </div>

        </div>
    </div>
{:else}
    <div class="text-center p-12 font-bold text-red-500">Territory Not Found (404)</div>
{/if}