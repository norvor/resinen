<script lang="ts">
    import { onMount } from 'svelte';
    import { authState, login, logout as storeLogout } from '$lib/stores';
    import { api } from '$lib/api';
    import { fade, fly, slide } from 'svelte/transition'; // Added slide
    import { cubicOut } from 'svelte/easing';
    import logo from '$lib/assets/logo.svg';

    // --- CONFIGURATION ---
    const APPS = [
        { name: 'Cinema', icon: '🎹', path: '/apps/cinema' },
        { name: 'Cosmos', icon: '🌌', path: '/apps/studio' },
        { name: 'TimePass', icon: '📙', path: '/apps/timepass' },
    ];

    const GAMES = [
        { name: '2048', icon: '🔢', path: '/games/2048' },
        { name: 'Battleship', icon: '🚢', path: '/games/battleship' },
        { name: 'Chess', icon: '♟️', path: '/games/chess' },
        { name: 'Cricket', icon: '🏏', path: '/games/cricket' },
        { name: 'Go', icon: '⚪', path: '/games/go' },
        { name: 'Minesweeper', icon: '💣', path: '/games/minesweeper' },
        { name: 'Poker', icon: '♠️', path: '/games/poker' },
        { name: 'Runner', icon: '🏃', path: '/games/runner' },
        { name: 'Snake', icon: '🐍', path: '/games/snake' },
        { name: 'Soccer', icon: '⚽', path: '/games/soccer' },
        { name: 'Sudoku', icon: '🧩', path: '/games/sudoku' },
        { name: 'Tetris', icon: '🧱', path: '/games/tetris' },
        { name: 'Ludo', icon: '🌈', path: '/games/ludo' }
    ];

    // --- AUTH STATE ---
    let isAuthenticated = $state(false);
    authState.subscribe(val => isAuthenticated = val.isAuthenticated);

    // Login Form State
    let email = $state("");
    let password = $state("");
    let error = $state("");
    let loading = $state(false);

    // --- DOCK UI STATE ---
    let isMinimized = $state(false);
    let activeDrawer = $state<string | null>(null); // 'apps' | 'games' | null
    
    // Drag Physics
    let orbX = $state(0);
    let orbY = $state(0);
    let isDragging = $state(false);
    let startX = 0, startY = 0;
    let initialOrbX = 0, initialOrbY = 0;
    let hasDragged = $state(false); 

    // --- ACTIONS ---
    function toggleDrawer(drawerId: string) {
        if (activeDrawer === drawerId) {
            activeDrawer = null;
        } else {
            activeDrawer = drawerId;
        }
    }

    async function handleLogin() {
        loading = true; error = "";
        try {
            const data = await api.auth.login(email, password);
            login(data.access_token); 
        } catch(e) {
            error = "Access Denied: Invalid Credentials";
        }
        loading = false;
    }

    function handleLogout() {
        if(confirm('Disconnect Neural Link?')) {
            storeLogout();
        }
    }

    // --- DOCK DRAG PHYSICS ---
    function onDragStart(e: MouseEvent | TouchEvent) {
        isDragging = true;
        hasDragged = false;
        
        const clientX = 'touches' in e ? e.touches[0].clientX : (e as MouseEvent).clientX;
        const clientY = 'touches' in e ? e.touches[0].clientY : (e as MouseEvent).clientY;

        startX = clientX;
        startY = clientY;
        initialOrbX = orbX;
        initialOrbY = orbY;
        
        window.addEventListener('mousemove', onDragMove);
        window.addEventListener('mouseup', onDragEnd);
        window.addEventListener('touchmove', onDragMove, { passive: false });
        window.addEventListener('touchend', onDragEnd);
    }

    function onDragMove(e: MouseEvent | TouchEvent) {
        if (!isDragging) return;
        
        const clientX = 'touches' in e ? e.touches[0].clientX : (e as MouseEvent).clientX;
        const clientY = 'touches' in e ? e.touches[0].clientY : (e as MouseEvent).clientY;

        const dx = clientX - startX;
        const dy = clientY - startY;

        if (Math.abs(dx) > 5 || Math.abs(dy) > 5) hasDragged = true;

        orbX = initialOrbX + dx;
        orbY = initialOrbY + dy;
    }

    function onDragEnd() {
        isDragging = false;
        window.removeEventListener('mousemove', onDragMove);
        window.removeEventListener('mouseup', onDragEnd);
        window.removeEventListener('touchmove', onDragMove);
        window.removeEventListener('touchend', onDragEnd);
    }

    function handleOrbClick() {
        if (!hasDragged) isMinimized = false;
    }

    function handleMinimize() {
        isMinimized = true;
        activeDrawer = null; // Close drawers on minimize
    }

    onMount(() => {
        // Set initial position (Bottom Center)
        orbX = window.innerWidth / 2 - 30;
        orbY = window.innerHeight - 100;
    });
