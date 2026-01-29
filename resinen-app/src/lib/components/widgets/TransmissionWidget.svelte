<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';

    // Define Interface locally to ensure type safety
    interface Transmission {
        id: number;
        title: string;
        url: string;
        type: string;
    }

    let feed = $state<Transmission[]>([]);
    let isAdding = $state(false);
    let viewingItem = $state<Transmission | null>(null);
    let errorMsg = $state("");
    
    // Inputs
    let newTitle = $state("");
    let newUrl = $state("");
    let newType = $state("link");

    onMount(async () => {
        if (typeof localStorage !== 'undefined') {
            const saved = localStorage.getItem('resinen_transmission');
            if (saved) feed = JSON.parse(saved);
        }

        try {
            const data = await api.widgets.loadDashboard();
            if (data && data.transmission) {
                feed = data.transmission;
                saveLocal();
            }
        } catch(e) { console.log("Offline"); }
    });

    // --- AUTO-DETECT & CLEAN ---
    function handleInput(e: Event) {
        const lower = newUrl.toLowerCase();
        if (lower.includes('youtube.com') || lower.includes('youtu.be')) {
            newType = 'video';
        } else if (lower.includes('spotify.com') || lower.includes('music.apple.com')) {
            newType = 'music';
        } else if (/\.(jpg|jpeg|png|webp|gif)$/i.test(lower)) {
            newType = 'photo';
        }
    }

    function cleanUrl(url: string, type: string): string {
        // Fixes "Signal Jam" by removing playlist data
        if (type === 'video' && (url.includes('youtube.com') || url.includes('youtu.be'))) {
            try {
                const urlObj = new URL(url);
                const v = urlObj.searchParams.get('v');
                if (v) return `https://www.youtube.com/watch?v=${v}`; // Strip everything else
                if (url.includes('youtu.be')) return url.split('?')[0]; 
            } catch(e) { return url; }
        }
        return url;
    }

    function validateSignal(url: string, type: string): boolean {
        const lower = url.toLowerCase();
        errorMsg = "";

        if (type === 'video') {
            if (lower.includes('youtube.com') || lower.includes('youtu.be')) return true;
            errorMsg = "PROTOCOL MISMATCH: YOUTUBE ONLY.";
            return false;
        }
        if (type === 'music') {
            if (lower.includes('spotify.com') || lower.includes('music.apple.com')) return true;
            errorMsg = "PROTOCOL MISMATCH: SPOTIFY/APPLE ONLY.";
            return false;
        }
        if (type === 'photo') {
            if (/\.(jpg|jpeg|png|webp|gif)$/i.test(lower)) return true;
            errorMsg = "FORMAT ERROR: IMAGE FILE REQUIRED.";
            return false;
        }
        return true;
    }

    async function addSignal() {
        if (!newTitle.trim() || !newUrl.trim()) return;
        
        const cleanedUrl = cleanUrl(newUrl, newType);

        if (!validateSignal(cleanedUrl, newType)) return;

        const tempTitle = newTitle;
        const tempType = newType;
        
        // Reset UI immediately
        newTitle = ""; newUrl = ""; errorMsg = ""; newType = "link";
        isAdding = false;

        try {
            const res = await api.widgets.createTransmission(tempTitle, cleanedUrl, tempType);
            feed = [res, ...feed]; 
            saveLocal();
        } catch(e) {
            console.error(e);
            alert(`Signal Jam: Server rejected data.`);
            newTitle = tempTitle;
            newUrl = cleanedUrl;
            newType = tempType;
            isAdding = true;
        }
    }

    async function deleteSignal(id: number) {
        if(viewingItem && viewingItem.id === id) viewingItem = null; 
        feed = feed.filter(t => t.id !== id);
        saveLocal();
        try { await api.widgets.deleteTransmission(id); } catch(e) {}
    }

    function saveLocal() {
        if (typeof localStorage !== 'undefined') localStorage.setItem('resinen_transmission', JSON.stringify(feed));
    }

    function getTypeIcon(type: string) {
        switch(type) {
            case 'video': return '📹';
            case 'music': return '📻'; 
            case 'photo': return '🎞️'; 
            default: return '🔗';
        }
    }

    function getEmbedUrl(item: Transmission): string {
        const url = item.url;
        if (item.type === 'video') {
            const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
            const match = url.match(regExp);
            const id = (match && match[2].length === 11) ? match[2] : null;
            return id ? `https://www.youtube.com/embed/${id}?autoplay=1&controls=1&rel=0` : url;
        }
        if (item.type === 'music') {
            if (url.includes('spotify.com')) {
                // Handle spotify link -> embed conversion
                try {
                    const u = new URL(url);
                    return `https://open.spotify.com/embed${u.pathname}`;
                } catch(e) { return url; }
            }
            if (url.includes('music.apple.com')) {
                return url.replace('music.apple.com', 'embed.music.apple.com');
            }
        }
        return url;
    }
</script>

