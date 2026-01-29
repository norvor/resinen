<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { api } from '$lib/api';

    // --- TYPES ---
    type Point = { x: number, y: number, w: number };
    type Stroke = { color: string, points: Point[] };

    // --- STATE ---
    let canvas: HTMLCanvasElement;
    let ctx: CanvasRenderingContext2D | null;
    let container: HTMLDivElement;
    
    // Non-reactive state for performance
    let history: Stroke[] = [];
    let currentStroke: Stroke | null = null;
    let isDrawing = false;
    
    // Brush Settings
    let currentColor = "#1f1f1f"; // Sumi Ink
    let baseWidth = 4;
    
    // Physics
    let lastX = 0;
    let lastY = 0;
    let lastTime = 0;

    const COLORS = [
        "#1f1f1f", // Sumi Ink
        "#b91c1c", // Vermilion
        "#1d4ed8", // Indigo
        "#15803d", // Bamboo
        "#a16207"  // Gold
    ];

    onMount(async () => {
        if (!canvas) return;
        ctx = canvas.getContext('2d', { alpha: false });
        
        const resizeObserver = new ResizeObserver(() => fitToContainer());
        resizeObserver.observe(container);

        try {
            const data = await api.widgets.loadDashboard();
            if (data && data.scribble) {
                try {
                    const parsed = JSON.parse(data.scribble);
                    if (Array.isArray(parsed)) {
                        history = parsed;
                        requestAnimationFrame(redrawAll);
                    }
                } catch(e) {}
            }
        } catch(e) {}

        return () => resizeObserver.disconnect();
    });

    function fitToContainer() {
        if (!canvas || !container) return;
        if (canvas.width !== container.clientWidth || canvas.height !== container.clientHeight) {
            canvas.width = container.clientWidth;
            canvas.height = container.clientHeight;
            redrawAll();
        }
    }

    // --- RENDER (Lag-Free) ---
    function drawSegment(p1: Point, p2: Point, color: string) {
        if (!ctx) return;
        ctx.beginPath();
        ctx.strokeStyle = color;
        ctx.fillStyle = color;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.lineWidth = (p1.w + p2.w) / 2; 
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.stroke();
        
        ctx.beginPath();
        ctx.arc(p2.x, p2.y, p2.w / 2, 0, Math.PI * 2);
        ctx.fill();
    }

    function redrawAll() {
        if (!ctx || !canvas) return;
        ctx.fillStyle = "#f4f1ea"; 
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        history.forEach(stroke => {
            if (stroke.points.length < 2) return;
            for (let i = 1; i < stroke.points.length; i++) {
                drawSegment(stroke.points[i - 1], stroke.points[i], stroke.color);
            }
        });
    }

    // --- INPUT ---
    function getPos(e: MouseEvent | TouchEvent) {
        const rect = canvas.getBoundingClientRect();
        const clientX = 'touches' in e ? e.touches[0].clientX : (e as MouseEvent).clientX;
        const clientY = 'touches' in e ? e.touches[0].clientY : (e as MouseEvent).clientY;
        return { x: clientX - rect.left, y: clientY - rect.top };
    }

    function start(e: MouseEvent | TouchEvent) {
        isDrawing = true;
        const { x, y } = getPos(e);
        lastX = x; lastY = y; lastTime = Date.now();

        currentStroke = { color: currentColor, points: [{ x, y, w: baseWidth }] };
        
        if(ctx) {
            ctx.fillStyle = currentColor;
            ctx.beginPath();
            ctx.arc(x, y, baseWidth/2, 0, Math.PI*2);
            ctx.fill();
        }
    }

    function move(e: MouseEvent | TouchEvent) {
        if (!isDrawing || !currentStroke) return;
        const { x, y } = getPos(e);
        const now = Date.now();
        
        // Fast Ink Physics
        const dist = Math.hypot(x - lastX, y - lastY);
        const time = Math.max(1, now - lastTime);
        const velocity = dist / time; 
        const targetWidth = Math.max(1.5, baseWidth - (velocity * 0.8));
        const prevWidth = currentStroke.points[currentStroke.points.length - 1].w;
        const smoothedWidth = prevWidth * 0.7 + targetWidth * 0.3;

        const newPoint = { x, y, w: smoothedWidth };
        const prevPoint = currentStroke.points[currentStroke.points.length - 1];

        drawSegment(prevPoint, newPoint, currentColor);
        currentStroke.points.push(newPoint);

        lastX = x; lastY = y; lastTime = now;
    }

    function end() {
        if (!isDrawing || !currentStroke) return;
        isDrawing = false;
        history.push(currentStroke);
        currentStroke = null;
        save();
    }

    async function save() {
        try { await api.widgets.updateScribble(JSON.stringify(history)); } catch(e) {}
    }

    function undo() {
        if (history.length > 0) {
            history.pop();
            redrawAll();
            save();
        }
    }

    function clearBoard() {
        if (confirm("Clear page?")) {
            history = [];
            redrawAll();
            save();
        }
    }
