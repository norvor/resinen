<script lang="ts">
    import { onMount } from 'svelte';
    import * as api from '$lib/api'; // <--- Import API

    let canvas: HTMLCanvasElement;
    let ctx: CanvasRenderingContext2D;
    let isDrawing = false;
    let color = $state('#2dd4bf');
    let brushSize = $state(3);
    let mode = $state<'draw' | 'erase'>('draw');
    let history: ImageData[] = [];
    let historyStep = -1;
    let points: {x: number, y: number}[] = [];
    const COLORS = ['#2dd4bf', '#f472b6', '#facc15', '#a78bfa', '#ffffff'];

    // ... (Keep getPos, startDraw, drawDot, draw functions exactly as before) ...
    // Copy them from the previous "World's Best Scribble" response 
    
    function getPos(e: MouseEvent | TouchEvent) {
        const rect = canvas.getBoundingClientRect();
        let clientX, clientY;
        if (window.TouchEvent && e instanceof TouchEvent) { clientX = e.touches[0].clientX; clientY = e.touches[0].clientY; } 
        else { clientX = (e as MouseEvent).clientX; clientY = (e as MouseEvent).clientY; }
        return { x: (clientX - rect.left) * (canvas.width / rect.width), y: (clientY - rect.top) * (canvas.height / rect.height) };
    }

    function startDraw(e: MouseEvent | TouchEvent) {
        if(e.cancelable) e.preventDefault(); isDrawing = true; const pos = getPos(e); points = [pos];
        ctx.beginPath(); ctx.moveTo(pos.x, pos.y);
        ctx.fillStyle = mode === 'erase' ? '#000' : color;
        if (mode === 'erase') { ctx.globalCompositeOperation = 'destination-out'; ctx.arc(pos.x, pos.y, brushSize / 2, 0, Math.PI * 2); ctx.fill(); } 
        else { ctx.globalCompositeOperation = 'source-over'; drawDot(pos.x, pos.y); }
    }
    function drawDot(x: number, y: number) { ctx.shadowBlur = 10; ctx.shadowColor = color; ctx.fillStyle = color; ctx.beginPath(); ctx.arc(x, y, brushSize / 2, 0, Math.PI * 2); ctx.fill(); }
    function draw(e: MouseEvent | TouchEvent) {
        if (!isDrawing) return; if(e.cancelable) e.preventDefault(); const pos = getPos(e); points.push(pos); if (points.length < 3) return;
        const i = points.length - 2; const p1 = points[i]; const p2 = points[i + 1]; const mid = { x: (p1.x + p2.x) / 2, y: (p1.y + p2.y) / 2 };
        ctx.lineWidth = mode === 'erase' ? brushSize * 4 : brushSize; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
        if (mode === 'erase') { ctx.globalCompositeOperation = 'destination-out'; ctx.shadowBlur = 0; } 
        else { ctx.globalCompositeOperation = 'source-over'; ctx.strokeStyle = color; ctx.shadowBlur = 8; ctx.shadowColor = color; }
        ctx.beginPath(); ctx.moveTo(points[i-1].x, points[i-1].y); ctx.quadraticCurveTo(p1.x, p1.y, mid.x, mid.y); ctx.stroke();
    }

    function stopDraw() {
        if (!isDrawing) return;
        isDrawing = false; points = [];
        saveHistory();
        saveData(); // <--- Changed from saveToLocal
    }

    function saveHistory() {
        historyStep++; if (historyStep < history.length) history.length = historyStep;
        history.push(ctx.getImageData(0, 0, canvas.width, canvas.height));
        if (history.length > 20) { history.shift(); historyStep--; }
    }

    function undo() {
        if (historyStep > 0) { historyStep--; ctx.putImageData(history[historyStep], 0, 0); saveData(); } 
        else if (historyStep === 0) { clearCanvas(false); historyStep = -1; }
    }

    function clearCanvas(saveState = true) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        if (saveState) { saveHistory(); saveData(); }
    }

    function download() { const link = document.createElement('a'); link.download = `scribble-${Date.now()}.png`; link.href = canvas.toDataURL(); link.click(); }

    // --- UPDATED SAVE ---
    function saveData() {
        // Saves the Base64 image string to Cloud
        api.saveData('resinen_scribble', canvas.toDataURL());
    }

    onMount(() => {
        ctx = canvas.getContext('2d')!;
        const dpr = window.devicePixelRatio || 1;
        const rect = canvas.getBoundingClientRect();
        canvas.width = rect.width * dpr; canvas.height = rect.height * dpr;
        
        const saved = localStorage.getItem('resinen_scribble');
        if (saved) {
            const img = new Image();
            img.onload = () => { ctx.drawImage(img, 0, 0); saveHistory(); };
            img.src = saved;
        } else { saveHistory(); }
    });
</script>

<div class="card scribble-widget">
    <div class="canvas-layer"><canvas bind:this={canvas} onmousedown={startDraw} onmousemove={draw} onmouseup={stopDraw} onmouseleave={stopDraw} ontouchstart={startDraw} ontouchmove={draw} ontouchend={stopDraw}></canvas></div>
    <div class="toolbar">
        <div class="color-group">{#each COLORS as c}<button class="tool-btn color-dot" class:selected={color === c && mode === 'draw'} style="background: {c}; box-shadow: 0 0 {color === c && mode === 'draw' ? '10px' : '0'} {c}" onclick={() => { color = c; mode = 'draw'; }}></button>{/each}</div>
        <div class="divider"></div>
        <div class="action-group"><button class="tool-btn icon" class:selected={mode === 'erase'} onclick={() => mode = 'erase'}>⌫</button><button class="tool-btn icon" onclick={undo} disabled={historyStep < 0}>↺</button><button class="tool-btn icon" onclick={() => clearCanvas()}>🗑</button><button class="tool-btn icon" onclick={download}>↓</button></div>
    </div>
</div>

<style>
    .scribble-widget { height: 220px; display: flex; flex-direction: column; background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(15px); border: 1px solid #334155; border-radius: 16px; position: relative; overflow: hidden; }
    .canvas-layer { position: absolute; top: 0; left: 0; width: 100%; height: 100%; cursor: crosshair; z-index: 1; } canvas { width: 100%; height: 100%; display: block; touch-action: none; }
    .toolbar { position: absolute; bottom: 10px; left: 50%; transform: translateX(-50%); display: flex; gap: 10px; padding: 6px 12px; background: rgba(2, 6, 23, 0.85); border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; z-index: 10; align-items: center; box-shadow: 0 5px 15px rgba(0,0,0,0.5); }
    .color-group { display: flex; gap: 6px; } .tool-btn { background: transparent; border: none; cursor: pointer; transition: transform 0.2s; display: flex; align-items: center; justify-content: center; } .tool-btn:hover { transform: scale(1.2); } .tool-btn:active { transform: scale(0.9); }
    .color-dot { width: 14px; height: 14px; border-radius: 50%; border: 1px solid rgba(255,255,255,0.2); } .color-dot.selected { border-color: #fff; transform: scale(1.2); }
    .divider { width: 1px; height: 14px; background: rgba(255,255,255,0.2); } .action-group { display: flex; gap: 8px; }
    .icon { color: #94a3b8; font-family: 'JetBrains Mono'; font-size: 0.9rem; width: 20px; height: 20px; border-radius: 4px; } .icon:hover { color: #fff; background: rgba(255,255,255,0.1); } .icon.selected { color: #ef4444; text-shadow: 0 0 10px #ef4444; } .icon:disabled { opacity: 0.3; cursor: not-allowed; }
</style>