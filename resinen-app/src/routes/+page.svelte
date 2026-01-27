<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import logo from '$lib/assets/logo.svg'; // <--- Add this line

    // --- STATE ---
    let planetary = $state<any>(null);
    let visuals = $state<any>(null);
    let feeds = $state<any>(null);
    let zen = $state<any>(null);
    let system = $state<any[]>([]);
    let loading = $state(true);
    let refreshTimer: any;

    // --- THEME STATE ---
    let theme = $state('night'); // 'night', 'sunrise', 'beach'
    function setTheme(t: string) { theme = t; }

    // --- TOP DOCK STATE ---
    let topDockCollapsed = $state(false);
    function toggleTopDock() { topDockCollapsed = !topDockCollapsed; }

    // --- SEARCH STATE ---
    let searchQuery = $state("");
    let searchEngine = $state("google"); 
    function handleSearch() {
        if (!searchQuery.trim()) return;
        const q = encodeURIComponent(searchQuery);
        let url = searchEngine === 'news' ? `https://www.google.com/search?tbm=nws&q=${q}` :
                  searchEngine === 'youtube' ? `https://www.youtube.com/results?search_query=${q}` :
                  `https://www.google.com/search?q=${q}`;
        window.open(url, '_blank');
    }

    // --- ART GALLERY STATE ---
    let artMode = $state('met');
    let artLoading = $state(false);

    // --- PREMIUM STATE ---
    let isPremium = $state(false);
    function checkPremiumStatus() {
        if (typeof localStorage !== 'undefined') {
            const user = JSON.parse(localStorage.getItem('resinen_user') || 'null');
            isPremium = (user && user.is_premium) === true;
        } else { isPremium = false; }
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
    
    async function fetchVisuals() {
        artLoading = true;
        try {
            const t = Date.now();
            const res = await fetch(`${API}/visuals?t=${t}&art_source=${artMode}`);
            visuals = await res.json();
        } catch(e) { console.error(e); }
        finally { artLoading = false; }
    }

    function toggleArtMode() { artMode = artMode === 'met' ? 'aic' : 'met'; fetchVisuals(); }
    function triggerPay() { alert("🔒 PREMIUM FEATURE LOCKED\n\nClick the pulsing 'UPGRADE' button in the global dock to Initialize Payment."); }

    async function fetchAll() {
        const t = Date.now();
        try {
            const [p, f, z, s] = await Promise.all([
                fetch(`${API}/planetary`), fetch(`${API}/feeds?t=${t}`), fetch(`${API}/zen?t=${t}`), fetch(`${API}/system`)
            ]);
            await fetchVisuals();
            planetary = await p.json(); feeds = await f.json(); zen = await z.json(); system = await s.json();
        } catch (e) { console.error("Dashboard Sync Failed", e); }
    }

    onMount(async () => { 
        try { 
            checkPremiumStatus();
            window.addEventListener('resinen-auth-change', checkPremiumStatus);
            if (typeof localStorage !== 'undefined') {
                const savedNote = localStorage.getItem('resinen_notes'); if (savedNote) noteContent = savedNote;
                const savedTodos = localStorage.getItem('resinen_todos'); if (savedTodos) todos = JSON.parse(savedTodos);
            }
            await fetchAll(); refreshTimer = setInterval(fetchAll, 300000);
        } catch (e) { console.error(e); } finally { loading = false; } 
    });
    
    onDestroy(() => { clearInterval(refreshTimer); clearInterval(timerInterval); if (typeof window !== 'undefined') window.removeEventListener('resinen-auth-change', checkPremiumStatus); });
</script>

<svelte:head>
    <title>Resinen // Life Command</title>
</svelte:head>

<div class="app-wrapper" class:theme-night={theme === 'night'} class:theme-sunrise={theme === 'sunrise'} class:theme-beach={theme === 'beach'}>
    {#if theme === 'night'}
        <div class="bg-layer stars"></div>
        <div class="bg-layer aurora"></div>
    {:else if theme === 'sunrise'}
        <div class="bg-layer lake-gradient"></div>
        <div class="bg-layer sun-glow"></div>
    {:else if theme === 'beach'}
        <div class="bg-layer sand-sea"></div>
        <div class="bg-layer bright-sun"></div>
    {/if}

    <div class="top-dock-container" class:collapsed={topDockCollapsed}>
        <div class="system-bar">
            <span class="sys-label">SYS:</span>{#each system as sys}<div class="sys-item"><span class="sys-dot"></span>{sys.name}</div>{/each}
            
            <div class="theme-switch">
                <button class:active={theme==='night'} onclick={() => setTheme('night')} title="Night Sky">🌙</button>
                <button class:active={theme==='sunrise'} onclick={() => setTheme('sunrise')} title="Lake Sunrise">🌅</button>
                <button class:active={theme==='beach'} onclick={() => setTheme('beach')} title="Sunny Beach">🏖️</button>
            </div>

            <div class="spacer"></div>
            <div class="date">{new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}</div>
            <button class="dock-collapse-btn" onclick={toggleTopDock} title="Collapse Dock">▲</button>
        </div>

        <div class="search-command-row">
            <div class="brand-display">
                <img src={logo} alt="Resinen" class="brand-logo" />
            </div>

            <div class="search-module">
                <div class="search-engines">
                    <button class:active={searchEngine === 'google'} onclick={() => searchEngine = 'google'}>GGL</button>
                    <button class:active={searchEngine === 'news'} onclick={() => searchEngine = 'news'}>NEWS</button>
                    <button class:active={searchEngine === 'youtube'} onclick={() => searchEngine = 'youtube'}>YT</button>
                </div>
                <input type="text" bind:value={searchQuery} onkeydown={(e) => e.key === 'Enter' && handleSearch()} placeholder="INITIATE GLOBAL SEARCH QUERY..." />
                <button class="go-btn" onclick={handleSearch}>→</button>
            </div>
            
            <div class="zen-mini">
                {#if zen}<span>"{zen.text}"</span>{:else}<span>...</span>{/if}
            </div>
        </div>
    </div>
    
    <button class="dock-handle" class:visible={topDockCollapsed} onclick={toggleTopDock}>▼</button>

    <div class="layout" class:shifted={!topDockCollapsed}>
        {#if loading}
            <div class="loading">ESTABLISHING GLOBAL UPLINK...</div>
        {:else}
            <div class="grid">
                <section class="col">
                    <div class="card hero"><div class="head">YUMMY</div>{#if visuals?.food}<div class="img-frame" style="background-image: url({visuals.food})"></div>{/if}</div>
                    
                    <div class="card animal-card">
                        <div class="head">COMPANION LINK</div>
                        {#if visuals?.animal}<div class="animal-frame"><img src={visuals.animal.url} alt="Animal" /><div class="animal-tag">DETECTED: {visuals.animal.type}</div></div>{/if}
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
                        {#if isPremium}<textarea bind:value={noteContent} oninput={saveNotes} placeholder="Type your thoughts..."></textarea>
                        {:else}<div class="locked-widget" onclick={triggerPay}><div class="lock-icon">🔒</div><div class="lock-text">PREMIUM FEATURE</div></div>{/if}
                    </div>

                    <div class="card todo">
                        <div class="head">TASKS {#if !isPremium}🔒{/if}</div>
                        {#if isPremium}
                            <div class="todo-input-row">
                                <input type="text" bind:value={todoInput} onkeydown={(e) => e.key === 'Enter' && addTodo()} placeholder="Add task..." />
                                <button onclick={addTodo}>+</button>
                            </div>
                            <div class="todo-list">
                                {#each todos as todo, i}<div class="todo-item" class:done={todo.done}><span onclick={() => toggleTodo(i)}>{todo.text}</span><button onclick={() => removeTodo(i)}>×</button></div>{/each}
                            </div>
                        {:else}<div class="locked-widget" onclick={triggerPay}><div class="lock-icon">🔒</div><div class="lock-text">PREMIUM FEATURE</div></div>{/if}
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
                        {:else}<div class="locked-widget" onclick={triggerPay}><div class="lock-icon">🔒</div><div class="lock-text">PREMIUM FEATURE</div></div>{/if}
                    </div>

                    <div class="card markets">
                        <div class="head">MARKETS</div>
                        {#if feeds?.markets}
                            <div class="ticker-row">{#each feeds.markets as m}<div class="tick"><span class="label">{m.name}</span><span class="val">${m.price}</span><span class="chg" class:pos={!m.change.includes('-')} class:neg={m.change.includes('-')}>{m.change}</span></div>{/each}</div>
                        {/if}
                    </div>

                    <div class="clock-row">
                        {#if planetary}{#each planetary.watch as c}<div class="clock"><span class="city">{c.city}</span><span class="t">{c.time}</span><span class="w">{c.icon}</span></div>{/each}{/if}
                    </div>
                </section>

                <section class="col">
                    {#if visuals?.art}
                        <div class="card art-card" style="background-image: url({visuals.art.url})">
                            <div class="overlay">
                                <div class="art-header">
                                    <div class="head">GALLERY LINK</div>
                                    <button class="art-toggle" onclick={toggleArtMode} disabled={artLoading}>
                                        <span class:active={artMode === 'met'}>MET</span><span class="div">/</span><span class:active={artMode === 'aic'}>AIC</span>
                                    </button>
                                </div>
                                <div class="art-info" class:blur={artLoading}>
                                    <h2>{visuals.art.title}</h2><div class="artist">{visuals.art.artist}</div><div class="source-tag">{visuals.art.source}</div>
                                </div>
                            </div>
                        </div>
                    {/if}

                    <div class="card sports">
                        <div class="head">GLOBAL SPORTS</div>
                        <div class="sports-list">{#if feeds?.sports}{#each feeds.sports as s}<a href={s.link} target="_blank" class="sports-item"><span class="sport-icon">⚽</span><span class="sport-title">{s.title}</span></a>{/each}{/if}</div>
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

    .brand-display {
        display: flex;
        align-items: center;
        gap: 12px;
        height: 36px;
        padding-right: 20px;
        user-select: none;
    }

    .brand-logo {
        height: 42px;
        width: auto;
        filter: drop-shadow(0 0 8px rgba(45, 212, 191, 0.4)); /* Soft accent glow */
    }
    :root { --accent: #2dd4bf; --card: rgba(30, 41, 59, 0.7); --border: #334155; --mono: 'JetBrains Mono', monospace; }
    .app-wrapper { min-height: 100vh; position: relative; padding-bottom: 220px; transition: background 0.5s; background-color: #020617; }
    
    /* THEMES */
    .app-wrapper.theme-night { background-color: #020617; }
    .app-wrapper.theme-night .stars { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; background: radial-gradient(#fff 1px, transparent 1px); background-size: 50px 50px; opacity: 0.1; }
    .app-wrapper.theme-night .aurora { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; background: radial-gradient(circle at 50% -10%, #4c1d95, transparent 60%); opacity: 0.3; filter: blur(80px); }

    .app-wrapper.theme-sunrise { background: linear-gradient(to bottom, #1e1b4b, #431407, #0f172a); }
    .app-wrapper.theme-sunrise .lake-gradient { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(to top, #7c2d12 0%, transparent 50%); opacity: 0.4; z-index: 0; }
    .app-wrapper.theme-sunrise .sun-glow { position: fixed; bottom: 0; left: 50%; transform: translateX(-50%); width: 800px; height: 400px; background: radial-gradient(circle, #ea580c, transparent 70%); filter: blur(60px); opacity: 0.6; z-index: 0; }

    .app-wrapper.theme-beach { background: linear-gradient(to bottom, #0284c7, #38bdf8); }
    .app-wrapper.theme-beach .sand-sea { position: fixed; bottom: 0; left: 0; width: 100%; height: 40%; background: linear-gradient(to top, #fde047 0%, #0ea5e9 100%); opacity: 0.8; z-index: 0; }
    .app-wrapper.theme-beach .bright-sun { position: fixed; top: -100px; right: -100px; width: 500px; height: 500px; background: radial-gradient(circle, #fef08a, transparent 60%); filter: blur(40px); opacity: 0.8; z-index: 0; }

    .theme-switch { display: flex; gap: 5px; margin-left: 10px; background: rgba(0,0,0,0.3); border-radius: 20px; padding: 2px; }
    .theme-switch button { background: transparent; border: none; font-size: 0.9rem; cursor: pointer; padding: 2px 6px; border-radius: 50%; transition: 0.2s; opacity: 0.5; }
    .theme-switch button:hover { opacity: 1; transform: scale(1.2); }
    .theme-switch button.active { opacity: 1; background: rgba(255,255,255,0.1); box-shadow: 0 0 5px rgba(255,255,255,0.2); }

    .layout { position: relative; z-index: 1; max-width: 1600px; margin: 0 auto; padding: 20px; transition: padding-top 0.4s cubic-bezier(0.16, 1, 0.3, 1); padding-top: 120px; }
    .layout.shifted { padding-top: 140px; }

    /* TOP DOCK */
    .top-dock-container { position: fixed; top: 0; left: 0; width: 100%; z-index: 2000; background: rgba(15, 23, 42, 0.95); border-bottom: 1px solid var(--border); backdrop-filter: blur(12px); box-shadow: 0 10px 30px rgba(0,0,0,0.5); transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
    .top-dock-container.collapsed { transform: translateY(-100%); }
    .dock-handle { position: fixed; top: 0; left: 50%; transform: translateX(-50%); z-index: 1999; background: var(--accent); color: #000; border: none; border-radius: 0 0 8px 8px; font-family: var(--mono); cursor: pointer; padding: 4px 15px; font-weight: bold; transition: transform 0.4s, opacity 0.4s; transform: translateX(-50%) translateY(-100%); opacity: 0; box-shadow: 0 5px 15px rgba(0,0,0,0.5); }
    .dock-handle.visible { transform: translateX(-50%) translateY(0); opacity: 1; }
    
    .system-bar { display: flex; flex-wrap: wrap; gap: 15px; font-family: var(--mono); font-size: 0.7rem; padding: 8px 20px; border-bottom: 1px solid rgba(255,255,255,0.05); align-items: center; }
    .sys-dot { width: 6px; height: 6px; background: var(--accent); border-radius: 50%; display: inline-block; margin-right: 5px; box-shadow: 0 0 5px var(--accent); }
    .dock-collapse-btn { background: transparent; border: none; color: #64748b; cursor: pointer; font-weight: bold; margin-left: 10px; transition: 0.2s; }
    .dock-collapse-btn:hover { color: var(--accent); }

    /* SEARCH + ZEN + STUDIO ROW */
    .search-command-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 20px; max-width: 1600px; margin: 0 auto; gap: 20px; }
    
    .studio-btn {
        background: rgba(147, 51, 234, 0.2); border: 1px solid #a855f7; color: #d8b4fe;
        padding: 5px 15px; border-radius: 4px; text-decoration: none; font-family: var(--mono);
        font-weight: bold; font-size: 0.8rem; display: flex; align-items: center; gap: 8px;
        transition: 0.3s; white-space: nowrap; height: 36px;
        box-shadow: 0 0 10px rgba(168, 85, 247, 0.2);
    }
    .studio-btn:hover { background: #a855f7; color: #fff; box-shadow: 0 0 20px rgba(168, 85, 247, 0.6); transform: translateY(-2px); }
    .rune-icon { font-size: 1.1rem; animation: pulse-rune 2s infinite ease-in-out; }
    @keyframes pulse-rune { 0% { opacity: 0.5; transform: scale(0.9); } 50% { opacity: 1; transform: scale(1.1); } 100% { opacity: 0.5; transform: scale(0.9); } }

    .search-module { display: flex; gap: 10px; flex: 1; max-width: 800px; }
    .search-engines { display: flex; gap: 0; border: 1px solid var(--border); border-radius: 4px; overflow: hidden; height: 36px; }
    .search-engines button { background: transparent; color: #64748b; border: none; font-family: var(--mono); font-size: 0.75rem; padding: 0 12px; cursor: pointer; border-right: 1px solid var(--border); transition: 0.2s; height: 100%; }
    .search-engines button:last-child { border-right: none; }
    .search-engines button:hover { color: #fff; background: rgba(255,255,255,0.05); }
    .search-engines button.active { background: var(--accent); color: #000; font-weight: bold; }
    
    .search-module input { flex: 1; background: rgba(0,0,0,0.3); border: 1px solid var(--border); color: #fff; font-family: var(--mono); font-size: 0.9rem; padding: 0 15px; outline: none; letter-spacing: 1px; border-radius: 4px; height: 36px; }
    .search-module input:focus { border-color: var(--accent); box-shadow: 0 0 15px rgba(45, 212, 191, 0.1); }
    .search-module .go-btn { background: transparent; color: var(--accent); border: 1px solid var(--accent); width: 40px; border-radius: 4px; cursor: pointer; font-weight: bold; transition: 0.2s; height: 36px; }
    .search-module .go-btn:hover { background: var(--accent); color: #000; }

    .zen-mini { font-family: var(--mono); font-style: italic; color: #94a3b8; font-size: 0.8rem; text-align: right; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 400px; border-left: 2px solid var(--accent); padding-left: 15px; opacity: 0.8; }

    /* GRID & LAYOUT */
    .grid { display: grid; grid-template-columns: 300px 1fr 300px; gap: 2rem; }
    .col { display: flex; flex-direction: column; gap: 1.5rem; }
    @media (max-width: 1024px) { .grid { grid-template-columns: 1fr 1fr; } .col:nth-child(3) { grid-column: span 2; display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; } }
    @media (max-width: 768px) { 
        .layout { padding: 10px; padding-top: 160px; } 
        .grid { display: flex; flex-direction: column; gap: 1rem; } 
        .col { width: 100%; } 
        .col:nth-child(3) { display: flex; flex-direction: column; } 
        .search-command-row { flex-direction: column; align-items: stretch; gap: 10px; }
        .zen-mini { text-align: center; border: none; padding: 0; border-top: 1px solid var(--border); padding-top: 5px; }
        .studio-btn { justify-content: center; }
    }

    /* CARDS & WIDGETS */
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 8px; overflow: hidden; backdrop-filter: blur(10px); transition: border-color 0.2s; } .card:hover { border-color: var(--accent); }
    .head { padding: 8px 12px; font-family: var(--mono); font-size: 0.65rem; color: var(--accent); border-bottom: 1px solid var(--border); background: rgba(0,0,0,0.2); display: flex; justify-content: space-between; } .head.clickable { cursor: pointer; user-select: none; } .head.clickable:hover { color: #fff; }
    .img-frame { height: 180px; background-size: cover; background-position: center; }
    .animal-frame { padding: 10px; position: relative; } .animal-frame img { width: 100%; border-radius: 4px; display: block; border: 1px solid var(--border); } .animal-tag { position: absolute; bottom: 15px; left: 15px; background: #000; color: var(--accent); padding: 2px 6px; font-size: 0.6rem; font-family: var(--mono); border: 1px solid var(--accent); }
    .art-card { height: 350px; background-size: cover; background-position: center; position: relative; transition: 0.3s; } .art-card .overlay { width: 100%; height: 100%; background: linear-gradient(to top, #000 10%, transparent 80%); padding: 20px; display: flex; flex-direction: column; justify-content: space-between; }
    .art-header { display: flex; justify-content: space-between; align-items: flex-start; } .art-toggle { background: rgba(0,0,0,0.6); border: 1px solid var(--border); color: #64748b; font-family: var(--mono); font-size: 0.7rem; padding: 4px 8px; border-radius: 4px; cursor: pointer; backdrop-filter: blur(5px); transition: 0.2s; } .art-toggle:hover { border-color: var(--accent); } .art-toggle span.active { color: var(--accent); font-weight: bold; text-shadow: 0 0 10px var(--accent); } .art-toggle .div { margin: 0 4px; opacity: 0.5; } .art-info { transition: 0.3s; } .art-info.blur { filter: blur(5px); opacity: 0.5; } .art-card h2 { margin: 0 0 5px 0; font-size: 1.1rem; text-shadow: 0 2px 4px #000; line-height: 1.2; } .artist { font-family: var(--mono); color: #cbd5e1; font-size: 0.8rem; margin-bottom: 8px; } .source-tag { display: inline-block; background: var(--accent); color: #000; font-family: var(--mono); font-size: 0.6rem; font-weight: bold; padding: 2px 6px; border-radius: 2px; }
    .sticky textarea { width: 100%; height: 150px; background: transparent; border: none; color: #fff; padding: 10px; font-family: var(--mono); font-size: 0.8rem; resize: none; outline: none; }
    .todo-input-row { display: flex; border-bottom: 1px solid var(--border); } .todo-input-row input { flex: 1; background: transparent; border: none; padding: 8px 12px; color: #fff; font-family: var(--mono); font-size: 0.8rem; outline: none; } .todo-input-row button { background: var(--accent); border: none; color: #000; font-weight: bold; width: 30px; cursor: pointer; } .todo-list { max-height: 150px; overflow-y: auto; } .todo-item { display: flex; justify-content: space-between; padding: 8px 12px; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 0.8rem; } .todo-item span { cursor: pointer; flex: 1; } .todo-item.done span { text-decoration: line-through; opacity: 0.5; color: var(--accent); } .todo-item button { background: none; border: none; color: #ef4444; cursor: pointer; font-weight: bold; }
    .news { padding: 10px; } .news-item { display: block; font-size: 0.8rem; margin-bottom: 8px; color: #cbd5e1; transition: color 0.2s; line-height: 1.3; } .news-item:hover { color: var(--accent); }
    .timer { text-align: center; padding-bottom: 15px; } .time { font-family: var(--mono); font-size: 3rem; font-weight: bold; margin: 10px 0; letter-spacing: 2px; text-shadow: 0 0 15px var(--accent); } .timer-modes { display: flex; justify-content: center; gap: 5px; margin-bottom: 15px; } .timer-modes button { background: transparent; border: 1px solid var(--border); color: #94a3b8; font-size: 0.7rem; padding: 2px 8px; cursor: pointer; } .timer-modes button.active { border-color: var(--accent); color: var(--accent); } .ctrls .main-btn { background: var(--accent); color: #000; border: none; font-weight: bold; padding: 8px 30px; font-family: var(--mono); cursor: pointer; border-radius: 4px; }
    .ticker-row { display: flex; justify-content: space-between; padding: 15px; flex-wrap: wrap; gap: 10px; } .tick { display: flex; flex-direction: column; align-items: center; min-width: 60px; } .tick .label { font-family: var(--mono); font-size: 0.65rem; color: #94a3b8; } .tick .val { color: #fff; font-weight: bold; font-size: 0.9rem; } .tick .chg { font-size: 0.7rem; } .pos { color: #4ade80; } .neg { color: #ef4444; }
    .clock-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(60px, 1fr)); gap: 5px; background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 10px; text-align: center; } .clock .city { font-size: 0.6rem; color: #94a3b8; font-family: var(--mono); display: block; } .clock .t { font-weight: bold; display: block; font-size: 1rem; }
    
    /* SPORTS UPDATES */
    .sports-list { padding: 10px; } 
    .sports-item { display: flex; gap: 10px; margin-bottom: 12px; align-items: flex-start; transition: 0.2s; color: #fff; /* WHITE TEXT */ } 
    .sports-item:hover { color: #bef264; transform: translateX(5px); } 
    .sport-icon { font-size: 1rem; color: #bef264; } 
    .sport-title { font-size: 0.85rem; line-height: 1.3; }

    .hist-content { padding: 15px; text-align: center; } .hist-year { font-family: var(--mono); font-size: 2rem; font-weight: bold; color: var(--accent); margin-bottom: 5px; } .hist-text { font-size: 0.9rem; line-height: 1.4; color: #cbd5e1; }
    .joke { padding: 15px; font-size: 0.9rem; line-height: 1.4; } .punch { margin-top: 5px; color: var(--accent); font-weight: bold; }
    .locked-widget { height: 150px; display: flex; flex-direction: column; justify-content: center; align-items: center; cursor: pointer; background: rgba(0,0,0,0.3); transition: 0.2s; border-radius: 8px; } .locked-widget:hover { background: rgba(239, 68, 68, 0.1); } .lock-icon { font-size: 2rem; margin-bottom: 10px; } .lock-text { font-family: 'JetBrains Mono'; color: #ef4444; font-size: 0.8rem; letter-spacing: 2px; }
    .spacer { flex: 1; }
    .loading { height: 80vh; display: flex; justify-content: center; align-items: center; color: var(--accent); font-family: var(--mono); letter-spacing: 2px; }
</style>