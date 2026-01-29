<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    import { slide } from 'svelte/transition';

    // --- TYPES ---
    type Mission = {
        id: number;
        codename: string;
        rune: string;
        color: string;
        status: 'ACTIVE' | 'STEALTH' | 'COMPLETED';
        progress: number;
        briefing: string;
    };

    // --- STATE ---
    let missions = $state<Mission[]>([]);
    let isCreating = $state(false);
    let expandedId = $state<number | null>(null);

    // New Mission Form
    let newCodename = $state("");
    let newBriefing = $state("");
    let newColor = $state("#2dd4bf");
    let newRune = $state("⚡");

    const COLORS = ["#ef4444", "#f97316", "#facc15", "#2dd4bf", "#3b82f6", "#a855f7", "#ec4899"];
    const RUNES = ["⚡", "🚀", "🛡️", "👁️", "🔮", "⚔️", "📡", "🧬"];

    onMount(async () => {
        await reload();
    });

    async function reload() {
        try {
            missions = await api.widgets.getMissions();
        } catch(e) { console.error(e); }
    }

    async function create() {
        if (!newCodename) return;
        try {
            await api.widgets.createMission({
                codename: newCodename,
                briefing: newBriefing,
                color: newColor,
                rune: newRune,
                status: "ACTIVE",
                progress: 0
            });
            isCreating = false;
            newCodename = ""; newBriefing = "";
            await reload();
        } catch(e) {}
    }

    async function updateProgress(m: Mission, val: number) {
        m.progress = val;
        missions = missions; 
        try { await api.widgets.updateMission(m.id, { progress: val }); } catch(e) {}
    }

    async function toggleStatus(m: Mission) {
        const next = m.status === 'ACTIVE' ? 'STEALTH' : m.status === 'STEALTH' ? 'COMPLETED' : 'ACTIVE';
        m.status = next;
        missions = missions;
        try { await api.widgets.updateMission(m.id, { status: next }); } catch(e) {}
    }

    async function abort(id: number) {
        if (!confirm("CONFIRM ABORT SEQUENCE?")) return;
        try { await api.widgets.abortMission(id); await reload(); } catch(e) {}
    }

    function toggleDetails(id: number) {
        expandedId = expandedId === id ? null : id;
    }
</script>

