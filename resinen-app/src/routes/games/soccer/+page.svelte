<script lang="ts">
    import { onMount } from 'svelte';

    let streak = $state(0);
    let bestStreak = $state(0);
    let gameState = $state<'aim' | 'goal' | 'save'>('aim'); // aim, goal, save
    let keeperPos = $state(1); // 0=Left, 1=Center, 2=Right
    let ballPos = $state(1);

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

    onMount(() => {
        if(typeof localStorage !== 'undefined') {
            const hs = localStorage.getItem('resinen_soccer_hs');
            if(hs) bestStreak = parseInt(hs);
        }
    });
</script>

<div class="game-container">
    <div class="header">
        <a href="/" class="back">← DOCK</a>
        <h1>NEON PENALTY</h1>
        <div class="stats">STREAK: {streak} <span class="hs">BEST: {bestStreak}</span></div>
    </div>

    <div class="field">
        <div class="goal-post">
            <div class="keeper" style="left: {keeperPos === 0 ? '10%' : keeperPos === 1 ? '50%' : '90%'}; transform: translateX(-50%) {gameState === 'save' ? 'scale(1.2)' : ''}">
                🧤
            </div>
            <div class="net"></div>
        </div>

        <div class="ball-area">
            <div class="ball" 
                 class:moving={gameState !== 'aim'}
                 style="left: {ballPos === 0 ? '20%' : ballPos === 1 ? '50%' : '80%'}; bottom: {gameState === 'aim' ? '0%' : '80%'}">
                ⚽
            </div>
        </div>
        
        {#if gameState === 'goal'}<div class="overlay goal-text">GOAL!</div>{/if}
        {#if gameState === 'save'}<div class="overlay save-text">SAVED!</div>{/if}
    </div>

    <div class="controls">
        <button onclick={() => shoot(0)}>LEFT</button>
        <button onclick={() => shoot(1)}>CENTER</button>
        <button onclick={() => shoot(2)}>RIGHT</button>
    </div>
</div>

<style>
    :global(body) { background: #020617; color: #fff; font-family: 'Space Grotesk', sans-serif; overflow: hidden; }
    .game-container { height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: space-between; padding: 20px; }
    
    .header { width: 100%; max-width: 600px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
    .back { color: #64748b; text-decoration: none; font-size: 0.9rem; font-weight: bold; }
    h1 { color: #22c55e; margin: 0; text-shadow: 0 0 15px rgba(34, 197, 94, 0.4); letter-spacing: 2px; }
    .stats { font-family: 'JetBrains Mono'; font-size: 1.2rem; } .hs { color: #64748b; font-size: 0.8rem; }

    .field { flex: 1; width: 100%; max-width: 600px; background: linear-gradient(to bottom, #064e3b, #065f46); border: 2px solid #fff; position: relative; border-radius: 8px; overflow: hidden; perspective: 1000px; }
    
    .goal-post { height: 40%; border-bottom: 2px solid #fff; position: relative; background: rgba(0,0,0,0.3); }
    .net { width: 100%; height: 100%; background-image: linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px); background-size: 20px 20px; opacity: 0.1; }
    
    .keeper { position: absolute; bottom: 0; font-size: 4rem; transition: left 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); filter: drop-shadow(0 0 10px #fff); }
    
    .ball-area { position: absolute; bottom: 0; left: 0; width: 100%; height: 60%; }
    .ball { position: absolute; font-size: 3rem; transform: translateX(-50%); transition: all 0.5s ease-out; filter: drop-shadow(0 10px 10px rgba(0,0,0,0.5)); }
    .ball.moving { transform: translateX(-50%) scale(0.5); } /* Ball gets smaller as it goes "away" */

    .overlay { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 5rem; font-weight: bold; text-shadow: 0 0 20px rgba(0,0,0,0.5); z-index: 10; font-style: italic; }
    .goal-text { color: #fbbf24; animation: pop 0.5s; }
    .save-text { color: #ef4444; animation: shake 0.5s; }

    .controls { display: flex; gap: 20px; margin-bottom: 20px; }
    button { background: transparent; border: 2px solid #fff; color: #fff; padding: 15px 30px; font-family: 'JetBrains Mono'; font-weight: bold; cursor: pointer; transition: 0.2s; border-radius: 4px; }
    button:hover { background: #fff; color: #000; box-shadow: 0 0 20px #fff; }

    @keyframes pop { 0% { transform: translate(-50%, -50%) scale(0); } 80% { transform: translate(-50%, -50%) scale(1.2); } 100% { transform: translate(-50%, -50%) scale(1); } }
    @keyframes shake { 0%, 100% { transform: translate(-50%, -50%); } 25% { transform: translate(-60%, -50%); } 75% { transform: translate(-40%, -50%); } }
</style>