</script>

<svelte:head>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;700&family=Space+Grotesk:wght@400;700&display=swap" rel="stylesheet">
</svelte:head>

{#if isAuthenticated}
    {#if isMinimized}
        <button 
            class="dock-restore-btn" 
            style="
                left: {orbX}px; 
                top: {orbY}px; 
                cursor: {isDragging ? 'grabbing' : 'grab'};
                transition: {isDragging ? 'none' : 'transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1)'};
            "
            onmousedown={onDragStart}
            ontouchstart={onDragStart}
            onclick={handleOrbClick}
            transition:fly={{ y: 50, duration: 400, easing: cubicOut }}
            aria-label="Open Dock"
        >
            <div class="restore-glow"></div>
            <img src={logo} alt="Resinen" />
        </button>
    {/if}

    <div class="dock-wrapper" class:hidden={isMinimized}>
        
        {#if activeDrawer}
            <div class="dock-drawer" transition:fly={{ y: 20, duration: 300, easing: cubicOut }}>
                <div class="drawer-header">
                    <span>{activeDrawer === 'apps' ? 'APPLICATIONS' : 'ENTERTAINMENT'}</span>
                    <button class="close-drawer" onclick={() => activeDrawer = null}>×</button>
                </div>
                <div class="drawer-grid">
                    {#if activeDrawer === 'apps'}
                        {#each APPS as app}
                            <a href={app.path} class="drawer-item" onclick={() => activeDrawer = null}>
                                <span class="d-icon">{app.icon}</span>
                                <span class="d-name">{app.name}</span>
                            </a>
                        {/each}
                    {:else}
                        {#each GAMES as game}
                            <a href={game.path} class="drawer-item" onclick={() => activeDrawer = null}>
                                <span class="d-icon">{game.icon}</span>
                                <span class="d-name">{game.name}</span>
                            </a>
                        {/each}
                    {/if}
                </div>
            </div>
        {/if}

        <button class="minimize-tab" onclick={handleMinimize} aria-label="Minimize Dock">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
        </button>

        <div class="command-dock">
            <a href="/" class="dock-item home">
                <img src={logo} alt="Resinen" />
                <span class="label">Zen</span>
            </a>

            <div class="divider"></div>

            <div class="dock-scroll-area desktop-view">
                <div class="dock-apps">
                    {#each APPS as app}
                        <a href={app.path} class="app-link">
                            <span>{app.icon}</span>
                            <div class="tooltip">{app.name}</div>
                        </a>
                    {/each}

                    <div class="mini-divider"></div>

                    {#each GAMES as game}
                        <a href={game.path} class="app-link">
                            <span>{game.icon}</span>
                            <div class="tooltip">{game.name}</div>
                        </a>
                    {/each}
                </div>
            </div>

            <div class="dock-mobile-controls mobile-view">
                <button class="mobile-folder" 
                    class:active={activeDrawer === 'apps'} 
                    onclick={() => toggleDrawer('apps')}>
                    <span class="icon">🚀</span>
                    <span class="label">Apps</span>
                </button>
                
                <button class="mobile-folder" 
                    class:active={activeDrawer === 'games'}
                    onclick={() => toggleDrawer('games')}>
                    <span class="icon">🎮</span>
                    <span class="label">Games</span>
                </button>
            </div>

            <div class="divider"></div>

            <div class="dock-auth">
                <button class="logout-icon" onclick={handleLogout} title="Disconnect">Logout</button>
            </div>
        </div>
    </div>

    <slot />
{:else}
    <div class="login-overlay">
        <div class="login-card">
            <div class="login-header">
                <div class="logo-mark">R</div>
                <h1>SYSTEM ACCESS</h1>
            </div>
            
            <div class="login-body">
                <input type="text" placeholder="OPERATOR ID" bind:value={email} />
                <input type="password" placeholder="PASSCODE" bind:value={password} onkeydown={e => e.key === 'Enter' && handleLogin()} />
                
                {#if error}
                    <div class="error-msg">{error}</div>
                {/if}

                <button onclick={handleLogin} disabled={loading}>
                    {loading ? 'AUTHENTICATING...' : 'INITIALIZE UPLINK'}
                </button>
            </div>
        </div>
    </div>
{/if}

<style>
    /* --- GLOBAL SETUP --- */
    :global(body) {
        margin: 0; padding: 0;
        font-family: 'Inter', sans-serif;
        background: #020617; color: #e2e8f0;
        overflow: hidden;
    }
    :global(*) { box-sizing: border-box; }
    :global(:root) { --accent: #2dd4bf; --card: rgba(30, 41, 59, 0.7); --border: #334155; --mono: 'JetBrains Mono', monospace; }

    /* --- LOGIN STYLES --- */
    .login-overlay {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: #020617; display: flex; align-items: center; justify-content: center; z-index: 9999;
    }
    .login-card {
        background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(45, 212, 191, 0.2);
        backdrop-filter: blur(20px); padding: 40px; border-radius: 12px;
        width: 100%; max-width: 400px; box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        animation: fadeIn 0.5s ease-out;
    }
    .login-header { display: flex; align-items: center; gap: 15px; margin-bottom: 30px; }
    .logo-mark {
        width: 40px; height: 40px; background: #2dd4bf; color: #000;
        font-weight: 900; display: flex; align-items: center; justify-content: center;
        border-radius: 8px; font-size: 1.5rem;
    }
    h1 { margin: 0; color: #fff; font-size: 1.2rem; letter-spacing: 2px; }
    .login-body { display: flex; flex-direction: column; gap: 15px; }
    input { background: rgba(0,0,0,0.3); border: 1px solid #334155; color: #fff; padding: 12px; border-radius: 6px; font-family: 'JetBrains Mono', monospace; outline: none; }
    input:focus { border-color: #2dd4bf; background: rgba(45, 212, 191, 0.05); }
    button { background: #2dd4bf; color: #000; border: none; padding: 12px; font-weight: 800; cursor: pointer; border-radius: 6px; margin-top: 10px; }
    .error-msg { color: #ef4444; font-size: 0.8rem; text-align: center; }

    /* --- RESTORE BUTTON (FLOATING) --- */
    .dock-restore-btn {
        position: fixed; width: 60px; height: 60px; border-radius: 50%;
        background: rgba(15, 23, 42, 0.8); border: 2px solid var(--accent);
        display: flex; justify-content: center; align-items: center; z-index: 9990;
        backdrop-filter: blur(10px); box-shadow: 0 0 30px rgba(45, 212, 191, 0.2);
        touch-action: none;
    }
    .dock-restore-btn img { width: 32px; filter: drop-shadow(0 0 5px var(--accent)); pointer-events: none; }
    .restore-glow { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border-radius: 50%; animation: pulse-ring 2s infinite; border: 1px solid var(--accent); opacity: 0; pointer-events: none; }

    /* --- DOCK WRAPPER --- */
    .dock-wrapper {
        position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); z-index: 9999;
        display: flex; flex-direction: column; align-items: center;
        transition: transform 0.5s cubic-bezier(0.2, 0.8, 0.2, 1), opacity 0.4s;
        max-width: 95vw;
    }
    .dock-wrapper.hidden { transform: translateX(-50%) translateY(160%); opacity: 0; pointer-events: none; }

    /* --- DRAWER (Mobile) --- */
    .dock-drawer {
        position: absolute; bottom: 100%; margin-bottom: 12px;
        width: 320px; max-width: 90vw;
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        backdrop-filter: blur(20px);
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        padding: 16px;
        display: flex; flex-direction: column; gap: 10px;
    }
    .drawer-header {
        display: flex; justify-content: space-between; align-items: center;
        font-family: var(--mono); font-size: 0.7rem; color: #94a3b8; font-weight: bold;
        border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px;
    }
    .close-drawer { background: none; border: none; color: #fff; font-size: 1.2rem; cursor: pointer; padding: 0 5px; }
    
    .drawer-grid {
        display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;
    }
    .drawer-item {
        display: flex; flex-direction: column; align-items: center; gap: 5px;
        text-decoration: none; color: #e2e8f0;
        padding: 10px 5px; border-radius: 8px;
        transition: 0.2s;
    }
    .drawer-item:hover { background: rgba(255,255,255,0.1); }
    .drawer-item .d-icon { font-size: 1.8rem; }
    .drawer-item .d-name { font-size: 0.65rem; text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; width: 100%; opacity: 0.8; }

    /* --- MINIMIZE TAB --- */
    .minimize-tab {
        background: rgba(15, 23, 42, 0.95); border: 1px solid rgba(255, 255, 255, 0.15); border-bottom: none;
        width: 60px; height: 24px; border-radius: 12px 12px 0 0; display: flex; justify-content: center; align-items: center;
        cursor: pointer; color: #94a3b8; transition: all 0.2s ease; margin-bottom: -1px; z-index: 2;
    }
    .minimize-tab svg { width: 16px; height: 16px; }

    /* --- MAIN DOCK --- */
    .command-dock { 
        background: rgba(15, 23, 42, 0.9); border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px; padding: 10px 20px; display: flex; align-items: center; gap: 16px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.6); backdrop-filter: blur(16px);
        max-width: 100%;
    }

    .divider { width: 1px; height: 24px; background: rgba(255,255,255,0.15); flex-shrink: 0; }
    .mini-divider { width: 1px; height: 16px; background: rgba(255,255,255,0.1); flex-shrink: 0; margin: 0 5px; }

    .dock-item.home { display: flex; align-items: center; gap: 10px; text-decoration: none; color: #fff; transition: 0.2s; flex-shrink: 0; }
    .dock-item.home img { height: 28px; width: auto; }
    .dock-item.home .label { font-weight: bold; font-family: 'Space Grotesk'; }

    /* DESKTOP VIEW */
    .dock-scroll-area {
        overflow-x: auto; overflow-y: hidden;
        max-width: 60vw; padding-bottom: 4px; scrollbar-width: none;
    }
    .dock-scroll-area::-webkit-scrollbar { display: none; } 
    .dock-apps { display: flex; gap: 12px; align-items: center; padding: 0 5px; }
    
    .app-link { 
        position: relative; font-size: 1.5rem; text-decoration: none; opacity: 0.7; 
        width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; 
        transition: 0.2s cubic-bezier(0.2, 0.8, 0.2, 1); flex-shrink: 0;
    }
    .app-link:hover { opacity: 1; transform: translateY(-5px) scale(1.15); }
    
    .tooltip { 
        position: absolute; bottom: 125%; left: 50%; transform: translateX(-50%);
        background: var(--accent); color: #000; padding: 4px 8px; border-radius: 6px;
        font-family: var(--mono); font-size: 0.7rem; font-weight: bold; opacity: 0; 
        transition: 0.2s; white-space: nowrap; pointer-events: none;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    .app-link:hover .tooltip { opacity: 1; transform: translateX(-50%) translateY(-5px); }

    /* MOBILE VIEW CONTROLS */
    .dock-mobile-controls { display: none; gap: 10px; }
    .mobile-folder {
        background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px; padding: 5px 12px; display: flex; flex-direction: column; align-items: center; justify-content: center;
        cursor: pointer; transition: 0.2s; min-width: 60px;
    }
    .mobile-folder.active { background: rgba(45, 212, 191, 0.2); border-color: var(--accent); }
    .mobile-folder .icon { font-size: 1.2rem; margin-bottom: 2px; }
    .mobile-folder .label { font-size: 0.6rem; color: #cbd5e1; font-family: var(--mono); }

    .logout-icon { background: none; border: none; color: #ef4444; font-size: 1.1rem; cursor: pointer; transition: 0.2s; flex-shrink: 0; }
    .logout-icon:hover { transform: scale(1.1); color: #f87171; }

    /* RESPONSIVE SWITCHING */
    @media (max-width: 768px) {
        .desktop-view { display: none; }
        .mobile-view { display: flex; }
        .command-dock { padding: 10px 15px; }
    }
    @media (min-width: 769px) {
        .desktop-view { display: block; }
        .mobile-view { display: none; }
    }

    @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes pulse-ring { 0% { transform: scale(1); opacity: 0.5; } 100% { transform: scale(1.5); opacity: 0; } }
</style>