<script lang="ts">
    import { onMount } from 'svelte';
    
    // Game State
    let score = $state(0);
    let ballsFaced = $state(0);
    let wickets = $state(0);
    let gameState = $state<'idle' | 'bowling' | 'hit' | 'result'>('idle');
    
    // Ball Physics
    let ballSize = $state(10); // px
    let ballTop = $state(20); // % from top
    let ballLeft = $state(50); // % from left
    let ballSpeed = 1000; // ms duration
    
    // Current Delivery Data
    let currentBallType = "";
    let statusMsg = $state("Press START to play");
    let commentary = $state("");

    // Timing Logic
    let bowlStartTime = 0;
    
    // --- API CALLS (Unchanged) ---
    async function startDelivery() {
        if (wickets >= 10) { resetGame(); return; }
        
        gameState = 'bowling';
        statusMsg = "Bowler run up...";
        ballTop = 20;
        ballSize = 10;
        ballLeft = 50;
        
        try {
            const res = await fetch('https://api.resinen.com/games/cricket/get-delivery', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ difficulty: 'normal' })
            });
            const data = await res.json();
            currentBallType = data.type;
            ballSpeed = data.speed_ms;
            
            setTimeout(() => {
                animateBall();
            }, 1000); // Wait for run-up
            
        } catch (e) {
            console.error(e);
            gameState = 'idle';
        }
    }

    function animateBall() {
        statusMsg = "Watch the ball!";
        bowlStartTime = Date.now();
        
        // CSS Transition handles the visual movement
        requestAnimationFrame(() => {
            ballTop = 85; // Move to bat position
            ballSize = 40; // Get bigger (3D effect)
            
            // Swing Logic
            if (currentBallType === 'spin') ballLeft = 40; 
            if (currentBallType === 'yorker') ballTop = 90;
        });

        // Auto-fail if user doesn't hit in time
        setTimeout(() => {
            if (gameState === 'bowling') {
                handleShot('miss');
            }
        }, ballSpeed + 200);
    }

    async function handleShot(shotType: string) {
        if (gameState !== 'bowling') return;
        
        const hitTime = Date.now();
        const delta = hitTime - bowlStartTime;
        
        // Calculate Timing Score
        const perfectTime = ballSpeed * 0.9; 
        const diff = Math.abs(delta - perfectTime);
        
        let timingScore = 0;
        if (diff < 50) timingScore = 100; // Perfect
        else if (diff < 100) timingScore = 80; // Good
        else if (diff < 200) timingScore = 50; // Okay
        else timingScore = 10; // Bad

        if (shotType === 'miss') timingScore = 0;

        // Visual Feedback
        gameState = 'hit';
        
        try {
            const res = await fetch('https://api.resinen.com/games/cricket/calculate-shot', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ 
                    timing_score: timingScore, 
                    shot_type: shotType, 
                    ball_type: currentBallType 
                })
            });
            const result = await res.json();
            
            gameState = 'result';
            commentary = result.comment;
            
            if (result.is_out) {
                wickets++;
                statusMsg = "OUT!";
            } else {
                score += result.runs;
                statusMsg = `+${result.runs} RUNS`;
            }
            ballsFaced++;

        } catch (e) { console.error(e); }
    }

    function handleKey(e: KeyboardEvent) {
        if (gameState !== 'bowling') {
            if (e.code === 'Space' && gameState !== 'bowling') startDelivery();
            return;
        }

        if (e.code === 'ArrowUp') handleShot('loft');
        if (e.code === 'ArrowDown') handleShot('drive');
        if (e.code === 'Space') handleShot('defend');
    }

    function resetGame() {
        score = 0;
        wickets = 0;
        ballsFaced = 0;
        gameState = 'idle';
        statusMsg = "Press START to Start Match";
    }

</script>

<svelte:window onkeydown={handleKey}/>

