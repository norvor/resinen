<script lang="ts">
    import { onMount } from 'svelte';

    // --- CONFIG ---
    const COLORS = ['#ef4444', '#2dd4bf', '#facc15', '#3b82f6']; // Red, Cyan(Green), Yellow, Blue
    const PLAYER_NAMES = ['RED', 'CYAN', 'YELLOW', 'BLUE'];
    
    // --- STATE ---
    let positions = $state([
        [-1, -1, -1, -1], // P0 (Red)
        [-1, -1, -1, -1], // P1 (Cyan)
        [-1, -1, -1, -1], // P2 (Yellow)
        [-1, -1, -1, -1]  // P3 (Blue)
    ]);
    
    let turn = $state(0); // 0=Red, 1=Cyan, 2=Yellow, 3=Blue
    let dice = $state(0);
    let rolled = $state(false);
    let message = $state("Red's Turn. Roll the dice.");
    let isMoving = $state(false);

    // --- BOARD MAPPING (15x15 Grid) ---
    const PATH_COORDS = [
        {x:1, y:6}, {x:2, y:6}, {x:3, y:6}, {x:4, y:6}, {x:5, y:6}, {x:6, y:5}, {x:6, y:4}, {x:6, y:3}, {x:6, y:2}, {x:6, y:1}, {x:6, y:0}, {x:7, y:0}, {x:8, y:0}, // Red Area
        {x:8, y:1}, {x:8, y:2}, {x:8, y:3}, {x:8, y:4}, {x:8, y:5}, {x:9, y:6}, {x:10, y:6}, {x:11, y:6}, {x:12, y:6}, {x:13, y:6}, {x:14, y:6}, {x:14, y:7}, {x:14, y:8}, // Green Area
        {x:13, y:8}, {x:12, y:8}, {x:11, y:8}, {x:10, y:8}, {x:9, y:8}, {x:8, y:9}, {x:8, y:10}, {x:8, y:11}, {x:8, y:12}, {x:8, y:13}, {x:8, y:14}, {x:7, y:14}, {x:6, y:14}, // Yellow Area
        {x:6, y:13}, {x:6, y:12}, {x:6, y:11}, {x:6, y:10}, {x:6, y:9}, {x:5, y:8}, {x:4, y:8}, {x:3, y:8}, {x:2, y:8}, {x:1, y:8}, {x:0, y:8}, {x:0, y:7}, {x:0, y:6}  // Blue Area
    ];

    const HOMES = [
        [{x:1, y:7}, {x:2, y:7}, {x:3, y:7}, {x:4, y:7}, {x:5, y:7}, {x:6, y:7}], // Red Home
        [{x:7, y:1}, {x:7, y:2}, {x:7, y:3}, {x:7, y:4}, {x:7, y:5}, {x:7, y:6}], // Cyan Home
        [{x:13, y:7}, {x:12, y:7}, {x:11, y:7}, {x:10, y:7}, {x:9, y:7}, {x:8, y:7}], // Yellow Home
        [{x:7, y:13}, {x:7, y:12}, {x:7, y:11}, {x:7, y:10}, {x:7, y:9}, {x:7, y:8}]  // Blue Home
    ];

    const BASES = [
        [{x:1, y:1}, {x:4, y:1}, {x:1, y:4}, {x:4, y:4}], // Red
        [{x:10, y:1}, {x:13, y:1}, {x:10, y:4}, {x:13, y:4}], // Cyan
        [{x:10, y:10}, {x:13, y:10}, {x:10, y:13}, {x:13, y:13}], // Yellow
        [{x:1, y:10}, {x:4, y:10}, {x:1, y:13}, {x:4, y:13}]  // Blue
    ];

    // --- GAME LOGIC ---
    function rollDice() {
        if (rolled || isMoving) return;
        dice = Math.floor(Math.random() * 6) + 1;
        rolled = true;
        message = `${PLAYER_NAMES[turn]} rolled a ${dice}.`;

        const canMove = positions[turn].some(pos => canMoveToken(pos, dice));
        if (!canMove) {
            setTimeout(() => {
                // If it was a 6 and we couldn't move (rare but possible if blocked), pass turn
                // Usually 6 gives another roll, but to keep logic simple for "stuck" state:
                message = "No valid moves. Skipping turn...";
                setTimeout(nextTurn, 1000);
            }, 1000);
        } else if (turn !== 0) {
            setTimeout(botMove, 1000);
        }
    }

    async function botMove() {
        try {
            const res = await fetch('https://api.resinen.com/games/ludo/bot-move', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ turn, dice, positions })
            });
            const data = await res.json();
            if (data.token_idx !== null && data.token_idx !== undefined) {
                moveToken(turn, data.token_idx);
            } else {
                nextTurn();
            }
        } catch (e) {
            nextTurn();
        }
    }

    function canMoveToken(pos: number, roll: number) {
        if (pos === 99) return false;
        if (pos === -1) return roll === 6;
        if (pos + roll > 57) return false;
        return true;
    }

    function moveToken(pIdx: number, tIdx: number) {
        if (pIdx !== turn || !rolled || isMoving) return;
        const currentPos = positions[pIdx][tIdx];

        if (!canMoveToken(currentPos, dice)) return;

        isMoving = true;
        
        if (currentPos === -1) {
            positions[pIdx][tIdx] = 0; 
        } else {
            positions[pIdx][tIdx] += dice;
        }

        handleCollision(pIdx, positions[pIdx][tIdx]);

        if (positions[pIdx][tIdx] === 57) positions[pIdx][tIdx] = 99;

        rolled = false;
        
        // --- LOGIC FIX HERE ---
        setTimeout(() => {
            isMoving = false; // Reset moving state first
            
            if (dice !== 6) {
                nextTurn();
            } else {
                // IT WAS A 6!
                message = `${PLAYER_NAMES[turn]} rolled a 6! Rolling again...`;
                
                // If AI, trigger roll again
                if (turn !== 0) {
                    setTimeout(rollDice, 1000);
                }
                // If Player, they just wait to click "Roll" again
            }
        }, 500);
    }

    function handleCollision(pIdx: number, relativePos: number) {
        if (relativePos > 51) return;
        const absPos = getAbsolutePos(pIdx, relativePos);
        
        for (let i = 0; i < 4; i++) {
            if (i === pIdx) continue;
            for (let j = 0; j < 4; j++) {
                const enemyPos = positions[i][j];
                if (enemyPos > -1 && enemyPos < 52) {
                    const enemyAbs = getAbsolutePos(i, enemyPos);
                    if (absPos === enemyAbs) {
                        positions[i][j] = -1;
                        message = "CAPTURED!";
                    }
                }
            }
        }
    }

    function nextTurn() {
        turn = (turn + 1) % 4;
        dice = 0;
        rolled = false;
        isMoving = false;
        message = `${PLAYER_NAMES[turn]}'s Turn.`;
        
        if (turn !== 0) {
            setTimeout(rollDice, 1000);
        }
    }

    // --- RENDERING ---
    function getAbsolutePos(pIdx: number, relPos: number) {
        const offset = pIdx * 13;
        return (relPos + offset) % 52;
    }

    function getTokenStyle(pIdx: number, tIdx: number) {
        const pos = positions[pIdx][tIdx];
        let x = 0, y = 0;

        if (pos === -1) {
            x = BASES[pIdx][tIdx].x;
            y = BASES[pIdx][tIdx].y;
        } else if (pos === 99) {
            x = 7; y = 7;
        } else if (pos > 51) {
            const homeIdx = pos - 52;
            const coord = HOMES[pIdx][homeIdx];
            x = coord.x; y = coord.y;
        } else {
            const abs = getAbsolutePos(pIdx, pos);
            const coord = PATH_COORDS[abs];
            x = coord.x; y = coord.y;
        }

        return `left: calc(${x} * 100% / 15 + 1.5%); top: calc(${y} * 100% / 15 + 1.5%); background-color: ${COLORS[pIdx]}; box-shadow: 0 0 10px ${COLORS[pIdx]};`;
    }

    onMount(() => {
        // If first turn is player, just wait. If we change starting player, logic handles it.
    });
