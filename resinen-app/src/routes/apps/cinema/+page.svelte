<script lang="ts">
    import { onMount } from 'svelte';

    // --- STATE ---
    let catalog = $state<any>(null);
    let activeVideo = $state<any>(null); 
    let scrollY = $state(0);

    async function loadCatalog() {
        try {
            const res = await fetch('https://api.resinen.com/cinema/catalog');
            catalog = await res.json();
        } catch(e) { console.error(e); }
    }

    function playVideo(video: any) {
        activeVideo = video;
    }

    function closePlayer() {
        activeVideo = null;
    }

    // --- HELPER: GENERATE URL ---
    function getEmbedUrl(item: any, autoplay = 1) {
        if (!item) return '';
        if (item.type === 'playlist') {
            // Playlist Embed Format
            // 'list' parameter takes the Playlist ID (PL...)
            // 'index' can be added to start at a specific video
            return `https://www.youtube.com/embed?listType=playlist&list=${item.id}&autoplay=${autoplay}&modestbranding=1&iv_load_policy=3`;
        } else {
            // Standard Video Format
            return `https://www.youtube.com/embed/${item.id}?autoplay=${autoplay}&modestbranding=1&iv_load_policy=3`;
        }
    }

    onMount(() => {
        loadCatalog();
        window.addEventListener('scroll', () => scrollY = window.scrollY);
    });
</script>

<svelte:head>
    <title>Resinen Cinema</title>
</svelte:head>

<div class="cinema-container">
    
    {#if catalog}
        <div class="hero">
            <div class="hero-bg">
                <iframe 
                    src={getEmbedUrl(catalog.hero, 1) + "&mute=1&controls=0&loop=1"} 
                    title="Hero" 
                    frameborder="0"
                    allow="autoplay; encrypted-media"
                ></iframe>
                <div class="hero-gradient"></div>
            </div>

            <div class="hero-content" style="opacity: {1 - scrollY/500}">
                <div class="badge">SERIES</div>
                <h1>{catalog.hero.title}</h1>
                <p>{catalog.hero.desc}</p>
                <div class="hero-btns">
                    <button class="play-btn" onclick={() => playVideo(catalog.hero)}>
                        ▶ PLAY SERIES
                    </button>
                    <button class="info-btn">
                        ℹ EPISODES
                    </button>
                </div>
            </div>
        </div>

        <div class="rows-container">
            {#each catalog.categories as cat}
                <div class="row">
                    <h3>{cat.title}</h3>
                    <div class="row-scroll">
                        {#each cat.videos as vid}
                            <div class="video-card" onclick={() => playVideo(vid)}>
                                <img src={vid.img} alt={vid.title} />
                                <div class="card-overlay">
                                    <span class="card-title">{vid.title}</span>
                                    <span class="type-badge">{vid.type === 'playlist' ? 'SERIES' : 'MOVIE'}</span>
                                    <span class="play-icon">▶</span>
                                </div>
                            </div>
                        {/each}
                    </div>
                </div>
            {/each}
        </div>
    {/if}

    {#if activeVideo}
        <div class="modal-overlay" onclick={closePlayer}>
            <div class="modal-content">
                <iframe 
                    src={getEmbedUrl(activeVideo, 1)} 
                    title="Player" 
                    frameborder="0" 
                    allow="autoplay; encrypted-media; fullscreen"
                    allowfullscreen
                ></iframe>
            </div>
        </div>
    {/if}

</div>

<style>
    :global(body) { background: #141414; color: #fff; font-family: 'Space Grotesk', sans-serif; overflow-x: hidden; margin: 0; }
    
    .cinema-container { padding-bottom: 100px; }

    /* HERO */
    .hero { position: relative; height: 80vh; width: 100%; overflow: hidden; margin-bottom: -150px; }
    .hero-bg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; pointer-events: none; }
    .hero-bg iframe { 
        width: 100vw; height: 56.25vw; 
        min-height: 100vh; min-width: 177.77vh; 
        position: absolute; top: 50%; left: 50%; 
        transform: translate(-50%, -50%) scale(1.3); 
        pointer-events: none; opacity: 0.6; /* Dimmed slightly */
    }
    .hero-gradient {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: linear-gradient(to top, #141414 10%, transparent 50%, rgba(0,0,0,0.8) 100%);
    }

    .hero-content { 
        position: absolute; bottom: 35%; left: 4%; z-index: 10; width: 40%; 
        text-shadow: 2px 2px 10px rgba(0,0,0,0.8);
    }
    .badge { background: #e50914; color: #fff; display: inline-block; padding: 2px 5px; font-size: 0.8rem; font-weight: bold; margin-bottom: 10px; border-radius: 2px; }
    .hero-content h1 { font-size: 4rem; margin: 0 0 10px 0; font-weight: 800; line-height: 0.9; }
    .hero-content p { font-size: 1.1rem; margin-bottom: 20px; color: #e5e5e5; font-family: 'JetBrains Mono'; }
    
    .hero-btns { display: flex; gap: 15px; }
    .play-btn { 
        background: #fff; color: #000; border: none; padding: 10px 25px; 
        font-size: 1.1rem; font-weight: bold; border-radius: 4px; cursor: pointer; display: flex; align-items: center; gap: 10px;
        transition: 0.2s;
    }
    .play-btn:hover { background: #e5e5e5; }
    .info-btn { 
        background: rgba(109, 109, 110, 0.7); color: #fff; border: none; padding: 10px 25px; 
        font-size: 1.1rem; font-weight: bold; border-radius: 4px; cursor: pointer; backdrop-filter: blur(5px);
    }
    .info-btn:hover { background: rgba(109, 109, 110, 0.4); }

    /* ROWS */
    .rows-container { position: relative; z-index: 20; padding-left: 4%; margin-top: 10vh; }
    .row { margin-bottom: 40px; }
    .row h3 { font-size: 1.4rem; color: #e5e5e5; margin-bottom: 10px; font-weight: bold; }
    
    .row-scroll { 
        display: flex; gap: 10px; overflow-x: auto; padding: 20px 0; 
        scrollbar-width: none; 
        scroll-behavior: smooth;
    }
    .row-scroll::-webkit-scrollbar { display: none; } 

    .video-card { 
        flex: 0 0 250px; aspect-ratio: 16/9; position: relative; 
        border-radius: 4px; overflow: hidden; cursor: pointer; transition: 0.3s; 
    }
    .video-card img { width: 100%; height: 100%; object-fit: cover; }
    
    .card-overlay {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.4); opacity: 0; transition: 0.3s;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        text-align: center; padding: 10px;
    }
    .card-title { font-weight: bold; font-size: 0.9rem; margin-bottom: 5px; }
    .type-badge { font-size: 0.6rem; background: #2dd4bf; color: #000; padding: 2px 4px; border-radius: 2px; margin-bottom: 5px; font-weight: bold; }
    .play-icon { font-size: 2rem; border: 2px solid #fff; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; padding-left: 4px; }

    .video-card:hover { transform: scale(1.4); z-index: 100; box-shadow: 0 0 20px rgba(0,0,0,0.8); }
    .video-card:hover .card-overlay { opacity: 1; }

    /* MODAL */
    .modal-overlay { 
        position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
        background: rgba(0,0,0,0.9); z-index: 9999; 
        display: flex; justify-content: center; align-items: center; 
        backdrop-filter: blur(5px);
    }
    .modal-content { width: 80%; aspect-ratio: 16/9; max-width: 1200px; background: #000; box-shadow: 0 0 50px rgba(255,255,255,0.1); }
    .modal-content iframe { width: 100%; height: 100%; }
</style>