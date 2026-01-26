<script lang="ts">
    import { onMount, onDestroy } from 'svelte'; // <--- FIXED IMPORT

    // --- STATE ---
    let board = $state<number[][]>([]); // The hidden values (-1=Mine, 0-8=Count)
    let revealed = $state<boolean[][]>([]); // Visual state
    let flagged = $state<boolean[][]>([]);
    
    let difficulty = $state("medium");
    let gameOver = $state(false);
    let win = $state(false);
    let mineCount = $state(40);
    let flagsUsed = $state(0);
    let timer = $state(0);
    let timerInterval: any;
    let loading = $state(true);

    // --- LOGIC ---
    async function newGame() {
        loading = true;
        gameOver = false;
        win = false;
        flagsUsed = 0;
        timer = 0;
        clearInterval(timerInterval);
        
        try {
            const res = await fetch(`http://localhost:8000/games/minesweeper/new?difficulty=${difficulty}`);
            const data = await res.json();
            board = data.board;
            
            const rows = board.length;
            const cols = board[0].length;
            
            revealed = Array(rows).fill(null).map(() => Array(cols).fill(false));
            flagged = Array(rows).fill(null).map(() => Array(cols).fill(false));
            
            // Set mine count based on difficulty
            if (difficulty === 'easy') mineCount = 10;
            else if (difficulty === 'hard') mineCount = 99;
            else mineCount = 40;

            timerInterval = setInterval(() => timer++, 1000);
        } catch (e) {
            console.error("Minesweeper Error", e);
        } finally {
            loading = false;
        }
    }

    function reveal(r: number, c: number) {
        if (gameOver || win || flagged[r][c] || revealed[r][c]) return;

        revealed[r][c] = true;

        if (board[r][c] === -1) {
            // BOOM
            gameOver = true;
            clearInterval(timerInterval);
            revealAll();
        } else if (board[r][c] === 0) {
            // Auto-reveal neighbors (Flood Fill)
            for (let i = -1; i <= 1; i++) {
                for (let j = -1; j <= 1; j++) {
                    const nr = r + i, nc = c + j;
                    if (nr >= 0 && nr < board.length && nc >= 0 && nc < board[0].length) {
                        if (!revealed[nr][nc]) reveal(nr, nc);
                    }
                }
            }
        }
        
        checkWin();
    }

    function toggleFlag(e: MouseEvent, r: number, c: number) {
        e.preventDefault(); // Stop context menu
        if (gameOver || win || revealed[r][c]) return;

        flagged[r][c] = !flagged[r][c];
        flagsUsed += flagged[r][c] ? 1 : -1;
    }

    function revealAll() {
        // Show all mines on game over
        revealed = revealed.map((row, r) => row.map((val, c) => board[r][c] === -1 ? true : val));
    }

    function checkWin() {
        // Check if all non-mine squares are revealed
        let safeSquaresLeft = 0;
        for (let r = 0; r < board.length; r++) {
            for (let c = 0; c < board[0].length; c++) {
                if (board[r][c] !== -1 && !revealed[r][c]) safeSquaresLeft++;
            }
        }
        if (safeSquaresLeft === 0) {
            win = true;
            clearInterval(timerInterval);
        }
    }

    // Color code numbers for that classic feel but neon
    function getNumColor(n: number) {
        const colors = ['transparent', '#3b82f6', '#4ade80', '#ef4444', '#a855f7', '#facc15', '#ec4899', '#fff', '#000'];
        return colors[n];
    }

    onMount(() => newGame());
    onDestroy(() => clearInterval(timerInterval));
</script>

