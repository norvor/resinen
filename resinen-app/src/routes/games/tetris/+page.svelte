<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    // --- GAME CONSTANTS ---
    const ROWS = 20;
    const COLS = 10;
    
    // DEFINING SHAPES IN SQUARE BOXES (Crucial for rotation)
    const SHAPES = {
        'I': { 
            color: '#2dd4bf', // Cyan
            matrix: [
                [0,0,0,0],
                [1,1,1,1],
                [0,0,0,0],
                [0,0,0,0]
            ]
        },
        'J': { 
            color: '#3b82f6', // Blue
            matrix: [
                [1,0,0],
                [1,1,1],
                [0,0,0]
            ]
        },
        'L': { 
            color: '#f97316', // Orange
            matrix: [
                [0,0,1],
                [1,1,1],
                [0,0,0]
            ]
        },
        'O': { 
            color: '#facc15', // Yellow
            matrix: [
                [1,1],
                [1,1]
            ]
        },
        'S': { 
            color: '#4ade80', // Green
            matrix: [
                [0,1,1],
                [1,1,0],
                [0,0,0]
            ]
        },
        'T': { 
            color: '#a78bfa', // Purple
            matrix: [
                [0,1,0],
                [1,1,1],
                [0,0,0]
            ]
        },
        'Z': { 
            color: '#ef4444', // Red
            matrix: [
                [1,1,0],
                [0,1,1],
                [0,0,0]
            ]
        }
    };

    // --- STATE ---
    let grid = $state<string[][]>(Array(ROWS).fill(null).map(() => Array(COLS).fill('')));
    let activePiece = $state<any>(null);
    let ghostY = $state(0);
    let score = $state(0);
    let level = $state(1);
    let gameOver = $state(false);
    let paused = $state(false);
    let dropInterval: any;
    let speed = 1000;

    // --- ENGINE ---
    function spawnPiece() {
        const keys = Object.keys(SHAPES);
        const type = keys[Math.floor(Math.random() * keys.length)];
        const shape = SHAPES[type as keyof typeof SHAPES];
        
        // Deep copy the matrix so we don't mutate the definition
        const matrix = shape.matrix.map(row => [...row]);

        activePiece = {
            type,
            matrix,
            color: shape.color,
            x: Math.floor(COLS / 2) - Math.ceil(matrix[0].length / 2),
            y: 0 // Start slightly higher if needed, but 0 is safe for these matrices
        };

        if (checkCollision(0, 0)) {
            gameOver = true;
            clearInterval(dropInterval);
        }
        updateGhost();
    }

    function checkCollision(offX: number, offY: number, matrix = activePiece.matrix) {
        for (let r = 0; r < matrix.length; r++) {
            for (let c = 0; c < matrix[r].length; c++) {
                if (matrix[r][c]) {
                    const newX = activePiece.x + c + offX;
                    const newY = activePiece.y + r + offY;
                    
                    if (newX < 0 || newX >= COLS || newY >= ROWS) return true; // Walls/Floor
                    if (newY >= 0 && grid[newY][newX]) return true; // Frozen blocks
                }
            }
        }
        return false;
    }

    function rotate() {
        if (!activePiece) return;
        
        const matrix = activePiece.matrix;
        const N = matrix.length;
        
        // 1. Transpose + Reverse Rows (Standard Matrix Rotation)
        const rotated = matrix[0].map((_, index) => matrix.map(row => row[index]).reverse());
        
        // 2. Wall Kicks (Prevent rotating into walls)
        const originalX = activePiece.x;
        let offset = 1;
        
        // Try normal rotation
        if (!checkCollision(0, 0, rotated)) {
            activePiece.matrix = rotated;
        } else {
            // Try shifting left/right to find space
            if (!checkCollision(1, 0, rotated)) {
                activePiece.x += 1;
                activePiece.matrix = rotated;
            } else if (!checkCollision(-1, 0, rotated)) {
                activePiece.x -= 1;
                activePiece.matrix = rotated;
            } else if (activePiece.type === 'I' && !checkCollision(2, 0, rotated)) {
                 // I-piece special kick
                activePiece.x += 2;
                activePiece.matrix = rotated;
            } else if (activePiece.type === 'I' && !checkCollision(-2, 0, rotated)) {
                activePiece.x -= 2;
                activePiece.matrix = rotated;
            }
        }
        updateGhost();
    }

    function move(dir: number) {
        if (!checkCollision(dir, 0)) {
            activePiece.x += dir;
            updateGhost();
        }
    }

    function drop() {
        if (!checkCollision(0, 1)) {
            activePiece.y++;
        } else {
            freeze();
            spawnPiece();
        }
    }

    function hardDrop() {
        while (!checkCollision(0, 1)) {
            activePiece.y++;
        }
        freeze();
        spawnPiece();
    }

    function updateGhost() {
        if (!activePiece) return;
        let y = activePiece.y;
        while (!checkCollision(0, y - activePiece.y + 1)) {
            y++;
        }
        ghostY = y;
    }

    function freeze() {
        // Lock piece into grid
        activePiece.matrix.forEach((row: number[], r: number) => {
            row.forEach((val: number, c: number) => {
                if (val) {
                    const y = activePiece.y + r;
                    const x = activePiece.x + c;
                    if (y >= 0 && y < ROWS && x >= 0 && x < COLS) {
                        grid[y][x] = activePiece.color;
                    }
                }
            });
        });
        
        // Clear Lines
        let linesCleared = 0;
        for (let r = ROWS - 1; r >= 0; r--) {
            if (grid[r].every(c => c !== '')) {
                grid.splice(r, 1);
                grid.unshift(Array(COLS).fill(''));
                linesCleared++;
                r++; // Check same row index again (since rows shifted down)
            }
        }

        if (linesCleared > 0) {
            // Scoring: 100, 300, 500, 800
            const points = [0, 100, 300, 500, 800];
            score += points[linesCleared] * level;
            
            // Speed up every 1000 points
            if (score > level * 1000) {
                level++;
                speed = Math.max(100, speed * 0.9);
                clearInterval(dropInterval);
                dropInterval = setInterval(gameLoop, speed);
            }
        }
    }

    function gameLoop() {
        if (!paused && !gameOver) drop();
    }

    function handleKey(e: KeyboardEvent) {
        if (gameOver) return;
        if (e.key === 'ArrowLeft') move(-1);
        if (e.key === 'ArrowRight') move(1);
        if (e.key === 'ArrowDown') drop();
        if (e.key === 'ArrowUp') rotate();
        if (e.key === ' ') hardDrop();
        if (e.key === 'p') paused = !paused;
    }

    onMount(() => {
        spawnPiece();
        dropInterval = setInterval(gameLoop, speed);
        window.addEventListener('keydown', handleKey);
        return () => {
            clearInterval(dropInterval);
            window.removeEventListener('keydown', handleKey);
        };
    });
