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
    
    // --- API CALLS ---
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
        // We trigger it by changing the state variables
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
        // Perfect timing is usually around 80-90% of ballSpeed
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
        statusMsg = "Press SPACE to Start Match";
    }

</script>

<svelte:window onkeydown={handleKey}/>

<div class="stadium">
    <div class="scoreboard">
        <div class="score">{score}/{wickets}</div>
        <div class="overs">{(ballsFaced/6).toFixed(1)} OVERS</div>
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
            <button class="start-btn" onclick={startDelivery}>
                {wickets >= 10 ? 'PLAY AGAIN' : 'BOWL NEXT BALL (SPACE)'}
            </button>
        {:else}
            <div class="shot-guide">
                <span class="key">⬆ LOFT (6)</span>
                <span class="key">⬇ DRIVE (4)</span>
                <span class="key">SPACE DEFEND</span>
            </div>
        {/if}
        <div class="status">{statusMsg}</div>
    </div>
</div>

<style>
    :global(body) { margin: 0; background: #1e293b; color: white; font-family: 'Space Grotesk', sans-serif; overflow: hidden; }

    .stadium {
        height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        background: radial-gradient(circle at 50% 30%, #064e3b 0%, #022c22 70%);
        perspective: 1000px;
    }

    .scoreboard {
        width: 100%;
        padding: 20px;
        background: rgba(0,0,0,0.5);
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-family: 'JetBrains Mono';
        z-index: 10;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    .score { font-size: 2.5rem; color: #fbbf24; font-weight: bold; }
    .last-comm { color: #fff; font-style: italic; animation: flash 0.5s; }

    .field-view {
        flex: 1;
        width: 100%;
        max-width: 600px;
        position: relative;
        display: flex;
        justify-content: center;
    }

    .pitch {
        width: 60%;
        height: 100%;
        background: #d97706; /* Mud color */
        transform: rotateX(40deg) scale(0.8);
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
        bottom: 15%;
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
        bottom: 5%;
        left: 50%;
        transform: translateX(-50%);
        font-size: 80px;
        transition: transform 0.1s;
    }
    .batsman.swing {
        transform: translateX(-50%) rotate(-45deg) translateY(-20px);
    }

    .controls-ui {
        height: 150px;
        width: 100%;
        background: #0f172a;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        border-top: 4px solid #334155;
    }

    .shot-guide { display: flex; gap: 20px; font-family: 'JetBrains Mono'; }
    .key { background: #334155; padding: 10px 20px; border-radius: 8px; border: 1px solid #475569; }

    .start-btn {
        background: #fbbf24;
        color: #000;
        font-size: 1.5rem;
        padding: 15px 40px;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        cursor: pointer;
        box-shadow: 0 0 20px rgba(251, 191, 36, 0.4);
    }
    .start-btn:hover { transform: scale(1.05); }

    .status { margin-top: 10px; color: #94a3b8; letter-spacing: 2px; }

    @keyframes flash { 0% { opacity: 0; } 100% { opacity: 1; } }
</style>