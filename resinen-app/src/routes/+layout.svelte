<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import logo from '$lib/assets/logo.svg';

    // --- AUTH & PAYMENT STATE ---
    let showAuth = $state(false);
    let authMode = $state('login'); 
    let email = $state("");
    let password = $state("");
    let authError = $state("");
    let user = $state<any>(null);
    let isPremium = $state(false);

    // --- STATE MANAGEMENT ---
    function broadcastState() {
        if (user) { localStorage.setItem('resinen_user', JSON.stringify(user)); } 
        else { localStorage.removeItem('resinen_user'); }
        if (typeof window !== 'undefined') window.dispatchEvent(new Event('resinen-auth-change'));
    }

    async function handleAuth() {
        authError = "";
        try {
            setTimeout(() => {
                user = { email: email || "test@resinen.com", token: "mock-token", is_premium: false };
                isPremium = false;
                broadcastState();
                showAuth = false;
                email = ""; password = "";
                window.location.reload(); 
            }, 500);
        } catch (e) { authError = "System Offline"; }
    }

    function logout() {
        if(confirm('Disconnect Neural Link?')) {
            user = null; isPremium = false;
            broadcastState();
            window.location.reload();
        }
    }

    async function simulatePayment() {
        if (!user) { showAuth = true; return; }
        if(confirm("Initialize Mock Payment Gateway?")) {
            alert("Contacting Bank Servers...");
            setTimeout(() => {
                user.is_premium = true;
                isPremium = true;
                broadcastState();
                alert("PAYMENT SUCCESSFUL. SYSTEM UNLOCKED.");
                window.location.reload();
            }, 1500);
        }
    }

    onMount(async () => {
        if (typeof localStorage !== 'undefined') {
            const saved = localStorage.getItem('resinen_user');
            if (saved) {
                user = JSON.parse(saved);
                isPremium = user.is_premium;
            }
        }
    });
</script>

<svelte:head>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Space+Grotesk:wght@400;700&display=swap" rel="stylesheet">
</svelte:head>