</script>

<div class="game-container">
    <div class="bg-layer stars"></div>
    
    <div class="game-ui">
        <div class="header">
            <a href="/" class="back-btn">← DOCK</a>
            <h1>NEON TETRIS</h1>
            <div class="stats">
                <span>SCORE: <span class="val">{score}</span></span>
                <span>LEVEL: <span class="val">{level}</span></span>
            </div>
        </div>

        <div class="tetris-board">
            {#if gameOver}
                <div class="overlay">
                    <h2>GAME OVER</h2>
                    <button onclick={() => location.reload()}>RETRY</button>
                </div>
            {/if}

            {#if paused && !gameOver}
                <div class="overlay">
                    <h2>PAUSED</h2>
                    <button onclick={() => paused = false}>RESUME</button>
                </div>
            {/if}

            {#each grid as row, r}
                <div class="row">
                    {#each row as cell, c}
                        {#if activePiece && 
                             r >= activePiece.y && r < activePiece.y + activePiece.matrix.length &&
                             c >= activePiece.x && c < activePiece.x + activePiece.matrix[0].length &&
                             activePiece.matrix[r - activePiece.y][c - activePiece.x]}
                            <div class="block active" style="background-color: {activePiece.color}; box-shadow: 0 0 10px {activePiece.color}"></div>
                        
                        {:else if activePiece && 
                             r >= ghostY && r < ghostY + activePiece.matrix.length &&
                             c >= activePiece.x && c < activePiece.x + activePiece.matrix[0].length &&
                             activePiece.matrix[r - ghostY][c - activePiece.x]}
                            <div class="block ghost" style="border-color: {activePiece.color}"></div>

                        {:else if cell}
                            <div class="block frozen" style="background-color: {cell}; border-color: rgba(0,0,0,0.2)"></div>
                        
                        {:else}
                            <div class="block empty"></div>
                        {/if}
                    {/each}
                </div>
            {/each}
        </div>

        <div class="controls-hint">
            ARROWS TO MOVE • UP TO ROTATE • SPACE TO DROP • P TO PAUSE
        </div>
    </div>
</div>

<style>
    :global(body) { margin: 0; background-color: #0f172a; color: #f8fafc; font-family: 'Space Grotesk', sans-serif; overflow: hidden; }
    .stars { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: radial-gradient(#fff 1px, transparent 1px); background-size: 50px 50px; opacity: 0.1; }
    
    .game-container { height: 100vh; display: flex; justify-content: center; align-items: center; position: relative; }
    .game-ui { z-index: 1; display: flex; flex-direction: column; align-items: center; gap: 20px; }
    
    .header { text-align: center; width: 100%; position: relative; margin-bottom: 10px; }
    .back-btn { position: absolute; left: -100px; top: 50%; transform: translateY(-50%); text-decoration: none; color: #94a3b8; font-family: 'JetBrains Mono'; font-size: 0.8rem; border: 1px solid #334155; padding: 5px 10px; border-radius: 4px; transition: 0.2s; }
    .back-btn:hover { color: #fff; border-color: #fff; }
    h1 { font-size: 2.5rem; letter-spacing: 2px; margin: 0; color: #fff; text-shadow: 0 0 20px #2dd4bf; }
    
    .stats { display: flex; gap: 30px; justify-content: center; font-family: 'JetBrains Mono'; font-size: 1rem; color: #94a3b8; margin-top: 5px; }
    .val { color: #fff; font-weight: bold; }

    .tetris-board { 
        display: grid; grid-template-rows: repeat(20, 30px); 
        border: 2px solid #334155; background: rgba(15, 23, 42, 0.9); 
        box-shadow: 0 0 50px rgba(0,0,0,0.5); position: relative;
    }
    
    .row { display: grid; grid-template-columns: repeat(10, 30px); }
    
    .block { width: 30px; height: 30px; box-sizing: border-box; }
    .block.empty { border: 1px solid rgba(255,255,255,0.05); }
    .block.active { border: 1px solid rgba(255,255,255,0.5); }
    .block.ghost { border: 2px dashed; opacity: 0.3; }
    .block.frozen { border: 1px solid rgba(0,0,0,0.2); }

    .overlay { 
        position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
        background: rgba(0,0,0,0.8); display: flex; flex-direction: column; 
        justify-content: center; align-items: center; z-index: 10;
        backdrop-filter: blur(5px);
    }
    .overlay h2 { font-size: 2rem; color: #ef4444; margin-bottom: 20px; text-shadow: 0 0 20px #ef4444; }
    .overlay button { 
        background: #fff; color: #000; border: none; padding: 10px 30px; 
        font-family: 'JetBrains Mono'; font-weight: bold; cursor: pointer; 
        transition: 0.2s;
    }
    .overlay button:hover { transform: scale(1.1); }

    .controls-hint { font-family: 'JetBrains Mono'; font-size: 0.7rem; color: #64748b; margin-top: 10px; letter-spacing: 1px; }
</style>