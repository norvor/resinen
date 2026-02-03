<script lang="ts">
    import { onMount } from 'svelte';

    // --- STATE ---
    let streak = $state(0);
    let bestStreak = $state(0);
    let gameState = $state<'aim' | 'goal' | 'save'>('aim'); // aim, goal, save
    let keeperPos = $state(1); // 0=Left, 1=Center, 2=Right
    let ballPos = $state(1);

    // --- TOUCH STATE ---
    let touchStartX = 0;
    let touchStartY = 0;

    // --- API & LOGIC ---
    async function shoot(dir: number) {
        if (gameState !== 'aim') return;
        
        ballPos = dir;

        try {
            const res = await fetch('https://api.resinen.com/games/soccer/shoot', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ direction: dir })
            });
            const data = await res.json();
            
            keeperPos = data.keeper_dive;
            
            if (data.is_goal) {
                gameState = 'goal';
                streak++;
                if (streak > bestStreak) {
                    bestStreak = streak;
                    if(typeof localStorage !== 'undefined') localStorage.setItem('resinen_soccer_hs', bestStreak.toString());
                }
                setTimeout(resetShot, 1500);
            } else {
                gameState = 'save';
                setTimeout(() => {
                    streak = 0;
                    resetShot();
                }, 2000);
            }
        } catch(e) { console.error(e); }
    }

    function resetShot() {
        gameState = 'aim';
        keeperPos = 1; // Reset keeper to center
        ballPos = 1; // Reset ball
    }

    // --- TOUCH HANDLERS ---
    function handleTouchStart(e: TouchEvent) {
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
    }

    function handleTouchEnd(e: TouchEvent) {
        if (gameState !== 'aim') return;

        const touchEndX = e.changedTouches[0].clientX;
        const touchEndY = e.changedTouches[0].clientY;

        const diffX = touchEndX - touchStartX;
        const diffY = touchEndY - touchStartY;

        // Minimum swipe distance
        if (Math.abs(diffX) < 30 && Math.abs(diffY) < 30) return;

        // Determine direction based on strongest axis
        if (Math.abs(diffX) > Math.abs(diffY)) {
            // Horizontal Swipe
            if (diffX < 0) shoot(0); // Left
            else shoot(2); // Right
        } else {
            // Vertical Swipe
            if (diffY < 0) shoot(1); // Up (Center)
        }
    }

    onMount(() => {
        if(typeof localStorage !== 'undefined') {
            const hs = localStorage.getItem('resinen_soccer_hs');
            if(hs) bestStreak = parseInt(hs);
        }
        
        // Prevent scrolling when swiping on the game container
        const container = document.querySelector('.game-container');
        container?.addEventListener('touchmove', (e: Event) => e.preventDefault(), { passive: false });
    });
</script>

