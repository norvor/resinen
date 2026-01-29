<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    
    // ASSETS
    import logo from '$lib/assets/logo.svg';

    // WIDGETS
    import MissionControl from '$lib/components/widgets/MissionControl.svelte';
    import NoteWidget from '$lib/components/widgets/NoteWidget.svelte';
    import TaskWidget from '$lib/components/widgets/TaskWidget.svelte';
    import HabitMatrix from '$lib/components/widgets/HabitMatrix.svelte';
    import BudgetWidget from '$lib/components/widgets/BudgetWidget.svelte';
    import ScribbleWidget from '$lib/components/widgets/ScribbleWidget.svelte';
    
    // NEW WIDGETS
    import BreathingOrb from '$lib/components/widgets/BreathingOrb.svelte';
    import TransmissionWidget from '$lib/components/widgets/TransmissionWidget.svelte';
    import LoveWidget from '$lib/components/widgets/LoveWidget.svelte';

    // --- STATE ---
    let theme = $state('night-aurora'); 
    let searchQuery = $state("");
    
    // Data Containers
    let news = $state<any[]>([]);
    let history = $state<any>(null);
    let joke = $state<any>(null);
    let planetary = $state<any>(null);
    let zen = $state<any>(null);

    // --- THE AWESOME COLLAGE ENGINE ---
    const AWESOME_COLLECTION = [
        { title: "Starry Night", tag: "WILD", url: "https://burgessart.wordpress.com/wp-content/uploads/2012/07/vincent.jpg" },
        { title: "Neon Tokyo", tag: "CYBER", url: "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?q=80&w=1000&auto=format&fit=crop" },
        { title: "Deep Nebula", tag: "SPACE", url: "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?q=80&w=1000&auto=format&fit=crop" },
        { title: "Alpine Peak", tag: "NATURE", url: "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?q=80&w=1000&auto=format&fit=crop" },
        { title: "Abstract Flow", tag: "ART", url: "https://images.unsplash.com/photo-1541701494587-cb58502866ab?q=80&w=1000&auto=format&fit=crop" },
        { title: "Urban Canyon", tag: "CITY", url: "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?q=80&w=1000&auto=format&fit=crop" },
        { title: "Golden Hour", tag: "VIBE", url: "https://images.unsplash.com/photo-1470252649378-9c29740c9fa8?q=80&w=1000&auto=format&fit=crop" },
        { title: "Icelandic Road", tag: "TRAVEL", url: "https://images.unsplash.com/photo-1476610182048-b716b8518aae?q=80&w=1000&auto=format&fit=crop" },
    ];

    // State for the 3 collage images
    let collage = $state(AWESOME_COLLECTION.slice(0, 3));

    // --- SEARCH FUNCTION ---
    function performSearch(engine: string) {
        const q = encodeURIComponent(searchQuery);
        let url = "";
        switch(engine) {
            case 'google': url = `https://www.google.com/search?q=${q}`; break;
            case 'youtube': url = `https://www.youtube.com/results?search_query=${q}`; break;
            case 'news': url = `https://news.google.com/search?q=${q}`; break;
            case 'chatgpt': url = `https://chatgpt.com/?q=${q}`; break; // Direct link
        }
        if(url) window.open(url, '_blank');
        searchQuery = ""; // Clear after search
    }

    function handleEnter(e: KeyboardEvent) {
        if (e.key === 'Enter') performSearch('google');
    }

    // --- LOAD LIVE DATA ---
    onMount(async () => {
        const shuffled = [...AWESOME_COLLECTION].sort(() => 0.5 - Math.random());
        collage = shuffled.slice(0, 3);

        try {
            const [feedsData, planetData, zenData] = await Promise.all([
                api.widgets.getFeeds(),
                api.widgets.getPlanetary(),
                api.widgets.getZen()
            ]);

            news = feedsData.business || [];
            history = feedsData.history;
            joke = feedsData.joke;
            planetary = planetData;
            zen = zenData;
        } catch(e) { console.error("Dash Load Error", e); }
    });

    function toggleTheme() {
        theme = theme === 'night-aurora' ? 'cloudy' : 'night-aurora';
        document.body.className = theme;
    }
</script>

<svelte:head>
    <title>Resinen OS</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
</svelte:head>

<div class="app-background">
    <div class="aurora-glow"></div>
    <div class="stars"></div>
</div>

