<script lang="ts">
    import { onMount } from 'svelte';

    // --- CONFIG ---
    const COLORS = ['#ef4444', '#22c55e', '#eab308', '#3b82f6']; // Red, Green, Yellow, Blue
    const BASES = [0, 13, 26, 39]; 
    const SAFE_SPOTS = [0, 8, 13, 21, 26, 34, 39, 47];

    // --- STATE ---
    let gameStarted = $state(false);
    // Default: P1 Human, others CPU
    let players = $state([
        { id: 0, color: 'red', pieces: [-1, -1, -1, -1], home: 0, isCpu: false },
        { id: 1, color: 'green', pieces: [-1, -1, -1, -1], home: 0, isCpu: true },
        { id: 2, color: 'yellow', pieces: [-1, -1, -1, -1], home: 0, isCpu: true },
        { id: 3, color: 'blue', pieces: [-1, -1, -1, -1], home: 0, isCpu: true }
    ]);
    
    let turn = $state(0);
    let diceValue = $state(1); 
    let diceRolling = $state(false);
    let canRoll = $state(true);
    let validMoves = $state<number[]>([]);
    let msg = $state("WAITING FOR HOST");
    let winner = $state<number | null>(null);

    // Derived state for validation
    let allAi = $derived(players.every(p => p.isCpu));

    // --- AUDIO & HAPTICS ---
    function pulse(pattern: number[]) {
        if (typeof navigator !== 'undefined' && navigator.vibrate) {
            navigator.vibrate(pattern);
        }
    }

    // --- SETUP LOGIC ---
    function toggleCpu(index: number) {
        players[index].isCpu = !players[index].isCpu;
    }
    
    function startGame() {
        if (allAi) {
            msg = "ERROR: HUMAN REQUIRED";
            return;
        }
        gameStarted = true;
        msg = `P1 (${players[0].isCpu ? 'BOT' : 'HUMAN'}) START`;
        if (players[0].isCpu) setTimeout(aiTurn, 1000);
    }

    function restartGame() {
        // Reset Logic
        gameStarted = false;
        winner = null;
        turn = 0;
        diceValue = 1;
        validMoves = [];
        msg = "WAITING FOR HOST";
        canRoll = true;
        diceRolling = false;

        // Reset positions but KEEP setup (isCpu)
        players = players.map(p => ({
            ...p,
            pieces: [-1, -1, -1, -1],
            home: 0
        }));
    }

    // --- CORE GAME LOGIC ---
    function rollDice() {
        if (!canRoll || winner !== null) return;
        
        canRoll = false;
        diceRolling = true;
        msg = "ROLLING...";
        pulse([10]);

        let count = 0;
        const interval = setInterval(() => {
            diceValue = Math.floor(Math.random() * 6) + 1;
            count++;
            if (count > 8) {
                clearInterval(interval);
                finalizeRoll();
            }
        }, 50);
    }

    function finalizeRoll() {
        diceRolling = false;
        diceValue = Math.floor(Math.random() * 6) + 1;
        
        validMoves = [];
        const p = players[turn];
        
        p.pieces.forEach((pos, i) => {
            if (pos === -1) {
                if (diceValue === 6) validMoves.push(i);
            } else if (pos < 100) {
                 if (pos + diceValue <= 57) validMoves.push(i); 
            }
        });

        if (validMoves.length === 0) {
            msg = "NO MOVES";
            setTimeout(nextTurn, 800);
        } else {
            msg = "MOVE";
            
            if (p.isCpu) {
                setTimeout(() => aiDecideMove(p.pieces, validMoves), 600);
            } else {
                // Optional: Auto-move if forced? Kept manual for feel.
            }
        }
    }

    function aiTurn() {
        if (winner !== null || !gameStarted) return;
        rollDice();
    }

    function aiDecideMove(currentPieces: number[], moves: number[]) {
        if (moves.length === 0) return;

        let bestMove = moves[0];
        let bestScore = -9999;

        moves.forEach(pieceIdx => {
            const currentPos = currentPieces[pieceIdx];
            let score = 0;
            
            let newPos = currentPos;
            if (currentPos === -1) newPos = 0;
            else newPos += diceValue;

            // HEURISTICS
            if (currentPos === -1) score += 50; // Leave base
            if (newPos === 56) score += 100; // Finish

            // Kill check
            if (newPos < 51) {
                const globalPos = getGlobalPos(turn, newPos);
                if (!SAFE_SPOTS.includes(globalPos)) {
                    players.forEach((opp, oppIdx) => {
                        if (oppIdx !== turn) {
                            opp.pieces.forEach(oppP => {
                                if (oppP !== -1 && oppP < 51) {
                                    if (getGlobalPos(oppIdx, oppP) === globalPos) {
                                        score += 200; // KILL!
                                    }
                                }
                            });
                        }
                    });
                }
            }

            // Safety check
            if (newPos < 51) {
                const globalPos = getGlobalPos(turn, newPos);
                if (SAFE_SPOTS.includes(globalPos)) score += 30;
            }

            if (score > bestScore) {
                bestScore = score;
                bestMove = pieceIdx;
            }
        });

        movePiece(bestMove);
    }

    function movePiece(pieceIdx: number) {
        if (!validMoves.includes(pieceIdx) || diceRolling) return;

        const p = players[turn];
        let currentPos = p.pieces[pieceIdx];
        
        if (currentPos === -1) {
            p.pieces[pieceIdx] = 0;
            pulse([30]);
        } else {
            let newPos = currentPos + diceValue;
            if (newPos === 56) {
                p.pieces[pieceIdx] = 106;
                p.home++;
                msg = "SECURED";
                pulse([50, 50]);
                if (p.home === 4) {
                    winner = turn;
                    msg = `P${turn+1} WINS!`;
                    return;
                }
            } else {
                p.pieces[pieceIdx] = newPos;
            }
            
            // Kill Logic
            if (newPos < 51) { 
                const globalPos = getGlobalPos(turn, newPos);
                if (!SAFE_SPOTS.includes(globalPos)) {
                    players.forEach((opp, oppIdx) => {
                        if (oppIdx !== turn) {
                            opp.pieces.forEach((oppP, oppI) => {
                                if (oppP !== -1 && oppP < 51) {
                                    if (getGlobalPos(oppIdx, oppP) === globalPos) {
                                        players[oppIdx].pieces[oppI] = -1;
                                        msg = "HIT!";
                                        pulse([50, 100]);
                                    }
                                }
                            });
                        }
                    });
                }
            }
        }
        
        finishMove();
    }

    function finishMove() {
        validMoves = [];
        if (diceValue === 6) {
            msg = "AGAIN";
            canRoll = true;
            if (players[turn].isCpu && winner === null) {
                setTimeout(aiTurn, 1000);
            }
        } else {
            nextTurn();
        }
    }

    function nextTurn() {
        turn = (turn + 1) % 4;
        canRoll = true;
        msg = `P${turn + 1}`;
        if (players[turn].isCpu && winner === null) {
            setTimeout(aiTurn, 1000);
        }
    }

    // --- MAPPINGS ---
    function getGlobalPos(playerIdx: number, relPos: number) {
        return (BASES[playerIdx] + relPos) % 52;
    }

    function getCoordinates(playerIdx: number, relPos: number) {
        if (relPos === -1) {
             const bases = [
                [[1,1], [1,2], [2,1], [2,2]], // Red
                [[1,10], [1,11], [2,10], [2,11]], // Green
                [[10,10], [10,11], [11,10], [11,11]], // Yellow
                [[10,1], [10,2], [11,1], [11,2]] // Blue
            ];
            return { r: bases[playerIdx][0][0], c: bases[playerIdx][0][1], isBase: true };
        }
        if (relPos >= 100) return { r: 6, c: 6, isCenter: true };

        const path0 = [
            [1,6],[2,6],[3,6],[4,6],[5,6], [6,5],[6,4],[6,3],[6,2],[6,1],[6,0], 
            [7,0], [8,0],[8,1],[8,2],[8,3],[8,4],[8,5], [9,6],[10,6],[11,6],[12,6],[13,6],[14,6],
            [14,7], [14,8],[13,8],[12,8],[11,8],[10,8],[9,8], [8,9],[8,10],[8,11],[8,12],[8,13],[8,14],
            [7,14], [6,14],[6,13],[6,12],[6,11],[6,10],[6,9], [5,8],[4,8],[3,8],[2,8],[1,8],[0,8],
            [0,7], 
            [1,7],[2,7],[3,7],[4,7],[5,7],[6,7] 
        ];

        const coords = path0[relPos];
        if (!coords) return { r: 7, c: 7 };

        let r = coords[0];
        let c = coords[1];
        for(let i=0; i<playerIdx; i++) {
            const temp = r;
            r = c;
            c = 14 - temp;
        }
        return { r, c };
    }
    
    function getDiceDots(val: number) {
        const map = {
            1: [4], 2: [0, 8], 3: [0, 4, 8],
            4: [0, 2, 6, 8], 5: [0, 2, 4, 6, 8], 6: [0, 2, 3, 5, 6, 8]
        };
        return map[val as keyof typeof map] || [];
    }
