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
    let isCustomizing = $state(false);

    // Data Containers
    let news = $state<any[]>([]);
    let history = $state<any>(null);
    let joke = $state<any>(null);
    let planetary = $state<any>(null);
    let zen = $state<any>(null);

    // --- PREFERENCES ---
    let widgetPrefs = $state({
        history: true,
        news: true,
        joke: true,
        zen: true,
        budget: true,
        tasks: true,
        scribble: true,
        notes: true,
        love: true,
        transmission: true
    });

    // --- SEARCH FUNCTION ---
    function performSearch(engine: string) {
        const q = encodeURIComponent(searchQuery);
        let url = "";
        switch(engine) {
            case 'google': url = `https://www.google.com/search?q=${q}`; break;
            case 'youtube': url = `https://www.youtube.com/results?search_query=${q}`; break;
            case 'news': url = `https://news.google.com/search?q=${q}`; break;
            case 'chatgpt': url = `https://chatgpt.com/?q=${q}`; break;
        }
        if(url) window.open(url, '_blank');
        searchQuery = "";
    }

    function handleEnter(e: KeyboardEvent) {
        if (e.key === 'Enter') performSearch('google');
    }

    // --- SAVE LAYOUT ---
    async function saveLayout() {
        try {
            const cleanPrefs = JSON.parse(JSON.stringify(widgetPrefs));
            await api.widgets.savePreferences(cleanPrefs);
            isCustomizing = false; 
        } catch(e) {
            console.error("Failed to save layout", e);
            alert("Could not save layout.");
        }
    }

    // --- LOAD LIVE DATA ---
    onMount(async () => {
        try {
            const [feedsData, planetData, zenData, prefsData] = await Promise.all([
                api.widgets.getFeeds(),
                api.widgets.getPlanetary(),
                api.widgets.getZen(),
                api.widgets.getPreferences()
            ]);

            news = feedsData.business || [];
            history = feedsData.history;
            joke = feedsData.joke;
            planetary = planetData;
            zen = zenData;
            
            if (prefsData) {
                widgetPrefs = { ...widgetPrefs, ...prefsData };
            }
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
                placeholder="Search the void..." 
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

        <div class="header-actions">
            <button class="theme-toggle" onclick={() => isCustomizing = true}>⚙️ Layout</button>
            <button class="theme-toggle" onclick={toggleTheme}>
                {theme === 'night-aurora' ? '🌙 Night' : '☁️ Day'}
            </button>
        </div>
    </header>

    {#if isCustomizing}
        <div class="modal-backdrop" onclick={() => isCustomizing = false} role="presentation"></div>
        <div class="modal-panel">
            <div class="modal-header">
                <h3>Dashboard Layout</h3>
                <button class="close-btn" onclick={() => isCustomizing = false}>✕</button>
            </div>
            <div class="modal-body">
                <div class="toggle-grid">
                    <label class="toggle-card {widgetPrefs.history ? 'active' : ''}">
                        <input type="checkbox" bind:checked={widgetPrefs.history}>
                        <span class="icon">📜</span> <span class="label">History</span>
                    </label>
                    <label class="toggle-card {widgetPrefs.news ? 'active' : ''}">
                        <input type="checkbox" bind:checked={widgetPrefs.news}>
                        <span class="icon">📡</span> <span class="label">News Feed</span>
                    </label>
                    <label class="toggle-card {widgetPrefs.transmission ? 'active' : ''}">
                        <input type="checkbox" bind:checked={widgetPrefs.transmission}>
                        <span class="icon">📶</span> <span class="label">Transmission</span>
                    </label>
                    <label class="toggle-card {widgetPrefs.joke ? 'active' : ''}">
                        <input type="checkbox" bind:checked={widgetPrefs.joke}>
                        <span class="icon">🃏</span> <span class="label">Jokes</span>
                    </label>
                    <label class="toggle-card {widgetPrefs.budget ? 'active' : ''}">
                        <input type="checkbox" bind:checked={widgetPrefs.budget}>
                        <span class="icon">💰</span> <span class="label">Budget</span>
                    </label>
                    <label class="toggle-card {widgetPrefs.zen ? 'active' : ''}">
                        <input type="checkbox" bind:checked={widgetPrefs.zen}>
                        <span class="icon">☯</span> <span class="label">Zen</span>
                    </label>
                    <label class="toggle-card {widgetPrefs.tasks ? 'active' : ''}">
                        <input type="checkbox" bind:checked={widgetPrefs.tasks}>
                        <span class="icon">✅</span> <span class="label">Tasks</span>
                    </label>
                    <label class="toggle-card {widgetPrefs.notes ? 'active' : ''}">
                        <input type="checkbox" bind:checked={widgetPrefs.notes}>
                        <span class="icon">📝</span> <span class="label">Notes</span>
                    </label>
                    <label class="toggle-card {widgetPrefs.love ? 'active' : ''}">
                        <input type="checkbox" bind:checked={widgetPrefs.love}>
                        <span class="icon">❤️</span> <span class="label">Love</span>
                    </label>
                    <label class="toggle-card {widgetPrefs.scribble ? 'active' : ''}">
                        <input type="checkbox" bind:checked={widgetPrefs.scribble}>
                        <span class="icon">✏️</span> <span class="label">Scribble</span>
                    </label>
                </div>
            </div>
            <div class="modal-footer">
                <button class="action-btn cancel" onclick={() => isCustomizing = false}>Cancel</button>
                <button class="action-btn save" onclick={saveLayout}>Save Changes</button>
            </div>
        </div>
    {/if}

    <main class="grid-container">

        <div class="col col-left">
            {#if widgetPrefs.history}
                <div class="card history-card">
                    <div class="icon-box">📜</div>
                    <div class="content">
                        <div class="label">ON THIS DAY {history?.year || '...'}</div>
                        <p>{history?.text || "Loading archives..."}</p>
                    </div>
                </div>
            {/if}

            {#if widgetPrefs.transmission}
                <TransmissionWidget />
            {/if}

            {#if widgetPrefs.news}
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
            {/if}

            {#if widgetPrefs.joke}
                <div class="card joke-card">
                    <div class="card-header">🃏 MORALE BOOST</div>
                    <div class="joke-body">
                        <p class="setup">{joke?.setup || "..."}</p>
                        <p class="punch">{joke?.punchline || ""}</p>
                    </div>
                </div>
            {/if}
        </div>

        <div class="col col-center">
            <section class="mission-section">
                <MissionControl />
            </section>
            
            <section class="workspace-split">
                <div class="ws-col">
                    {#if widgetPrefs.budget}
                        <BudgetWidget />
                    {/if}

                    {#if widgetPrefs.zen}
                        <div class="card zen-card">
                            <div class="zen-icon">☯</div>
                            <p>"{zen?.text || "Stillness is the key."}"</p>
                        </div>
                    {/if}
                </div>

                <div class="ws-col">
                    {#if widgetPrefs.tasks}
                        <TaskWidget />
                    {/if}
                    <BreathingOrb />
                </div>
            </section>
            
            <section class="note-section">
                {#if widgetPrefs.notes}
                    <NoteWidget />
                {/if}
            </section>
        </div>

        <div class="col col-right">
            <HabitMatrix />

            {#if widgetPrefs.love}
                <LoveWidget />
            {/if}
            
            {#if widgetPrefs.scribble}
                <ScribbleWidget />
            {/if}
        </div>

    </main>
</div>

<style>
    /* =========================================
       GLOBAL & THEMES
       ========================================= */
    :global(body) { transition: background 0.5s; }
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
       LAYOUT GRID
       ========================================= */
    .dashboard-layout {
        height: 100vh; display: flex; flex-direction: column;
        padding: 20px 40px; box-sizing: border-box; overflow-y: auto;
    }

    .grid-container {
        display: grid; grid-template-columns: 320px 1fr 320px;
        gap: 24px; flex: 1; max-width: 1920px; margin: 0 auto; width: 100%;
    }

    .col { display: flex; flex-direction: column; gap: 24px; }

    /* =========================================
       HEADER
       ========================================= */
    .top-bar {
        display: grid; grid-template-columns: 250px 1fr 250px;
        align-items: center; margin-bottom: 25px; padding: 10px 0; gap: 20px;
    }
    .brand { display: flex; align-items: center; gap: 15px; }
    .app-logo { height: 40px; width: auto; }
    .logo-text { font-weight: 800; font-size: 1.2rem; letter-spacing: 2px; }

    .search-deck {
        display: flex; align-items: center; gap: 10px;
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255,255,255,0.1);
        padding: 6px 10px; border-radius: 50px;
        width: 100%; max-width: 600px; margin: 0 auto;
        backdrop-filter: blur(12px); transition: 0.3s;
    }
    :global(body.cloudy) .search-deck { background: #fff; border-color: #cbd5e1; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }

    .search-input {
        flex: 1; background: transparent; border: none; outline: none;
        color: inherit; font-family: 'Inter', sans-serif; font-size: 0.9rem;
        padding: 5px 10px; -webkit-appearance: none;
    }
    .search-buttons { display: flex; gap: 5px; }
    .s-btn {
        width: 32px; height: 32px; border-radius: 50%; border: none;
        cursor: pointer; display: flex; align-items: center; justify-content: center;
        transition: 0.2s; color: #fff;
    }
    .s-btn:hover { transform: scale(1.1); }
    .google { background: #4285f4; }
    .header-actions { justify-self: end; display: flex; gap: 10px; }
    .theme-toggle {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        color: inherit; padding: 8px 16px; border-radius: 8px; cursor: pointer;
        font-family: inherit; font-size: 0.85rem; font-weight: 600; transition: 0.2s;
    }
    .theme-toggle:hover { background: rgba(255,255,255,0.1); }
    :global(body.cloudy) .theme-toggle { background: #fff; border-color: #cbd5e1; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }

    /* =========================================
       MODAL: CUSTOMIZATION
       ========================================= */
    .modal-backdrop {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.6); backdrop-filter: blur(4px); z-index: 998;
    }
    .modal-panel {
        position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
        width: 100%; max-width: 800px;
        background: #0f172a; border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px; padding: 0; z-index: 999;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        color: #fff; display: flex; flex-direction: column;
    }
    :global(body.cloudy) .modal-panel { background: #ffffff; color: #0f172a; border-color: #e2e8f0; }

    .modal-header {
        padding: 20px 24px; border-bottom: 1px solid rgba(255,255,255,0.05);
        display: flex; justify-content: space-between; align-items: center;
    }
    :global(body.cloudy) .modal-header { border-bottom-color: #e2e8f0; }
    .modal-header h3 { margin: 0; font-size: 1.2rem; font-weight: 600; }
    .close-btn { background: none; border: none; font-size: 1.2rem; cursor: pointer; color: inherit; opacity: 0.5; }
    .close-btn:hover { opacity: 1; }
    .modal-body { padding: 24px; max-height: 60vh; overflow-y: auto; }
    .toggle-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; }

    .toggle-card {
        display: flex; align-items: center; gap: 12px; padding: 12px 16px;
        background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px; cursor: pointer; transition: 0.2s;
    }
    .toggle-card:hover { background: rgba(255,255,255,0.06); }
    .toggle-card.active { background: rgba(16, 185, 129, 0.1); border-color: rgba(16, 185, 129, 0.4); }
    :global(body.cloudy) .toggle-card { background: #f8fafc; border-color: #e2e8f0; }
    :global(body.cloudy) .toggle-card.active { background: #ecfdf5; border-color: #34d399; }
    .toggle-card input { display: none; }
    .toggle-card .icon { font-size: 1.2rem; }
    .toggle-card .label { font-weight: 500; font-size: 0.95rem; }

    .modal-footer {
        padding: 16px 24px; border-top: 1px solid rgba(255,255,255,0.05);
        display: flex; justify-content: flex-end; gap: 12px;
    }
    :global(body.cloudy) .modal-footer { border-top-color: #e2e8f0; }
    .action-btn {
        padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: 600;
        font-size: 0.9rem; border: none; transition: 0.2s;
    }
    .action-btn.cancel { background: transparent; color: inherit; opacity: 0.7; }
    .action-btn.cancel:hover { opacity: 1; background: rgba(255,255,255,0.05); }
    .action-btn.save { background: #10b981; color: #fff; }
    .action-btn.save:hover { background: #059669; }

    /* =========================================
       WIDGETS & CARDS
       ========================================= */
    .mission-section { width: 100%; }
    .workspace-split { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; width: 100%; }
    .ws-col { display: flex; flex-direction: column; gap: 24px; }
    .note-section { width: 100%; flex: 1; min-height: 400px; display: flex; flex-direction: column; }
    :global(.note-section .notebook-editor), :global(.note-section .app-root) { min-height: 500px; flex: 1; }

    .card {
        background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px); border-radius: 12px; padding: 20px; transition: 0.3s;
    }
    :global(body.cloudy) .card {
        background: #ffffff; border: 1px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0,0,0,0.03); color: #1e293b;
    }

    .history-card { display: flex; gap: 15px; align-items: flex-start; background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), transparent); border-color: rgba(245, 158, 11, 0.2); }
    .history-card .icon-box { font-size: 1.5rem; }
    .history-card .label { font-size: 0.7rem; font-weight: 700; color: #facc15; margin-bottom: 4px; letter-spacing: 1px; }
    :global(body.cloudy) .history-card .label { color: #d97706; }
    .history-card p { margin: 0; font-size: 0.9rem; line-height: 1.4; }

    .news-card { padding: 0; overflow: hidden; }
    .news-card .card-header { padding: 12px 20px; background: rgba(0,0,0,0.1); font-size: 0.75rem; font-weight: 700; opacity: 0.8; letter-spacing: 1px; }
    .news-list { display: flex; flex-direction: column; }
    .news-item { padding: 12px 20px; border-bottom: 1px solid rgba(255,255,255,0.05); text-decoration: none; color: inherit; font-size: 0.9rem; transition: 0.2s; }
    .news-item:hover { background: rgba(255,255,255,0.03); color: #2dd4bf; }
    :global(body.cloudy) .news-item { border-bottom-color: #f1f5f9; }
    :global(body.cloudy) .news-item:hover { background: #f8fafc; color: #0284c7; }
    .loading { padding: 20px; text-align: center; opacity: 0.6; font-size: 0.8rem; font-style: italic; }

    .joke-card { text-align: center; border-left: 4px solid #a855f7; }
    .joke-card .card-header { font-size: 0.7rem; color: #a855f7; font-weight: 700; margin-bottom: 10px; }
    .setup { font-weight: 600; margin-bottom: 4px; }
    .punch { font-style: italic; opacity: 0.8; }

    .zen-card { 
        display: flex; align-items: center; justify-content: center; gap: 15px; 
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), transparent); 
        border-color: rgba(16, 185, 129, 0.2); font-style: italic; color: #10b981; min-height: 80px;
    }
    .zen-icon { font-size: 1.5rem; }
    :global(body.cloudy) .zen-card { background: #ecfdf5; border-color: #d1fae5; color: #059669; }

    /* =========================================
       RESPONSIVE
       ========================================= */
    @media (max-width: 1400px) {
        .dashboard-layout { padding: 10px 20px; }
        .grid-container { grid-template-columns: 300px 1fr; gap: 20px; }
        .col-right { grid-column: span 2; display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .top-bar { grid-template-columns: 200px 1fr 150px; }
    }
    @media (max-width: 850px) {
        :global(body) { overflow-y: auto !important; overflow-x: hidden !important; }
        .dashboard-layout { height: auto; min-height: 100dvh; overflow: visible; padding: 10px; }
        .grid-container { display: flex; flex-direction: column; }
        .top-bar { display: flex; flex-direction: column; gap: 15px; }
        .search-deck { width: 100%; order: 2; }
        .header-actions { order: 1; align-self: flex-end; }
        .workspace-split { grid-template-columns: 1fr; }
        .col-right { display: flex; flex-direction: column; }
    }
</style>