<div class="game-container">
    <div class="header">
        <h1>NEON PENALTY</h1>
        <div class="stats">STREAK: {streak} <span class="hs">BEST: {bestStreak}</span></div>
    </div>

    <div class="field" 
         ontouchstart={handleTouchStart} 
         ontouchend={handleTouchEnd}>
         
        <div class="goal-post">
            <div class="keeper" 
                 style="left: {keeperPos === 0 ? '15%' : keeperPos === 1 ? '50%' : '85%'}; 
                        transform: translateX(-50%) {gameState === 'save' ? 'scale(1.2)' : ''}">
                🧤
            </div>
            <div class="net"></div>
        </div>

        <div class="ball-area">
            <div class="ball" 
                 class:moving={gameState !== 'aim'}
                 style="left: {ballPos === 0 ? '20%' : ballPos === 1 ? '50%' : '80%'}; 
                        bottom: {gameState === 'aim' ? '10%' : '80%'}">
                ⚽
            </div>
        </div>
        
        {#if gameState === 'goal'}<div class="overlay goal-text">GOAL!</div>{/if}
        {#if gameState === 'save'}<div class="overlay save-text">SAVED!</div>{/if}
        
        <div class="swipe-hint">SWIPE TO SHOOT</div>
    </div>

    <div class="controls">
        <button onclick={() => shoot(0)}>LEFT</button>
        <button onclick={() => shoot(1)}>CENTER</button>
        <button onclick={() => shoot(2)}>RIGHT</button>
    </div>
</div>

<style>
    :global(body) { background: #020617; color: #fff; font-family: 'Space Grotesk', sans-serif; overflow: hidden; margin: 0; touch-action: none; }
    
    .game-container { 
        height: 100vh; width: 100vw; 
        display: flex; flex-direction: column; 
        align-items: center; justify-content: space-between; 
        padding: 20px; box-sizing: border-box;
    }
    
    .header { width: 100%; max-width: 600px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; flex-shrink: 0; }
    h1 { color: #22c55e; margin: 0; text-shadow: 0 0 15px rgba(34, 197, 94, 0.4); letter-spacing: 2px; font-size: 1.5rem; }
    .stats { font-family: 'JetBrains Mono'; font-size: 1rem; } 
    .hs { color: #64748b; font-size: 0.8rem; margin-left: 10px; }

    /* Field is now responsive to remaining height */
    .field { 
        flex-grow: 1; 
        width: 100%; max-width: 600px; 
        background: linear-gradient(to bottom, #064e3b, #065f46); 
        border: 2px solid #fff; 
        position: relative; 
        border-radius: 8px; 
        overflow: hidden; 
        perspective: 1000px; 
        margin-bottom: 20px;
        touch-action: none; /* Critical for swipe */
    }
    
    .goal-post { height: 35%; border-bottom: 2px solid #fff; position: relative; background: rgba(0,0,0,0.3); }
    .net { width: 100%; height: 100%; background-image: linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px); background-size: 20px 20px; opacity: 0.1; }
    
    .keeper { position: absolute; bottom: 0; font-size: 4rem; transition: left 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); filter: drop-shadow(0 0 10px #fff); }
    
    .ball-area { position: absolute; bottom: 0; left: 0; width: 100%; height: 65%; pointer-events: none; }
    .ball { position: absolute; font-size: 3rem; transform: translateX(-50%); transition: all 0.5s ease-out; filter: drop-shadow(0 10px 10px rgba(0,0,0,0.5)); }
    .ball.moving { transform: translateX(-50%) scale(0.5); } 

    .overlay { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 4rem; font-weight: bold; text-shadow: 0 0 20px rgba(0,0,0,0.5); z-index: 10; font-style: italic; white-space: nowrap; }
    .goal-text { color: #fbbf24; animation: pop 0.5s; }
    .save-text { color: #ef4444; animation: shake 0.5s; }

    .swipe-hint { position: absolute; bottom: 10px; width: 100%; text-align: center; color: rgba(255,255,255,0.3); font-family: 'JetBrains Mono'; font-size: 0.8rem; pointer-events: none; }

    .controls { display: flex; gap: 10px; margin-bottom: 10px; width: 100%; max-width: 600px; }
    button { 
        flex: 1;
        background: transparent; border: 2px solid #fff; color: #fff; 
        padding: 15px 0; font-family: 'JetBrains Mono'; font-weight: bold; 
        cursor: pointer; transition: 0.2s; border-radius: 4px; 
        font-size: 1rem;
    }
    button:hover, button:active { background: #fff; color: #000; box-shadow: 0 0 20px #fff; }

    @keyframes pop { 0% { transform: translate(-50%, -50%) scale(0); } 80% { transform: translate(-50%, -50%) scale(1.2); } 100% { transform: translate(-50%, -50%) scale(1); } }
    @keyframes shake { 0%, 100% { transform: translate(-50%, -50%); } 25% { transform: translate(-60%, -50%); } 75% { transform: translate(-40%, -50%); } }

    /* Mobile Adjustments */
    @media (max-width: 600px) {
        .keeper { font-size: 3rem; }
        .ball { font-size: 2.5rem; }
        .overlay { font-size: 3rem; }
        h1 { font-size: 1.2rem; }
        .controls { display: none; } /* Hide buttons on mobile if you want purely swipe, or keep them if you prefer: */
        /* If you want to keep buttons on mobile, remove 'display: none' above */
    }
    
    /* Ensure buttons show on larger screens or if user prefers clicking */
    @media (min-width: 601px) {
        .swipe-hint { display: none; }
    }
</style>