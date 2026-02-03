<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    // --- CONFIG ---
    const GRID_SIZE = 20;
    const SPEED_START = 150;
    const SPEED_MIN = 50;

    // --- STATE ---
    let snake = $state([{x: 10, y: 10}, {x: 10, y: 11}, {x: 10, y: 12}]);
    let food = $state({x: 5, y: 5});
    let direction = $state({x: 0, y: -1}); // Moving Up
    let nextDirection = $state({x: 0, y: -1}); // Buffer for rapid inputs
    let score = $state(0);
    let highScore = $state(0);
    let speed = $state(SPEED_START);
    let gameOver = $state(false);
    let paused = $state(false);
    let gameInterval: any;

    // --- TOUCH STATE ---
    let touchStartX = 0;
    let touchStartY = 0;

    // --- ENGINE ---
    function startGame() {
        snake = [{x: 10, y: 10}, {x: 10, y: 11}, {x: 10, y: 12}];
        direction = {x: 0, y: -1};
        nextDirection = {x: 0, y: -1};
        score = 0;
        speed = SPEED_START;
        gameOver = false;
        paused = false;
        spawnFood();
        clearInterval(gameInterval);
        gameInterval = setInterval(gameLoop, speed);
    }

    function spawnFood() {
        let newFood;
        while (true) {
            newFood = {
                x: Math.floor(Math.random() * GRID_SIZE),
                y: Math.floor(Math.random() * GRID_SIZE)
            };
            // Ensure food doesn't spawn inside snake
            const onSnake = snake.some(s => s.x === newFood.x && s.y === newFood.y);
            if (!onSnake) break;
        }
        food = newFood;
    }

    function gameLoop() {
        if (paused || gameOver) return;

        direction = nextDirection; // Apply buffered input
        const head = { x: snake[0].x + direction.x, y: snake[0].y + direction.y };

        // 1. Wall Collision
        if (head.x < 0 || head.x >= GRID_SIZE || head.y < 0 || head.y >= GRID_SIZE) {
            endGame();
            return;
        }

        // 2. Self Collision
        if (snake.some(s => s.x === head.x && s.y === head.y)) {
            endGame();
            return;
        }

        // Move Snake
        snake.unshift(head); // Add new head

        // 3. Eat Food
        if (head.x === food.x && head.y === food.y) {
            score += 10;
            spawnFood();
            // Speed Up
            if (speed > SPEED_MIN) {
                speed *= 0.98;
                clearInterval(gameInterval);
                gameInterval = setInterval(gameLoop, speed);
            }
        } else {
            snake.pop(); // Remove tail if not eating
        }
    }

    function endGame() {
        gameOver = true;
        clearInterval(gameInterval);
        if (score > highScore) {
            highScore = score;
            if(typeof localStorage !== 'undefined') localStorage.setItem('resinen_snake_hiscore', highScore.toString());
        }
    }

    function handleKey(e: KeyboardEvent) {
        if (gameOver) return;
        if (e.key === 'p') paused = !paused;

        // Prevent 180 turns
        if (e.key === 'ArrowUp' && direction.y === 0) nextDirection = {x: 0, y: -1};
        if (e.key === 'ArrowDown' && direction.y === 0) nextDirection = {x: 0, y: 1};
        if (e.key === 'ArrowLeft' && direction.x === 0) nextDirection = {x: -1, y: 0};
        if (e.key === 'ArrowRight' && direction.x === 0) nextDirection = {x: 1, y: 0};
    }

    // --- TOUCH HANDLERS ---
    function handleTouchStart(e: TouchEvent) {
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
    }

    function handleTouchEnd(e: TouchEvent) {
        if (gameOver || paused) return;

        const touchEndX = e.changedTouches[0].clientX;
        const touchEndY = e.changedTouches[0].clientY;

        const diffX = touchEndX - touchStartX;
        const diffY = touchEndY - touchStartY;

        // Threshold to prevent accidental micro-touches
        if (Math.abs(diffX) < 20 && Math.abs(diffY) < 20) return;

        if (Math.abs(diffX) > Math.abs(diffY)) {
            // Horizontal
            if (diffX > 0 && direction.x === 0) nextDirection = {x: 1, y: 0}; // Right
            if (diffX < 0 && direction.x === 0) nextDirection = {x: -1, y: 0}; // Left
        } else {
            // Vertical
            if (diffY > 0 && direction.y === 0) nextDirection = {x: 0, y: 1}; // Down
            if (diffY < 0 && direction.y === 0) nextDirection = {x: 0, y: -1}; // Up
        }
    }

    onMount(() => {
        if(typeof localStorage !== 'undefined') {
            const saved = localStorage.getItem('resinen_snake_hiscore');
            if (saved) highScore = parseInt(saved);
        }
        startGame();
        window.addEventListener('keydown', handleKey);
        
        // Prevent default touch actions (scrolling)
        const container = document.querySelector('.game-container');
        container?.addEventListener('touchmove', (e: Event) => e.preventDefault(), { passive: false });

        return () => {
            clearInterval(gameInterval);
            window.removeEventListener('keydown', handleKey);
        };
    });
</script>

