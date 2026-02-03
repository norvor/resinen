<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { fly, fade, scale } from 'svelte/transition';
    import { elasticOut } from 'svelte/easing';
    import * as THREE from 'three';

    // --- 1. NASA / SPACE ARCHIVE (20 IMAGES) ---
const NASA_ARCHIVE = [
        // REEL 01: NEBULAS
        { id: 'n1', title: 'PILLARS OF CREATION', date: 'HST-2014', url: 'https://images-assets.nasa.gov/image/PIA18906/PIA18906~medium.jpg' },
        { id: 'n2', title: 'COSMIC CLIFFS', date: 'JWST-2022', url: 'https://images-assets.nasa.gov/image/PIA25287/PIA25287~medium.jpg' },
        { id: 'n3', title: 'ORION NEBULA', date: 'SPITZER', url: 'https://images-assets.nasa.gov/image/PIA08653/PIA08653~medium.jpg' },
        { id: 'n4', title: 'TARANTULA NEBULA', date: 'HST-2023', url: 'https://images-assets.nasa.gov/image/PIA25432/PIA25432~medium.jpg' },
        { id: 'n5', title: 'HORSEHEAD NEBULA', date: 'EUCLID', url: 'https://images-assets.nasa.gov/image/PIA16839/PIA16839~medium.jpg' },

        // REEL 02: PLANETARY SYSTEMS
        { id: 'p1', title: 'JUPITER ABYSS', date: 'JUNO', url: 'https://images-assets.nasa.gov/image/PIA22946/PIA22946~medium.jpg' },
        { id: 'p2', title: 'SATURN & RINGS', date: 'CASSINI', url: 'https://images-assets.nasa.gov/image/PIA14922/PIA14922~medium.jpg' },
        { id: 'p3', title: 'MARS PERSEVERANCE', date: 'ROVER', url: 'https://images-assets.nasa.gov/image/PIA25666/PIA25666~medium.jpg' },
        { id: 'p4', title: 'BLUE MARBLE', date: 'EARTH', url: 'https://images-assets.nasa.gov/image/PIA18033/PIA18033~medium.jpg' },
        { id: 'p5', title: 'LUNAR TERMINATOR', date: 'GALILEO', url: 'https://images-assets.nasa.gov/image/PIA00405/PIA00405~medium.jpg' },

        // REEL 03: DEEP FIELD
        { id: 'd1', title: 'ANDROMEDA GALAXY', date: 'GALEX', url: 'https://images-assets.nasa.gov/image/PIA15416/PIA15416~medium.jpg' },
        { id: 'd2', title: 'MILKY WAY CORE', date: 'CHANDRA', url: 'https://images-assets.nasa.gov/image/PIA12348/PIA12348~medium.jpg' },
        { id: 'd3', title: 'BLACK HOLE VIZ', date: 'SIM', url: 'https://images-assets.nasa.gov/image/PIA23465/PIA23465~medium.jpg' },
        { id: 'd4', title: 'WESTERLUND CLUSTER', date: 'HUBBLE', url: 'https://images-assets.nasa.gov/image/PIA19343/PIA19343~medium.jpg' },
        { id: 'd5', title: 'CRAB NEBULA', date: 'X-RAY', url: 'https://images-assets.nasa.gov/image/PIA03606/PIA03606~medium.jpg' },

        // REEL 04: HUMAN EXPLORATION
        { id: 'h1', title: 'THE UNTETHERED', date: '1984', url: 'https://images-assets.nasa.gov/image/s84-27017/s84-27017~medium.jpg' },
        { id: 'h2', title: 'SPACE STATION', date: 'ISS', url: 'https://images-assets.nasa.gov/image/iss056e201262/iss056e201262~medium.jpg' },
        { id: 'h3', title: 'ATLANTIS LAUNCH', date: 'STS-135', url: 'https://images-assets.nasa.gov/image/KSC-2011-4835/KSC-2011-4835~medium.jpg' },
        { id: 'h4', title: 'CREW DRAGON', date: 'SPACEX', url: 'https://images-assets.nasa.gov/image/nhq202005300045/nhq202005300045~medium.jpg' },
        { id: 'h5', title: 'ARTEMIS EARTHRISE', date: 'ORION', url: 'https://images-assets.nasa.gov/image/art001e000672/art001e000672~medium.jpg' }
    ];

    // Chunk slides into "Reels" of 5
    function chunkArray(arr: any[], size: number) {
        return Array.from({ length: Math.ceil(arr.length / size) }, (v, i) =>
            arr.slice(i * size, i * size + size)
        );
    }

    const chunks = chunkArray(NASA_ARCHIVE, 5);
    const ARCHIVE = chunks.map((slides, i) => ({
        id: `REEL-${i}`,
        label: `REEL 0${i + 1}`,
        // Color coding the reels: Green(Nebula), Amber(Planets), Blue(Deep Space), Pink(Human)
        color: ['#10b981', '#f59e0b', '#3b82f6', '#ec4899'][i % 4], 
        slides: slides
    }));

    // --- 2. STATE ---
    let activeCartridge = $state<any>(null);
    let slideIndex = $state(0);
    let isProjectorOn = $state(false);
    let isTransitioning = $state(false);
    
    // ThreeJS References
    let canvasContainer: HTMLElement;
    let scene: THREE.Scene;
    let camera: THREE.PerspectiveCamera;
    let renderer: THREE.WebGLRenderer;
    let starSystem: THREE.Points;
    let cloudSystem: THREE.Group;
    let frameId: number;

    // --- 3. THREE.JS COSMIC ENGINE ---
    onMount(() => {
        initThreeJS();
        animate();
        window.addEventListener('resize', onResize);
    });

    onDestroy(() => {
        if (typeof window !== 'undefined') {
            window.removeEventListener('resize', onResize);
            cancelAnimationFrame(frameId);
            renderer?.dispose();
        }
    });

    function initThreeJS() {
        scene = new THREE.Scene();
        // Fog for depth
        scene.fog = new THREE.FogExp2(0x000000, 0.001);

        camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 1, 1000);
        camera.position.z = 1;
        camera.rotation.x = 1.16;
        camera.rotation.y = -0.12;
        camera.rotation.z = 0.27;

        renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        canvasContainer.appendChild(renderer.domElement);

        // A. STARS
        const starGeo = new THREE.BufferGeometry();
        const starCount = 6000;
        const positions = new Float32Array(starCount * 3);
        const velocities = []; // Store velocity for warp effect

        for(let i=0; i<starCount; i++) {
            positions[i*3] = (Math.random() - 0.5) * 600;
            positions[i*3+1] = (Math.random() - 0.5) * 600;
            positions[i*3+2] = (Math.random() - 0.5) * 600;
            velocities.push(0);
        }
        
        starGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        const starMat = new THREE.PointsMaterial({
            color: 0xffffff,
            size: 0.7,
            transparent: true,
            opacity: 0.8
        });
        starSystem = new THREE.Points(starGeo, starMat);
        scene.add(starSystem);

        // B. NEBULA CLOUDS (Procedural Texture)
        cloudSystem = new THREE.Group();
        const cloudTexture = createCloudTexture();
        const cloudGeo = new THREE.PlaneGeometry(500, 500);
        
        // Add multiple cloud layers with different cosmic colors
        const colors = [0x6366f1, 0xec4899, 0x10b981, 0x3b82f6]; // Indigo, Pink, Emerald, Blue

        for(let p=0; p<15; p++) {
            const material = new THREE.MeshLambertMaterial({
                map: cloudTexture,
                transparent: true,
                opacity: 0.15, // Very subtle
                color: colors[p % colors.length],
                depthWrite: false,
                blending: THREE.AdditiveBlending
            });
            const cloud = new THREE.Mesh(cloudGeo, material);
            cloud.position.set(
                Math.random()*800 - 400,
                Math.random()*800 - 400,
                Math.random()*800 - 600 // Push them back
            );
            cloud.rotation.z = Math.random() * 2 * Math.PI;
            (cloud as any).rotationSpeed = Math.random() * 0.002 - 0.001; // Custom property
            cloudSystem.add(cloud);
        }
        scene.add(cloudSystem);

        // Ambient Light for clouds
        const ambient = new THREE.AmbientLight(0x555555);
        scene.add(ambient);
        
        // Directional Light (The "Sun")
        const directionalLight = new THREE.DirectionalLight(0xff8c19);
        directionalLight.position.set(0,0,1);
        scene.add(directionalLight);
    }

    // Generate a smoke texture in memory (No assets needed!)
    function createCloudTexture() {
        const canvas = document.createElement('canvas');
        canvas.width = 32; canvas.height = 32;
        const context = canvas.getContext('2d');
        if(!context) return new THREE.Texture();

        const gradient = context.createRadialGradient(16, 16, 0, 16, 16, 16);
        gradient.addColorStop(0, 'rgba(255,255,255,1)');
        gradient.addColorStop(1, 'rgba(255,255,255,0)');
        context.fillStyle = gradient;
        context.fillRect(0,0,32,32);

        const texture = new THREE.Texture(canvas);
        texture.needsUpdate = true;
        return texture;
    }

    function onResize() {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    }

    function animate() {
        // Rotate Stars
        starSystem.rotation.y -= 0.0005;
        
        // Warp Effect logic (if transitioning)
        const positions = starSystem.geometry.attributes.position.array as Float32Array;
        for(let i=0; i<positions.length; i+=3) {
            // Slight movement towards camera
            positions[i+2] += 0.1;
            if (positions[i+2] > 200) positions[i+2] = -200;
        }
        starSystem.geometry.attributes.position.needsUpdate = true;

        // Rotate Clouds
        cloudSystem.children.forEach((cloud: any) => {
            cloud.rotation.z += cloud.rotationSpeed;
        });

        renderer.render(scene, camera);
        frameId = requestAnimationFrame(animate);
    }

    // --- ACTIONS ---
    function loadCartridge(cart: any) {
        activeCartridge = cart;
        slideIndex = 0;
        isProjectorOn = true;
        // Warp speed effect could be added here by modifying star velocity
    }

    function ejectCartridge() {
        isProjectorOn = false;
        setTimeout(() => { activeCartridge = null; }, 500);
    }

    function nextSlide() {
        if (!activeCartridge || isTransitioning) return;
        triggerTransition(() => {
            slideIndex = (slideIndex + 1) % activeCartridge.slides.length;
        });
    }

    function prevSlide() {
        if (!activeCartridge || isTransitioning) return;
        triggerTransition(() => {
            slideIndex = (slideIndex - 1 + activeCartridge.slides.length) % activeCartridge.slides.length;
        });
    }

    function triggerTransition(callback: () => void) {
        isTransitioning = true;
        // Simulate projector "Dark" phase
        setTimeout(() => callback(), 150);
        setTimeout(() => isTransitioning = false, 300);
    }

    function handleKey(e: KeyboardEvent) {
        if (!isProjectorOn) return;
        if (e.key === 'ArrowRight' || e.key === ' ') nextSlide();
        if (e.key === 'ArrowLeft') prevSlide();
        if (e.key === 'Escape') ejectCartridge();
    }