<div class="stadium">
    <div class="scoreboard">
        <div class="score-group">
            <div class="score">{score}/{wickets}</div>
            <div class="overs">{(ballsFaced/6).toFixed(1)} OVERS</div>
        </div>
        <div class="last-comm">{commentary}</div>
    </div>

    <div class="field-view">
        <div class="pitch">
            <div class="stumps far"></div>
            
            {#if gameState === 'bowling'}
                <div class="ball" 
                     style="
                        top: {ballTop}%; 
                        left: {ballLeft}%; 
                        width: {ballSize}px; 
                        height: {ballSize}px; 
                        transition: top {ballSpeed}ms linear, width {ballSpeed}ms linear, left {ballSpeed}ms ease-in-out;"
                ></div>
            {/if}

            <div class="crease-line"></div>
            
            <div class="batsman" class:swing={gameState==='hit'}>🏏</div>
        </div>
    </div>

    <div class="controls-ui">
        {#if gameState === 'idle' || gameState === 'result'}
            <button class="start-btn" onclick={startDelivery} ontouchstart={startDelivery}>
                {wickets >= 10 ? 'PLAY AGAIN' : 'BOWL (TAP HERE)'}
            </button>
        {:else}
            <div class="shot-buttons">
                <button class="shot-btn loft" onclick={() => handleShot('loft')} ontouchstart={(e) => { e.preventDefault(); handleShot('loft'); }}>
                    <span class="icon">⬆</span>
                    <span class="label">LOFT</span>
                </button>
                
                <button class="shot-btn defend" onclick={() => handleShot('defend')} ontouchstart={(e) => { e.preventDefault(); handleShot('defend'); }}>
                    <span class="icon">●</span>
                    <span class="label">DEFEND</span>
                </button>

                <button class="shot-btn drive" onclick={() => handleShot('drive')} ontouchstart={(e) => { e.preventDefault(); handleShot('drive'); }}>
                    <span class="icon">⬇</span>
                    <span class="label">DRIVE</span>
                </button>
            </div>
        {/if}
        <div class="status">{statusMsg}</div>
    </div>
</div>

<style>
    :global(body) { margin: 0; background: #1e293b; color: white; font-family: 'Space Grotesk', sans-serif; overflow: hidden; touch-action: none; }

    .stadium {
        height: 100dvh; /* Dynamic viewport height for mobile browsers */
        display: flex;
        flex-direction: column;
        align-items: center;
        background: radial-gradient(circle at 50% 30%, #064e3b 0%, #022c22 70%);
        perspective: 1000px;
    }

    .scoreboard {
        width: 100%;
        padding: 15px 20px;
        background: linear-gradient(180deg, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0.4) 100%);
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 5px;
        font-family: 'JetBrains Mono';
        z-index: 10;
        box-sizing: border-box;
    }
    .score-group { display: flex; gap: 20px; align-items: baseline; }
    .score { font-size: 2rem; color: #fbbf24; font-weight: bold; line-height: 1; }
    .overs { font-size: 1rem; opacity: 0.8; }
    .last-comm { color: #fff; font-style: italic; animation: flash 0.5s; font-size: 0.9rem; text-align: center; min-height: 1.2em; }

    .field-view {
        flex: 1;
        width: 100%;
        max-width: 600px;
        position: relative;
        display: flex;
        justify-content: center;
        overflow: hidden; /* Prevent pitch overflow */
    }

    .pitch {
        width: 60%;
        height: 120%; /* Extend closer to camera */
        background: #d97706; 
        transform: rotateX(40deg) scale(0.8) translateY(-10%);
        border-left: 10px solid rgba(255,255,255,0.2);
        border-right: 10px solid rgba(255,255,255,0.2);
        position: relative;
        box-shadow: 0 0 50px rgba(0,0,0,0.5);
    }

    .stumps.far {
        position: absolute;
        top: 10%;
        left: 50%;
        transform: translateX(-50%);
        width: 40px;
        height: 60px;
        background: url('https://img.icons8.com/emoji/96/cricket-game-emoji.png') no-repeat center/contain;
    }

    .crease-line {
        position: absolute;
        bottom: 25%; /* Adjusted for better mobile perspective */
        width: 100%;
        height: 4px;
        background: white;
    }

    .ball {
        position: absolute;
        background: #ef4444;
        border-radius: 50%;
        box-shadow: 0 5px 15px rgba(0,0,0,0.5) inset;
        transform: translate(-50%, -50%);
        z-index: 5;
    }

    .batsman {
        position: absolute;
        bottom: 15%;
        left: 50%;
        transform: translateX(-50%);
        font-size: min(80px, 15vh); /* Responsive size */
        transition: transform 0.1s;
    }
    .batsman.swing {
        transform: translateX(-50%) rotate(-45deg) translateY(-20px);
    }

    .controls-ui {
        height: auto;
        min-height: 25vh; /* Ensure touch area is large enough */
        width: 100%;
        background: #0f172a;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        border-top: 4px solid #334155;
        padding: 20px 0;
        gap: 15px;
    }

    /* New Interactive Buttons */
    .shot-buttons {
        display: flex;
        gap: 10px;
        width: 90%;
        max-width: 400px;
        height: 80px;
    }

    .shot-btn {
        flex: 1;
        background: #334155;
        border: 1px solid #475569;
        border-radius: 12px;
        color: white;
        font-family: 'JetBrains Mono';
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.1s;
        touch-action: manipulation;
    }
    
    .shot-btn:active { background: #475569; transform: scale(0.95); }
    .shot-btn.loft { border-bottom: 4px solid #3b82f6; }
    .shot-btn.drive { border-bottom: 4px solid #10b981; }
    .shot-btn.defend { border-bottom: 4px solid #f59e0b; }

    .shot-btn .icon { font-size: 1.5rem; margin-bottom: 4px; }
    .shot-btn .label { font-size: 0.75rem; opacity: 0.8; }

    .start-btn {
        background: #fbbf24;
        color: #000;
        font-size: 1.2rem;
        padding: 20px 60px;
        border: none;
        border-radius: 50px;
        font-weight: bold;
        cursor: pointer;
        box-shadow: 0 0 20px rgba(251, 191, 36, 0.4);
        width: 80%;
        max-width: 300px;
    }
    .start-btn:active { transform: scale(0.98); }

    .status { color: #94a3b8; letter-spacing: 1px; font-size: 0.9rem; text-align: center; }

    @keyframes flash { 0% { opacity: 0; } 100% { opacity: 1; } }
</style>