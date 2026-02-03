<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    // --- CONFIG ---
    const GRAVITY = 0.6;
    const JUMP_FORCE = -10;
    const SPEED_START = 8;
    const SPEED_MAX = 20;
    
    // --- STATE ---
    let canvas: HTMLCanvasElement;
    let ctx: CanvasRenderingContext2D;
    let reqId: number;
    
    let gameSpeed = SPEED_START;
    let score = 0;
    let highScore = 0;
    let gameOver = false;
    let running = false;
    
    // PLAYER
    let player = {
        x: 50,
        y: 0, // Calculated dynamically
        w: 40,
        h: 40,
        dy: 0,
        grounded: true,
        ducking: false,
        color: '#2dd4bf'
    };

    // OBSTACLES
    let obstacles: any[] = [];
    let particles: any[] = [];
    let spawnTimer = 0;

    // --- ENGINE ---
    function init() {
        if (typeof localStorage !== 'undefined') {
            highScore = parseInt(localStorage.getItem('resinen_runner_hiscore') || '0');
        }
        
        // Canvas Setup - Internal Resolution Fixed at 800x400
        canvas.width = 800;
        canvas.height = 400;
        ctx = canvas.getContext('2d')!;
        
        reset();
        loop();
    }

    function reset() {
        gameSpeed = SPEED_START;
        score = 0;
        gameOver = false;
        running = true;
        obstacles = [];
        particles = [];
        player.y = canvas.height - 100 - player.h;
        player.dy = 0;
        player.ducking = false;
        spawnTimer = 0;
    }

    function spawnObstacle() {
        const type = Math.random() > 0.5 ? 'CACTUS' : 'BIRD';
        
        if (type === 'CACTUS') {
            // Ground Obstacle
            const size = 30 + Math.random() * 20;
            obstacles.push({
                x: canvas.width,
                y: canvas.height - 100 - size,
                w: 20 + Math.random() * 20,
                h: size,
                type: 'CACTUS',
                passed: false
            });
        } else {
            // Air Obstacle (Duck under)
            obstacles.push({
                x: canvas.width,
                y: canvas.height - 100 - player.h - 40, // High enough to duck
                w: 40,
                h: 20,
                type: 'BIRD',
                passed: false
            });
        }
    }

    function update() {
        if (!running || gameOver) return;

        // 1. Player Physics
        if (player.ducking) {
            player.h = 20;
            // Force player to ground level if ducking while on ground
            if (player.grounded) player.y = canvas.height - 100 - 20;
        } else {
            player.h = 40;
            if (player.grounded) player.y = canvas.height - 100 - 40;
        }

        if (!player.grounded) {
            player.dy += GRAVITY;
            player.y += player.dy;
        }

        // Ground Collision
        const groundY = canvas.height - 100 - player.h;
        if (player.y >= groundY) {
            player.y = groundY;
            player.dy = 0;
            player.grounded = true;
        } else {
            player.grounded = false;
        }

        // 2. Obstacles
        spawnTimer--;
        if (spawnTimer <= 0) {
            spawnObstacle();
            spawnTimer = 60 + Math.random() * 60 - (gameSpeed * 2); 
            if (spawnTimer < 20) spawnTimer = 20;
        }

        for (let i = obstacles.length - 1; i >= 0; i--) {
            let obs = obstacles[i];
            obs.x -= gameSpeed;

            // Collision Detection (AABB)
            if (
                player.x < obs.x + obs.w &&
                player.x + player.w > obs.x &&
                player.y < obs.y + obs.h &&
                player.y + player.h > obs.y
            ) {
                crash();
            }

            // Cleanup
            if (obs.x + obs.w < 0) {
                obstacles.splice(i, 1);
                score++;
                if (gameSpeed < SPEED_MAX) gameSpeed += 0.05;
            }
        }

        // 3. Particles (Thruster trail)
        particles.push({
            x: player.x,
            y: player.y + player.h,
            vx: -gameSpeed,
            vy: Math.random() * 2 - 1,
            life: 1.0
        });

        for (let i = particles.length - 1; i >= 0; i--) {
            let p = particles[i];
            p.x += p.vx;
            p.y += p.vy;
            p.life -= 0.05;
            if (p.life <= 0) particles.splice(i, 1);
        }
    }

    function draw() {
        if (!ctx) return;
        
        // Clear
        ctx.fillStyle = '#0f172a';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Ground Line (Neon Grid effect)
        ctx.strokeStyle = '#334155';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(0, canvas.height - 100);
        ctx.lineTo(canvas.width, canvas.height - 100);
        ctx.stroke();

        // Moving Grid Lines
        const gridOffset = (Date.now() / 2 * gameSpeed / 10) % 50;
        ctx.beginPath();
        for (let i = 0; i < canvas.width; i += 50) {
            // Perspective lines
             ctx.moveTo(i - gridOffset, canvas.height - 100);
             ctx.lineTo(i - gridOffset - 100, canvas.height);
        }
        ctx.strokeStyle = 'rgba(45, 212, 191, 0.2)';
        ctx.stroke();

        // Player
        ctx.shadowBlur = 20;
        ctx.shadowColor = player.color;
        ctx.fillStyle = player.color;
        ctx.fillRect(player.x, player.y, player.w, player.h);
        ctx.shadowBlur = 0;

        // Obstacles
        obstacles.forEach(obs => {
            ctx.fillStyle = obs.type === 'CACTUS' ? '#ef4444' : '#facc15';
            ctx.shadowBlur = 10;
            ctx.shadowColor = ctx.fillStyle;
            ctx.fillRect(obs.x, obs.y, obs.w, obs.h);
            ctx.shadowBlur = 0;
        });

        // Particles
        particles.forEach(p => {
            ctx.fillStyle = `rgba(45, 212, 191, ${p.life})`;
            ctx.fillRect(p.x, p.y, 4, 4);
        });

        // UI
        if (gameOver) {
            ctx.fillStyle = 'rgba(0,0,0,0.7)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#fff';
            ctx.font = 'bold 30px Space Grotesk';
            ctx.textAlign = 'center';
            ctx.fillText("SYSTEM CRASH", canvas.width/2, canvas.height/2);
            ctx.font = '20px JetBrains Mono';
            ctx.fillText("TAP TO REBOOT", canvas.width/2, canvas.height/2 + 40);
        }
    }

    function loop() {
        update();
        draw();
        reqId = requestAnimationFrame(loop);
    }

    function crash() {
        gameOver = true;
        if (score > highScore) {
            highScore = score;
            localStorage.setItem('resinen_runner_hiscore', highScore.toString());
        }
    }

    // --- INPUT HANDLERS ---
    
    function jump() {
        if (gameOver) {
            reset();
            return;
        }
        if (player.grounded) {
            player.dy = JUMP_FORCE;
            player.grounded = false;
        }
    }

    function duck(isDucking: boolean) {
        if (gameOver) return;
        player.ducking = isDucking;
    }

    // Keyboard
    function handleKeyDown(e: KeyboardEvent) {
        if (e.code === 'Space' || e.code === 'ArrowUp') {
            e.preventDefault();
            jump();
        }
        if (e.code === 'ArrowDown') {
            e.preventDefault();
            duck(true);
        }
    }

    function handleKeyUp(e: KeyboardEvent) {
        if (e.code === 'ArrowDown') duck(false);
    }

    // Touch
    function handleTouchStart(e: TouchEvent) {
        // Prevent default to stop scrolling/zooming
        // e.preventDefault(); (Optional, handled via CSS touch-action)
        
        const touchX = e.touches[0].clientX;
        const screenWidth = window.innerWidth;

        if (gameOver) {
            reset();
            return;
        }

        // Left side = Duck, Right side = Jump
        if (touchX < screenWidth / 2) {
            duck(true);
        } else {
            jump();
        }
    }

    function handleTouchEnd(e: TouchEvent) {
        // If we were ducking, stop ducking
        // Simple logic: If fingers lift, stop ducking. 
        // We can check if any remaining finger is on left side, but simple toggle off is safer.
        duck(false);
    }

    onMount(() => {
        init();
        window.addEventListener('keydown', handleKeyDown);
        window.addEventListener('keyup', handleKeyUp);
        
        // Prevent default touch actions (scrolling)
        const container = document.querySelector('.game-container');
        container?.addEventListener('touchmove', (e: Event) => e.preventDefault(), { passive: false });

        return () => {
            cancelAnimationFrame(reqId);
            window.removeEventListener('keydown', handleKeyDown);
            window.removeEventListener('keyup', handleKeyUp);
        };
    });
