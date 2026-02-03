<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    // --- STATE ---
    let grid = $state<number[][]>(Array(4).fill(null).map(() => Array(4).fill(0)));
    let score = $state(0);
    let best = $state(0);
    let gameOver = $state(false);

    // --- TOUCH STATE ---
    let touchStartX = 0;
    let touchStartY = 0;

    // --- ENGINE ---
    function init() {
        if (typeof localStorage !== 'undefined') best = parseInt(localStorage.getItem('resinen_2048_best') || '0');
        reset();
    }

    function reset() {
        grid = Array(4).fill(null).map(() => Array(4).fill(0));
        score = 0;
        gameOver = false;
        spawn();
        spawn();
    }

    function spawn() {
        let empty = [];
        for(let r=0; r<4; r++) for(let c=0; c<4; c++) if(grid[r][c] === 0) empty.push({r, c});
        if (empty.length > 0) {
            const {r, c} = empty[Math.floor(Math.random() * empty.length)];
            grid[r][c] = Math.random() > 0.9 ? 4 : 2;
        }
    }

    function move(dir: 'UP'|'DOWN'|'LEFT'|'RIGHT') {
        if (gameOver) return;
        
        // Deep copy
        let newGrid = grid.map(row => [...row]);
        
        const slideRow = (row: number[]) => {
            let arr = row.filter(x => x); // Remove zeros
            let missing = 4 - arr.length;
            let zeros = Array(missing).fill(0);
            return arr.concat(zeros);
        };
        const mergeRow = (row: number[]) => {
            for(let i=0; i<3; i++) {
                if(row[i] !== 0 && row[i] === row[i+1]) {
                    row[i] *= 2;
                    row[i+1] = 0;
                    score += row[i];
                }
            }
            return row;
        };
        const operate = (row: number[]) => slideRow(mergeRow(slideRow(row)));

        if (dir === 'LEFT') {
            newGrid = newGrid.map(row => operate(row));
        } else if (dir === 'RIGHT') {
            newGrid = newGrid.map(row => operate(row.reverse()).reverse());
        } else if (dir === 'UP') {
            // Transpose, operate left, transpose back
            newGrid = transpose(newGrid).map(row => operate(row));
            newGrid = transpose(newGrid);
        } else if (dir === 'DOWN') {
            newGrid = transpose(newGrid).map(row => operate(row.reverse()).reverse());
            newGrid = transpose(newGrid);
        }

        // Check change
        if (JSON.stringify(grid) !== JSON.stringify(newGrid)) {
            grid = newGrid;
            spawn();
            checkGameOver();
        }
    }

    function transpose(matrix: number[][]) {
        return matrix[0].map((col, i) => matrix.map(row => row[i]));
    }

    function checkGameOver() {
        // Simple check: Any empty?
        for(let r=0; r<4; r++) for(let c=0; c<4; c++) if(grid[r][c] === 0) return;
        // Check neighbors
        for(let r=0; r<4; r++) {
            for(let c=0; c<4; c++) {
                if (c<3 && grid[r][c] === grid[r][c+1]) return;
                if (r<3 && grid[r][c] === grid[r+1][c]) return;
            }
        }
        gameOver = true;
        if (score > best) {
            best = score;
            localStorage.setItem('resinen_2048_best', best.toString());
        }
    }

    function handleKey(e: KeyboardEvent) {
        if (e.key === 'ArrowUp') move('UP');
        if (e.key === 'ArrowDown') move('DOWN');
        if (e.key === 'ArrowLeft') move('LEFT');
        if (e.key === 'ArrowRight') move('RIGHT');
    }

    // --- TOUCH HANDLERS ---
    function handleTouchStart(e: TouchEvent) {
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
    }

    function handleTouchEnd(e: TouchEvent) {
        if (gameOver) return;
        
        const touchEndX = e.changedTouches[0].clientX;
        const touchEndY = e.changedTouches[0].clientY;
        
        const diffX = touchEndX - touchStartX;
        const diffY = touchEndY - touchStartY;
        
        // Threshold to ignore accidental taps
        if (Math.abs(diffX) < 30 && Math.abs(diffY) < 30) return;

        if (Math.abs(diffX) > Math.abs(diffY)) {
            // Horizontal
            if (diffX > 0) move('RIGHT');
            else move('LEFT');
        } else {
            // Vertical
            if (diffY > 0) move('DOWN');
            else move('UP');
        }
    }

    function getColor(val: number) {
        const colors: any = { 
            2: '#eee4da', 4: '#ede0c8', 8: '#f2b179', 16: '#f59563', 
            32: '#f67c5f', 64: '#f65e3b', 128: '#edcf72', 256: '#edcc61', 
            512: '#edc850', 1024: '#edc53f', 2048: '#edc22e'
        };
        return colors[val] || '#3c3a32';
    }

    onMount(() => { 
        init(); 
        window.addEventListener('keydown', handleKey);
        
        // Prevent scrolling when swiping inside the game area
        const container = document.querySelector('.game-container');
        container?.addEventListener('touchmove', (e: Event) => e.preventDefault(), { passive: false });
    });
    
    onDestroy(() => { 
        if(typeof window!=='undefined') window.removeEventListener('keydown', handleKey); 
    });