</script>

<div class="game-container">
    <div class="bg-layer stars"></div>
    
    <div class="game-ui">
        <div class="header">
            <a href="/" class="back-btn">← DOCK</a>
            <h1>NEON LUDO</h1>
            <div class="status-bar">
                <span class="turn-indicator" style="color: {COLORS[turn]}">TURN: {PLAYER_NAMES[turn]}</span>
                {#if dice > 0}<span class="dice-val">🎲 {dice}</span>{/if}
            </div>
        </div>

        <div class="board-wrapper">
            <div class="ludo-board">
                {#each PATH_COORDS as _, i}<div class="cell track" style="grid-column: {PATH_COORDS[i].x + 1}; grid-row: {PATH_COORDS[i].y + 1}"></div>{/each}
                
                {#each HOMES[0] as h}<div class="cell home-r" style="grid-column: {h.x+1}; grid-row: {h.y+1}"></div>{/each}
                {#each HOMES[1] as h}<div class="cell home-g" style="grid-column: {h.x+1}; grid-row: {h.y+1}"></div>{/each}
                {#each HOMES[2] as h}<div class="cell home-y" style="grid-column: {h.x+1}; grid-row: {h.y+1}"></div>{/each}
                {#each HOMES[3] as h}<div class="cell home-b" style="grid-column: {h.x+1}; grid-row: {h.y+1}"></div>{/each}
                
                <div class="base base-r"></div>
                <div class="base base-g"></div>
                <div class="base base-y"></div>
                <div class="base base-b"></div>
                
                <div class="center-zone"></div>
            </div>

            <div class="token-layer">
                {#each positions as playerTokens, pIdx}
                    {#each playerTokens as _, tIdx}
                        <div 
                            class="token" 
                            class:clickable={turn === 0 && pIdx === 0 && rolled && canMoveToken(positions[pIdx][tIdx], dice)}
                            style={getTokenStyle(pIdx, tIdx)}
                            onclick={() => moveToken(pIdx, tIdx)}
                        ></div>
                    {/each}
                {/each}
            </div>
        </div>

        <div class="controls">
            <div class="msg">{message}</div>
            {#if turn === 0 && !rolled}
                <button class="roll-btn" onclick={rollDice}>ROLL DICE</button>
            {/if}
        </div>
    </div>
</div>

<style>
    :global(body) { margin: 0; background-color: #0f172a; color: #f8fafc; font-family: 'Space Grotesk', sans-serif; overflow: hidden; }
    .stars { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: radial-gradient(#fff 1px, transparent 1px); background-size: 50px 50px; opacity: 0.1; }
    
    .game-container { height: 100vh; display: flex; justify-content: center; align-items: center; position: relative; }
    .game-ui { z-index: 1; display: flex; flex-direction: column; align-items: center; gap: 20px; }
    
    .header { text-align: center; width: 100%; position: relative; }
    .back-btn { position: absolute; left: -120px; top: 50%; transform: translateY(-50%); text-decoration: none; color: #94a3b8; font-family: 'JetBrains Mono'; font-size: 0.8rem; border: 1px solid #334155; padding: 5px 10px; border-radius: 4px; }
    h1 { font-size: 2.5rem; letter-spacing: 2px; margin: 0; color: #fff; text-shadow: 0 0 10px #fff; }
    
    .status-bar { font-family: 'JetBrains Mono'; margin-top: 10px; font-size: 1.2rem; display: flex; gap: 20px; justify-content: center; }
    .dice-val { color: #fff; animation: bounce 0.5s; }

    .board-wrapper { position: relative; width: 500px; height: 500px; box-shadow: 0 0 50px rgba(0,0,0,0.5); border-radius: 12px; background: #0f172a; border: 4px solid #334155; }
    
    .ludo-board { 
        width: 100%; height: 100%; 
        display: grid; grid-template-columns: repeat(15, 1fr); grid-template-rows: repeat(15, 1fr); 
        gap: 1px;
    }
    
    .cell { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.02); }
    .cell.track { background: rgba(255,255,255,0.1); }
    .home-r { background: rgba(239, 68, 68, 0.2); }
    .home-g { background: rgba(45, 212, 191, 0.2); }
    .home-y { background: rgba(250, 204, 21, 0.2); }
    .home-b { background: rgba(59, 130, 246, 0.2); }

    .base { position: absolute; width: 40%; height: 40%; border-radius: 12px; opacity: 0.2; }
    .base-r { top: 0; left: 0; background: #ef4444; }
    .base-g { top: 0; right: 0; background: #2dd4bf; }
    .base-y { bottom: 0; right: 0; background: #facc15; }
    .base-b { bottom: 0; left: 0; background: #3b82f6; }
    
    .center-zone { 
        grid-column: 7 / 10; grid-row: 7 / 10; 
        background: radial-gradient(circle, #fff, transparent); 
        opacity: 0.1; 
    }

    .token-layer { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; }
    .token { 
        position: absolute; width: 4%; height: 4%; 
        border-radius: 50%; border: 2px solid #fff; 
        transition: all 0.5s ease; pointer-events: auto;
    }
    .token.clickable { cursor: pointer; animation: pulse 1s infinite; border-color: #fff; }
    
    .controls { text-align: center; margin-top: 10px; height: 60px; }
    .msg { font-family: 'JetBrains Mono'; color: #94a3b8; font-size: 0.9rem; margin-bottom: 10px; }
    .roll-btn { 
        background: #fff; color: #000; border: none; padding: 10px 30px; 
        font-family: 'JetBrains Mono'; font-weight: bold; cursor: pointer; 
        border-radius: 4px; transition: 0.2s;
    }
    .roll-btn:hover { transform: scale(1.05); box-shadow: 0 0 15px #fff; }

    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.3); } 100% { transform: scale(1); } }
    @keyframes bounce { 0% { transform: translateY(0); } 50% { transform: translateY(-10px); } 100% { transform: translateY(0); } }
</style>