</script>

<svelte:window onkeydown={handleKey} />
<svelte:head><title>Cosmic Studio</title></svelte:head>

<div class="three-canvas" bind:this={canvasContainer}></div>

<div class="studio-ui">

    {#if !isProjectorOn}
        <div class="shelf-container" in:fade>
            <h1 class="shelf-title">
                <span class="neon-text">COSMIC ARCHIVE</span>
            </h1>
            
            <div class="cartridge-grid">
                {#each ARCHIVE as cart, i}
                    <button 
                        class="cartridge-box"
                        style="--accent: {cart.color}"
                        onclick={() => loadCartridge(cart)}
                        in:fly={{ y: 50, delay: i * 100, easing: elasticOut }}
                    >
                        <div class="energy-core"></div>
                        <div class="holo-label">
                            <span class="label-text">{cart.label}</span>
                            <span class="count">{cart.slides.length} SLIDES</span>
                        </div>
                    </button>
                {/each}
            </div>
            
            <a href="/" class="exit-btn">ABORT SIMULATION</a>
        </div>
    {/if}

    {#if isProjectorOn && activeCartridge}
        <div class="projector-scene" transition:fade={{ duration: 1000 }}>
            
            <div class="holo-screen">
                {#if !isTransitioning}
                    <div class="projector-beam"></div>
                    
                    <div class="slide-wrapper" in:scale={{ start: 0.9, duration: 400, easing: elasticOut }}>
                        <img 
                            src={activeCartridge.slides[slideIndex].url} 
                            alt="Slide" 
                            class="projected-img"
                        />
                        <div class="hex-grid"></div>
                        <div class="scanline"></div>
                    </div>
                    
                    <div class="slide-info">
                        <h2>{activeCartridge.slides[slideIndex].title}</h2>
                        <div class="meta">
                            <span class="pill" style="border-color: {activeCartridge.color}">
                                {activeCartridge.slides[slideIndex].date}
                            </span>
                            <span class="pill">{slideIndex + 1} / {activeCartridge.slides.length}</span>
                        </div>
                    </div>
                {:else}
                    <div class="warp-flash"></div>
                {/if}
            </div>

            <div class="glass-dock">
                <button class="dock-btn eject" onclick={ejectCartridge}>⏏</button>
                <div class="nav-cluster">
                    <button class="dock-btn" onclick={prevSlide}>◀</button>
                    <div class="dots">
                        {#each activeCartridge.slides as _, i}
                            <div class="dot {i === slideIndex ? 'active' : ''}" style="background-color: {i === slideIndex ? activeCartridge.color : '#555'}"></div>
                        {/each}
                    </div>
                    <button class="dock-btn" onclick={nextSlide}>▶</button>
                </div>
            </div>

        </div>
    {/if}

</div>

<style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700;900&display=swap');

    /* --- LAYOUT --- */
    .three-canvas {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: radial-gradient(circle at bottom, #111827 0%, #000000 100%);
        z-index: 0;
    }

    .studio-ui {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        z-index: 10;
        display: flex; justify-content: center; align-items: center;
        font-family: 'Rajdhani', sans-serif;
        color: #fff;
    }

    /* --- SHELF --- */
    .shelf-container { text-align: center; }
    
    .shelf-title {
        font-size: 4rem; letter-spacing: 10px; margin-bottom: 60px;
        text-shadow: 0 0 20px rgba(100, 200, 255, 0.5);
    }
    .neon-text { font-weight: 900; background: linear-gradient(to right, #fff, #a5f3fc); -webkit-background-clip: text; color: transparent; }

    .cartridge-grid { display: flex; gap: 40px; justify-content: center; flex-wrap: wrap; }

    .cartridge-box {
        width: 160px; height: 220px;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        cursor: pointer; position: relative;
        backdrop-filter: blur(10px);
        transition: 0.4s;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }
    .cartridge-box:hover {
        transform: translateY(-20px) scale(1.05);
        border-color: var(--accent);
        box-shadow: 0 0 40px var(--accent);
    }

    .energy-core {
        width: 60px; height: 60px; border-radius: 50%;
        background: radial-gradient(circle, var(--accent) 0%, transparent 70%);
        opacity: 0.5; filter: blur(10px);
        animation: pulse 2s infinite alternate;
    }

    .holo-label { margin-top: 20px; display: flex; flex-direction: column; align-items: center; }
    .label-text { font-size: 1.5rem; font-weight: 700; color: #fff; text-shadow: 0 0 10px var(--accent); }
    .count { font-size: 0.8rem; color: #aaa; letter-spacing: 2px; margin-top: 5px; }

    .exit-btn {
        display: inline-block; margin-top: 60px;
        color: #ef4444; text-decoration: none; border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 10px 30px; border-radius: 30px; font-weight: 700; letter-spacing: 2px;
        transition: 0.2s; backdrop-filter: blur(5px);
    }
    .exit-btn:hover { background: rgba(239, 68, 68, 0.2); box-shadow: 0 0 20px #ef4444; }

    /* --- PROJECTOR MODE --- */
    .projector-scene {
        width: 100%; height: 100%;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
    }

    .holo-screen {
        width: 80vw; max-width: 1200px;
        aspect-ratio: 16/9;
        position: relative;
        display: flex; justify-content: center; align-items: center;
    }

    /* The "Beam" coming from camera direction */
    .projector-beam {
        position: absolute; width: 100%; height: 100%;
        background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 60%);
        filter: blur(20px); pointer-events: none;
    }

    .slide-wrapper {
        width: 100%; height: 100%;
        border-radius: 12px; overflow: hidden;
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 0 50px rgba(0,100,255,0.1);
        position: relative;
    }
    .projected-img {
        width: 100%; height: 100%; object-fit: contain;
        /* Sci-fi tint */
        filter: contrast(1.1) brightness(1.1) saturate(1.2); 
    }

    .hex-grid {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background-image: url("data:image/svg+xml,%3Csvg width='20' height='20' viewBox='0 0 20 20' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M10 0L20 10L10 20L0 10Z' fill='none' stroke='rgba(255,255,255,0.05)' stroke-width='1'/%3E%3C/svg%3E");
        pointer-events: none;
    }
    .scanline {
        position: absolute; top: 0; left: 0; width: 100%; height: 10px;
        background: linear-gradient(to bottom, transparent, rgba(255,255,255,0.2), transparent);
        animation: scan 5s linear infinite; pointer-events: none;
    }

    .slide-info {
        position: absolute; bottom: -80px; left: 0;
        width: 100%; display: flex; justify-content: space-between; align-items: center;
    }
    .slide-info h2 {
        font-size: 2.5rem; margin: 0; letter-spacing: 2px;
        text-shadow: 0 0 20px rgba(255,255,255,0.5);
    }
    .meta { display: flex; gap: 15px; }
    .pill {
        background: rgba(255,255,255,0.1); padding: 5px 15px;
        border-radius: 20px; border: 1px solid rgba(255,255,255,0.2);
        font-size: 1rem;
    }

    .warp-flash {
        width: 100%; height: 100%; background: #fff;
        mix-blend-mode: overlay; opacity: 0.5;
    }

    /* --- DOCK --- */
    .glass-dock {
        position: fixed; bottom: 40px;
        background: rgba(0,0,0,0.5); backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.1);
        padding: 15px 40px; border-radius: 60px;
        display: flex; gap: 40px; align-items: center;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    }

    .dock-btn {
        background: transparent; border: none; color: #fff;
        font-size: 1.5rem; cursor: pointer; opacity: 0.7; transition: 0.2s;
    }
    .dock-btn:hover { opacity: 1; transform: scale(1.2); text-shadow: 0 0 10px #fff; }
    
    .nav-cluster { display: flex; align-items: center; gap: 20px; }
    .dots { display: flex; gap: 8px; }
    .dot { width: 6px; height: 6px; border-radius: 50%; transition: 0.3s; }
    .dot.active { transform: scale(1.5); box-shadow: 0 0 10px currentColor; }

    @keyframes pulse { from { opacity: 0.3; transform: scale(0.9); } to { opacity: 0.6; transform: scale(1.1); } }
    @keyframes scan { 0% { top: -10%; } 100% { top: 110%; } }
</style>