<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';

    // --- GLOBAL AUDIO STATE ---
    let audioConfig = $state<any>(null);
    let activeAudioKey = $state('lotr');
    let isPlaying = $state(false);
    let currentTrack = $derived(audioConfig ? audioConfig[activeAudioKey] : null);
    let audioUrl = $derived(currentTrack ? `https://www.youtube-nocookie.com/embed/${currentTrack.id}?autoplay=1&controls=0&disablekb=1&fs=0&loop=1&playlist=${currentTrack.id}&modestbranding=1` : '');

    function setAudio(key: string) { activeAudioKey = key; if (!isPlaying) isPlaying = true; }
    function toggleAudio() { isPlaying = !isPlaying; }

    // --- DRAGGABLE PORTAL ---
    let videoX = $state(20); let videoY = $state(80);
    let isDragging = $state(false); let startX = 0, startY = 0;
    function startDrag(e: MouseEvent) { isDragging = true; startX = e.clientX - videoX; startY = e.clientY - videoY; window.addEventListener('mousemove', onDrag); window.addEventListener('mouseup', stopDrag); }
    function onDrag(e: MouseEvent) { if (!isDragging) return; videoX = e.clientX - startX; videoY = e.clientY - startY; }
    function stopDrag() { isDragging = false; window.removeEventListener('mousemove', onDrag); window.removeEventListener('mouseup', stopDrag); }

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
        if (user) {
            localStorage.setItem('resinen_user', JSON.stringify(user));
        } else {
            localStorage.removeItem('resinen_user');
        }
        if (typeof window !== 'undefined') window.dispatchEvent(new Event('resinen-auth-change'));
    }

    async function handleAuth() {
        authError = "";
        try {
            // FAUX AUTH FOR TESTING (Accepts any email/pass)
            // To restore real auth, uncomment the fetch block below
            /*
            const endpoint = authMode === 'login' ? '/auth/login' : '/auth/signup';
            const res = await fetch(`http://localhost:8000${endpoint}`, { ... });
            */
            
            // SIMULATED LOGIN SUCCESS
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
            user = null;
            isPremium = false;
            broadcastState();
            window.location.reload();
        }
    }

    // --- FAUX PAYMENT LOGIC ---
    async function simulatePayment() {
        if (!user) { showAuth = true; return; }

        if(confirm("Initialize Mock Payment Gateway?")) {
            // Fake processing delay
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
        try {
            const res = await fetch('http://localhost:8000/dashboard/audio');
            audioConfig = await res.json();
        } catch (e) { }
    });
</script>

<svelte:head>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Space+Grotesk:wght@400;700&display=swap" rel="stylesheet">
    </svelte:head>