</script>

<div class="scene">
    <div class="bg-stars"></div>
    
    {#if !gameStarted}
        <div class="setup-overlay">
            <h1>NEON LUDO</h1>
            <div class="setup-grid">
                {#each players as p, i}
                    <button class="player-toggle" 
                        class:cpu={p.isCpu}
                        style="--c: {COLORS[i]}"
                        onclick={() => toggleCpu(i)}
                    >
                        <span class="p-name">PLAYER {i+1}</span>
                        <span class="p-type">{p.isCpu ? 'BOT' : 'HUMAN'}</span>
                        <div class="p-status-light"></div>
                    </button>
                {/each}
            </div>
            
            {#if allAi}
                <div class="error-msg">⚠ AT LEAST 1 HUMAN REQUIRED</div>
            {/if}

            <button class="start-btn" onclick={startGame} disabled={allAi}>
                {allAi ? 'LOCKED' : 'INITIATE'}
            </button>
            <a href="/" class="exit-link">EXIT TO DOCK</a>
        </div>
    {/if}

    <div class="ui-layer top">
        {#if gameStarted}
            <a href="/" class="back-btn">← DOCK</a>
            <div class="status-bar">{msg}</div>
            <button class="restart-btn" onclick={restartGame}>↻ RESTART</button>
        {/if}
    </div>

    <div class="board-container" class:blurred={!gameStarted}>
        <div class="board-tilt">
            <div class="board-thickness"></div>
            <div class="board-surface">
                <div class="zone red"></div>
                <div class="zone green"></div>
                <div class="zone yellow"></div>
                <div class="zone blue"></div>
                <div class="zone center"></div>

                {#each Array(15) as _, r}
                    {#each Array(15) as _, c}
                        {#if (r>=6 && r<=8) || (c>=6 && c<=8)}
                           <div class="cell" style="grid-row: {r+1}; grid-column: {c+1};"
                                class:safe={ (r===6&&c===2) || (r===8&&c===1) || (r===12&&c===6) || (r===13&&c===8) || (r===8&&c===12) || (r===6&&c===13) || (r===2&&c===8) || (r===1&&c===6) }
                           ></div>
                        {/if}
                    {/each}
                {/each}

                {#each players as p, pIdx}
                    {#each p.pieces as pos, pieceIdx}
                        {@const coords = getCoordinates(pIdx, pos)}
                        {@const baseOffsets = [{x:0, y:0}, {x:100, y:0}, {x:0, y:100}, {x:100, y:100}]}
                        
                        <button 
                            class="token"
                            class:active={gameStarted && turn === pIdx && validMoves.includes(pieceIdx)}
                            disabled={!gameStarted}
                            style="
                                --color: {COLORS[pIdx]};
                                grid-row: {coords.r + 1};
                                grid-column: {coords.c + 1};
                                transform: {pos === -1 ? `translate(${baseOffsets[pieceIdx].x}%, ${baseOffsets[pieceIdx].y}%)` : 'none'} translateZ(10px);
                            "
                            onclick={() => movePiece(pieceIdx)}
                        >
                            <div class="token-body"></div>
                            <div class="token-shadow"></div>
                        </button>
                    {/each}
                {/each}
            </div>
        </div>
    </div>

    {#if gameStarted}
        <div class="flat-controls">
            <div class="turn-indicators">
                {#each players as p, i}
                    <div class="p-dot" 
                        class:active={turn === i} 
                        style="background: {COLORS[i]}; box-shadow: 0 0 {turn===i ? '15px' : '0'} {COLORS[i]}">
                        {#if p.isCpu}
                             <span class="cpu-tag">AI</span>
                        {/if}
                    </div>
                {/each}
            </div>

            <button class="real-die-btn" 
                onclick={rollDice} 
                disabled={!canRoll || diceRolling || (players[turn].isCpu)}
                class:rolling={diceRolling}
                class:cpu-turn={players[turn].isCpu}
            >
                <div class="die-face">
                    {#each Array(9) as _, i}
                        <div class="dot" class:visible={getDiceDots(diceValue).includes(i)}></div>
                    {/each}
                </div>
            </button>
        </div>
    {/if}
</div>

<style>
    :global(body) { 
        margin: 0; background: #000; color: #fff; 
        font-family: 'Space Grotesk', sans-serif; overflow: hidden; 
        touch-action: none;
    }

    .scene {
        height: 100dvh;
        width: 100vw;
        perspective: 1200px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: radial-gradient(circle at 50% 30%, #1e293b 0%, #000 70%);
        overflow: hidden;
    }
    
    .bg-stars {
        position: absolute; width: 100%; height: 100%;
        background-image: radial-gradient(rgba(255,255,255,0.2) 1px, transparent 1px);
        background-size: 40px 40px; opacity: 0.3; pointer-events: none;
    }

    /* --- SETUP OVERLAY --- */
    .setup-overlay {
        position: absolute; z-index: 200;
        width: 100%; height: 100%;
        background: rgba(0,0,0,0.85);
        backdrop-filter: blur(10px);
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        gap: 20px;
        animation: fadeIn 0.5s;
    }
    .setup-overlay h1 { font-size: 3rem; margin: 0; color: #fff; text-shadow: 0 0 20px #2dd4bf; letter-spacing: 4px; }
    
    .setup-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; width: 90%; max-width: 400px; }
    
    .player-toggle {
        background: rgba(255,255,255,0.05);
        border: 1px solid var(--c);
        padding: 15px; border-radius: 8px;
        display: flex; flex-direction: column; align-items: center;
        cursor: pointer; transition: 0.2s;
        color: #fff; font-family: 'JetBrains Mono';
        position: relative; overflow: hidden;
    }
    .player-toggle:hover { background: rgba(255,255,255,0.1); }
    .player-toggle .p-status-light {
        width: 100%; height: 4px; background: var(--c);
        position: absolute; bottom: 0; left: 0;
        box-shadow: 0 0 10px var(--c);
    }
    .player-toggle.cpu { opacity: 0.7; border-style: dashed; }
    .player-toggle.cpu .p-type { color: #94a3b8; }
    .p-name { font-weight: bold; }
    .p-type { font-size: 0.8rem; margin-top: 5px; }

    .error-msg { color: #ef4444; font-family: 'JetBrains Mono'; font-weight: bold; background: rgba(239, 68, 68, 0.1); padding: 5px 10px; border-radius: 4px; }

    .start-btn {
        background: #2dd4bf; color: #000;
        border: none; padding: 15px 40px;
        font-family: 'JetBrains Mono'; font-weight: bold; font-size: 1.2rem;
        border-radius: 4px; cursor: pointer; margin-top: 10px;
        transition: 0.2s;
    }
    .start-btn:hover { transform: scale(1.05); box-shadow: 0 0 20px #2dd4bf; }
    .start-btn:disabled { background: #334155; color: #94a3b8; cursor: not-allowed; box-shadow: none; transform: none; }
    
    .exit-link { color: #64748b; text-decoration: none; font-family: 'JetBrains Mono'; font-size: 0.9rem; }

    /* --- TOP UI --- */
    .ui-layer.top {
        position: absolute; top: 0; width: 100%; 
        padding: 20px; display: flex; justify-content: space-between; align-items: flex-start; z-index: 100;
        pointer-events: none;
    }
    
    .back-btn, .restart-btn { 
        pointer-events: auto; text-decoration: none; color: #64748b; 
        border: 1px solid #334155; padding: 5px 10px; border-radius: 4px;
        font-family: 'JetBrains Mono'; font-size: 0.8rem; background: rgba(0,0,0,0.8);
        cursor: pointer;
    }
    .restart-btn:hover { color: #fff; border-color: #fff; }
    
    .status-bar {
        font-family: 'JetBrains Mono'; color: #2dd4bf; 
        background: rgba(0,0,0,0.8); padding: 5px 15px; border-radius: 20px;
        border: 1px solid rgba(45, 212, 191, 0.3); font-weight: bold;
        letter-spacing: 1px;
    }

    /* --- BOARD --- */
    .board-container {
        width: 90vmin; height: 90vmin;
        max-width: 600px; max-height: 600px;
        transform-style: preserve-3d;
        transform: rotateX(40deg) translateY(-80px); 
        transition: transform 0.5s, filter 0.5s;
    }
    .board-container.blurred { filter: blur(5px) brightness(0.5); transform: rotateX(20deg) scale(0.9); }
    
    .board-tilt { width: 100%; height: 100%; transform-style: preserve-3d; position: relative; }
    .board-thickness {
        position: absolute; top: 10px; left: 10px; width: 100%; height: 100%;
        background: #0f172a; transform: translateZ(-20px);
        border-radius: 12px; box-shadow: 0 50px 80px rgba(0,0,0,0.8);
    }
    .board-surface {
        width: 100%; height: 100%;
        background: rgba(15, 23, 42, 0.9); border: 2px solid #334155;
        border-radius: 12px; display: grid;
        grid-template-columns: repeat(15, 1fr); grid-template-rows: repeat(15, 1fr);
        transform-style: preserve-3d; backdrop-filter: blur(5px);
        box-shadow: inset 0 0 50px rgba(0,0,0,0.5);
    }

    /* Zones */
    .zone { position: absolute; opacity: 0.2; }
    .zone.red { grid-area: 1/1/7/7; background: #ef4444; border-bottom: 2px solid #ef4444; border-right: 2px solid #ef4444; }
    .zone.green { grid-area: 1/10/7/16; background: #22c55e; border-bottom: 2px solid #22c55e; border-left: 2px solid #22c55e; }
    .zone.yellow { grid-area: 10/10/16/16; background: #eab308; border-top: 2px solid #eab308; border-left: 2px solid #eab308; }
    .zone.blue { grid-area: 10/1/16/7; background: #3b82f6; border-top: 2px solid #3b82f6; border-right: 2px solid #3b82f6; }
    .zone.center { grid-area: 7/7/10/10; background: radial-gradient(circle, #fff 0%, #000 100%); opacity: 0.1; }

    .cell { border: 1px solid rgba(255,255,255,0.05); }
    .cell.safe { background: rgba(255,255,255,0.1); box-shadow: inset 0 0 10px rgba(255,255,255,0.1); }

    /* Tokens */
    .token {
        width: 60%; height: 60%; justify-self: center; align-self: center;
        background: none; border: none; cursor: pointer; padding: 0;
        transform-style: preserve-3d; transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .token-body {
        width: 100%; height: 100%; border-radius: 50%; background: var(--color);
        box-shadow: inset 0 -5px 10px rgba(0,0,0,0.5), 0 0 10px var(--color);
        transform: rotateX(-40deg);
    }
    .token-shadow {
        position: absolute; bottom: -10px; left: 10%; width: 80%; height: 20%;
        background: rgba(0,0,0,0.6); filter: blur(4px); border-radius: 50%;
        transform: translateZ(-10px);
    }
    .token.active .token-body { animation: float 1s infinite ease-in-out; border: 2px solid #fff; }
    @keyframes float { 0%, 100% { transform: rotateX(-40deg) translateY(0); } 50% { transform: rotateX(-40deg) translateY(-15px); } }

    /* --- FLAT CONTROLS --- */
    .flat-controls {
        position: absolute; bottom: 40px;
        display: flex; flex-direction: column; align-items: center; gap: 20px;
        z-index: 200; width: 100%;
        pointer-events: none;
    }
    .flat-controls button { pointer-events: auto; }

    .turn-indicators {
        display: flex; gap: 15px; background: rgba(0,0,0,0.5);
        padding: 8px 15px; border-radius: 20px;
        backdrop-filter: blur(5px);
    }
    .p-dot { 
        width: 12px; height: 12px; border-radius: 50%; opacity: 0.3; transition: 0.3s; 
        position: relative;
    }
    .p-dot.active { opacity: 1; transform: scale(1.4); }
    .cpu-tag {
        position: absolute; top: -15px; left: 50%; transform: translateX(-50%);
        font-size: 0.6rem; font-family: 'JetBrains Mono'; color: #fff;
    }

    /* REAL DIE BUTTON */
    .real-die-btn {
        width: 80px; height: 80px; background: #e2e8f0; border-radius: 16px; border: none;
        box-shadow: 0 8px 0 #94a3b8, 0 10px 20px rgba(0,0,0,0.5);
        cursor: pointer; transition: all 0.1s;
        display: flex; justify-content: center; align-items: center;
    }
    .real-die-btn:active { transform: translateY(8px); box-shadow: 0 0 0 #94a3b8, 0 0 0 rgba(0,0,0,0.5); }
    .real-die-btn:disabled { filter: grayscale(1) brightness(0.7); cursor: not-allowed; }
    .real-die-btn.rolling { animation: shake 0.1s infinite; }
    .real-die-btn.cpu-turn { opacity: 0.8; cursor: wait; pointer-events: none; }

    .die-face {
        width: 100%; height: 100%; display: grid;
        grid-template-columns: repeat(3, 1fr); grid-template-rows: repeat(3, 1fr);
        padding: 12px; box-sizing: border-box;
    }
    .dot {
        width: 12px; height: 12px; background: #000; border-radius: 50%;
        align-self: center; justify-self: center; opacity: 0;
    }
    .dot.visible { opacity: 1; }

    @keyframes shake {
        0% { transform: rotate(0deg); }
        25% { transform: rotate(5deg); }
        75% { transform: rotate(-5deg); }
        100% { transform: rotate(0deg); }
    }
    @keyframes fadeIn { from { opacity: 0; transform: scale(0.9); } to { opacity: 1; transform: scale(1); } }
</style>