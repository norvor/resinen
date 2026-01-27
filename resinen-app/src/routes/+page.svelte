<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    // --- STATE ---
    let planetary = $state<any>(null);
    let visuals = $state<any>(null);
    let feeds = $state<any>(null);
    let zen = $state<any>(null);
    let system = $state<any[]>([]);
    let loading = $state(true);
    let refreshTimer: any;

    // --- PREMIUM STATE ---
    let isPremium = $state(false);

    // --- HELPER: CHECK AUTH ---
    // This runs on mount AND whenever the layout says "Auth Changed"
    function checkPremiumStatus() {
        if (typeof localStorage !== 'undefined') {
            const user = JSON.parse(localStorage.getItem('resinen_user') || 'null');
            // If user exists AND has is_premium flag
            isPremium = (user && user.is_premium) === true;
        } else {
            isPremium = false;
        }
    }

    // --- POMODORO ---
    let timerSeconds = $state(1500); let timerRunning = $state(false); let timerMode = $state('focus'); let timerInterval: any;
    function formatTime(s: number) { const m = Math.floor(s/60).toString().padStart(2,'0'); const sec = (s%60).toString().padStart(2,'0'); return `${m}:${sec}`; }
    function setTimerMode(m: string) { timerMode = m; timerRunning = false; clearInterval(timerInterval); timerSeconds = m === 'focus' ? 1500 : m === 'short' ? 300 : 900; }
    function toggleTimer() { if (timerRunning) { clearInterval(timerInterval); timerRunning = false; } else { timerRunning = true; timerInterval = setInterval(() => { if(timerSeconds>0) timerSeconds--; else { clearInterval(timerInterval); timerRunning = false; } }, 1000); } }

    // --- WIDGETS ---
    let noteContent = $state("");
    function saveNotes() { if(typeof localStorage !== 'undefined') localStorage.setItem('resinen_notes', noteContent); }
    
    let todoInput = $state("");
    let todos = $state<{text: string, done: boolean}[]>([]);
    function addTodo() { if (!todoInput.trim()) return; todos = [...todos, { text: todoInput, done: false }]; todoInput = ""; saveTodos(); }
    function toggleTodo(i: number) { todos[i].done = !todos[i].done; saveTodos(); }
    function removeTodo(i: number) { todos = todos.filter((_, idx) => idx !== i); saveTodos(); }
    function saveTodos() { if(typeof localStorage !== 'undefined') localStorage.setItem('resinen_todos', JSON.stringify(todos)); }

    // --- DATA & INIT ---
    const API = "https://api.resinen.com/dashboard";
    
    async function fetchAll() {
        const t = Date.now();
        try {
            const [p, v, f, z, s] = await Promise.all([
                fetch(`${API}/planetary`), fetch(`${API}/visuals?t=${t}`), fetch(`${API}/feeds?t=${t}`),
                fetch(`${API}/zen?t=${t}`), fetch(`${API}/system`)
            ]);
            planetary = await p.json(); visuals = await v.json(); feeds = await f.json();
            zen = await z.json(); system = await s.json();
        } catch (e) { console.error("Dashboard Sync Failed", e); }
    }

    function triggerPay() {
        alert("🔒 PREMIUM FEATURE LOCKED\n\nClick the pulsing 'UPGRADE' button in the top dock to Initialize Payment.");
    }

    onMount(async () => { 
        try { 
            // 1. Initial Check
            checkPremiumStatus();

            // 2. Listen for Login/Logout events from Layout
            window.addEventListener('resinen-auth-change', checkPremiumStatus);

            // 3. Load Widget Data
            if (typeof localStorage !== 'undefined') {
                const savedNote = localStorage.getItem('resinen_notes');
                if (savedNote) noteContent = savedNote;
                const savedTodos = localStorage.getItem('resinen_todos');
                if (savedTodos) todos = JSON.parse(savedTodos);
            }

            // 4. Fetch Data
            await fetchAll(); 
            refreshTimer = setInterval(fetchAll, 300000);
        } 
        catch (e) { console.error(e); } 
        finally { loading = false; } 
    });
    
    onDestroy(() => { 
        clearInterval(refreshTimer); 
        clearInterval(timerInterval);
        if (typeof window !== 'undefined') {
            window.removeEventListener('resinen-auth-change', checkPremiumStatus);
        }
    });
