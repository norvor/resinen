<script lang="ts">
    import { onMount } from 'svelte';

    // --- STATE ---
    let puzzle = $state<number[][]>([]);
    let solution = $state<number[][]>([]);
    let userGrid = $state<number[][]>([]);
    let initialMask = $state<boolean[][]>([]); // True if fixed/initial
    let selected = $state<{r: number, c: number} | null>(null);
    let difficulty = $state("medium");
    let loading = $state(true);
    let mistakes = $state(0);
    let solved = $state(false);

    // --- API & LOGIC ---
    async function newGame() {
        loading = true;
        solved = false;
        mistakes = 0;
        selected = null;
        try {
            // Using the requested API endpoint
            const res = await fetch(`https://api.resinen.com/games/sudoku/new?difficulty=${difficulty}`);
            const data = await res.json();
            puzzle = data.puzzle;
            solution = data.solution;
            
            // Deep copy for user input
            userGrid = puzzle.map(row => [...row]);
            
            // Mark initial cells so user can't edit them
            initialMask = puzzle.map(row => row.map(val => val !== 0));
        } catch (e) {
            console.error("Sudoku Uplink Failed", e);
        } finally {
            loading = false;
        }
    }

    function selectCell(r: number, c: number) {
        selected = { r, c };
    }

    function handleInput(num: number) {
        if (!selected || solved) return;
        const { r, c } = selected;

        if (initialMask[r][c]) return; // Can't edit fixed cells

        // Logic
        if (num === solution[r][c]) {
            userGrid[r][c] = num;
            checkWin();
        } else {
            mistakes++;
        }
    }

    function handleKeydown(e: KeyboardEvent) {
        if (!selected) return;
        
        // Navigation
        if (e.key === 'ArrowUp') selected = { r: Math.max(0, selected.r - 1), c: selected.c };
        if (e.key === 'ArrowDown') selected = { r: Math.min(8, selected.r + 1), c: selected.c };
        if (e.key === 'ArrowLeft') selected = { r: selected.r, c: Math.max(0, selected.c - 1) };
        if (e.key === 'ArrowRight') selected = { r: selected.r, c: Math.min(8, selected.c + 1) };

        // Input
        if (e.key >= '1' && e.key <= '9') handleInput(parseInt(e.key));
        if (e.key === 'Backspace' || e.key === 'Delete') {
            if (!initialMask[selected.r][selected.c]) userGrid[selected.r][selected.c] = 0;
        }
    }

    function checkWin() {
        for (let i = 0; i < 9; i++) {
            for (let j = 0; j < 9; j++) {
                if (userGrid[i][j] !== solution[i][j]) return;
            }
        }
        solved = true;
    }

    onMount(() => {
        newGame();
        window.addEventListener('keydown', handleKeydown);
        return () => window.removeEventListener('keydown', handleKeydown);
    });
</script>

