<script lang="ts">
    import { onMount } from 'svelte';
    import { api, type Community, type User, type Post } from '$lib/api';
    import { fade, scale, fly } from 'svelte/transition';

    // --- IMPORT WIDGETS ---
    import ArenaWidget from '$lib/components/widgets/ArenaWidget.svelte';
    import GardenWidget from '$lib/components/widgets/GardenWidget.svelte';
    import AcademyWidget from '$lib/components/widgets/AcademyWidget.svelte';
    import ClubWidget from '$lib/components/widgets/ClubWidget.svelte';
    import BazaarWidget from '$lib/components/widgets/BazaarWidget.svelte';
    import BunkerWidget from '$lib/components/widgets/BunkerWidget.svelte';
    import LibraryWidget from '$lib/components/widgets/LibraryWidget.svelte';
    import StageWidget from '$lib/components/widgets/StageWidget.svelte';
    import SenateWidget from '$lib/components/widgets/SenateWidget.svelte';
    import GuildWidget from '$lib/components/widgets/GuildWidget.svelte';

    // --- STATE ---
    let user: User | null = null;
    let myCommunities: Community[] = [];
    let latestPosts: Post[] = [];
    let loading = true;
    let showBackpack = false;
    
    // --- 3D TILT STATE ---
    let cardRotateX = 0;
    let cardRotateY = 0;

    // --- DECORATION ---
    const stickers = [
        { emoji: '🍕', top: '10%', left: '80%', rot: '12deg' },
        { emoji: '🛹', top: '60%', left: '5%', rot: '-10deg' },
        { emoji: '👾', top: '85%', left: '90%', rot: '5deg' }
    ];

    onMount(async () => {
        try {
            const [userData, comms, feed] = await Promise.all([
                api.getMe().catch(() => null),
                api.getCommunities(),
                api.getFeed('global').catch(() => [])
            ]);
            user = userData;
            myCommunities = comms;
            latestPosts = feed.slice(0, 2); 
        } finally {
            loading = false;
        }
    });

    function handleMouseMove(e: MouseEvent) {
        const card = e.currentTarget as HTMLElement;
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        cardRotateY = ((x - centerX) / centerX) * 15;
        cardRotateX = ((y - centerY) / centerY) * -15;
    }

    function resetCard() {
        cardRotateX = 0;
        cardRotateY = 0;
    }
</script>

