<script lang="ts">
    import { onMount } from 'svelte';
    import { fly, scale, fade } from 'svelte/transition';
    import { elasticOut, cubicOut } from 'svelte/easing';

    // --- 1. DATA (The "Film Rolls") ---
    type Photo = {
        id: string;
        url: string;
        category: 'SPACE' | 'NATURE' | 'CITIES' | 'ANIMALS';
        title: string;
        date: string; // Added date for retro feel
        rotation: number; // For the "scattered" look
    };

    const RAW_DATA: Photo[] = [
        // SPACE
        { id: 's1', category: 'SPACE', title: 'Deep Nebula', date: 'AUG 1992', rotation: -2, url: 'https://images.unsplash.com/photo-1462331940025-496dfbfc7564?q=80&w=1600&auto=format&fit=crop' },
        { id: 's2', category: 'SPACE', title: 'The Void', date: 'SEP 1994', rotation: 3, url: 'https://images.unsplash.com/photo-1506318137071-a8bcbf6d2806?q=80&w=1600&auto=format&fit=crop' },
        
        // NATURE
        { id: 'n1', category: 'NATURE', title: 'Alpine Peak', date: 'JAN 1988', rotation: 1, url: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?q=80&w=1600&auto=format&fit=crop' },
        { id: 'n2', category: 'NATURE', title: 'Silent Forest', date: 'OCT 1995', rotation: -3, url: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=1600&auto=format&fit=crop' },
        { id: 'n3', category: 'NATURE', title: 'Desert Storm', date: 'JUL 1985', rotation: 2, url: 'https://images.unsplash.com/photo-1473580044384-7ba9967e16a0?q=80&w=1600&auto=format&fit=crop' },

        // CITIES
        { id: 'c1', category: 'CITIES', title: 'Neon Tokyo', date: 'NOV 2077', rotation: -1, url: 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?q=80&w=1600&auto=format&fit=crop' },
        { id: 'c2', category: 'CITIES', title: 'NYC Rain', date: 'MAR 1999', rotation: 4, url: 'https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?q=80&w=1600&auto=format&fit=crop' },
        
        // ANIMALS
        { id: 'a1', category: 'ANIMALS', title: 'The King', date: 'FEB 2001', rotation: -2, url: 'https://images.unsplash.com/photo-1614027164847-1b28cfe1df60?q=80&w=1600&auto=format&fit=crop' },
    ];

    // --- 2. STATE ---
    let activeCategory = $state<string>('ALL');
    let focusedPhoto = $state<Photo | null>(null);

    // Filter Logic
    let filteredPhotos = $derived(
        activeCategory === 'ALL' 
        ? RAW_DATA 
        : RAW_DATA.filter(p => p.category === activeCategory)
    );

    function focusPhoto(photo: Photo) {
        focusedPhoto = photo;
    }

    function closeFocus() {
        focusedPhoto = null;
    }
</script>

<svelte:head>
    <title>Resinen Analog Studio</title>
</svelte:head>

<div class="desk-surface">
    
    <header class="studio-header">
        <div class="brand-plate">
            <h1>RESINEN STUDIO</h1>
            <span class="est">EST. 2025</span>
        </div>

        <nav class="film-tabs">
            {#each ['ALL', 'SPACE', 'NATURE', 'CITIES', 'ANIMALS'] as cat}
                <button 
                    class="tab {activeCategory === cat ? 'active' : ''}"
                    onclick={() => activeCategory = cat}
                >
                    {cat}
                </button>
            {/each}
        </nav>
        
        <a href="/" class="exit-link">CLOSE ALBUM ✕</a>
    </header>

    <main class="album-container">
        <div class="photo-grid">
            {#each filteredPhotos as photo (photo.id)}
                <button 
                    class="polaroid"
                    style="transform: rotate({photo.rotation}deg)"
                    onclick={() => focusPhoto(photo)}
                    in:fly={{ y: 50, duration: 800, easing: elasticOut }}
                >
                    <div class="frame">
                        <img src={photo.url} alt={photo.title} loading="lazy" />
                        <div class="tape"></div>
                    </div>
                    <div class="caption">
                        <span class="handwritten">{photo.title}</span>
                        <span class="stamp">{photo.date}</span>
                    </div>
                </button>
            {/each}
        </div>
    </main>

    {#if focusedPhoto}
        <div class="overlay" transition:fade={{ duration: 200 }} onclick={closeFocus} role="presentation">
            <div 
                class="photo-inspection"
                in:scale={{ start: 0.8, duration: 400, easing: cubicOut }}
                onclick={(e) => e.stopPropagation()}
                role="presentation"
            >
                <div class="large-polaroid">
                    <img src={focusedPhoto.url} alt={focusedPhoto.title} />
                    <div class="large-caption">
                        <h2>{focusedPhoto.title}</h2>
                        <div class="metadata">
                            <span>CATEGORY: {focusedPhoto.category}</span>
                            <span>CAPTURED: {focusedPhoto.date}</span>
                        </div>
                    </div>
                </div>
                <button class="put-back-btn" onclick={closeFocus}>Put Back</button>
            </div>
        </div>
    {/if}

</div>

<style>
    /* --- FONTS & TEXTURES --- */
    @import url('https://fonts.googleapis.com/css2?family=Courier+Prime:ital,wght@0,400;0,700;1,400&family=Permanent+Marker&display=swap');

    /* --- LAYOUT --- */
    .desk-surface {
        min-height: 100vh;
        background-color: #2a2320;
        /* Wood Texture Pattern */
        background-image: 
            linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)),
            url("https://www.transparenttextures.com/patterns/wood-pattern.png");
        display: flex; flex-direction: column;
        overflow-x: hidden;
        color: #e2e8f0;
    }

    /* --- HEADER --- */
    .studio-header {
        padding: 20px 40px;
        display: flex; justify-content: space-between; align-items: center;
        background: rgba(0,0,0,0.4);
        border-bottom: 2px solid rgba(255,255,255,0.05);
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }

    .brand-plate {
        border: 2px solid #eab308;
        padding: 8px 16px;
        border-radius: 4px;
        color: #eab308;
        text-align: center;
        background: rgba(0,0,0,0.6);
    }
    .brand-plate h1 {
        margin: 0; font-family: 'Courier Prime', monospace; 
        font-weight: 700; font-size: 1.2rem; letter-spacing: 2px;
    }
    .brand-plate .est {
        font-size: 0.7rem; opacity: 0.8; font-family: 'Courier Prime', monospace;
    }

    .film-tabs {
        display: flex; gap: 10px;
        background: #1c1917;
        padding: 5px; border-radius: 50px;
        box-shadow: inset 0 2px 5px rgba(0,0,0,0.5);
    }
    .tab {
        background: transparent; border: none;
        color: #78716c;
        font-family: 'Courier Prime', monospace; font-weight: 700; font-size: 0.9rem;
        padding: 8px 16px; border-radius: 20px;
        cursor: pointer; transition: 0.3s;
    }
    .tab:hover { color: #d6d3d1; }
    .tab.active {
        background: #eab308; color: #2a2320;
        box-shadow: 0 2px 10px rgba(234, 179, 8, 0.3);
    }

    .exit-link {
        color: #ef4444; text-decoration: none; 
        font-family: 'Courier Prime', monospace; font-weight: 700;
        font-size: 0.9rem; border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 8px 16px; border-radius: 4px;
        transition: 0.3s;
    }
    .exit-link:hover { background: rgba(239, 68, 68, 0.1); }

    /* --- PHOTO GRID --- */
    .album-container {
        flex: 1; padding: 60px;
        display: flex; justify-content: center;
    }

    .photo-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 60px;
        width: 100%; max-width: 1600px;
    }

    /* --- POLAROID STYLE --- */
    .polaroid {
        background: #fdfbf7; /* Off-white paper */
        padding: 15px 15px 50px 15px; /* Big bottom padding for caption */
        box-shadow: 
            2px 8px 15px rgba(0,0,0,0.4),
            0 1px 3px rgba(0,0,0,0.2);
        border: none;
        cursor: pointer;
        transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s;
        position: relative;
        display: flex; flex-direction: column;
    }

    .polaroid:hover {
        transform: scale(1.05) rotate(0deg) !important; /* Straighten on hover */
        box-shadow: 
            5px 20px 30px rgba(0,0,0,0.5),
            0 5px 10px rgba(0,0,0,0.3);
        z-index: 10;
    }

    .frame {
        width: 100%; aspect-ratio: 1/1;
        background: #000;
        overflow: hidden;
        position: relative;
        filter: sepia(20%); /* Slight vintage tint */
    }
    
    .frame img {
        width: 100%; height: 100%; object-fit: cover;
        opacity: 0.9;
    }

    /* Tape Effect */
    .tape {
        position: absolute; top: -15px; left: 50%; transform: translateX(-50%);
        width: 80px; height: 30px;
        background: rgba(255,255,255,0.4);
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transform: translateX(-50%) rotate(-2deg);
        pointer-events: none;
    }

    .caption {
        margin-top: 15px;
        display: flex; justify-content: space-between; align-items: flex-end;
        color: #2a2320;
    }
    
    .handwritten {
        font-family: 'Permanent Marker', cursive;
        font-size: 1.3rem;
        transform: rotate(-2deg);
    }
    
    .stamp {
        font-family: 'Courier Prime', monospace;
        font-size: 0.7rem;
        opacity: 0.6;
        border: 1px solid #2a2320;
        padding: 2px 4px;
        transform: rotate(2deg);
    }

    /* --- INSPECTION OVERLAY --- */
    .overlay {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.85);
        backdrop-filter: blur(8px);
        z-index: 100;
        display: flex; justify-content: center; align-items: center;
    }

    .photo-inspection {
        display: flex; flex-direction: column; align-items: center; gap: 30px;
    }

    .large-polaroid {
        background: #fff;
        padding: 20px 20px 80px 20px;
        box-shadow: 0 25px 50px rgba(0,0,0,0.5);
        transform: rotate(1deg);
        max-width: 600px; width: 90vw;
    }

    .large-polaroid img {
        width: 100%; height: auto;
        border: 1px solid #eee;
    }

    .large-caption {
        margin-top: 30px;
        color: #333;
        font-family: 'Courier Prime', monospace;
    }

    .large-caption h2 {
        font-family: 'Permanent Marker', cursive;
        font-size: 2.5rem; margin: 0 0 10px 0;
        color: #1a1a1a;
    }

    .metadata {
        display: flex; gap: 20px;
        font-size: 0.9rem; color: #666;
        border-top: 1px dashed #ccc;
        padding-top: 10px;
    }

    .put-back-btn {
        background: transparent;
        border: 2px solid #fff; color: #fff;
        padding: 12px 30px; font-size: 1.1rem;
        font-family: 'Courier Prime', monospace; font-weight: 700;
        cursor: pointer; transition: 0.2s;
        border-radius: 50px;
    }
    .put-back-btn:hover { background: #fff; color: #000; }

    /* RESPONSIVE */
    @media (max-width: 768px) {
        .studio-header { flex-direction: column; gap: 15px; }
        .film-tabs { width: 100%; overflow-x: auto; justify-content: flex-start; }
        .album-container { padding: 30px 15px; }
        .photo-grid { gap: 30px; }
    }
</style>