<div class="card transmission-widget noir-theme">
    <div class="grain-overlay"></div>
    <div class="amber-glow"></div>

    <div class="header">
        <span class="header-title">/// INCOMING TRANSMISSION</span>
        {#if viewingItem}
            <button class="noir-btn back" onclick={() => viewingItem = null}>⏏ EJECT</button>
        {:else}
            <button class="noir-btn" onclick={() => isAdding = !isAdding}>{isAdding ? '✖ ABORT' : '✚ RECEIVE'}</button>
        {/if}
    </div>

    {#if isAdding && !viewingItem}
        <div class="add-form">
            <div class="form-group">
                <input type="text" bind:value={newTitle} placeholder="SIGNAL IDENTIFIER..." autoFocus />
            </div>
            <div class="form-group">
                <input 
                    type="text" 
                    bind:value={newUrl} 
                    oninput={handleInput}
                    placeholder="PROTOCOL (https://...)" 
                />
            </div>
            <div class="form-group">
                <select bind:value={newType}>
                    <option value="link">DATA LINK</option>
                    <option value="video">VISUAL FEED</option>
                    <option value="music">AUDIO FEED</option>
                    <option value="photo">STATIC IMG</option>
                </select>
            </div>
            
            {#if errorMsg}
                <div class="error-msg">⚠ {errorMsg}</div>
            {/if}
            <button class="save-btn" onclick={addSignal}>INITIATE UPLOAD</button>
        </div>
    {/if}

    {#if viewingItem}
        <div class="screen-container">
            <div class="screen-chassis">
                <div class="screen-display">
                    {#if viewingItem.type === 'photo'}
                        <img src={viewingItem.url} alt="Signal" class="screen-content-img"/>
                    {:else if viewingItem.type === 'video' || viewingItem.type === 'music'}
                        <iframe 
                            src={getEmbedUrl(viewingItem)} 
                            title="Transmission" 
                            frameborder="0" 
                            allow="autoplay; encrypted-media; picture-in-picture" 
                            allowfullscreen
                            class="screen-content-frame"
                        ></iframe>
                    {:else}
                        <div class="text-terminal">
                            <div class="term-line">ENCRYPTED DATA STREAM</div>
                            <div class="term-line">SOURCE: {viewingItem.title}</div>
                            <br/>
                            <a href={viewingItem.url} target="_blank" class="term-link">>> DECRYPT EXTERNAL LINK</a>
                        </div>
                    {/if}
                </div>
                <div class="screen-controls">
                    <div class="pwr-indicator"></div>
                    <span class="ch-indicator">CH-{viewingItem.id}</span>
                </div>
            </div>
        </div>
    
    {:else}
        <div class="feed-list">
            {#each feed as item (item.id)}
                <div class="feed-item">
                    <div class="feed-icon">{getTypeIcon(item.type)}</div>
                    
                    <button class="feed-content" onclick={() => viewingItem = item}>
                        <div class="feed-title">{item.title}</div>
                        <div class="feed-meta">
                            <span class="type-badge">{item.type.toUpperCase()}</span>
                            <span class="url-text"> // {new URL(item.url).hostname.replace('www.','')}</span>
                        </div>
                    </button>

                    <button class="del-btn" onclick={(e) => { e.stopPropagation(); deleteSignal(item.id); }}>✖</button>
                </div>
            {/each}
            {#if feed.length === 0 && !isAdding}
                <div class="empty-state">
                    STATIC INTERFERENCE.<br>
                    AWAITING SIGNAL...
                </div>
            {/if}
        </div>
    {/if}
</div>

<style>
    /* === VINTAGE NOIR THEME === */
    .noir-theme {
        background: #0f0a05; /* Very Dark Brown/Black */
        border: 2px solid #5d4037; /* Leather Brown */
        border-radius: 4px;
        position: relative;
        overflow: hidden;
        display: flex; flex-direction: column;
        min-height: 300px;
        font-family: 'Courier New', monospace; /* Classic Typewriter */
        color: #d2b48c; /* Tan/Sepia Text */
        box-shadow: inset 0 0 40px rgba(0,0,0,0.8);
    }

    /* OVERLAYS */
    .grain-overlay {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.05'/%3E%3C/svg%3E");
        pointer-events: none; z-index: 10;
        opacity: 0.3;
    }
    
    .amber-glow {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: radial-gradient(circle, rgba(205, 133, 63, 0.05) 0%, rgba(0,0,0,0.6) 100%);
        pointer-events: none; z-index: 9;
    }

    /* HEADER */
    .header {
        display: flex; justify-content: space-between; align-items: center;
        padding: 12px 16px; 
        border-bottom: 2px solid #3e2723;
        background: rgba(62, 39, 35, 0.3);
        z-index: 12;
    }
    .header-title { 
        font-weight: bold; letter-spacing: 1px; color: #cd853f; /* Peru color */
        text-shadow: 0 0 4px rgba(205, 133, 63, 0.4);
    }

    .noir-btn {
        background: transparent; border: 1px solid #8d6e63; color: #8d6e63;
        font-family: inherit; font-size: 0.75rem; cursor: pointer;
        padding: 4px 10px; transition: 0.2s;
        text-transform: uppercase; letter-spacing: 1px;
    }
    .noir-btn:hover { 
        background: #8d6e63; color: #1a1005; 
        box-shadow: 0 0 8px #8d6e63; 
    }

    /* FORM STYLES (Fixed Spacing) */
    .add-form { 
        padding: 20px; display: flex; flex-direction: column; gap: 15px; z-index: 12; 
        background: rgba(0,0,0,0.4);
    }
    .form-group { width: 100%; }
    
    input, select {
        width: 100%; box-sizing: border-box; /* Fix width issues */
        background: #1a1005; border: 1px solid #5d4037; color: #d2b48c;
        padding: 10px; font-family: inherit; font-size: 0.9rem; outline: none;
        border-radius: 2px;
    }
    input::placeholder { color: #5d4037; font-style: italic; }
    input:focus, select:focus { 
        border-color: #cd853f; 
        box-shadow: 0 0 8px rgba(205, 133, 63, 0.2); 
    }

    .error-msg { 
        color: #e57373; background: rgba(50, 0, 0, 0.5); 
        padding: 8px; font-size: 0.75rem; text-align: center; border: 1px solid #e57373; 
    }

    .save-btn {
        width: 100%;
        margin-top: 5px; background: #3e2723; color: #d2b48c; border: 1px solid #5d4037; 
        padding: 12px; cursor: pointer; font-family: inherit; font-weight: bold; letter-spacing: 1px;
        transition: 0.2s;
    }
    .save-btn:hover { background: #5d4037; color: #fff; }

    /* FEED LIST */
    .feed-list { 
        flex: 1; 
        overflow-y: auto; 
        padding: 10px 15px; 
        z-index: 12; 
        display: flex; 
        flex-direction: column; 
        gap: 8px; 
        /* Added max-height to ensure scrolling works within the container */
        max-height: 250px; 
    }
    
    .feed-item {
        display: flex; align-items: center; gap: 12px; padding: 10px;
        border-bottom: 1px dashed #3e2723; transition: 0.2s;
        background: rgba(255, 255, 255, 0.02);
        /* Prevent item shrinking */
        flex-shrink: 0;
    }
    .feed-item:hover {
        background: rgba(205, 133, 63, 0.05);
        border-bottom-color: #cd853f;
    }

    .feed-icon { font-size: 1.2rem; filter: sepia(100%); opacity: 0.8; }
    
    .feed-content { flex: 1; background: none; border: none; text-align: left; cursor: pointer; }
    .feed-title { color: #d2b48c; font-weight: bold; font-size: 0.9rem; text-shadow: 0 0 2px rgba(0,0,0,0.5); }
    .feed-meta { display: flex; gap: 8px; font-size: 0.7rem; color: #8d6e63; margin-top: 4px; }
    .type-badge { color: #cd853f; font-weight: bold; }
    
    .del-btn { background: none; border: none; color: #5d4037; cursor: pointer; font-family: inherit; font-weight: bold; }
    .del-btn:hover { color: #e57373; }

    .empty-state { text-align: center; color: #5d4037; margin-top: 40px; font-size: 0.8rem; font-style: italic; }

    /* === SCREEN VIEW === */
    .screen-container { 
        flex: 1; padding: 15px; display: flex; justify-content: center; align-items: center; z-index: 15;
        animation: flicker 0.2s ease-in;
    }

    .screen-chassis {
        width: 100%; height: 100%;
        background: #000; border: 8px solid #3e2723; border-radius: 4px;
        box-shadow: 0 0 30px rgba(0,0,0,0.9);
        display: flex; flex-direction: column;
    }

    .screen-display {
        flex: 1; background: #111; overflow: hidden; position: relative;
        border: 1px solid #222;
    }
    
    .screen-content-frame, .screen-content-img { width: 100%; height: 100%; object-fit: cover; }
    
    .screen-controls {
        height: 30px; display: flex; align-items: center; justify-content: space-between; 
        padding: 0 10px; background: #1b1b1b; border-top: 2px solid #3e2723;
    }
    .pwr-indicator { width: 6px; height: 6px; background: #cd853f; border-radius: 50%; box-shadow: 0 0 6px #cd853f; }
    .ch-indicator { font-size: 0.7rem; color: #555; font-weight: bold; }

    /* TEXT FALLBACK */
    .text-terminal {
        height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 20px;
        color: #cd853f;
    }
    .term-link { color: #fff; text-decoration: underline; margin-top: 10px; font-size: 0.8rem; opacity: 0.7; }
    .term-link:hover { opacity: 1; }

    @keyframes flicker { 0% { opacity: 0.5; } 100% { opacity: 1; } }

    .feed-list::-webkit-scrollbar { width: 6px; }
    .feed-list::-webkit-scrollbar-thumb { background: #5d4037; border-radius: 3px; }
</style>