<div class="min-h-screen bg-[#f0f0f4] text-zinc-900 pb-40 p-4 md:p-8 font-sans relative overflow-x-hidden selection:bg-yellow-200">

    <div class="absolute inset-0 pointer-events-none opacity-[0.03]" 
         style="background-image: linear-gradient(#000 1px, transparent 1px), linear-gradient(90deg, #000 1px, transparent 1px); background-size: 20px 20px;">
    </div>

    <div class="max-w-[1200px] mx-auto flex justify-between items-end mb-10 relative z-10">
        <div>
            <div class="inline-block bg-black text-white text-[10px] font-bold uppercase px-2 py-1 mb-2 tracking-widest">
                Spring Semester 2026
            </div>
            <h1 class="text-5xl md:text-6xl font-black tracking-tighter text-zinc-900 leading-none font-serif italic">
                Campus<span class="text-blue-700 not-italic">OS</span>
            </h1>
        </div>
        <div class="hidden md:block text-right">
            <div class="text-4xl font-black text-zinc-200">
                {new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
            </div>
        </div>
    </div>

    {#if loading}
        <div class="h-[50vh] flex flex-col items-center justify-center gap-4">
            <div class="w-16 h-16 border-4 border-zinc-300 border-t-blue-600 rounded-full animate-spin"></div>
            <div class="font-mono text-xs uppercase tracking-widest text-zinc-400">Opening Lockers...</div>
        </div>
    {:else}
        
        <div class="max-w-[1200px] mx-auto grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6 grid-rows-[auto_auto_auto] relative z-10">

            <div class="md:col-span-1 lg:row-span-2 relative h-[450px] perspective-1000 group">
                <div class="absolute -top-16 left-1/2 -translate-x-1/2 w-32 h-20 border-x-2 border-b-2 border-zinc-300 rounded-b-full z-0"></div>
                
                <div 
                    class="w-full h-full bg-white rounded-2xl shadow-xl border border-zinc-200 p-6 flex flex-col justify-between relative overflow-hidden transition-transform duration-100 ease-linear z-10"
                    style="transform: rotateX({cardRotateX}deg) rotateY({cardRotateY}deg); transform-style: preserve-3d;"
                    on:mousemove={handleMouseMove}
                    on:mouseleave={resetCard}
                >
                    <div class="absolute inset-0 bg-gradient-to-tr from-transparent via-blue-200/20 to-transparent opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-20 mix-blend-overlay"></div>

                    <div class="flex justify-between items-start z-10">
                        <div class="flex flex-col">
                            <span class="text-[10px] font-black uppercase text-blue-800 tracking-widest">Resinen University</span>
                            <span class="text-[9px] font-bold text-zinc-400 uppercase">Valid Thru 2027</span>
                        </div>
                        <div class="w-12 h-3 bg-zinc-100 rounded-full shadow-inner border border-zinc-200"></div>
                    </div>

                    <div class="flex-1 flex flex-col items-center justify-center z-10 my-4">
                        <div class="w-32 h-32 bg-zinc-100 border-4 border-white shadow-md rotate-1 relative">
                            {#if user?.avatar_url}
                                <img src={user.avatar_url} alt="User" class="w-full h-full object-cover grayscale contrast-125 mix-blend-multiply" />
                            {:else}
                                <div class="w-full h-full flex items-center justify-center text-4xl bg-zinc-200">🎓</div>
                            {/if}
                            <div class="absolute -top-3 left-1/2 -translate-x-1/2 w-16 h-6 bg-yellow-200/50 rotate-1"></div>
                        </div>
                        <h2 class="mt-6 text-xl font-black uppercase text-center leading-none tracking-tight font-serif">
                            {user?.full_name || 'Guest Student'}
                        </h2>
                        <div class="mt-2 inline-block bg-blue-100 text-blue-800 px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-widest">
                            Undergraduate
                        </div>
                    </div>

                    <div class="z-10">
                        <div class="flex justify-between text-[10px] font-mono font-bold text-zinc-500 mb-1">
                            <span>ID: {user?.id.substring(0,8) || '000000'}</span>
                            <span>LVL {user?.level || 1}</span>
                        </div>
                        <div class="h-10 w-full bg-black mask-barcode opacity-80"></div>
                    </div>
                </div>
            </div>

            <div class="md:col-span-2 bg-[#1a1a1a] text-white rounded-2xl p-8 flex flex-col justify-between relative overflow-hidden shadow-2xl group cursor-pointer border-4 border-[#2a2a2a] min-h-[220px]">
                <div class="absolute inset-0 opacity-20 bg-[url('https://www.transparenttextures.com/patterns/stardust.png')]"></div>
                
                <div class="relative z-10">
                    <div class="flex items-center gap-2 mb-4">
                        <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                        <span class="text-xs font-bold text-zinc-400 uppercase tracking-widest">Admin Block</span>
                    </div>
                    <h3 class="text-3xl font-serif font-bold italic mb-2 text-white">Platform Constitution</h3>
                    <p class="text-zinc-400 text-sm max-w-md font-medium leading-relaxed">
                        "Order is the first law of the Universe."
                    </p>
                </div>
                
                <div class="relative z-10 mt-6 flex items-center gap-4">
                    <span class="text-xs font-black uppercase border-b-2 border-white pb-1 hover:text-yellow-300 hover:border-yellow-300 transition-colors">
                        Enter Hall ->
                    </span>
                </div>
            </div>

            <div class="md:col-span-1 h-[220px]">
                <ArenaWidget communityId={myCommunities[0]?.id || ''} />
            </div>

            <div class="md:col-span-1 h-[220px]">
                <GardenWidget communityId={myCommunities[0]?.id || ''} />
            </div>

            <div class="md:col-span-1 h-[220px]">
                <AcademyWidget communityId={myCommunities[0]?.id || ''} />
            </div>

            <div class="md:col-span-1 h-[220px]">
                <ClubWidget communityId={myCommunities[0]?.id || ''} />
            </div>

            <div class="md:col-span-1 h-[220px]">
                <BazaarWidget communityId={myCommunities[0]?.id || ''} />
            </div>

            <div class="md:col-span-1 h-[220px]">
                <BunkerWidget communityId={myCommunities[0]?.id || ''} />
            </div>

            <div class="md:col-span-1 h-[220px]">
                <LibraryWidget communityId={myCommunities[0]?.id || ''} />
            </div>

            <div class="md:col-span-1 h-[220px]">
                <StageWidget communityId={myCommunities[0]?.id || ''} />
            </div>

            <div class="md:col-span-1 h-[220px]">
                <SenateWidget communityId={myCommunities[0]?.id || ''} />
            </div>

            <div class="md:col-span-1 h-[220px]">
                <GuildWidget communityId={myCommunities[0]?.id || ''} />
            </div>

            <div class="md:col-span-1 lg:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-4 h-[220px]">
                {#each latestPosts as post, i}
                    <div class="bg-[#fefce8] p-4 shadow-[4px_4px_10px_rgba(0,0,0,0.1)] relative transition-transform hover:scale-105 hover:z-20 cursor-pointer border border-yellow-200/50 h-full flex flex-col"
                         style="transform: rotate({i % 2 === 0 ? '-1deg' : '1deg'});">
                        <div class="absolute -top-3 left-1/2 -translate-x-1/2 w-3 h-3 rounded-full bg-red-500 shadow-sm border border-black/20"></div>
                        
                        <div class="flex items-center gap-2 mb-2 border-b border-yellow-200 pb-2">
                            <div class="w-6 h-6 bg-yellow-200 rounded-full text-[10px] flex items-center justify-center font-bold">
                                {post.author_name.substring(0,1)}
                            </div>
                            <div class="text-[10px] font-bold text-zinc-500 uppercase truncate">{post.author_name}</div>
                        </div>
                        <p class="font-handwriting text-zinc-800 text-xs leading-tight line-clamp-4 flex-1">
                            "{post.content}"
                        </p>
                    </div>
                {/each}
            </div>

            <div class="md:col-span-1 lg:row-span-1 h-[220px] bg-zinc-900 rounded-2xl p-1 border border-zinc-800 shadow-2xl relative group">
                <div class="w-full h-full border border-dashed border-zinc-700 rounded-xl p-6 flex flex-col relative overflow-hidden justify-between">
                     <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-purple-500 to-transparent opacity-50"></div>
                    
                    <div class="relative z-10">
                        <div class="text-[10px] font-mono text-purple-400 mb-1 blink">ACCESS: 05</div>
                        <h3 class="text-2xl font-black uppercase leading-none text-white">
                            Secret<br>Society
                        </h3>
                    </div>

                    <div class="space-y-2 relative z-10">
                        <div class="p-2 bg-zinc-800 rounded border border-zinc-700 flex justify-between items-center group-hover:border-purple-500/50 transition-colors cursor-pointer">
                            <span class="text-xs font-bold text-white">Phoenix</span>
                            <span class="text-[9px] text-zinc-500">BETA</span>
                        </div>
                    </div>
                </div>
            </div>

        </div>

        {#each stickers as s}
            <div class="absolute text-4xl pointer-events-none opacity-80 animate-float z-0" 
                 style="top: {s.top}; left: {s.left}; transform: rotate({s.rot});">
                {s.emoji}
            </div>
        {/each}

    {/if}

    <div class="fixed bottom-8 left-1/2 -translate-x-1/2 z-50">
        <div class="bg-zinc-900/90 backdrop-blur-md border border-zinc-700 shadow-2xl rounded-full px-4 py-3 flex items-center gap-3">
            
            <button 
                on:click={() => showBackpack = !showBackpack}
                class="w-12 h-12 bg-white rounded-full flex items-center justify-center text-black shadow-lg hover:scale-110 transition-transform border-2 border-zinc-200"
            >
                <span class="text-xl">🎒</span>
            </button>

            <div class="w-[1px] h-6 bg-zinc-700 mx-1"></div>

            {#each myCommunities.slice(0, 3) as app}
                <a href="/communities/{app.slug}" class="w-10 h-10 bg-zinc-800 rounded-full border border-zinc-700 flex items-center justify-center text-xs font-black text-white hover:scale-110 hover:bg-blue-600 hover:border-blue-500 transition-all group relative">
                    {app.name.substring(0,1)}
                    <span class="absolute -top-10 bg-black text-white text-[10px] px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
                        {app.name}
                    </span>
                </a>
            {/each}
        </div>
    </div>

    {#if showBackpack}
        <div class="fixed inset-0 z-[100] bg-zinc-900/95 backdrop-blur-xl flex flex-col items-center justify-center p-8 text-white" transition:fade={{ duration: 200 }}>
            <h2 class="text-2xl font-black uppercase tracking-widest mb-12 border-b-2 border-white pb-2">My Backpack</h2>
            
            <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-8">
                {#each myCommunities as app, i}
                    <a href="/communities/{app.slug}" class="flex flex-col items-center gap-4 group" in:scale={{ delay: i * 50, start: 0.8 }}>
                        <div class="w-24 h-24 bg-zinc-800 rounded-2xl shadow-xl border-2 border-zinc-700 flex items-center justify-center text-3xl font-black group-hover:bg-white group-hover:text-black group-hover:scale-110 transition-all">
                            {app.name.substring(0,1)}
                        </div>
                        <span class="text-sm font-bold text-zinc-400 group-hover:text-white uppercase tracking-widest">{app.name}</span>
                    </a>
                {/each}
                
                <a href="/communities/create" class="flex flex-col items-center gap-4 group opacity-50 hover:opacity-100 transition-opacity">
                    <div class="w-24 h-24 border-2 border-dashed border-zinc-600 rounded-2xl flex items-center justify-center text-3xl text-zinc-600">
                        +
                    </div>
                    <span class="text-sm font-bold text-zinc-600">New Club</span>
                </a>
            </div>
            
            <button on:click={() => showBackpack = false} class="absolute bottom-10 text-xs font-black uppercase text-zinc-500 hover:text-white transition-colors">
                Zip It Up (Close)
            </button>
        </div>
    {/if}

</div>

<style>
    .perspective-1000 { perspective: 1000px; }
    .font-handwriting { font-family: 'Courier New', Courier, monospace; }
    
    .mask-barcode {
        -webkit-mask-image: url('https://upload.wikimedia.org/wikipedia/commons/5/5d/UPC-A-036000291452.png');
        mask-image: url('https://upload.wikimedia.org/wikipedia/commons/5/5d/UPC-A-036000291452.png');
        -webkit-mask-size: cover;
        mask-size: cover;
    }

    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(var(--rot)); }
        50% { transform: translateY(-10px) rotate(var(--rot)); }
    }
    .animate-float { animation: float 6s ease-in-out infinite; }
</style>