<div class="game-container">
    <div class="bg-layer stars"></div>
    
    <div class="game-ui">
        <div class="header">
            <a href="/" class="back-btn">← DOCK</a>
            <h1>NEON BREACH</h1>
            <div class="stats">
                <span class="stat">MINES: <span class="val">{mineCount - flagsUsed}</span></span>
                <span class="stat">TIME: <span class="val">{timer}s</span></span>
            </div>
        </div>

        {#if loading}
            <div class="loading">GENERATING GRID...</div>
        {:else}
            <div class="grid-wrapper" class:shake={gameOver && !win}>
                {#if gameOver}
                    <div class="overlay fail">
                        <h2>SYSTEM FAILURE</h2>
                        <button onclick={newGame}>RETRY</button>
                    </div>
                {/if}
                {#if win}
                    <div class="overlay win">
                        <h2>ACCESS GRANTED</h2>
                        <button onclick={newGame}>NEXT NODE</button>
                    </div>
                {/if}

                <div class="mine-grid" style="grid-template-columns: repeat({board[0].length}, 30px);">
                    {#each board as row, r}
                        {#each row as cell, c}
                            <div 
                                class="cell" 
                                class:revealed={revealed[r][c]}
                                class:flagged={flagged[r][c]}
                                class:mine={revealed[r][c] && cell === -1}
                                onclick={() => reveal(r, c)}
                                oncontextmenu={(e) => toggleFlag(e, r, c)}
                                style="color: {revealed[r][c] && cell > 0 ? getNumColor(cell) : 'inherit'}"
                            >
                                {#if flagged[r][c]}
                                    🚩
                                {:else if revealed[r][c]}
                                    {#if cell === -1}
                                        💣
                                    {:else if cell > 0}
                                        {cell}
                                    {/if}
                                {/if}
                            </div>
                        {/each}
                    {/each}
                </div>
            </div>
        {/if}

        <div class="controls">
            <button onclick={() => { difficulty = 'easy'; newGame(); }} class:active={difficulty === 'easy'}>EASY</button>
            <button onclick={() => { difficulty = 'medium'; newGame(); }} class:active={difficulty === 'medium'}>MEDIUM</button>
            <button onclick={() => { difficulty = 'hard'; newGame(); }} class:active={difficulty === 'hard'}>HARD</button>
        </div>
    </div>
</div>

<style>
    :global(body) { margin: 0; background-color: #0f172a; color: #f8fafc; font-family: 'Space Grotesk', sans-serif; overflow: hidden; }
    .stars { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: radial-gradient(#fff 1px, transparent 1px); background-size: 50px 50px; opacity: 0.1; }
    
    .game-container { height: 100vh; display: flex; justify-content: center; align-items: center; position: relative; }
    .game-ui { z-index: 1; display: flex; flex-direction: column; align-items: center; gap: 20px; }
    
    .header { text-align: center; width: 100%; position: relative; margin-bottom: 10px; }
    .back-btn { position: absolute; left: -100px; top: 50%; transform: translateY(-50%); text-decoration: none; color: #94a3b8; font-family: 'JetBrains Mono'; font-size: 0.8rem; border: 1px solid #334155; padding: 5px 10px; border-radius: 4px; }
    h1 { font-size: 2.5rem; letter-spacing: 2px; margin: 0; color: #fff; text-shadow: 0 0 20px #ef4444; }
    
    .stats { display: flex; gap: 30px; justify-content: center; font-family: 'JetBrains Mono'; font-size: 1.2rem; color: #94a3b8; margin-top: 5px; }
    .val { color: #ef4444; font-weight: bold; text-shadow: 0 0 10px rgba(239, 68, 68, 0.5); }

    .grid-wrapper { position: relative; border: 2px solid #334155; box-shadow: 0 0 50px rgba(0,0,0,0.5); border-radius: 8px; overflow: hidden; }
    .grid-wrapper.shake { animation: shake 0.5s; border-color: #ef4444; }

    .mine-grid { display: grid; gap: 1px; background: #334155; }
    
    .cell { 
        width: 30px; height: 30px; background: #1e293b; 
        display: flex; justify-content: center; align-items: center; 
        cursor: pointer; font-family: 'JetBrains Mono'; font-weight: bold; font-size: 1.1rem;
        transition: background 0.1s; user-select: none;
    }
    .cell:hover { background: #334155; }
    
    .cell.revealed { background: #0f172a; box-shadow: inset 0 0 5px rgba(0,0,0,0.5); cursor: default; }
    .cell.mine { background: #450a0a; border: 1px solid #ef4444; }
    .cell.flagged { color: #facc15; }

    .overlay { 
        position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
        background: rgba(0,0,0,0.8); display: flex; flex-direction: column; 
        justify-content: center; align-items: center; z-index: 10;
        backdrop-filter: blur(5px);
    }
    .overlay.fail h2 { color: #ef4444; text-shadow: 0 0 20px #ef4444; }
    .overlay.win h2 { color: #4ade80; text-shadow: 0 0 20px #4ade80; }
    
    .overlay button { 
        background: transparent; border: 1px solid #fff; color: #fff; padding: 10px 30px; 
        font-family: 'JetBrains Mono'; font-weight: bold; cursor: pointer; transition: 0.2s;
    }
    .overlay button:hover { background: #fff; color: #000; }

    .controls { display: flex; gap: 10px; margin-top: 10px; }
    .controls button {
        background: transparent; border: 1px solid #334155; color: #64748b; 
        padding: 5px 15px; font-family: 'JetBrains Mono'; font-size: 0.8rem; 
        cursor: pointer; transition: 0.2s; border-radius: 4px;
    }
    .controls button:hover, .controls button.active { border-color: #ef4444; color: #fff; }

    @keyframes shake { 0% { transform: translateX(0); } 25% { transform: translateX(5px); } 75% { transform: translateX(-5px); } 100% { transform: translateX(0); } }
</style>