<div class="layout-shell">
    
    {#if isPlaying && currentTrack}
        <div class="video-portal" style="left: {videoX}px; top: {videoY}px;" onmousedown={startDrag} role="button" tabindex="0">
            <div class="portal-handle"><span>:: {currentTrack.name}</span><button class="close-btn" onclick={toggleAudio}>×</button></div>
            <div class="portal-screen">
                {#if isDragging}<div class="drag-shield"></div>{/if}
                <iframe src={audioUrl} title="Portal" frameborder="0" allow="autoplay"></iframe>
            </div>
        </div>
    {/if}

    {#if audioConfig}
        <div class="global-dock">
            <div class="dock-inner">
                
                {#if user}
                    <button class="logout-btn" onclick={logout} title="Sign Out">⏻</button>
                {/if}

                {#if user}
                    <button 
                        class="user-btn logged-in" 
                        class:upgrade-mode={!isPremium}
                        onclick={() => !isPremium && simulatePayment()} 
                        title={isPremium ? `Operator: ${user.email}` : "Click to Upgrade"}
                    >
                        <span class="online-dot" class:premium={isPremium}></span> 
                        {isPremium ? 'PRO' : 'UPGRADE'}
                    </button>
                {:else}
                    <button class="user-btn" onclick={() => showAuth = true}>👤</button>
                {/if}

                <div class="sep"></div>

                <div class="eq-visual" class:active={isPlaying}><span></span><span></span><span></span></div>
                
                {#each ['lotr', 'disney', 'hp', 'atla'] as key}
                    <button class="channel-btn" class:active={activeAudioKey === key} style="--glow: {audioConfig[key].color}" onclick={() => setAudio(key)}>{audioConfig[key].icon}</button>
                {/each}
                
                <div class="sep"></div>
                <button class="power-btn" onclick={toggleAudio} class:on={isPlaying}>{isPlaying ? 'PAUSE' : 'PLAY'}</button>
            </div>
        </div>
    {/if}

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
    /* ... keep all previous styles ... */
    :global(body) { margin: 0; background-color: #020617; color: #f8fafc; font-family: 'Space Grotesk', sans-serif; overflow-x: hidden; }
    :global(*) { box-sizing: border-box; }
    
    .layout-shell { min-height: 100vh; position: relative; }
    .page-content { position: relative; z-index: 1; transition: filter 0.3s; }
    .page-content.blurred { filter: blur(5px) brightness(0.7); pointer-events: none; }

    .global-dock { position: fixed; top: 20px; left: 50%; transform: translateX(-50%); z-index: 9999; width: 90%; max-width: 480px; pointer-events: none; }
    .dock-inner { pointer-events: auto; background: rgba(15, 23, 42, 0.95); border: 1px solid #334155; border-radius: 50px; padding: 8px 20px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 10px 30px rgba(0,0,0,0.5); backdrop-filter: blur(10px); gap: 10px; }

    /* CONTROLS */
    .channel-btn { background: transparent; border: none; font-size: 1.2rem; cursor: pointer; opacity: 0.5; transition: 0.2s; padding: 0 5px; }
    .channel-btn:hover { opacity: 1; transform: scale(1.2); }
    .channel-btn.active { opacity: 1; text-shadow: 0 0 10px var(--glow); transform: scale(1.1); }
    
    /* LOGOUT BUTTON */
    .logout-btn { 
        background: transparent; border: 1px solid #334155; color: #94a3b8; 
        width: 30px; height: 30px; border-radius: 50%; 
        font-size: 0.8rem; cursor: pointer; transition: 0.2s;
        display: flex; align-items: center; justify-content: center;
    }
    .logout-btn:hover { color: #ef4444; border-color: #ef4444; }

    /* USER BUTTON */
    .user-btn { background: transparent; border: none; font-size: 1.2rem; cursor: pointer; opacity: 0.8; transition: 0.2s; display: flex; align-items: center; gap: 5px; }
    .user-btn:hover { transform: scale(1.1); opacity: 1; }
    .user-btn.logged-in { font-family: 'JetBrains Mono'; font-size: 0.8rem; font-weight: bold; color: #94a3b8; }
    
    .user-btn.upgrade-mode { color: #facc15; animation: pulse-gold 2s infinite; }
    @keyframes pulse-gold { 
        0% { text-shadow: 0 0 0 rgba(250, 204, 21, 0); }
        50% { text-shadow: 0 0 10px rgba(250, 204, 21, 0.5); }
        100% { text-shadow: 0 0 0 rgba(250, 204, 21, 0); }
    }

    .online-dot { width: 8px; height: 8px; background: #64748b; border-radius: 50%; box-shadow: 0 0 5px #64748b; }
    .online-dot.premium { background: #facc15; box-shadow: 0 0 8px #facc15; }

    .sep { width: 1px; height: 20px; background: #334155; margin: 0 5px; }
    .power-btn { background: transparent; border: 1px solid #ef4444; color: #ef4444; font-family: 'JetBrains Mono'; font-size: 0.7rem; font-weight: bold; padding: 4px 10px; border-radius: 4px; cursor: pointer; transition: 0.2s; }
    .power-btn.on { border-color: #2dd4bf; color: #2dd4bf; }

    .eq-visual { display: flex; gap: 2px; height: 10px; align-items: flex-end; margin-right: 5px; }
    .eq-visual span { width: 3px; background: #94a3b8; height: 2px; transition: 0.1s; }
    .eq-visual.active span { background: #2dd4bf; }
    .eq-visual.active span:nth-child(1) { animation: bounce 0.5s infinite alternate; }
    .eq-visual.active span:nth-child(2) { animation: bounce 0.7s infinite alternate; }
    .eq-visual.active span:nth-child(3) { animation: bounce 0.4s infinite alternate; }
    @keyframes bounce { 0% { height: 2px; } 100% { height: 10px; } }

    /* AUTH OVERLAY */
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

    /* VIDEO PORTAL */
    .video-portal { position: fixed; width: 320px; max-width: 90vw; background: #000; border: 1px solid #2dd4bf; border-radius: 8px; z-index: 9998; box-shadow: 0 0 20px rgba(45, 212, 191, 0.2); overflow: hidden; }
    .portal-handle { background: rgba(45, 212, 191, 0.1); padding: 5px 10px; font-family: 'JetBrains Mono'; font-size: 0.7rem; color: #2dd4bf; display: flex; justify-content: space-between; cursor: grab; }
    .portal-screen { position: relative; padding-bottom: 56.25%; }
    .portal-screen iframe { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }
    .drag-shield { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 10; }
    .close-btn { background: none; border: none; color: #fff; cursor: pointer; }

    /* PAYWALL */
    .paywall-overlay { height: 80vh; display: flex; justify-content: center; align-items: center; background: radial-gradient(circle, rgba(15,23,42,0.9), #020617); z-index: 50; }
    .paywall-card { text-align: center; border: 2px solid #ef4444; padding: 40px; background: rgba(0,0,0,0.8); backdrop-filter: blur(10px); border-radius: 12px; box-shadow: 0 0 50px rgba(239, 68, 68, 0.3); animation: shake 0.5s; width: 90%; max-width: 500px; }
    .paywall-card h1 { color: #ef4444; font-size: 2.5rem; margin: 0 0 10px 0; letter-spacing: 5px; }
    .paywall-card p { color: #94a3b8; font-family: 'JetBrains Mono'; margin-bottom: 20px; }
    .price { font-size: 2rem; color: #fff; margin-bottom: 30px; font-weight: bold; }
    .upgrade-btn { background: #ef4444; color: #000; border: none; padding: 15px 40px; font-size: 1.2rem; font-weight: bold; cursor: pointer; font-family: 'JetBrains Mono'; transition: 0.2s; border-radius: 6px; }
    .upgrade-btn:hover { background: #fff; box-shadow: 0 0 30px #ef4444; }
    .retreat-link { display: block; margin-top: 20px; color: #64748b; font-size: 0.8rem; font-family: 'JetBrains Mono'; }
</style>