<script lang="ts">
    import { onMount } from 'svelte';

    // --- CONFIGURATION ---
    const COLORS = {
        red: { main: '#ef4444', glow: '#fca5a5', dark: '#991b1b' },
        green: { main: '#10b981', glow: '#6ee7b7', dark: '#047857' },
        yellow: { main: '#eab308', glow: '#fde047', dark: '#a16207' },
        blue: { main: '#3b82f6', glow: '#93c5fd', dark: '#1e40af' }
    };
    const PLAYER_ORDER = ['red', 'green', 'yellow', 'blue'];
    const SAFE_SPOTS = [0, 8, 13, 21, 26, 34, 39, 47]; // Global indices
    const BASES = [0, 13, 26, 39]; // Starting offsets

    // --- STATE ---
    let gameStarted = $state(false);
    let players = $state([
        { id: 0, color: 'red', pieces: [-1, -1, -1, -1], home: 0, isCpu: false },
        { id: 1, color: 'green', pieces: [-1, -1, -1, -1], home: 0, isCpu: true },
        { id: 2, color: 'yellow', pieces: [-1, -1, -1, -1], home: 0, isCpu: true },
        { id: 3, color: 'blue', pieces: [-1, -1, -1, -1], home: 0, isCpu: true }
    ]);

    let turn = $state(0);
    let diceVal = $state(1);
    let isRolling = $state(false);
    let canRoll = $state(true);
    let validMoves = $state<number[]>([]); // Indices of pieces that can move
    let msg = $state("AWAITING SYNC");
    let winner = $state<number | null>(null);

    // --- DERIVED ---
    let allAi = $derived(players.every(p => p.isCpu));
    let turnColor = $derived(COLORS[PLAYER_ORDER[turn] as keyof typeof COLORS].main);

    // --- AUDIO / HAPTICS ---
    function feedback(type: 'tap' | 'success' | 'error' | 'heavy') {
        if (typeof navigator !== 'undefined' && navigator.vibrate) {
            if (type === 'tap') navigator.vibrate(5);
            if (type === 'success') navigator.vibrate([10, 30, 10]);
            if (type === 'error') navigator.vibrate([50, 20, 50]);
            if (type === 'heavy') navigator.vibrate(40);
        }
    }

    // --- GAME LOOP ---
    function toggleCpu(idx: number) {
        players[idx].isCpu = !players[idx].isCpu;
        feedback('tap');
    }

    function initGame() {
        if (allAi) return;
        gameStarted = true;
        msg = "GAME START";
        feedback('success');
        if (players[0].isCpu) setTimeout(aiTurn, 1000);
    }

    function resetGame() {
        gameStarted = false;
        winner = null;
        turn = 0;
        canRoll = true;
        validMoves = [];
        players = players.map(p => ({ ...p, pieces: [-1, -1, -1, -1], home: 0 }));
        msg = "SYSTEM RESET";
    }

    // --- DICE LOGIC ---
    function handleRoll() {
        if (!canRoll || winner !== null || isRolling) return;
        
        isRolling = true;
        canRoll = false;
        msg = "ROLLING...";
        feedback('heavy');

        // Animation timing matches CSS
        setTimeout(() => {
            diceVal = Math.floor(Math.random() * 6) + 1;
            finalizeRoll();
        }, 600); 
    }

    function finalizeRoll() {
        isRolling = false;
        validMoves = [];
        
        // Calculate valid moves
        players[turn].pieces.forEach((pos, i) => {
            if (pos === -1) {
                if (diceVal === 6) validMoves.push(i);
            } else if (pos < 100) { // Not already home
                if (pos + diceVal <= 56) validMoves.push(i);
            }
        });

        if (validMoves.length === 0) {
            msg = "NO MOVES";
            setTimeout(nextTurn, 800);
        } else {
            msg = "SELECT PIECE";
            if (players[turn].isCpu) {
                setTimeout(aiMove, 500);
            }
        }
    }

    function aiMove() {
        if (validMoves.length === 0) return;
        
        // Simple AI: Prioritize Cutting > Entering Home > Opening > Advancing
        let bestPiece = validMoves[0];
        let bestScore = -100;

        validMoves.forEach(idx => {
            let score = 0;
            const currentPos = players[turn].pieces[idx];
            const nextPos = currentPos === -1 ? 0 : currentPos + diceVal;
            
            // 1. Opening is good
            if (currentPos === -1) score += 50;

            // 2. Scoring is great
            if (nextPos === 56) score += 100;

            // 3. Cutting is best
            if (nextPos < 51) {
                const globalPos = getGlobalIndex(turn, nextPos);
                if (!SAFE_SPOTS.includes(globalPos)) {
                    // Check collision
                    players.forEach((p, pId) => {
                        if (pId !== turn) {
                            p.pieces.forEach(ep => {
                                if (ep !== -1 && ep < 51 && getGlobalIndex(pId, ep) === globalPos) {
                                    score += 200; // Kill!
                                }
                            });
                        }
                    });
                }
                // 4. Safety
                if (SAFE_SPOTS.includes(globalPos)) score += 20;
            }
            
            if (score > bestScore) {
                bestScore = score;
                bestPiece = idx;
            }
        });

        handleMove(bestPiece);
    }

    function handleMove(pieceIdx: number) {
        if (!validMoves.includes(pieceIdx)) return;

        const p = players[turn];
        const currentPos = p.pieces[pieceIdx];
        let nextPos = 0;
        let cutHappened = false;

        if (currentPos === -1) {
            nextPos = 0; // Move to start
            feedback('success');
        } else {
            nextPos = currentPos + diceVal;
            feedback('tap');
        }

        // Check Victory
        if (nextPos === 56) {
            p.pieces[pieceIdx] = 106; // Done state
            p.home++;
            msg = "HOME!";
            feedback('success');
            if (p.home === 4) {
                winner = turn;
                msg = `PLAYER ${turn+1} WINS!`;
                return;
            }
        } else {
            p.pieces[pieceIdx] = nextPos;
        }

        // Collision Logic
        if (nextPos < 51) {
            const globalPos = getGlobalIndex(turn, nextPos);
            if (!SAFE_SPOTS.includes(globalPos)) {
                players.forEach((opp, oppIdx) => {
                    if (oppIdx !== turn) {
                        opp.pieces.forEach((oppPos, oppPIdx) => {
                            if (oppPos !== -1 && oppPos < 51) {
                                if (getGlobalIndex(oppIdx, oppPos) === globalPos) {
                                    players[oppIdx].pieces[oppPIdx] = -1; // Send home
                                    msg = "CAPTURED!";
                                    cutHappened = true;
                                    feedback('heavy');
                                }
                            }
                        });
                    }
                });
            }
        }

        // Next Turn Logic
        if (diceVal === 6 || cutHappened || nextPos === 56) {
            // Bonus turn
            validMoves = [];
            canRoll = true;
            msg = "BONUS ROLL";
            if (p.isCpu && winner === null) setTimeout(aiTurn, 1000);
        } else {
            nextTurn();
        }
    }

    function nextTurn() {
        validMoves = [];
        turn = (turn + 1) % 4;
        canRoll = true;
        msg = `P${turn+1} TURN`;
        if (players[turn].isCpu && winner === null) setTimeout(aiTurn, 1000);
    }

    function aiTurn() {
        if (!gameStarted || winner !== null) return;
        handleRoll();
    }

    // --- COORDINATE SYSTEM ---
    function getGlobalIndex(pIdx: number, localPos: number) {
        return (BASES[pIdx] + localPos) % 52;
    }

    function getGridPos(pIdx: number, localPos: number, pieceIdx: number) {
        // 1. BASE STATE
        if (localPos === -1) {
            const baseGrids = [
                [{r:2,c:2}, {r:2,c:3}, {r:3,c:2}, {r:3,c:3}], // Red
                [{r:2,c:13}, {r:2,c:14}, {r:3,c:13}, {r:3,c:14}], // Green
                [{r:13,c:13}, {r:13,c:14}, {r:14,c:13}, {r:14,c:14}], // Yellow
                [{r:13,c:2}, {r:13,c:3}, {r:14,c:2}, {r:14,c:3}], // Blue
            ];
            return { ...baseGrids[pIdx][pieceIdx], z: 0 };
        }

        // 2. VICTORY STATE
        if (localPos >= 100) {
            return { r: 8, c: 8, z: 1 }; // Dead center
        }

        // 3. TRACK STATE
        const path0 = [
            [7,2], [7,3], [7,4], [7,5], [7,6], // 0-4 (Out & Right)
            [6,7], [5,7], [4,7], [3,7], [2,7], [1,7], // 5-10 (Up)
            [1,8], [1,9], // 11-12 (Turn)
            [2,9], [3,9], [4,9], [5,9], [6,9], // 13-17 (Down)
            [7,10], // 18 (Turn Right)
            [7,11], [7,12], [7,13], [7,14], [7,15], // 19-23 (Right)
            [8,15], [9,15], // 24-25 (Turn)
            [9,14], [9,13], [9,12], [9,11], [9,10], // 26-30 (Left)
            [10,9], // 31 (Turn Down)
            [11,9], [12,9], [13,9], [14,9], [15,9], // 32-36 (Down)
            [15,8], [15,7], // 37-38 (Turn)
            [14,7], [13,7], [12,7], [11,7], [10,7], // 39-43 (Up)
            [9,6], // 44 (Turn Left)
            [9,5], [9,4], [9,3], [9,2], [9,1], // 45-49 (Left)
            [8,1], // 50 (Turn Up - Ready for Home)
            // HOME RUN (51-56)
            [8,2], [8,3], [8,4], [8,5], [8,6], [8,7] 
        ];

        let coords = path0[localPos];
        if (!coords) return { r: 8, c: 8, z: 0 };

        let r = coords[0];
        let c = coords[1];

        // Rotate for other players
        for(let i=0; i<pIdx; i++) {
            let oldR = r;
            r = c;
            c = 16 - oldR;
        }

        return { r, c, z: 0 };
    }

    // --- COLLISION VISUALIZER ---
    // Calculates offset if multiple pieces are on the same cell
    function getVisualOffset(pIdx: number, pieceIdx: number, r: number, c: number) {
        // Find all pieces at this location
        const occupants: { pid: number, uid: number }[] = [];
        
        players.forEach((p, i) => {
            p.pieces.forEach((pos, j) => {
                const posCoords = getGridPos(i, pos, j);
                if (posCoords.r === r && posCoords.c === c) {
                    occupants.push({ pid: i, uid: j });
                }
            });
        });

        // If only 1, no offset needed
        if (occupants.length <= 1) return { x: 0, y: 0, scale: 1 };

        // Deterministic sort to keep positions stable
        occupants.sort((a, b) => (a.pid * 4 + a.uid) - (b.pid * 4 + b.uid));
        
        const myIndex = occupants.findIndex(o => o.pid === pIdx && o.uid === pieceIdx);
        
        // Circular spread logic
        const spread = 20; // Pixels apart
        const angle = (360 / occupants.length) * myIndex;
        // Convert to radians
        const rad = angle * (Math.PI / 180);
        
        return {
            x: Math.cos(rad) * spread,
            y: Math.sin(rad) * spread,
            scale: 0.7 // Shrink overlapping pieces
        };
    }