</script>

<div class="game-container"
     ontouchstart={handleTouchStart}
     ontouchend={handleTouchEnd}>
     
    <div class="bg-layer stars"></div>
    
    <div class="game-ui">
        <div class="header">
            <h1>NEON RUNNER</h1>
            <div class="stats">
                <span>SCORE: <span class="val">{Math.floor(score)}</span></span>
                <span>HI-SCORE: <span class="val hi">{highScore}</span></span>
            </div>
        </div>

        <div class="canvas-wrapper">
            <canvas bind:this={canvas}></canvas>
        </div>

        <div class="controls-hint">
            <span class="desktop-hint">SPACE TO JUMP • DOWN TO DUCK</span>
            <span class="mobile-hint">HOLD LEFT TO DUCK • TAP RIGHT TO JUMP</span>
        </div>
    </div>
</div>

<style>
    :global(body) { margin: 0; background-color: #0f172a; color: #f8fafc; font-family: 'Space Grotesk', sans-serif; overflow: hidden; touch-action: none; }
    .stars { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: radial-gradient(#fff 1px, transparent 1px); background-size: 50px 50px; opacity: 0.1; pointer-events: none;}
    
    .game-container { height: 100vh; width: 100vw; display: flex; justify-content: center; align-items: center; position: relative; }
    .game-ui { z-index: 1; display: flex; flex-direction: column; align-items: center; gap: 20px; width: 100%; max-width: 800px; padding: 20px; box-sizing: border-box; }
    
    .header { text-align: center; width: 100%; position: relative; margin-bottom: 5px; }
    h1 { font-size: 2.5rem; letter-spacing: 2px; margin: 0; color: #fff; text-shadow: 0 0 20px #2dd4bf; }
    
    .stats { display: flex; gap: 30px; justify-content: center; font-family: 'JetBrains Mono'; font-size: 1.2rem; color: #94a3b8; margin-top: 5px; }
    .val { color: #2dd4bf; font-weight: bold; }
    .hi { color: #facc15; }

    .canvas-wrapper { 
        width: 100%;
        border: 4px solid #334155; 
        border-radius: 8px; 
        box-shadow: 0 0 50px rgba(0,0,0,0.5); 
        line-height: 0; /* Fix canvas gap */
        background: #0f172a;
    }

    /* CSS Scaling: Canvas tries to be full width but maintain aspect ratio */
    canvas {
        width: 100%;
        height: auto;
        /* Optional: set max height to ensure it fits on very wide/short screens */
        max-height: 60vh;
        object-fit: contain;
    }

    .controls-hint { font-family: 'JetBrains Mono'; font-size: 0.7rem; color: #64748b; margin-top: 10px; letter-spacing: 1px; }
    .mobile-hint { display: none; }

    /* MOBILE TWEAKS */
    @media (max-width: 600px) {
        h1 { font-size: 1.8rem; }
        .stats { font-size: 0.9rem; gap: 15px; }
        .desktop-hint { display: none; }
        .mobile-hint { display: block; }
    }
</style>