<div class="game-container">
    <div class="bg-layer stars"></div>
    
    <div class="game-ui">
        <div class="header">
            <h1>NEON SUDOKU</h1>
            <div class="stats">
                <span>MISTAKES: <span class="err">{mistakes}/3</span></span>
                <span>DIFFICULTY: {difficulty.toUpperCase()}</span>
            </div>
        </div>

        {#if loading}
            <div class="loading">
                <span>GENERATING MATRIX...</span>
            </div>
        {:else if solved}
            <div class="win-screen">
                <h2>SYSTEM SOLVED</h2>
                <button onclick={newGame}>NEXT PUZZLE</button>
            </div>
        {:else}
            <div class="sudoku-grid">
                {#each userGrid as row, r}
                    <div class="row">
                        {#each row as cell, c}
                            <div 
                                class="cell" 
                                role="button"
                                tabindex="0"
                                class:fixed={initialMask[r][c]}
                                class:selected={selected?.r === r && selected?.c === c}
                                class:highlight={selected && (selected.r === r || selected.c === c)}
                                class:match={selected && cell !== 0 && cell === userGrid[selected.r][selected.c]}
                                class:err={cell !== 0 && cell !== solution[r][c]}
                                onclick={() => selectCell(r, c)}
                            >
                                {cell !== 0 ? cell : ''}
                            </div>
                        {/each}
                    </div>
                {/each}
            </div>

            <div class="numpad">
                {#each [1, 2, 3, 4, 5, 6, 7, 8, 9] as n}
                    <button onclick={() => handleInput(n)}>{n}</button>
                {/each}
            </div>
        {/if}
        
        <div class="controls">
            <button onclick={() => { difficulty = 'easy'; newGame(); }}>EASY</button>
            <button onclick={() => { difficulty = 'medium'; newGame(); }}>MEDIUM</button>
            <button onclick={() => { difficulty = 'hard'; newGame(); }}>HARD</button>
        </div>
    </div>
</div>

<style>
    :global(body) { margin: 0; background-color: #020617; color: #f8fafc; font-family: 'Space Grotesk', sans-serif; overflow: hidden; user-select: none; }
    .stars { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; background: radial-gradient(#fff 1px, transparent 1px); background-size: 50px 50px; opacity: 0.1; pointer-events: none;}
    
    .game-container { height: 100vh; width: 100vw; display: flex; justify-content: center; align-items: center; position: relative; }
    .game-ui { z-index: 1; display: flex; flex-direction: column; align-items: center; gap: 20px; width: 100%; max-width: 600px; padding: 10px; box-sizing: border-box; }
    
    .header { text-align: center; width: 100%; position: relative; }
    h1 { font-size: 2rem; letter-spacing: 2px; margin: 0; color: #fff; text-shadow: 0 0 10px #2dd4bf; }
    .stats { font-family: 'JetBrains Mono'; color: #94a3b8; font-size: 0.8rem; margin-top: 5px; display: flex; gap: 20px; justify-content: center; }
    .err { color: #ef4444; }

    /* RESPONSIVE GRID LOGIC */
    .sudoku-grid { 
        /* Calculate cell size to fit:
           1. 10.5% of Viewport Width (mobile)
           2. 5.5% of Viewport Height (landscape)
           3. Max 50px (Desktop)
        */
        --cell-size: min(50px, 10.5vw, 5.5vh);
        
        border: 2px solid #2dd4bf; 
        background: rgba(15, 23, 42, 0.9); 
        display: flex; flex-direction: column; 
        box-shadow: 0 0 40px rgba(45, 212, 191, 0.2);
        touch-action: manipulation; /* Prevents double-tap zoom */
    }
    
    .row { display: flex; }
    
    .cell { 
        width: var(--cell-size); 
        height: var(--cell-size); 
        border: 1px solid #334155; 
        display: flex; justify-content: center; align-items: center; 
        font-family: 'JetBrains Mono'; 
        font-size: calc(var(--cell-size) * 0.6); /* Responsive font */
        cursor: pointer; transition: 0.1s;
    }
    
    /* Grid Borders */
    .cell:nth-child(3n) { border-right: 2px solid #2dd4bf; }
    .cell:nth-child(9) { border-right: 1px solid #334155; }
    .row:nth-child(3n) .cell { border-bottom: 2px solid #2dd4bf; }
    .row:nth-child(9) .cell { border-bottom: 1px solid #334155; }

    /* States */
    .cell.fixed { color: #94a3b8; font-weight: normal; }
    .cell:not(.fixed) { color: #2dd4bf; font-weight: bold; text-shadow: 0 0 10px #2dd4bf; }
    
    .cell.selected { background: rgba(45, 212, 191, 0.3); border-color: #fff; }
    .cell.highlight { background: rgba(45, 212, 191, 0.1); }
    .cell.match { background: rgba(45, 212, 191, 0.4); color: #fff; }
    .cell.err { color: #ef4444; text-shadow: 0 0 10px #ef4444; animation: shake 0.3s; }

    .numpad { display: flex; gap: 5px; margin-top: 10px; flex-wrap: wrap; justify-content: center; }
    .numpad button { 
        width: 40px; height: 40px; 
        background: transparent; border: 1px solid #334155; 
        color: #2dd4bf; font-family: 'JetBrains Mono'; font-size: 1.2rem; cursor: pointer; 
        border-radius: 4px; transition: 0.2s; 
    }
    .numpad button:hover, .numpad button:active { border-color: #2dd4bf; background: rgba(45, 212, 191, 0.1); }

    .controls { display: flex; gap: 10px; margin-top: 20px; flex-wrap: wrap; justify-content: center; }
    .controls button {
        background: transparent; border: 1px solid #94a3b8; color: #94a3b8; 
        padding: 8px 20px; font-family: 'JetBrains Mono'; font-size: 0.8rem; 
        cursor: pointer; transition: 0.2s; border-radius: 4px;
    }
    .controls button:hover { border-color: #fff; color: #fff; }

    /* Responsive Loading/Win Screen */
    .loading, .win-screen { 
        /* Match grid size approx */
        height: calc(var(--cell-size, 50px) * 9); 
        width: calc(var(--cell-size, 50px) * 9); 
        max-width: 100%;
        display: flex; flex-direction: column; justify-content: center; align-items: center; 
        color: #2dd4bf; font-family: 'JetBrains Mono'; border: 2px solid #2dd4bf; 
        background: rgba(15, 23, 42, 0.9); 
    }
    .win-screen h2 { font-size: 1.5rem; margin-bottom: 20px; text-shadow: 0 0 20px #2dd4bf; text-align: center; }
    .win-screen button { background: #2dd4bf; color: #000; border: none; padding: 10px 30px; font-weight: bold; cursor: pointer; font-family: 'JetBrains Mono'; }

    @keyframes shake { 0% { transform: translateX(0); } 25% { transform: translateX(5px); } 75% { transform: translateX(-5px); } 100% { transform: translateX(0); } }

    /* MOBILE TWEAKS */
    @media (max-width: 500px) {
        h1 { font-size: 1.5rem; }
        .game-ui { gap: 10px; }
        .numpad button { width: 10vw; height: 10vw; max-width: 40px; max-height: 40px; }
    }
</style>