</script>

<svelte:head>
    <title>Resinen // Life Command</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Space+Grotesk:wght@400;700&display=swap" rel="stylesheet">
</svelte:head>

<div class="app-wrapper">
    <div class="bg-layer stars"></div>
    <div class="bg-layer aurora"></div>

    <div class="holy-grail-dock">
        <a href="/apps/cinema" class="grail-rune" title="Cinema">🎬</a>
        <a href="/games/chess" class="grail-rune" title="Chess">♟️</a>
        <a href="/games/poker" class="grail-rune" title="Poker">♠️</a>
        <a href="/games/go" class="grail-rune" title="Go">⚪</a>
        <a href="/games/tetris" class="grail-rune" title="Tetris">🕹️</a>
        <a href="/games/sudoku" class="grail-rune" title="Sudoku">🔢</a>
        <a href="/games/ludo" class="grail-rune" title="Ludo">🎲</a>
        <a href="/games/minesweeper" class="grail-rune" title="Minesweeper">💣</a>
        <a href="/games/snake" class="grail-rune" title="Snake">🐍</a>
        <a href="/games/saataath" class="grail-rune" title="Saat Aath">🃏</a>
        <a href="/games/runner" class="grail-rune" title="Runner">🏃</a>
        <a href="/games/2048" class="grail-rune" title="2048">🧱</a>
        <a href="/games/battleship" class="grail-rune" title="Battleship">🚢</a>
    </div>

    <div class="system-bar">
        <span class="sys-label">SYS:</span>{#each system as sys}<div class="sys-item"><span class="sys-dot"></span>{sys.name}</div>{/each}
        <div class="spacer"></div><div class="date">{new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}</div>
    </div>

    <div class="layout">
        <header class="masthead">
            <div class="brand"><h1>RESINEN</h1><div class="sub">PASSIVE LIFE COMMAND</div></div>
            <div class="zen-header">
                {#if zen}<div class="zen-text">"{zen.text}"</div>{:else}<div class="zen-text">...</div>{/if}
            </div>
        </header>

        {#if loading}
            <div class="loading">ESTABLISHING GLOBAL UPLINK...</div>
        {:else}
            <div class="grid">
                
                <section class="col">
                    <div class="card hero"><div class="head">YUMMY</div>{#if visuals?.food}<div class="img-frame" style="background-image: url({visuals.food})"></div>{/if}</div>
                    <div class="card animal-card">
                        <div class="head">COMPANION LINK</div>
                        {#if visuals?.animal}
                            <div class="animal-frame"><img src={visuals.animal.url} alt="Animal" /><div class="animal-tag">DETECTED: {visuals.animal.type}</div></div>
                        {/if}
                    </div>
                    <div class="card news">
                        <div class="head">UPLIFTING</div>
                        {#if feeds?.uplifting}{#each feeds.uplifting as n}<a href={n.url} target="_blank" class="news-item">★ {n.title}</a>{/each}{/if}
                    </div>
                    {#if feeds?.joke}<div class="card joke"><div class="head">HUMOR</div><div class="joke-text"><p>Q: {feeds.joke.setup}</p><p class="punch">A: {feeds.joke.punchline}</p></div></div>{/if}
                </section>

                <section class="col">
                    <div class="card sticky">
                        <div class="head">NOTES {#if !isPremium}🔒{/if}</div>
                        {#if isPremium}
                            <textarea bind:value={noteContent} oninput={saveNotes} placeholder="Type your thoughts..."></textarea>
                        {:else}
                            <div class="locked-widget" onclick={triggerPay}>
                                <div class="lock-icon">🔒</div>
                                <div class="lock-text">PREMIUM FEATURE</div>
                            </div>
                        {/if}
                    </div>

                    <div class="card todo">
                        <div class="head">TASKS {#if !isPremium}🔒{/if}</div>
                        {#if isPremium}
                            <div class="todo-input-row">
                                <input type="text" bind:value={todoInput} onkeydown={(e) => e.key === 'Enter' && addTodo()} placeholder="Add task..." />
                                <button onclick={addTodo}>+</button>
                            </div>
                            <div class="todo-list">
                                {#each todos as todo, i}
                                    <div class="todo-item" class:done={todo.done}>
                                        <span onclick={() => toggleTodo(i)}>{todo.text}</span><button onclick={() => removeTodo(i)}>×</button>
                                    </div>
                                {/each}
                            </div>
                        {:else}
                            <div class="locked-widget" onclick={triggerPay}>
                                <div class="lock-icon">🔒</div>
                                <div class="lock-text">PREMIUM FEATURE</div>
                            </div>
                        {/if}
                    </div>

                    <div class="card timer">
                        <div class="head">POMODORO {#if !isPremium}🔒{/if}</div>
                        {#if isPremium}
                            <div class="time">{formatTime(timerSeconds)}</div>
                            <div class="timer-modes">
                                <button class:active={timerMode === 'focus'} onclick={() => setTimerMode('focus')}>Focus</button>
                                <button class:active={timerMode === 'short'} onclick={() => setTimerMode('short')}>Short</button>
                                <button class:active={timerMode === 'long'} onclick={() => setTimerMode('long')}>Long</button>
                            </div>
                            <div class="ctrls"><button class="main-btn" onclick={toggleTimer}>{timerRunning ? 'PAUSE' : 'START'}</button></div>
                        {:else}
                            <div class="locked-widget" onclick={triggerPay}>
                                <div class="lock-icon">🔒</div>
                                <div class="lock-text">PREMIUM FEATURE</div>
                            </div>
                        {/if}
                    </div>

                    <div class="card markets">
                        <div class="head">MARKETS</div>
                        {#if feeds?.markets}
                            <div class="ticker-row">
                                {#each feeds.markets as m}
                                    <div class="tick"><span class="label">{m.name}</span><span class="val">${m.price}</span><span class="chg" class:pos={!m.change.includes('-')} class:neg={m.change.includes('-')}>{m.change}</span></div>
                                {/each}
                            </div>
                        {/if}
                    </div>

                    <div class="clock-row">
                        {#if planetary}{#each planetary.watch as c}<div class="clock"><span class="city">{c.city}</span><span class="t">{c.time}</span><span class="w">{c.icon}</span></div>{/each}{/if}
                    </div>
                </section>

                <section class="col">
                    {#if visuals?.world}
                        <div class="card world" style="background-image: url({visuals.world.url})">
                            <div class="overlay"><div class="head">WORLD VIEW</div><h2>{visuals.world.title}</h2></div>
                        </div>
                    {/if}
                    <div class="card sports">
                        <div class="head">GLOBAL SPORTS</div>
                        <div class="sports-list">
                            {#if feeds?.sports}{#each feeds.sports as s}<a href={s.link} target="_blank" class="sports-item"><span class="sport-icon">⚽</span><span class="sport-title">{s.title}</span></a>{/each}{/if}
                        </div>
                    </div>
                    <div class="card history">
                        <div class="head">TIME CAPSULE</div>
                        {#if feeds?.history}<div class="hist-content"><div class="hist-year">{feeds.history.year}</div><div class="hist-text">{feeds.history.text}</div></div>{/if}
                    </div>
                </section>

            </div>
        {/if}
    </div>
</div>

<style>
    :global(body) { 
        margin: 0; 
        background-color: #020617; 
        color: #f8fafc; 
        font-family: 'Space Grotesk', sans-serif; 
        overflow-x: hidden; 
        overflow-y: auto !important;
    }
    
    h1, h2, span, div, a { color: inherit; text-decoration: none; box-sizing: border-box; }
    :root { --accent: #2dd4bf; --card: rgba(30, 41, 59, 0.7); --border: #334155; --mono: 'JetBrains Mono', monospace; }

    .app-wrapper { min-height: 100vh; position: relative; padding-bottom: 100px; }
    .stars { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; background: radial-gradient(#fff 1px, transparent 1px); background-size: 50px 50px; opacity: 0.1; }
    .aurora { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; background: radial-gradient(circle at 50% -10%, #4c1d95, transparent 60%); opacity: 0.3; filter: blur(80px); }
    
    .layout { position: relative; z-index: 1; max-width: 1600px; margin: 0 auto; padding: 20px; }
    
    /* RESPONSIVE GRID */
    .grid { display: grid; grid-template-columns: 300px 1fr 300px; gap: 2rem; }
    .col { display: flex; flex-direction: column; gap: 1.5rem; }

    @media (max-width: 1024px) {
        .grid { grid-template-columns: 1fr 1fr; }
        .col:nth-child(3) { grid-column: span 2; display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
    }
    @media (max-width: 768px) {
        .layout { padding: 10px; }
        .grid { display: flex; flex-direction: column; gap: 1rem; }
        .col { width: 100%; }
        .col:nth-child(3) { display: flex; flex-direction: column; }
        .masthead { flex-direction: column; text-align: center; gap: 1rem; }
        .zen-header { text-align: center; max-width: 100%; }
    }

    /* LOCKED WIDGET STYLE */
    .locked-widget {
        height: 150px; display: flex; flex-direction: column; justify-content: center; align-items: center;
        cursor: pointer; background: rgba(0,0,0,0.3); transition: 0.2s; border-radius: 8px;
    }
    .locked-widget:hover { background: rgba(239, 68, 68, 0.1); }
    .lock-icon { font-size: 2rem; margin-bottom: 10px; }
    .lock-text { font-family: 'JetBrains Mono'; color: #ef4444; font-size: 0.8rem; letter-spacing: 2px; }

    /* DOCK */
    .holy-grail-dock {
        position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
        background: rgba(15, 23, 42, 0.95); border: 1px solid var(--border);
        border-radius: 50px; padding: 10px 20px;
        display: flex; gap: 15px; z-index: 1000;
        box-shadow: 0 10px 40px rgba(0,0,0,0.6);
        backdrop-filter: blur(12px);
        max-width: 90vw; overflow-x: auto; white-space: nowrap;
        -webkit-overflow-scrolling: touch; scrollbar-width: none;
    }
    .holy-grail-dock::-webkit-scrollbar { display: none; }
    .grail-rune { font-size: 1.5rem; text-decoration: none; transition: transform 0.2s; filter: grayscale(100%); opacity: 0.7; flex-shrink: 0; }
    .grail-rune:hover { transform: scale(1.2) translateY(-5px); filter: grayscale(0%); opacity: 1; }

    .masthead { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 2rem; margin-bottom: 2rem; }
    .brand h1 { font-size: clamp(2rem, 5vw, 3rem); margin: 0; line-height: 1; letter-spacing: -2px; text-shadow: 0 0 10px var(--accent); }
    .sub { font-family: var(--mono); color: var(--accent); font-size: 0.7rem; letter-spacing: 2px; }

    .zen-header { text-align: right; max-width: 300px; margin-left: auto; }
    .zen-text { font-family: var(--mono); font-style: italic; color: #cbd5e1; font-size: 0.85rem; line-height: 1.4; border-right: 2px solid var(--accent); padding-right: 15px; }

    .card { background: var(--card); border: 1px solid var(--border); border-radius: 8px; overflow: hidden; backdrop-filter: blur(10px); transition: border-color 0.2s; }
    .card:hover { border-color: var(--accent); }
    .head { padding: 8px 12px; font-family: var(--mono); font-size: 0.65rem; color: var(--accent); border-bottom: 1px solid var(--border); background: rgba(0,0,0,0.2); }
    .img-frame { height: 180px; background-size: cover; background-position: center; }

    .animal-frame { padding: 10px; position: relative; }
    .animal-frame img { width: 100%; border-radius: 4px; display: block; border: 1px solid var(--border); }
    .animal-tag { position: absolute; bottom: 15px; left: 15px; background: #000; color: var(--accent); padding: 2px 6px; font-size: 0.6rem; font-family: var(--mono); border: 1px solid var(--accent); }

    .world { height: 250px; background-size: cover; display: flex; align-items: flex-end; }
    .overlay { width: 100%; background: linear-gradient(to top, #000, transparent); padding: 15px; }
    .world h2 { margin: 0; font-size: 1.2rem; text-shadow: 0 2px 4px #000; }

    .sticky textarea { width: 100%; height: 150px; background: transparent; border: none; color: #fff; padding: 10px; font-family: var(--mono); font-size: 0.8rem; resize: none; outline: none; }
    
    .todo-input-row { display: flex; border-bottom: 1px solid var(--border); }
    .todo-input-row input { flex: 1; background: transparent; border: none; padding: 8px 12px; color: #fff; font-family: var(--mono); font-size: 0.8rem; outline: none; }
    .todo-input-row button { background: var(--accent); border: none; color: #000; font-weight: bold; width: 30px; cursor: pointer; }
    .todo-list { max-height: 150px; overflow-y: auto; }
    .todo-item { display: flex; justify-content: space-between; padding: 8px 12px; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 0.8rem; }
    .todo-item span { cursor: pointer; flex: 1; }
    .todo-item.done span { text-decoration: line-through; opacity: 0.5; color: var(--accent); }
    .todo-item button { background: none; border: none; color: #ef4444; cursor: pointer; font-weight: bold; }

    .news { padding: 10px; }
    .news-item { display: block; font-size: 0.8rem; margin-bottom: 8px; color: #cbd5e1; transition: color 0.2s; line-height: 1.3; }
    .news-item:hover { color: var(--accent); }

    .timer { text-align: center; padding-bottom: 15px; }
    .time { font-family: var(--mono); font-size: 3rem; font-weight: bold; margin: 10px 0; letter-spacing: 2px; text-shadow: 0 0 15px var(--accent); }
    .timer-modes { display: flex; justify-content: center; gap: 5px; margin-bottom: 15px; }
    .timer-modes button { background: transparent; border: 1px solid var(--border); color: #94a3b8; font-size: 0.7rem; padding: 2px 8px; cursor: pointer; }
    .timer-modes button.active { border-color: var(--accent); color: var(--accent); }
    .ctrls .main-btn { background: var(--accent); color: #000; border: none; font-weight: bold; padding: 8px 30px; font-family: var(--mono); cursor: pointer; border-radius: 4px; }

    .ticker-row { display: flex; justify-content: space-between; padding: 15px; flex-wrap: wrap; gap: 10px; }
    .tick { display: flex; flex-direction: column; align-items: center; min-width: 60px; }
    .tick .label { font-family: var(--mono); font-size: 0.65rem; color: #94a3b8; }
    .tick .val { color: #fff; font-weight: bold; font-size: 0.9rem; }
    .tick .chg { font-size: 0.7rem; }
    .pos { color: #4ade80; } .neg { color: #ef4444; }

    .clock-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(60px, 1fr)); gap: 5px; background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 10px; text-align: center; }
    .clock .city { font-size: 0.6rem; color: #94a3b8; font-family: var(--mono); display: block; }
    .clock .t { font-weight: bold; display: block; font-size: 1rem; }

    .sports-list { padding: 10px; }
    .sports-item { display: flex; gap: 10px; margin-bottom: 12px; align-items: flex-start; transition: 0.2s; }
    .sports-item:hover { color: var(--accent); transform: translateX(5px); }
    .sport-icon { font-size: 1rem; }
    .sport-title { font-size: 0.85rem; line-height: 1.3; }

    .hist-content { padding: 15px; text-align: center; }
    .hist-year { font-family: var(--mono); font-size: 2rem; font-weight: bold; color: var(--accent); margin-bottom: 5px; }
    .hist-text { font-size: 0.9rem; line-height: 1.4; color: #cbd5e1; }

    .joke { padding: 15px; font-size: 0.9rem; line-height: 1.4; }
    .punch { margin-top: 5px; color: var(--accent); font-weight: bold; }

    .system-bar { display: flex; flex-wrap: wrap; gap: 15px; font-family: var(--mono); font-size: 0.7rem; background: rgba(0,0,0,0.5); padding: 5px 20px; border-bottom: 1px solid var(--border); }
    .sys-dot { width: 6px; height: 6px; background: var(--accent); border-radius: 50%; display: inline-block; margin-right: 5px; box-shadow: 0 0 5px var(--accent); }
    .spacer { flex: 1; }
    .loading { height: 80vh; display: flex; justify-content: center; align-items: center; color: var(--accent); font-family: var(--mono); letter-spacing: 2px; }
</style>