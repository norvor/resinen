<script lang="ts">
    import { onMount } from 'svelte';

    // --- STATE ---
    let myBoard = $state<number[][]>([]); // 0=Empty, 1=Ship, 2=Miss, 3=Hit
    let enemyBoard = $state<number[][]>([]); // 0=Unknown, 2=Miss, 3=Hit
    let token = $state("");
    let msg = $state("Initializing Radar...");
    let turn = $state("PLAYER"); // PLAYER or CPU
    let gameOver = $state(false);
    let playerHits = 0;
    let cpuHits = 0;
    const TOTAL_HITS_NEEDED = 17; // 5+4+3+3+2

    // --- LOGIC ---
    async function startGame() {
        // Init Boards
        myBoard = Array(10).fill(null).map(() => Array(10).fill(0));
        enemyBoard = Array(10).fill(null).map(() => Array(10).fill(0));
        
        // Randomly place OUR ships (Client side simple placement for now)
        placeShips(myBoard);

        const res = await fetch('http://localhost:8000/games/battleship/new', { method: 'POST' });
        const data = await res.json();
        token = data.token;
        msg = "Radar Active. Select coordinates.";
        turn = "PLAYER";
        gameOver = false;
        playerHits = 0;
        cpuHits = 0;
    }

    function placeShips(board: number[][]) {
        // Simplified random placement for player visual
        const ships = [5, 4, 3, 3, 2];
        ships.forEach(size => {
            let placed = false;
            while (!placed) {
                const vert = Math.random() > 0.5;
                const r = Math.floor(Math.random() * 10);
                const c = Math.floor(Math.random() * 10);
                if ((vert && r + size > 10) || (!vert && c + size > 10)) continue;
                // Overlap check skipped for brevity in this snippet, but easy to add
                for(let i=0; i<size; i++) {
                    if (vert) board[r+i][c] = 1; else board[r][c+i] = 1;
                }
                placed = true;
            }
        });
    }

    async function handleFire(r: number, c: number) {
        if (gameOver || turn !== "PLAYER" || enemyBoard[r][c] !== 0) return;

        // Optimistic UI
        enemyBoard[r][c] = 2; // Assume miss first to show click

        const res = await fetch('http://localhost:8000/games/battleship/fire', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ token, r, c })
        });
        const data = await res.json();

        if (data.hit) {
            enemyBoard[r][c] = 3; // HIT
            msg = "TARGET HIT!";
            playerHits++;
            if (playerHits >= TOTAL_HITS_NEEDED) {
                msg = "ENEMY FLEET DESTROYED. YOU WIN.";
                gameOver = true;
                return;
            }
        } else {
            enemyBoard[r][c] = 2; // MISS
            msg = "Miss.";
            turn = "CPU";
            setTimeout(cpuTurn, 1000);
        }
    }

    function cpuTurn() {
        if (gameOver) return;
        // Simple random AI
        let r, c;
        do {
            r = Math.floor(Math.random() * 10);
            c = Math.floor(Math.random() * 10);
        } while (myBoard[r][c] > 1); // Don't shoot same spot

        if (myBoard[r][c] === 1) {
            myBoard[r][c] = 3; // HIT
            cpuHits++;
            msg = "WARNING: WE ARE HIT!";
            if (cpuHits >= TOTAL_HITS_NEEDED) {
                msg = "CRITICAL FAILURE. WE ARE SUNK.";
                gameOver = true;
            } else {
                setTimeout(cpuTurn, 1000); // CPU fires again if hit
            }
        } else {
            myBoard[r][c] = 2; // MISS
            msg = "Enemy missed. Your turn.";
            turn = "PLAYER";
        }
    }

    onMount(() => startGame());
</script>

<div class="game-container">
    <div class="bg-layer stars"></div>
    <div class="game-ui">
        <div class="header">
            <a href="/" class="back-btn">← DOCK</a>
            <h1>NEON BATTLESHIP</h1>
            <div class="status">{msg}</div>
        </div>

        <div class="boards">
            <div class="board-container">
                <h3>ENEMY SECTOR</h3>
                <div class="grid">
                    {#each enemyBoard as row, r}
                        {#each row as cell, c}
                            <div 
                                class="cell enemy" 
                                class:hit={cell === 3} 
                                class:miss={cell === 2}
                                onclick={() => handleFire(r, c)}
                            ></div>
                        {/each}
                    {/each}
                </div>
            </div>

            <div class="board-container">
                <h3>HOME FLEET</h3>
                <div class="grid">
                    {#each myBoard as row, r}
                        {#each row as cell, c}
                            <div 
                                class="cell friendly" 
                                class:ship={cell === 1}
                                class:hit={cell === 3} 
                                class:miss={cell === 2}
                            ></div>
                        {/each}
                    {/each}
                </div>
            </div>
        </div>
        
        {#if gameOver}
            <button class="reset-btn" onclick={startGame}>RESTART WARGAME</button>
        {/if}
    </div>
</div>

<style>
    :global(body) { margin: 0; background-color: #020617; color: #f8fafc; font-family: 'Space Grotesk', sans-serif; }
    .stars { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: radial-gradient(#fff 1px, transparent 1px); background-size: 50px 50px; opacity: 0.1; }
    .game-container { height: 100vh; display: flex; justify-content: center; align-items: center; position: relative; }
    .game-ui { z-index: 1; display: flex; flex-direction: column; align-items: center; gap: 30px; }
    .header { text-align: center; width: 100%; position: relative; }
    .back-btn { position: absolute; left: -100px; top: 50%; transform: translateY(-50%); text-decoration: none; color: #94a3b8; font-family: 'JetBrains Mono'; font-size: 0.8rem; border: 1px solid #334155; padding: 5px 10px; border-radius: 4px; }
    h1 { font-size: 2.5rem; margin: 0; color: #10b981; text-shadow: 0 0 20px #10b981; letter-spacing: 2px; }
    .status { font-family: 'JetBrains Mono'; color: #fff; margin-top: 10px; }

    .boards { display: flex; gap: 50px; }
    .board-container { text-align: center; }
    h3 { font-family: 'JetBrains Mono'; font-size: 0.9rem; color: #64748b; margin-bottom: 10px; }

    .grid { display: grid; grid-template-columns: repeat(10, 30px); gap: 2px; background: #0f172a; padding: 5px; border: 2px solid #334155; border-radius: 4px; }
    .cell { width: 30px; height: 30px; background: #1e293b; cursor: crosshair; transition: 0.1s; }
    .cell.enemy:hover { background: #334155; }
    
    .cell.ship { background: #3b82f6; }
    .cell.hit { background: #ef4444; box-shadow: 0 0 10px #ef4444; }
    .cell.miss { background: #94a3b8; opacity: 0.5; }
    
    .reset-btn { padding: 10px 30px; background: #10b981; color: #000; border: none; font-weight: bold; cursor: pointer; font-family: 'JetBrains Mono'; }
</style>