</script>

<div class="game-container" 
     ontouchstart={handleTouchStart} 
     ontouchend={handleTouchEnd}>
     
    <div class="bg-layer stars"></div>
    
    <div class="game-ui">
        <div class="header">
            <h1>NEON 2048</h1>
            <div class="stats">
                <span>SCORE: <span class="val">{score}</span></span>
                <span>BEST: <span class="val hi">{best}</span></span>
            </div>
        </div>

        <div class="board-wrapper">
            {#if gameOver}
                <div class="overlay">
                    <h2>GRID LOCKED</h2>
                    <button onclick={reset}>REBOOT</button>
                </div>
            {/if}
            <div class="grid">
                {#each grid as row}
                    {#each row as cell}
                        <div class="cell" 
                             class:empty={cell===0} 
                             style="
                                background-color: {cell ? getColor(cell) : 'rgba(255,255,255,0.05)'}; 
                                color: {cell > 4 ? '#fff' : '#776e65'}; 
                                box-shadow: 0 0 {cell > 0 ? 10 : 0}px {getColor(cell)};
                             ">
                            {cell > 0 ? cell : ''}
                        </div>
                    {/each}
                {/each}
            </div>
        </div>
        
        <div class="hint">
            <span class="desktop-hint">USE ARROW KEYS TO MERGE</span>
            <span class="mobile-hint">SWIPE TO MERGE</span>
        </div>
    </div>
</div>

<style>
    :global(body) { margin: 0; background-color: #020617; color: #f8fafc; font-family: 'Space Grotesk', sans-serif; overflow: hidden; touch-action: none; }
    .stars { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: radial-gradient(#fff 1px, transparent 1px); background-size: 50px 50px; opacity: 0.1; pointer-events: none; }
    
    .game-container { height: 100vh; width: 100vw; display: flex; justify-content: center; align-items: center; position: relative; }
    .game-ui { z-index: 1; display: flex; flex-direction: column; align-items: center; gap: 20px; width: 100%; max-width: 600px; }
    
    .header { text-align: center; position: relative; width: 100%; }
    h1 { font-size: 2.5rem; margin: 0; color: #facc15; text-shadow: 0 0 20px #facc15; }
    .stats { display: flex; gap: 20px; justify-content: center; font-family: 'JetBrains Mono'; color: #94a3b8; margin-top: 5px; }
    .val { color: #fff; font-weight: bold; }

    .board-wrapper { position: relative; padding: 10px; background: #1e293b; border-radius: 6px; box-shadow: 0 0 40px rgba(0,0,0,0.5); touch-action: none; }
    
    /* RESPONSIVE GRID */
    .grid { 
        /* Calculate cell size: Max 80px, but shrink if screen is narrow (20vw) or short (18vh) */
        --cell-size: min(80px, 20vw, 18vh);
        --gap: min(10px, 2vw);
        
        display: grid; 
        grid-template-columns: repeat(4, var(--cell-size)); 
        grid-template-rows: repeat(4, var(--cell-size)); 
        gap: var(--gap); 
    }
    
    .cell { 
        display: flex; justify-content: center; align-items: center; 
        font-weight: bold; border-radius: 4px; transition: 0.1s;
        /* Dynamic font size based on cell size */
        font-size: calc(var(--cell-size) * 0.4);
    }
    .cell.empty { background: rgba(255,255,255,0.05); }

    .overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); display: flex; flex-direction: column; justify-content: center; align-items: center; border-radius: 6px; backdrop-filter: blur(5px); z-index: 10; }
    .overlay h2 { color: #ef4444; margin-bottom: 20px; font-size: 1.5rem; }
    .overlay button { background: #fff; border: none; padding: 10px 30px; font-weight: bold; cursor: pointer; }
    
    .hint { font-family: 'JetBrains Mono'; font-size: 0.8rem; color: #64748b; margin-top: 10px; text-align: center;}
    .mobile-hint { display: none; }

    /* MOBILE TWEAKS */
    @media (max-width: 600px) {
        h1 { font-size: 2rem; }
        .desktop-hint { display: none; }
        .mobile-hint { display: inline; }
    }
</style>