</script>

<div class="card sketchbook-widget" bind:this={container}>
    <div class="paper-texture"></div>

    <div class="book-header">
        <span class="jp-title">落書き</span>
        <span class="en-title">SKETCHBOOK</span>
    </div>

    <canvas 
        bind:this={canvas}
        onmousedown={start} onmousemove={move} onmouseup={end} onmouseleave={end}
        ontouchstart={start} ontouchmove={move} ontouchend={end}
    ></canvas>

    <div class="side-dock">
        <div class="palette">
            {#each COLORS as c}
                <button 
                    class="ink-pot" 
                    style="background: {c};"
                    class:selected={currentColor === c}
                    onclick={() => currentColor = c}
                ></button>
            {/each}
        </div>
        <div class="divider"></div>
        <button class="tool-btn undo" onclick={undo} title="Undo">⤺</button>
        <button class="tool-btn clear" onclick={clearBoard} title="Clear">
            <span class="stamp-text">消</span>
        </button>
    </div>
</div>

<style>
    .sketchbook-widget {
        display: flex; flex-direction: column;
        height: 380px; /* FIXED HEIGHT LIMIT */
        width: 100%;
        background: #f4f1ea; 
        border: 1px solid #d6d3cd;
        border-radius: 4px;
        position: relative;
        overflow: hidden;
        box-shadow: 2px 4px 10px rgba(0,0,0,0.1);
    }

    .paper-texture {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.08'/%3E%3C/svg%3E");
        pointer-events: none; z-index: 1; mix-blend-mode: multiply;
    }

    .book-header {
        position: absolute; top: 15px; left: 20px; z-index: 5;
        display: flex; flex-direction: column; pointer-events: none; opacity: 0.6;
    }
    .jp-title { font-family: serif; font-size: 1.5rem; color: #333; font-weight: bold; line-height: 1; margin-bottom: 2px; }
    .en-title { font-family: serif; font-size: 0.65rem; color: #666; letter-spacing: 3px; }

    canvas {
        display: block; width: 100%; height: 100%; position: relative; z-index: 2;
        cursor: crosshair; touch-action: none;
    }

    .side-dock {
        position: absolute; top: 50%; right: 15px; transform: translateY(-50%);
        background: #fff; padding: 10px 6px; border-radius: 8px;
        border: 1px solid #e5e5e5; display: flex; flex-direction: column; align-items: center; gap: 12px;
        z-index: 10; box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    .palette { display: flex; flex-direction: column; gap: 10px; }
    .ink-pot {
        width: 20px; height: 20px; border-radius: 50%; border: 2px solid #fff;
        cursor: pointer; box-shadow: 0 1px 3px rgba(0,0,0,0.2); transition: 0.2s;
    }
    .ink-pot:hover { transform: scale(1.1); }
    .ink-pot.selected { border-color: #333; transform: scale(1.2); }

    .divider { width: 80%; height: 1px; background: #eee; }

    .tool-btn {
        background: transparent; border: none; color: #666; cursor: pointer; font-size: 1.2rem;
        width: 28px; height: 28px; display: flex; align-items: center; justify-content: center;
        border-radius: 4px; transition: 0.2s;
    }
    .tool-btn:hover { color: #000; background: #f5f5f5; }

    .tool-btn.clear { border: 1px solid #b91c1c; color: #b91c1c; }
    .tool-btn.clear:hover { background: #b91c1c; color: #fff; }
    .stamp-text { font-family: serif; font-size: 0.9rem; font-weight: bold; }
</style>