<div class="game-container"
     ontouchstart={handleTouchStart} 
     ontouchend={handleTouchEnd}>
     
    <div class="bg-layer stars"></div>
    
    <div class="game-ui">
        <div class="header">
            <h1>NEON SERPENT</h1>
            <div class="stats">
                <span>SCORE: <span class="val">{score}</span></span>
                <span>HI-SCORE: <span class="val hi">{highScore}</span></span>
            </div>
        </div>

        <div class="grid-wrapper">
            {#if gameOver}
                <div class="overlay">
                    <h2>SYSTEM CRASH</h2>
                    <button onclick={startGame}>REBOOT</button>
                </div>
            {/if}
            {#if paused}
                <div class="overlay pause">
                    <h2>PAUSED</h2>
                    <button onclick={() => paused = false}>RESUME</button>
                </div>
            {/if}

            <div class="snake-grid">
                {#each Array(GRID_SIZE * GRID_SIZE) as _, i}
                    {@const x = i % GRID_SIZE}
                    {@const y = Math.floor(i / GRID_SIZE)}
                    {@const isHead = snake[0].x === x && snake[0].y === y}
                    {@const isBody = !isHead && snake.some(s => s.x === x && s.y === y)}
                    {@const isFood = food.x === x && food.y === y}
                    
                    <div 
                        class="cell" 
                        class:head={isHead}
                        class:body={isBody}
                        class:food={isFood}
                    ></div>
                {/each}
            </div>
        </div>

        <div class="controls-hint">
            <span class="desktop-hint">USE ARROW KEYS • P TO PAUSE</span>
            <span class="mobile-hint">SWIPE TO MOVE</span>
        </div>
    </div>
</div>

<style>
    :global(body) { margin: 0; background-color: #0f172a; color: #f8fafc; font-family: 'Space Grotesk', sans-serif; overflow: hidden; touch-action: none; }
    .stars { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: radial-gradient(#fff 1px, transparent 1px); background-size: 50px 50px; opacity: 0.1; pointer-events: none;}
    
    .game-container { height: 100vh; width: 100vw; display: flex; justify-content: center; align-items: center; position: relative; }
    .game-ui { z-index: 1; display: flex; flex-direction: column; align-items: center; gap: 20px; width: 100%; max-width: 600px; }
    
    .header { text-align: center; width: 100%; position: relative; margin-bottom: 5px; }
    h1 { font-size: 2.5rem; letter-spacing: 2px; margin: 0; color: #fff; text-shadow: 0 0 20px #4ade80; }
    
    .stats { display: flex; gap: 30px; justify-content: center; font-family: 'JetBrains Mono'; font-size: 1.2rem; color: #94a3b8; margin-top: 5px; }
    .val { color: #4ade80; font-weight: bold; }
    .hi { color: #facc15; }

    .grid-wrapper { position: relative; border: 4px solid #334155; box-shadow: 0 0 50px rgba(74, 222, 128, 0.2); border-radius: 4px; touch-action: none; }

    .snake-grid { 
        /* Responsive Grid Calculation:
           - Base size: 25px
           - Max width constraint: 4.5vw (so 20 columns fit in 90vw)
           - Max height constraint: 3.5vh (so vertical fits on phones)
        */
        --cell-size: min(25px, 4.5vw, 3.5vh);

        display: grid; 
        grid-template-columns: repeat(20, var(--cell-size)); 
        grid-template-rows: repeat(20, var(--cell-size));
        background: #020617;
    }
    
    .cell { width: var(--cell-size); height: var(--cell-size); border: 1px solid rgba(255,255,255,0.02); }
    
    .cell.head { background: #fff; box-shadow: 0 0 15px #fff; border-radius: 2px; z-index: 2; }
    .cell.body { background: #4ade80; box-shadow: 0 0 10px #4ade80; opacity: 0.8; transition: opacity 0.2s; }
    
    .cell.food { 
        background: #ef4444; border-radius: 50%; 
        transform: scale(0.6); 
        box-shadow: 0 0 20px #ef4444; 
        animation: pulse 0.8s infinite alternate; 
    }

    .overlay { 
        position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
        background: rgba(0,0,0,0.8); display: flex; flex-direction: column; 
        justify-content: center; align-items: center; z-index: 10;
        backdrop-filter: blur(5px);
    }
    .overlay h2 { font-size: 2rem; color: #ef4444; margin-bottom: 20px; text-shadow: 0 0 20px #ef4444; }
    .overlay.pause h2 { color: #facc15; text-shadow: 0 0 20px #facc15; }
    
    .overlay button { 
        background: transparent; border: 1px solid #fff; color: #fff; padding: 10px 30px; 
        font-family: 'JetBrains Mono'; font-weight: bold; cursor: pointer; transition: 0.2s;
    }
    .overlay button:hover { background: #fff; color: #000; box-shadow: 0 0 20px #fff; }

    .controls-hint { font-family: 'JetBrains Mono'; font-size: 0.7rem; color: #64748b; margin-top: 10px; letter-spacing: 1px; }
    .mobile-hint { display: none; }

    @keyframes pulse { from { transform: scale(0.5); opacity: 0.7; } to { transform: scale(0.8); opacity: 1; } }

    /* MOBILE TWEAKS */
    @media (max-width: 600px) {
        h1 { font-size: 1.8rem; }
        .stats { font-size: 0.9rem; gap: 15px; }
        .desktop-hint { display: none; }
        .mobile-hint { display: block; }
    }
</style>