<div class="layout-shell">
    
    <div class="command-dock">
        <a href="/" class="dock-item home">
            <img src={logo} alt="Resinen" />
            <span class="label">Focus</span>
        </a>

        <div class="divider"></div>

        <div class="dock-apps">
            <a href="/apps/cinema" class="app-link"><span>🎬</span><div class="tooltip">Cinema</div></a>
            <a href="/games/chess" class="app-link"><span>♟️</span><div class="tooltip">Chess</div></a>
            <a href="/games/poker" class="app-link"><span>♠️</span><div class="tooltip">Poker</div></a>
            <a href="/games/go" class="app-link"><span>⚪</span><div class="tooltip">Go</div></a>
            <a href="/games/tetris" class="app-link"><span>🕹️</span><div class="tooltip">Tetris</div></a>
            <a href="/games/sudoku" class="app-link"><span>🔢</span><div class="tooltip">Sudoku</div></a>
            <a href="/games/ludo" class="app-link"><span>🎲</span><div class="tooltip">Ludo</div></a>
            <a href="/games/minesweeper" class="app-link"><span>💣</span><div class="tooltip">Minesweeper</div></a>
            <a href="/games/snake" class="app-link"><span>🐍</span><div class="tooltip">Snake</div></a>
            <a href="/games/runner" class="app-link"><span>🏃</span><div class="tooltip">Runner</div></a>
            <a href="/games/2048" class="app-link"><span>🧱</span><div class="tooltip">2048</div></a>
            <a href="/games/battleship" class="app-link"><span>🚢</span><div class="tooltip">Battleship</div></a>
        </div>

        <div class="divider"></div>

        <div class="dock-auth">
            {#if user}
                <button class="user-pill" class:premium={isPremium} onclick={() => !isPremium && simulatePayment()} title={isPremium ? "Pro License Active" : "Click to Upgrade"}>
                    <div class="status-dot"></div>
                    <span>{isPremium ? 'PRO' : 'UPG'}</span>
                </button>
                <button class="logout-icon" onclick={logout} title="Disconnect">⏻</button>
            {:else}
                <button class="login-btn" onclick={() => showAuth = true}>
                    <span>👤</span> <span class="label">Login</span>
                </button>
            {/if} 
        </div>
    </div>

    {#if showAuth}
        <div class="auth-overlay">
            <div class="auth-glass" class:shake={authError}>
                <button class="close-auth" onclick={() => showAuth = false}>×</button>
                <div class="auth-header">
                    <h2>{authMode === 'login' ? 'SYSTEM LOGIN' : 'NEW OPERATOR'}</h2>
                    <div class="auth-sub">MOCK MODE ACTIVE</div>
                </div>
                <div class="auth-form">
                    <div class="input-group">
                        <label for="email">IDENTITY</label>
                        <input type="email" id="email" bind:value={email} placeholder="any@email.com" />
                    </div>
                    <div class="input-group">
                        <label for="password">ACCESS CODE</label>
                        <input type="password" id="password" bind:value={password} placeholder="any password" onkeydown={(e) => e.key === 'Enter' && handleAuth()} />
                    </div>
                    {#if authError}<div class="error-msg">{authError}</div>{/if}
                    <button class="action-btn" onclick={handleAuth}>{authMode === 'login' ? 'AUTHENTICATE' : 'INITIALIZE'}</button>
                </div>
            </div>
        </div>
    {/if}

    <main class="page-content" class:blurred={showAuth}>
        {#if $page.url.pathname.startsWith('/games') && !isPremium}
            <div class="paywall-overlay">
                <div class="paywall-card">
                    <h1>ACCESS DENIED</h1>
                    <p>Advanced neural training requires a Premium License.</p>
                    <div class="price">₹499 / Lifetime</div>
                    <button class="upgrade-btn" onclick={simulatePayment}>UNLOCK SYSTEM (MOCK)</button>
                    <a href="/" class="retreat-link">Retreat to Dashboard</a>
                </div>
            </div>
        {:else}
            <slot />
        {/if}
    </main>
</div>

<style>
    /* GLOBAL SETUP */
    :global(html) { height: 100%; overflow-y: scroll; scroll-behavior: smooth; }
    :global(body) { 
        margin: 0; min-height: 100vh;
        background-color: #020617; color: #f8fafc; 
        font-family: 'Space Grotesk', sans-serif; 
        overflow-x: hidden; position: relative;
    }
    :global(:root) { --accent: #2dd4bf; --card: rgba(30, 41, 59, 0.7); --border: #334155; --mono: 'JetBrains Mono', monospace; }
    :global(*) { box-sizing: border-box; }
    
    .layout-shell { min-height: 100vh; position: relative; display: flex; flex-direction: column; }
    .page-content { flex: 1; position: relative; z-index: 1; transition: filter 0.3s; width: 100%; }
    .page-content.blurred { filter: blur(5px) brightness(0.7); pointer-events: none; }

    /* --- MERGED COMMAND DOCK --- */
    .command-dock { 
        position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
        background: rgba(15, 23, 42, 0.9); 
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 8px 16px;
        display: flex; align-items: center; gap: 12px;
        z-index: 9999;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        backdrop-filter: blur(12px);
        max-width: 95vw;
        overflow-x: auto; /* Allow scroll on small screens */
        white-space: nowrap;
    }

    .divider { width: 1px; height: 24px; background: rgba(255,255,255,0.1); flex-shrink: 0; }

    /* HOME ITEM */
    .dock-item.home { 
        display: flex; align-items: center; gap: 8px; 
        text-decoration: none; color: #fff; 
        padding-right: 5px; transition: 0.2s;
    }
    .dock-item.home img { height: 24px; width: auto; filter: drop-shadow(0 0 5px rgba(45, 212, 191, 0.5)); }
    .dock-item.home .label { font-family: 'Space Grotesk'; font-weight: bold; font-size: 0.9rem; }
    .dock-item.home:hover { opacity: 0.8; transform: scale(1.05); }

    /* APPS GRID */
    .dock-apps { display: flex; gap: 10px; align-items: center; }
    .app-link { 
        position: relative; font-size: 1.4rem; text-decoration: none; 
        transition: 0.2s; opacity: 0.7; filter: grayscale(100%);
        width: 36px; height: 36px; display: flex; justify-content: center; align-items: center;
    }
    .app-link:hover { transform: translateY(-5px) scale(1.1); opacity: 1; filter: grayscale(0%); }
    
    /* TOOLTIP */
    .tooltip { 
        position: absolute; bottom: 110%; left: 50%; transform: translateX(-50%);
        background: var(--accent); color: #000; padding: 2px 6px; border-radius: 4px;
        font-family: var(--mono); font-size: 0.65rem; font-weight: bold; pointer-events: none;
        opacity: 0; transition: 0.2s; white-space: nowrap; box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }
    .app-link:hover .tooltip { opacity: 1; transform: translateX(-50%) translateY(-5px); }

    /* AUTH ITEMS */
    .dock-auth { display: flex; gap: 8px; align-items: center; }
    
    .user-pill {
        background: rgba(255,255,255,0.05); border: 1px solid var(--border);
        color: #94a3b8; padding: 4px 10px; border-radius: 20px;
        display: flex; align-items: center; gap: 6px; cursor: pointer; transition: 0.2s;
        font-family: var(--mono); font-size: 0.75rem;
    }
    .user-pill:hover { background: rgba(255,255,255,0.1); color: #fff; }
    .user-pill.premium { border-color: #facc15; color: #facc15; }
    .user-pill.premium .status-dot { background: #facc15; box-shadow: 0 0 5px #facc15; }
    
    .status-dot { width: 6px; height: 6px; background: #64748b; border-radius: 50%; }
    
    .logout-icon { 
        background: none; border: none; color: #ef4444; font-size: 0.9rem; 
        cursor: pointer; padding: 5px; opacity: 0.7; transition: 0.2s; 
    }
    .logout-icon:hover { opacity: 1; transform: scale(1.1); }

    .login-btn {
        background: transparent; border: 1px solid var(--accent); color: var(--accent);
        padding: 4px 12px; border-radius: 20px; cursor: pointer; font-family: var(--mono);
        font-size: 0.75rem; display: flex; align-items: center; gap: 6px; transition: 0.2s;
    }
    .login-btn:hover { background: var(--accent); color: #000; }

    /* --- AUTH & PAYWALL OVERLAYS --- */
    .auth-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 10000; display: flex; justify-content: center; align-items: center; background: rgba(2, 6, 23, 0.4); }
    .auth-glass { width: 400px; padding: 40px; border-radius: 16px; background: rgba(30, 41, 59, 0.6); backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5); position: relative; animation: slideIn 0.3s ease-out; }
    .auth-glass.shake { animation: shake 0.4s; border-color: #ef4444; }
    .close-auth { position: absolute; top: 15px; right: 20px; background: none; border: none; color: #94a3b8; font-size: 1.5rem; cursor: pointer; }
    .auth-header { text-align: center; margin-bottom: 30px; }
    .auth-header h2 { margin: 0; color: #2dd4bf; letter-spacing: 2px; text-shadow: 0 0 15px rgba(45, 212, 191, 0.3); }
    .auth-sub { font-family: 'JetBrains Mono'; font-size: 0.7rem; color: #94a3b8; margin-top: 5px; }
    .input-group { margin-bottom: 20px; }
    .input-group label { display: block; font-family: 'JetBrains Mono'; font-size: 0.7rem; color: #94a3b8; margin-bottom: 5px; }
    .input-group input { width: 100%; padding: 12px; background: rgba(0, 0, 0, 0.3); border: 1px solid #334155; border-radius: 6px; color: #fff; font-family: 'Space Grotesk'; outline: none; transition: 0.2s; }
    .input-group input:focus { border-color: #2dd4bf; box-shadow: 0 0 10px rgba(45, 212, 191, 0.2); }
    .error-msg { color: #ef4444; font-family: 'JetBrains Mono'; font-size: 0.7rem; margin-bottom: 15px; text-align: center; }
    .action-btn { width: 100%; padding: 15px; background: #2dd4bf; color: #020617; border: none; border-radius: 6px; font-weight: bold; font-family: 'JetBrains Mono'; cursor: pointer; transition: 0.2s; }
    .action-btn:hover { background: #fff; box-shadow: 0 0 20px #2dd4bf; }

    .paywall-overlay { height: 80vh; display: flex; justify-content: center; align-items: center; background: radial-gradient(circle, rgba(15,23,42,0.9), #020617); z-index: 50; }
    .paywall-card { text-align: center; border: 2px solid #ef4444; padding: 40px; background: rgba(0,0,0,0.8); backdrop-filter: blur(10px); border-radius: 12px; box-shadow: 0 0 50px rgba(239, 68, 68, 0.3); animation: shake 0.5s; width: 90%; max-width: 500px; }
    .paywall-card h1 { color: #ef4444; font-size: 2.5rem; margin: 0 0 10px 0; letter-spacing: 5px; }
    .paywall-card p { color: #94a3b8; font-family: 'JetBrains Mono'; margin-bottom: 20px; }
    .price { font-size: 2rem; color: #fff; margin-bottom: 30px; font-weight: bold; }
    .upgrade-btn { background: #ef4444; color: #000; border: none; padding: 15px 40px; font-size: 1.2rem; font-weight: bold; cursor: pointer; font-family: 'JetBrains Mono'; transition: 0.2s; border-radius: 6px; }
    .upgrade-btn:hover { background: #fff; box-shadow: 0 0 30px #ef4444; }
    .retreat-link { display: block; margin-top: 20px; color: #64748b; font-size: 0.8rem; font-family: 'JetBrains Mono'; }
    
    @keyframes shake { 0%, 100% { transform: translateX(0); } 25% { transform: translateX(-5px); } 75% { transform: translateX(5px); } }
    @keyframes slideIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>