<div class="cockpit-panel">
    <div class="hud-scanlines"></div>
    <div class="hud-vignette"></div>

    <div class="hud-header">
        <div class="hud-title">
            <span class="blink-led"></span>
            <span>PROJECTS</span>
        </div>
        <button class="tactical-btn" onclick={() => isCreating = !isCreating}>
            {isCreating ? '[ CEASE ]' : '[ + INIT ]'}
        </button>
    </div>

    {#if isCreating}
        <div class="cmd-terminal" transition:slide>
            <div class="cmd-row">
                <span class="cmd-prompt">CODE:</span>
                <input bind:value={newCodename} placeholder="OP NAME..." class="cmd-input" autoFocus />
            </div>
            <div class="cmd-row">
                <span class="cmd-prompt">ICON:</span>
                <div class="rune-picker">
                    {#each RUNES as r}
                        <button class="rune-btn" class:selected={newRune === r} onclick={() => newRune = r}>{r}</button>
                    {/each}
                </div>
            </div>
            <div class="cmd-row">
                <span class="cmd-prompt">SIG:</span>
                <div class="color-picker">
                    {#each COLORS as c}
                        <button 
                            class="color-node" 
                            style="background: {c}; box-shadow: 0 0 {newColor === c ? '10px' : '0'} {c}"
                            class:active={newColor === c}
                            onclick={() => newColor = c}
                        ></button>
                    {/each}
                </div>
            </div>
            <textarea bind:value={newBriefing} placeholder="> PARAMETERS..." class="cmd-text"></textarea>
            <button class="launch-btn" onclick={create}>:: ENGAGE ::</button>
        </div>
    {/if}

    <div class="systems-track">
        {#each missions as m (m.id)}
            <div 
                class="instrument-panel" 
                style="--glow: {m.color}" 
                class:stealth={m.status === 'STEALTH'} 
                class:completed={m.status === 'COMPLETED'}
            >
                <div class="panel-header">
                    <div class="status-indicator">
                        <div class="led-light"></div>
                        <span class="status-text">{m.status}</span>
                    </div>
                    <button class="panel-expander" onclick={() => toggleDetails(m.id)}>
                        {expandedId === m.id ? '▲' : '▼'}
                    </button>
                </div>

                <div class="panel-display">
                    <span class="rune-display">{m.rune}</span>
                    <span class="code-display">{m.codename}</span>
                </div>

                <div class="control-surface">
                    <div class="gauge-container">
                        <div class="gauge-track">
                            <div class="gauge-fill" style="width: {m.progress}%"></div>
                        </div>
                        <input 
                            type="range" min="0" max="100" value={m.progress} 
                            oninput={(e) => updateProgress(m, parseInt(e.currentTarget.value))}
                            class="tactical-slider"
                        />
                    </div>
                    <div class="gauge-val">{m.progress}%</div>

                    <div class="switch-array">
                        <button class="toggle-switch" onclick={() => toggleStatus(m)} title="Cycle">⟳</button>
                        {#if m.status !== 'COMPLETED'}
                            <button class="kill-switch" onclick={() => abort(m.id)} title="Abort">×</button>
                        {/if}
                    </div>
                </div>

                {#if expandedId === m.id}
                    <div class="data-readout" transition:slide>
                        {m.briefing || "NO DATA."}
                    </div>
                {/if}
            </div>
        {/each}

        {#if missions.length === 0 && !isCreating}
            <div class="radar-empty">
                <div class="radar-sweep"></div>
                <span>NO SIGNALS</span>
            </div>
        {/if}
    </div>
</div>

<style>
    /* === COCKPIT CONTAINER === */
    .cockpit-panel {
        background: #0b1120;
        border: 1px solid #1e293b;
        border-radius: 8px;
        /* Remove fixed min-height to allow it to shrink if needed, 
           or keep it small so it doesn't take unnecessary space */
        min-height: 200px; 
        display: flex; flex-direction: column;
        font-family: 'JetBrains Mono', monospace;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }

    /* HUD OVERLAYS */
    .hud-scanlines {
        position: absolute; inset: 0; pointer-events: none; z-index: 10;
        background: repeating-linear-gradient(to bottom, transparent 0px, transparent 2px, rgba(0,0,0,0.1) 3px);
        opacity: 0.5;
    }
    .hud-vignette {
        position: absolute; inset: 0; pointer-events: none; z-index: 11;
        background: radial-gradient(circle, transparent 50%, rgba(0,0,0,0.6) 100%);
    }

    /* HEADER */
    .hud-header {
        display: flex; justify-content: space-between; align-items: center;
        padding: 8px 12px; background: #0f172a;
        border-bottom: 1px solid #1e293b; z-index: 20;
    }
    .hud-title {
        color: #38bdf8; font-weight: bold; letter-spacing: 1px; font-size: 0.75rem;
        display: flex; align-items: center; gap: 8px;
    }
    .blink-led {
        width: 6px; height: 6px; background: #38bdf8; border-radius: 50%;
        box-shadow: 0 0 6px #38bdf8; animation: pulse 2s infinite;
    }

    .tactical-btn {
        background: transparent; border: 1px solid #38bdf8; color: #38bdf8;
        font-family: inherit; font-size: 0.65rem; padding: 2px 6px;
        cursor: pointer; text-transform: uppercase; transition: 0.2s;
    }
    .tactical-btn:hover { background: rgba(56, 189, 248, 0.2); }

    /* FORM COMPACT */
    .cmd-terminal {
        background: #020617; border-bottom: 1px solid #334155; padding: 10px;
        display: flex; flex-direction: column; gap: 6px; z-index: 20;
    }
    .cmd-row { display: flex; align-items: center; gap: 8px; }
    .cmd-prompt { color: #64748b; font-size: 0.7rem; min-width: 40px; }
    
    .cmd-input {
        background: transparent; border: none; border-bottom: 1px dashed #334155;
        color: #fff; font-family: inherit; flex: 1; padding: 4px; outline: none; font-size: 0.8rem;
    }
    
    .rune-picker { display: flex; gap: 4px; }
    .rune-btn {
        background: #1e293b; border: 1px solid #334155; color: #fff;
        cursor: pointer; padding: 2px 4px; border-radius: 2px; font-size: 0.9rem;
    }
    .rune-btn.selected { border-color: #38bdf8; background: rgba(56, 189, 248, 0.2); }

    .color-picker { display: flex; gap: 6px; }
    .color-node {
        width: 14px; height: 14px; border-radius: 2px; border: none; cursor: pointer; opacity: 0.5;
    }
    .color-node.active { opacity: 1; transform: scale(1.1); border: 1px solid #fff; }

    .cmd-text {
        background: #0f172a; border: 1px solid #334155; color: #94a3b8;
        padding: 6px; font-family: inherit; font-size: 0.75rem; resize: none; outline: none; height: 40px;
    }
    .launch-btn {
        background: #38bdf8; color: #000; border: none; padding: 6px;
        font-weight: bold; cursor: pointer; font-size: 0.75rem;
    }

    /* === SYSTEMS TRACK (Horizontal Scroll) === */
    .systems-track {
        flex: 1; 
        padding: 15px; 
        z-index: 15;
        display: flex; /* Flex row for horizontal scrolling */
        flex-direction: row;
        gap: 12px;
        overflow-x: auto; /* Horizontal scroll enabled */
        overflow-y: hidden;
        align-items: flex-start; /* Prevents vertical stretching (fixes whitespace) */
    }

    /* COMPACT MODULE */
    .instrument-panel {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid #334155;
        border-top: 2px solid var(--glow);
        border-radius: 4px;
        padding: 8px 10px;
        display: flex; flex-direction: column; gap: 6px;
        transition: 0.2s;
        
        /* Fixed width for uniform look in horizontal list */
        min-width: 240px; 
        width: 240px;
        flex-shrink: 0; /* Prevents squishing */
        
        /* Important: Fixes the whitespace issue */
        height: max-content; 
    }
    
    .instrument-panel:hover {
        background: rgba(30, 41, 59, 0.8);
        border-color: var(--glow);
    }
    .instrument-panel.stealth { opacity: 0.5; filter: grayscale(1); border-top-style: dotted; }
    .instrument-panel.completed { border-color: #10b981; opacity: 0.7; }

    /* MODULE HEADER */
    .panel-header { display: flex; justify-content: space-between; align-items: center; }
    .status-indicator { display: flex; align-items: center; gap: 4px; }
    .led-light {
        width: 4px; height: 4px; background: var(--glow); border-radius: 50%;
        box-shadow: 0 0 4px var(--glow);
    }
    .status-text { font-size: 0.55rem; color: #64748b; letter-spacing: 0.5px; }
    
    .panel-expander { background: none; border: none; color: #475569; cursor: pointer; font-size: 0.55rem; padding: 0; }
    .panel-expander:hover { color: #fff; }

    /* MODULE DISPLAY */
    .panel-display { 
        display: flex; align-items: center; gap: 8px; 
        padding-bottom: 6px; border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    .rune-display { font-size: 1.2rem; line-height: 1; filter: drop-shadow(0 0 3px var(--glow)); }
    .code-display { 
        font-size: 0.85rem; font-weight: bold; color: #e2e8f0; 
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis; 
    }

    /* CONTROLS */
    .control-surface { display: flex; align-items: center; gap: 6px; }
    
    .gauge-container { flex: 1; position: relative; height: 12px; display: flex; align-items: center; }
    .gauge-track { 
        width: 100%; height: 4px; background: #1e293b; border-radius: 2px; overflow: hidden;
    }
    .gauge-fill { 
        height: 100%; background: var(--glow); 
    }
    .tactical-slider {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%; opacity: 0; cursor: col-resize; margin: 0;
    }
    .gauge-val { font-size: 0.65rem; color: var(--glow); min-width: 22px; text-align: right; }

    .switch-array { display: flex; gap: 2px; }
    .toggle-switch, .kill-switch {
        background: rgba(255,255,255,0.05); border: 1px solid #334155; color: #64748b;
        width: 18px; height: 18px; border-radius: 2px; cursor: pointer;
        display: flex; align-items: center; justify-content: center; font-size: 0.7rem; padding: 0;
    }
    .toggle-switch:hover { color: var(--glow); border-color: var(--glow); }
    .kill-switch:hover { color: #ef4444; border-color: #ef4444; }

    /* READOUT */
    .data-readout {
        background: #020617; padding: 6px 8px;
        border: 1px dashed #334155; font-size: 0.65rem; color: #94a3b8;
        line-height: 1.3; margin-top: 4px;
    }

    /* EMPTY STATE */
    .radar-empty {
        width: 100%; height: 150px;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        color: #334155; font-size: 0.7rem;
    }
    .radar-sweep {
        width: 60px; height: 60px; border: 1px dashed #334155; border-radius: 50%;
        margin-bottom: 8px; position: relative;
    }
    .radar-sweep::after {
        content: ''; position: absolute; top: 50%; left: 50%; width: 50%; height: 1px;
        background: linear-gradient(to right, transparent, #38bdf8);
        transform-origin: left; animation: radar-spin 2s infinite linear;
    }

    @keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }
    @keyframes radar-spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    
    /* Horizontal Scrollbar Styling */
    .systems-track::-webkit-scrollbar { height: 6px; }
    .systems-track::-webkit-scrollbar-track { background: #020617; }
    .systems-track::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
    .systems-track::-webkit-scrollbar-thumb:hover { background: #38bdf8; }
</style>