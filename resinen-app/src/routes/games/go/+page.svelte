<script lang="ts">
    import { onMount } from 'svelte';

    // --- STATE ---
    let board = $state<number[][]>(Array(9).fill(null).map(() => Array(9).fill(0)));
    let capturedPlayer = $state(0);
    let capturedBot = $state(0);
    let message = $state("Your Turn (Cyan).");
    let isThinking = $state(false);

    // --- LOGIC ---
    async function handleIntersectClick(r: number, c: number) {
        if (isThinking || board[r][c] !== 0) return;

        isThinking = true;
        message = "Computing...";

        try {
            const res = await fetch('https://api.resinen.com/games/go/move', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ board, row: r, col: c })
            });
            const data = await res.json();

            if (!data.valid) {
                message = "Invalid Move (Suicide).";
                isThinking = false;
                return;
            }

            board = data.board;
            capturedPlayer += data.captured_by_player;
            capturedBot += data.captured_by_bot;
            message = "Your Turn.";
        } catch (e) {
            message = "Connection Lost.";
        } finally {
            isThinking = false;
        }
    }

    function resetGame() {
        board = Array(9).fill(null).map(() => Array(9).fill(0));
        capturedPlayer = 0;
        capturedBot = 0;
        message = "New Game. Your Turn.";
    }

    // --- VISUALS ---
    const GRID_SIZE = 500;
    const CELL_SIZE = GRID_SIZE / 9;
    const PADDING = CELL_SIZE / 2;
</script>

<div class="game-container">
    <div class="bg-layer stars"></div>
    
    <div class="game-ui">
        <div class="header">
            <a href="/" class="back-btn">← DOCK</a>
            <h1>NEON GO</h1>
            <div class="scores">
                <span class="p1">YOU: {capturedPlayer}</span>
                <span class="p2">BOT: {capturedBot}</span>
            </div>
        </div>

        <div class="go-board-wrapper">
            <div class="status">{message}</div>
            
            <div class="board" style="width: {GRID_SIZE}px; height: {GRID_SIZE}px;">
                {#each Array(9) as _, i}
                    <div class="line h" style="top: {PADDING + i * CELL_SIZE}px; left: {PADDING}px; width: {GRID_SIZE - CELL_SIZE}px;"></div>
                    <div class="line v" style="left: {PADDING + i * CELL_SIZE}px; top: {PADDING}px; height: {GRID_SIZE - CELL_SIZE}px;"></div>
                {/each}

                {#each board as row, r}
                    {#each row as cell, c}
                        <div 
                            class="intersection" 
                            style="top: {PADDING + r * CELL_SIZE}px; left: {PADDING + c * CELL_SIZE}px;"
                            onclick={() => handleIntersectClick(r, c)}
                        >
                            {#if cell === 1}
                                <div class="stone player"></div>
                            {:else if cell === 2}
                                <div class="stone bot"></div>
                            {:else}
                                <div class="hover-guide"></div>
                            {/if}
                        </div>
                    {/each}
                {/each}
                
                {#each [[2,2], [2,6], [6,2], [6,6], [4,4]] as [r, c]}
                    <div class="hoshi" style="top: {PADDING + r * CELL_SIZE}px; left: {PADDING + c * CELL_SIZE}px;"></div>
                {/each}
            </div>
        </div>

        <div class="controls">
            <button onclick={resetGame}>CLEAR BOARD</button>
        </div>
    </div>
</div>

<style>
    :global(body) { margin: 0; background-color: #0f172a; color: #f8fafc; font-family: 'Space Grotesk', sans-serif; overflow: hidden; }
    .stars { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: radial-gradient(#fff 1px, transparent 1px); background-size: 50px 50px; opacity: 0.1; }
    
    .game-container { height: 100vh; display: flex; justify-content: center; align-items: center; position: relative; }
    .game-ui { z-index: 1; display: flex; flex-direction: column; align-items: center; gap: 20px; }
    
    .header { text-align: center; width: 100%; position: relative; }
    .back-btn { position: absolute; left: -100px; top: 50%; transform: translateY(-50%); text-decoration: none; color: #94a3b8; font-family: 'JetBrains Mono'; font-size: 0.8rem; border: 1px solid #334155; padding: 5px 10px; border-radius: 4px; }
    h1 { font-size: 2.5rem; letter-spacing: 2px; margin: 0; color: #fff; text-shadow: 0 0 10px #2dd4bf; }
    
    .scores { font-family: 'JetBrains Mono'; color: #94a3b8; display: flex; gap: 20px; justify-content: center; margin-top: 5px; }
    .p1 { color: #2dd4bf; }
    .p2 { color: #c084fc; }

    .go-board-wrapper { display: flex; flex-direction: column; align-items: center; gap: 10px; }
    .status { font-family: 'JetBrains Mono'; color: #fff; font-size: 0.9rem; min-height: 20px; }

    .board { position: relative; background: rgba(30, 41, 59, 0.5); border-radius: 4px; box-shadow: 0 0 50px rgba(0,0,0,0.5); }
    
    /* Grid Lines */
    .line { position: absolute; background: #475569; }
    .line.h { height: 2px; transform: translateY(-1px); }
    .line.v { width: 2px; transform: translateX(-1px); }
    
    /* Hoshi (Star Points) */
    .hoshi { 
        position: absolute; width: 8px; height: 8px; background: #94a3b8; 
        border-radius: 50%; transform: translate(-50%, -50%); 
    }

    /* Intersections & Stones */
    .intersection { 
        position: absolute; width: 40px; height: 40px; 
        transform: translate(-50%, -50%); cursor: pointer;
        display: flex; justify-content: center; align-items: center;
        border-radius: 50%;
    }
    .intersection:hover .hover-guide { opacity: 1; transform: scale(1); }

    .hover-guide { 
        width: 15px; height: 15px; background: rgba(45, 212, 191, 0.3); 
        border-radius: 50%; opacity: 0; transition: 0.2s; transform: scale(0.5);
    }

    .stone { 
        width: 36px; height: 36px; border-radius: 50%; 
        box-shadow: inset 0 0 10px rgba(0,0,0,0.5), 0 0 10px rgba(0,0,0,0.5);
        transition: transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        transform: scale(0); animation: pop 0.2s forwards;
    }
    @keyframes pop { to { transform: scale(1); } }

    .stone.player { background: radial-gradient(circle at 30% 30%, #2dd4bf, #0f766e); box-shadow: 0 0 15px #2dd4bf; }
    .stone.bot { background: radial-gradient(circle at 30% 30%, #e879f9, #7e22ce); box-shadow: 0 0 15px #c084fc; }

    .controls button {
        background: transparent; border: 1px solid #94a3b8; color: #94a3b8; 
        padding: 10px 30px; font-family: 'JetBrains Mono'; font-weight: bold; 
        cursor: pointer; border-radius: 4px; transition: 0.2s;
    }
    .controls button:hover { border-color: #fff; color: #fff; }
</style>