</script>

<div class="viewport">
    <div class="ambient-glow" style="--turn-color: {turnColor}"></div>

    {#if !gameStarted}
        <div class="overlay">
            <div class="glass-panel menu">
                <h1 class="logo">RESINEN<span>PRIME</span></h1>
                <div class="player-grid">
                    {#each players as p, i}
                        <button class="p-card" 
                            onclick={() => toggleCpu(i)}
                            style="--p-color: {COLORS[PLAYER_ORDER[i]].main}">
                            <div class="p-icon" class:cpu={p.isCpu}>
                                {p.isCpu ? 'AI' : 'P'+(i+1)}
                            </div>
                            <div class="p-label">{p.isCpu ? 'DROID' : 'HUMAN'}</div>
                        </button>
                    {/each}
                </div>
                {#if allAi}
                    <div class="warning">REQUIRES HUMAN OPERATOR</div>
                {/if}
                <button class="action-btn" disabled={allAi} onclick={initGame}>
                    INITIALIZE SEQUENCE
                </button>
            </div>
        </div>
    {/if}

    {#if gameStarted}
        <div class="hud top">
            <div class="status-pill">{msg}</div>
            <button class="icon-btn" onclick={resetGame}>↺</button>
        </div>
    {/if}

    <div class="board-stage">
        <div class="board-plate">
            <div class="zone base red"></div>
            <div class="zone base green"></div>
            <div class="zone base yellow"></div>
            <div class="zone base blue"></div>

            {#each Array(15) as _, r}
                {#each Array(15) as _, c}
                    {#if !((r<6 && c<6) || (r<6 && c>8) || (r>8 && c<6) || (r>8 && c>8))}
                        <div class="cell" style="grid-row: {r+1}; grid-column: {c+1}"></div>
                    {/if}
                {/each}
            {/each}

            <svg class="markings" viewBox="0 0 150 150" xmlns="http://www.w3.org/2000/svg">
                <rect x="60" y="60" width="30" height="30" fill="#1e293b" rx="2" />
                
                <path d="M60 60 L75 75 L60 90 Z" fill={COLORS.red.main} opacity="0.2" /> <path d="M60 60 L90 60 L75 75 Z" fill={COLORS.green.main} opacity="0.2" /> <path d="M90 60 L90 90 L75 75 Z" fill={COLORS.yellow.main} opacity="0.2" /> <path d="M60 90 L90 90 L75 75 Z" fill={COLORS.blue.main} opacity="0.2" /> <rect x="10" y="60" width="10" height="10" fill={COLORS.red.main} opacity="0.3"/>
                <rect x="80" y="10" width="10" height="10" fill={COLORS.green.main} opacity="0.3"/>
                <rect x="130" y="80" width="10" height="10" fill={COLORS.yellow.main} opacity="0.3"/>
                <rect x="60" y="130" width="10" height="10" fill={COLORS.blue.main} opacity="0.3"/>

                <text x="75" y="77" fill="#facc15" font-size="10" text-anchor="middle" style="filter: drop-shadow(0 0 2px rgba(0,0,0,0.5))">★</text>
            </svg>

            {#each players as p, pIdx}
                {#each p.pieces as pos, i}
                    {@const coords = getGridPos(pIdx, pos, i)}
                    {@const visual = getVisualOffset(pIdx, i, coords.r, coords.c)}
                    
                    <button class="piece"
                        class:movable={gameStarted && turn === pIdx && validMoves.includes(i)}
                        onclick={() => handleMove(i)}
                        style="
                            --p-color: {COLORS[PLAYER_ORDER[pIdx]].main};
                            --p-glow: {COLORS[PLAYER_ORDER[pIdx]].glow};
                            grid-row: {coords.r};
                            grid-column: {coords.c};
                            transform: translate({visual.x}px, {visual.y}px) scale({visual.scale});
                            z-index: {visual.scale < 1 ? 20 : 10};
                        ">
                        <div class="piece-head"></div>
                        <div class="piece-base"></div>
                    </button>
                {/each}
            {/each}
        </div>
    </div>

    {#if gameStarted}
        <div class="hud bottom">
            <div class="turn-stripe">
                {#each players as p, i}
                    <div class="turn-dot" 
                        class:active={turn === i}
                        style="--d-color: {COLORS[PLAYER_ORDER[i]].main}">
                    </div>
                {/each}
            </div>

            <div class="dice-stage">
                <button class="cube-wrap" onclick={handleRoll} disabled={!canRoll}>
                    <div class="cube" class:spinning={isRolling} 
                        style="transform: rotateX({isRolling ? 720 : 0}deg) rotateY({isRolling ? 720 : 0}deg)">
                        <div class="face front">
                            {#each Array(diceVal) as _}<span class="dot"></span>{/each}
                        </div>
                        <div class="face back"></div>
                        <div class="face right"></div>
                        <div class="face left"></div>
                        <div class="face top"></div>
                        <div class="face bottom"></div>
                    </div>
                </button>
            </div>
        </div>
    {/if}
</div>

<style>
    /* === RESINEN PRIME: THEME ENGINE === */
    :global(body) {
        margin: 0;
        background: #020617;
        color: #fff;
        font-family: 'Rajdhani', 'Segoe UI', sans-serif;
        overflow: hidden;
        user-select: none;
        -webkit-tap-highlight-color: transparent;
    }

    /* UTILS */
    .viewport {
        position: relative;
        width: 100vw; height: 100dvh;
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        perspective: 1200px;
    }

    .ambient-glow {
        position: absolute; inset: 0;
        background: radial-gradient(circle at 50% 50%, var(--turn-color) 0%, transparent 60%);
        opacity: 0.15;
        transition: background 1s ease;
        pointer-events: none;
    }

    /* --- BOARD ARCHITECTURE --- */
    .board-stage {
        transform-style: preserve-3d;
        /* Mobile Portrait Default */
        width: 94vw; height: 94vw;
        max-width: 600px; max-height: 600px;
        transform: rotateX(25deg) translateY(-20px);
        transition: transform 0.5s cubic-bezier(0.2, 0.8, 0.2, 1);
    }

    /* Landscape Override */
    @media (min-aspect-ratio: 1/1) {
        .board-stage {
            width: 80vh; height: 80vh;
            transform: rotateX(35deg) translateY(-40px);
        }
    }

    .board-plate {
        width: 100%; height: 100%;
        background: rgba(15, 23, 42, 0.6);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 
            0 20px 50px -10px rgba(0, 0, 0, 0.5),
            inset 0 0 0 1px rgba(255, 255, 255, 0.05);
        display: grid;
        grid-template-columns: repeat(15, 1fr);
        grid-template-rows: repeat(15, 1fr);
        padding: 12px;
        gap: 2px;
        transform-style: preserve-3d;
    }

    /* ZONES */
    .zone.base {
        border-radius: 16px;
        position: relative;
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.3);
    }
    .zone.red { grid-area: 1/1/7/7; background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); }
    .zone.green { grid-area: 1/10/7/16; background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); }
    .zone.yellow { grid-area: 10/10/16/16; background: rgba(234, 179, 8, 0.15); border: 1px solid rgba(234, 179, 8, 0.3); }
    .zone.blue { grid-area: 10/1/16/7; background: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.3); }

    /* CELLS */
    .cell {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 2px;
    }

    /* MARKINGS (SVG) */
    .markings {
        position: absolute; inset: 0; width: 100%; height: 100%;
        pointer-events: none;
        z-index: 1;
        padding: 12px; /* Match board padding */
    }

    /* --- PIECES (Gottis) --- */
    .piece {
        position: relative;
        width: 80%; height: 80%;
        justify-self: center; align-self: center;
        background: none; border: none; padding: 0;
        cursor: pointer;
        transform-style: preserve-3d;
        transition: transform 0.3s cubic-bezier(0.3, 1.5, 0.5, 1);
        z-index: 10;
    }

    .piece-head {
        position: absolute; inset: 0;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #fff, var(--p-color));
        box-shadow: 0 0 10px var(--p-color);
        transform: translateZ(10px);
        border: 2px solid rgba(255,255,255,0.8);
    }
    
    .piece-base {
        position: absolute; inset: 2px;
        border-radius: 50%;
        background: #000;
        opacity: 0.5;
        filter: blur(4px);
        transform: translateZ(1px);
    }

    .piece.movable {
        animation: pulse 1.5s infinite;
    }
    .piece.movable .piece-head {
        border-color: #fff;
        box-shadow: 0 0 20px #fff, 0 0 40px var(--p-color);
    }

    @keyframes pulse {
        0%, 100% { transform: scale(1) translateZ(0); }
        50% { transform: scale(1.1) translateZ(5px); }
    }

    /* --- DICE (3D Cube) --- */
    .dice-stage {
        width: 80px; height: 80px;
        perspective: 400px;
    }
    .cube-wrap {
        width: 100%; height: 100%; background: none; border: none; padding: 0; cursor: pointer;
    }
    .cube {
        width: 100%; height: 100%;
        position: relative;
        transform-style: preserve-3d;
        transition: transform 0.6s cubic-bezier(0.2, 0.8, 0.2, 1.2);
    }
    .cube.spinning {
        animation: tumble 0.6s linear infinite;
    }
    .face {
        position: absolute; width: 80px; height: 80px;
        background: #fff;
        border: 4px solid #cbd5e1;
        border-radius: 12px;
        display: flex; flex-wrap: wrap; align-items: center; justify-content: center; gap: 8px; padding: 12px;
        backface-visibility: hidden;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.2);
    }
    .face.front  { transform: rotateY(0deg) translateZ(40px); }
    .face.back   { transform: rotateY(180deg) translateZ(40px); }
    .face.right  { transform: rotateY(90deg) translateZ(40px); }
    .face.left   { transform: rotateY(-90deg) translateZ(40px); }
    .face.top    { transform: rotateX(90deg) translateZ(40px); }
    .face.bottom { transform: rotateX(-90deg) translateZ(40px); }

    .dot { width: 14px; height: 14px; background: #0f172a; border-radius: 50%; box-shadow: inset 0 2px 2px rgba(0,0,0,0.5); }

    @keyframes tumble {
        0% { transform: rotateX(0) rotateY(0) rotateZ(0); }
        100% { transform: rotateX(360deg) rotateY(720deg) rotateZ(360deg); }
    }

    /* --- UI HUD --- */
    .hud {
        position: absolute; width: 100%; max-width: 500px;
        display: flex; justify-content: center; align-items: center;
        z-index: 100;
        pointer-events: none;
    }
    .hud button { pointer-events: auto; }
    
    .hud.top { top: 20px; justify-content: space-between; padding: 0 20px; }
    .hud.bottom { bottom: 40px; flex-direction: column; gap: 20px; }

    .status-pill {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(255,255,255,0.2);
        padding: 8px 16px; border-radius: 30px;
        font-weight: 700; letter-spacing: 1px;
        backdrop-filter: blur(10px);
        font-size: 0.9rem;
    }

    .icon-btn {
        width: 40px; height: 40px;
        border-radius: 50%;
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        color: #fff; font-size: 1.2rem;
        cursor: pointer;
        backdrop-filter: blur(5px);
    }

    .turn-stripe {
        display: flex; gap: 12px;
        background: rgba(15, 23, 42, 0.8);
        padding: 10px 20px; border-radius: 40px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .turn-dot {
        width: 12px; height: 12px; border-radius: 50%;
        background: var(--d-color);
        opacity: 0.3; transition: 0.3s;
    }
    .turn-dot.active { opacity: 1; box-shadow: 0 0 10px var(--d-color); transform: scale(1.3); }

    /* --- OVERLAY MENU --- */
    .overlay {
        position: absolute; inset: 0;
        background: rgba(2, 6, 23, 0.8);
        backdrop-filter: blur(15px);
        z-index: 200;
        display: flex; align-items: center; justify-content: center;
    }
    
    .glass-panel {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255,255,255,0.1);
        padding: 40px; border-radius: 24px;
        display: flex; flex-direction: column; align-items: center; gap: 24px;
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
    }

    .logo { 
        font-size: 3rem; margin: 0; font-weight: 800; letter-spacing: 4px; 
        background: linear-gradient(to right, #fff, #94a3b8);
        -webkit-background-clip: text; color: transparent;
    }
    .logo span { font-size: 1rem; color: #3b82f6; letter-spacing: 2px; margin-left: 10px; }

    .player-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; width: 100%; }
    
    .p-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        padding: 16px; border-radius: 12px;
        display: flex; flex-direction: column; align-items: center; gap: 8px;
        cursor: pointer; color: #fff; transition: 0.2s;
    }
    .p-card:hover { background: rgba(255,255,255,0.1); }
    .p-icon {
        width: 40px; height: 40px; border-radius: 50%;
        background: var(--p-color);
        display: flex; align-items: center; justify-content: center;
        font-weight: 800; text-shadow: 0 1px 2px rgba(0,0,0,0.3);
    }
    .p-icon.cpu { filter: grayscale(0.5); border: 2px dashed rgba(255,255,255,0.5); }
    .p-label { font-size: 0.7rem; letter-spacing: 1px; opacity: 0.7; }

    .action-btn {
        background: #fff; color: #020617;
        padding: 16px 48px; border-radius: 100px;
        font-weight: 800; font-size: 1rem; letter-spacing: 1px;
        border: none; cursor: pointer;
        transition: transform 0.2s;
    }
    .action-btn:hover { transform: scale(1.05); }
    .action-btn:disabled { opacity: 0.5; cursor: not-allowed; }
    .warning { color: #ef4444; font-size: 0.8rem; letter-spacing: 1px; font-weight: 700; }
</style>