<div class="dashboard-layout">
    
    <header class="top-bar">
        <div class="brand">
            <img src={logo} alt="Resinen" class="app-logo" />
            <span class="logo-text">RESINEN</span>
        </div>
        
        <div class="search-deck">
            <input 
                type="search" 
                class="search-input" 
                placeholder="Google Search..." 
                bind:value={searchQuery}
                onkeydown={handleEnter}
                enterkeyhint="search"
                autocomplete="off"
            />
            <div class="search-buttons">
                <button class="s-btn google" onclick={() => performSearch('google')} title="Google Search">
                    <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12.48 10.92v3.28h7.84c-.24 1.84-.853 3.187-1.787 4.133-1.147 1.147-2.933 2.4-6.053 2.4-4.827 0-8.6-3.893-8.6-8.72s3.773-8.72 8.6-8.72c2.6 0 4.507 1.027 5.907 2.347l2.307-2.307C18.747 1.44 16.133 0 12.48 0 5.867 0 .307 5.387.307 12s5.56 12 12.173 12c3.573 0 6.267-1.173 8.373-3.36 2.16-2.16 2.84-5.213 2.84-7.667 0-.76-.053-1.467-.173-2.053H12.48z"/></svg>
                </button>
            </div>
        </div>

        <button class="theme-toggle" onclick={toggleTheme}>
            {theme === 'night-aurora' ? '🌙 Night Aurora' : '☁️ Cloudy'}
        </button>
    </header>

    <main class="grid-container">

        <div class="col col-left">
            
            <div class="card history-card">
                <div class="icon-box">📜</div>
                <div class="content">
                    <div class="label">ON THIS DAY {history?.year || '...'}</div>
                    <p>{history?.text || "Loading archives..."}</p>
                </div>
            </div>

            <TransmissionWidget />

            <div class="card news-card">
                <div class="card-header">
                    <span>📡 GLOBAL FEED</span>
                </div>
                <div class="news-list">
                    {#each news.slice(0, 5) as item}
                        <a href={item.link} target="_blank" class="news-item">
                            {item.title}
                        </a>
                    {/each}
                    {#if news.length === 0}
                        <div class="loading">Scanning frequencies...</div>
                    {/if}
                </div>
            </div>

            <div class="card joke-card">
                <div class="card-header">🃏 MORALE BOOST</div>
                <div class="joke-body">
                    <p class="setup">{joke?.setup || "..."}</p>
                    <p class="punch">{joke?.punchline || ""}</p>
                </div>
            </div>

            <HabitMatrix />
        </div>

        <div class="col col-center">
            
            <section class="mission-section">
                <MissionControl />
            </section>
            
            <section class="workspace-split">
                <div class="ws-col">
                    <BudgetWidget />
                    
                    <div class="card zen-card">
                        <div class="zen-icon">☯</div>
                        <p>"{zen?.text || "Stillness is the key."}"</p>
                    </div>
                </div>

                <div class="ws-col">
                    <TaskWidget />
                    
                    <BreathingOrb />
                </div>
            </section>
            
            <section class="note-section">
                <NoteWidget />
            </section>
        </div>

        <div class="col col-right">
            
            <div class="photo-frame">
                <div class="visual-card">
                    <img src={collage[0].url} alt="Inspiration" />
                </div>
            </div>

            <div class="split-visuals">
                <div class="photo-frame small">
                    <div class="visual-card small">
                        <img src={collage[1].url} alt="Inspiration" />
                    </div>
                </div>

                <div class="photo-frame small">
                    <div class="visual-card small">
                        <img src={collage[2].url} alt="Inspiration" />
                    </div>
                </div>
            </div>

            <LoveWidget />

            <ScribbleWidget />
        </div>

    </main>
</div>

<style>
    /* =========================================
       GLOBAL & THEMES
       ========================================= */
    :global(body) { margin: 0; padding: 0; font-family: 'Inter', sans-serif; transition: background 0.5s; overflow-x: hidden; }
    :global(body.night-aurora) { background: #020617; color: #e2e8f0; }
    :global(body.cloudy) { background: #f1f5f9; color: #334155; }

    .app-background { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; pointer-events: none; }
    
    :global(body.night-aurora) .aurora-glow {
        position: absolute; top: -20%; left: -20%; width: 140%; height: 140%;
        background: radial-gradient(circle at 50% 0%, rgba(45, 212, 191, 0.15), transparent 60%),
                    radial-gradient(circle at 80% 20%, rgba(168, 85, 247, 0.1), transparent 50%);
        filter: blur(80px); opacity: 1; transition: 1s;
    }

    /* =========================================
       LAYOUT GRID (RESTORED DESKTOP)
       ========================================= */
    .dashboard-layout {
        /* DESKTOP DEFAULT: Fixed height with internal scroll */
        height: 100vh; 
        display: flex; flex-direction: column;
        padding: 20px 40px; box-sizing: border-box;
        overflow-y: auto; /* Required for desktop scrolling */
    }

    .grid-container {
        display: grid;
        grid-template-columns: 320px 1fr 320px; /* Desktop: Fixed Sides, Fluid Center */
        gap: 24px;
        flex: 1;
        max-width: 1920px; margin: 0 auto; width: 100%;
    }

    .col { display: flex; flex-direction: column; gap: 24px; }

    /* =========================================
       HEADER & SEARCH DECK
       ========================================= */
    .top-bar {
        display: grid; 
        grid-template-columns: 250px 1fr 250px; /* Left Brand, Center Search, Right Theme */
        align-items: center;
        margin-bottom: 25px; padding: 10px 0; gap: 20px;
    }
    
    .brand { display: flex; align-items: center; gap: 15px; }
    .app-logo { height: 40px; width: auto; }
    .logo-text { font-weight: 800; font-size: 1.2rem; letter-spacing: 2px; }

    /* SEARCH DECK */
    .search-deck {
        display: flex; align-items: center; gap: 10px;
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255,255,255,0.1);
        padding: 6px 10px; border-radius: 50px;
        width: 100%; max-width: 600px; margin: 0 auto;
        backdrop-filter: blur(12px);
        transition: 0.3s;
    }
    :global(body.cloudy) .search-deck {
        background: #fff; border-color: #cbd5e1; box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }

    .search-input {
        flex: 1; background: transparent; border: none; outline: none;
        color: inherit; font-family: 'Inter', sans-serif; font-size: 0.9rem;
        padding: 5px 10px;
        -webkit-appearance: none;
    }
    
    .search-buttons { display: flex; gap: 5px; }
    .s-btn {
        width: 32px; height: 32px; border-radius: 50%; border: none;
        cursor: pointer; display: flex; align-items: center; justify-content: center;
        transition: 0.2s; color: #fff;
    }
    .s-btn svg { width: 16px; height: 16px; }
    .s-btn:hover { transform: scale(1.1); }

    .chatgpt { background: #10a37f; }
    .google { background: #4285f4; }
    .youtube { background: #ff0000; }
    .news { background: #fbbc05; color: #000; }

    .theme-toggle {
        justify-self: end;
        background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
        color: inherit; padding: 8px 16px; border-radius: 8px; cursor: pointer;
        font-family: inherit; font-size: 0.85rem; font-weight: 600; transition: 0.2s;
    }
    :global(body.cloudy) .theme-toggle { background: #fff; border-color: #cbd5e1; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }

    /* =========================================
       CENTER COLUMN
       ========================================= */
    .mission-section { width: 100%; }
    
    .workspace-split {
        display: grid; grid-template-columns: 1fr 1fr; gap: 24px; width: 100%;
    }
    .ws-col { display: flex; flex-direction: column; gap: 24px; }

    .note-section { width: 100%; flex: 1; min-height: 400px; display: flex; flex-direction: column; }
    :global(.note-section .notebook-editor) { min-height: 500px; flex: 1; }
    :global(.note-section .app-root) { min-height: 500px; flex: 1; }

    /* =========================================
       CARDS & WIDGETS
       ========================================= */
    .card {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        border-radius: 12px;
        padding: 20px;
        transition: 0.3s;
    }
    :global(body.cloudy) .card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        color: #1e293b;
    }

    /* History */
    .history-card { display: flex; gap: 15px; align-items: flex-start; background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), transparent); border-color: rgba(245, 158, 11, 0.2); }
    .history-card .icon-box { font-size: 1.5rem; }
    .history-card .label { font-size: 0.7rem; font-weight: 700; color: #facc15; margin-bottom: 4px; letter-spacing: 1px; }
    :global(body.cloudy) .history-card .label { color: #d97706; }
    .history-card p { margin: 0; font-size: 0.9rem; line-height: 1.4; }

    /* News */
    .news-card { padding: 0; overflow: hidden; }
    .news-card .card-header { padding: 12px 20px; background: rgba(0,0,0,0.1); font-size: 0.75rem; font-weight: 700; opacity: 0.8; letter-spacing: 1px; }
    .news-list { display: flex; flex-direction: column; }
    .news-item { padding: 12px 20px; border-bottom: 1px solid rgba(255,255,255,0.05); text-decoration: none; color: inherit; font-size: 0.9rem; transition: 0.2s; }
    .news-item:hover { background: rgba(255,255,255,0.03); color: #2dd4bf; }
    :global(body.cloudy) .news-item { border-bottom-color: #f1f5f9; }
    :global(body.cloudy) .news-item:hover { background: #f8fafc; color: #0284c7; }

    /* Joke */
    .joke-card { text-align: center; border-left: 4px solid #a855f7; }
    .joke-card .card-header { font-size: 0.7rem; color: #a855f7; font-weight: 700; margin-bottom: 10px; }
    .setup { font-weight: 600; margin-bottom: 4px; }
    .punch { font-style: italic; opacity: 0.8; }

    /* Zen */
    .zen-card { 
        display: flex; align-items: center; justify-content: center; gap: 15px; 
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), transparent); 
        border-color: rgba(16, 185, 129, 0.2);
        font-style: italic; color: #10b981; min-height: 80px;
    }
    .zen-icon { font-size: 1.5rem; }
    :global(body.cloudy) .zen-card { background: #ecfdf5; border-color: #d1fae5; color: #059669; }

    /* Visuals (Collage) - PHOTO FRAMES - FIXED IMAGE FITTING */
    .photo-frame {
        background: #fff;
        padding: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        transform: rotate(-1deg);
        transition: transform 0.3s;
        display: flex; justify-content: center; align-items: center;
    }
    
    /* FIX: Only apply hover scale if device actually supports hover */
    @media (hover: hover) {
        .photo-frame:hover { transform: rotate(0deg) scale(1.02); z-index: 10; }
    }
    
    .photo-frame.small { padding: 6px; transform: rotate(1deg); }

    .visual-card {
        height: 200px; width: 100%; padding: 0; 
        overflow: hidden; 
        background: #000; /* Matting background */
        border: 1px solid #eee; border-radius: 0;
        display: flex; justify-content: center; align-items: center;
    }
    .visual-card img {
        width: 100%; height: 100%; 
        object-fit: contain; 
        display: block;
    }
    
    .split-visuals { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    .visual-card.small { height: 110px; }

    /* =========================================
       RESPONSIVE BREAKPOINTS
       ========================================= */
    
    /* Tablet (Two Columns) */
    @media (max-width: 1400px) {
        .dashboard-layout { padding: 10px 20px; }
        .grid-container { 
            grid-template-columns: 300px 1fr; 
            gap: 20px;
        }
        .col-right { 
            grid-column: span 2; 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 20px;
        }
        .photo-frame { grid-column: span 1; }
        .split-visuals { grid-column: span 1; }
        
        .top-bar { grid-template-columns: 200px 1fr 150px; }
    }

    /* Mobile (Single Column) */
    @media (max-width: 850px) {
        .dashboard-layout { 
            /* MOBILE OVERRIDE: Grow with content, let window scroll */
            height: auto; 
            min-height: 100dvh; 
            overflow-y: visible; 
            padding: 10px; 
        }
        .grid-container { 
            display: flex; flex-direction: column; 
        }
        
        .top-bar { display: flex; flex-direction: column; gap: 15px; }
        .brand { margin-bottom: 0; }
        .search-deck { width: 100%; order: 2; }
        .theme-toggle { order: 1; align-self: flex-end; }
        
        /* FIX: Prevent iOS zoom by enforcing 16px font size on inputs */
        .search-input { font-size: 16px; }

        /* FIX: Larger touch targets for search buttons (44px min) */
        .s-btn { width: 44px; height: 44px; }
        .search-buttons { gap: 10px; }
        
        .workspace-split { grid-template-columns: 1fr; }
        
        .col-right { display: flex; flex-direction: column; }
        .photo-frame { transform: none; width: 100%; box-sizing: border-box; }
        /* Reset any lingering transforms on mobile */
        .photo-frame:hover { transform: none; }
    }
</style>