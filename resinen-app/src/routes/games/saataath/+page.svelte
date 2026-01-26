<script lang="ts">
    import { onMount } from 'svelte';

    // --- STATE ---
    let hand = $state<string[]>([]);
    let botCount = $state(5);
    let trick = $state<any[]>([]);
    let scores = $state({0: 0, 1: 0});
    let trump = $state<string | null>(null);
    let turn = $state(0); // 0=You, 1=Bot
    let phase = $state("TRUMP_SELECT");
    let msg = $state("Select a Trump Suit");
    let loading = $state(false);

    // --- LOGIC ---
    async function fetchState() {
        const res = await fetch('https://api.resinen.com/games/saataath/state');
        updateFromData(await res.json());
    }

    function updateFromData(data: any) {
        hand = data.hand;
        botCount = data.bot_hand_count;
        trick = data.trick;
        scores = data.tricks_won;
        trump = data.trump;
        turn = data.turn;
        phase = data.phase;

        if (phase === 'TRUMP_SELECT') msg = "Select a Trump Suit based on your hand.";
        else if (phase === 'FINISHED') {
            const win = scores[0] >= 8;
            msg = win ? "VICTORY! You won 8+ hands." : "DEFEAT! You failed to reach 8.";
        } else {
            if (turn === 0) msg = "Your Turn.";
            else {
                msg = "Bot is thinking...";
                setTimeout(triggerBotLead, 1000); 
            }
        }
    }

    async function newGame() {
        loading = true;
        const res = await fetch('http://localhost:8000/games/saataath/new', { method: 'POST' });
        updateFromData(await res.json());
        loading = false;
    }

    async function selectTrump(suit: string) {
        const res = await fetch('http://localhost:8000/games/saataath/trump', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ suit })
        });
        updateFromData(await res.json());
    }

    async function playCard(idx: number) {
        if (turn !== 0 || phase !== 'PLAYING') return;
        
        const res = await fetch('http://localhost:8000/games/saataath/play', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ card_idx: idx })
        });
        const data = await res.json();
        
        if (data.error) {
            msg = "⚠️ " + data.error;
        } else {
            updateFromData(data);
        }
    }

    async function triggerBotLead() {
        if (turn === 1 && trick.length === 0) {
            const res = await fetch('http://localhost:8000/games/saataath/bot-lead', { method: 'POST' });
            updateFromData(await res.json());
        }
    }

    // --- VISUALS ---
    function getSuitSymbol(s: string) {
        if (s === 'H') return '♥';
        if (s === 'D') return '♦';
        if (s === 'S') return '♠';
        if (s === 'C') return '♣';
        return '';
    }
    
    // --- FIX IS HERE ---
    function getCardColor(c: string) {
        // Red for Hearts/Diamonds, Pure Black for Spades/Clubs
        return (c[1] === 'H' || c[1] === 'D') ? '#ef4444' : '#000000';
    }

    onMount(() => newGame());
</script>

<div class="game-container">
    <div class="bg-layer stars"></div>
    
    <div class="game-ui">
        <div class="header">
            <a href="/" class="back-btn">← DOCK</a>
            <h1>SAAT AATH</h1>
            <div class="scoreboard">
                <div class="score-box p1" class:win={scores[0] >= 8}>
                    <span class="label">YOU (CUTTER)</span>
                    <span class="val">{scores[0]} / 8</span>
                </div>
                <div class="score-box p2">
                    <span class="label">BOT (DEALER)</span>
                    <span class="val">{scores[1]} / 7</span>
                </div>
            </div>
            {#if trump}<div class="trump-badge">TRUMP: <span style="color: {getCardColor('x'+trump)}">{getSuitSymbol(trump)}</span></div>{/if}
        </div>

        <div class="table-felt">
            <div class="status-msg">{msg}</div>

            <div class="bot-hand">
                {#each Array(botCount) as _}
                    <div class="card back"></div>
                {/each}
            </div>

            <div class="trick-area">
                {#each trick as [pIdx, card]}
                    <div class="played-card" class:p1={pIdx===0} class:p2={pIdx===1}>
                        <div class="card face" style="color: {getCardColor(card)}">
                            <div class="rank">{card[0] === 'T' ? '10' : card[0]}</div>
                            <div class="suit">{getSuitSymbol(card[1])}</div>
                        </div>
                        <div class="label">{pIdx===0 ? 'YOU' : 'BOT'}</div>
                    </div>
                {/each}
            </div>

            {#if phase === 'TRUMP_SELECT'}
                <div class="trump-selector">
                    <h3>CHOOSE TRUMP</h3>
                    <div class="suit-btns">
                        <button onclick={() => selectTrump('S')}>♠</button>
                        <button onclick={() => selectTrump('H')} class="red">♥</button>
                        <button onclick={() => selectTrump('C')}>♣</button>
                        <button onclick={() => selectTrump('D')} class="red">♦</button>
                    </div>
                </div>
            {/if}

            <div class="player-hand">
                {#each hand as card, i}
                    <div 
                        class="card face" 
                        class:playable={turn === 0}
                        style="color: {getCardColor(card)}"
                        onclick={() => playCard(i)}
                    >
                        <div class="rank">{card[0] === 'T' ? '10' : card[0]}</div>
                        <div class="suit">{getSuitSymbol(card[1])}</div>
                    </div>
                {/each}
            </div>
        </div>

        {#if phase === 'FINISHED'}
            <button class="retry-btn" onclick={newGame}>DEAL NEW HAND</button>
        {/if}
    </div>
</div>

<style>
    :global(body) { margin: 0; background-color: #0f172a; color: #f8fafc; font-family: 'Space Grotesk', sans-serif; overflow: hidden; }
    .stars { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: radial-gradient(#fff 1px, transparent 1px); background-size: 50px 50px; opacity: 0.1; }
    
    .game-container { height: 100vh; display: flex; justify-content: center; align-items: center; position: relative; }
    .game-ui { z-index: 1; display: flex; flex-direction: column; align-items: center; gap: 20px; width: 100%; }
    
    .header { text-align: center; width: 100%; position: relative; }
    .back-btn { position: absolute; left: 20px; top: 50%; transform: translateY(-50%); text-decoration: none; color: #94a3b8; font-family: 'JetBrains Mono'; font-size: 0.8rem; border: 1px solid #334155; padding: 5px 10px; border-radius: 4px; }
    h1 { font-size: 2.5rem; letter-spacing: 2px; margin: 0; color: #facc15; text-shadow: 0 0 10px #facc15; }
    
    .scoreboard { display: flex; gap: 40px; justify-content: center; margin-top: 10px; }
    .score-box { text-align: center; font-family: 'JetBrains Mono'; border: 1px solid #334155; padding: 5px 15px; border-radius: 4px; }
    .score-box.win { border-color: #facc15; color: #facc15; }
    .label { display: block; font-size: 0.7rem; color: #94a3b8; }
    .val { font-size: 1.2rem; font-weight: bold; }
    .trump-badge { margin-top: 10px; font-family: 'JetBrains Mono'; border: 1px solid #facc15; display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; }

    .table-felt { 
        width: 800px; height: 500px; background: #064e3b; 
        border: 8px solid #3f2c22; border-radius: 100px; 
        position: relative; display: flex; flex-direction: column; justify-content: space-between; align-items: center;
        padding: 20px; box-shadow: inset 0 0 50px rgba(0,0,0,0.5);
    }

    .status-msg { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: rgba(0,0,0,0.6); padding: 5px 10px; border-radius: 4px; font-family: 'JetBrains Mono'; font-size: 0.9rem; z-index: 10; }

    /* CARDS */
    .card { width: 60px; height: 90px; border-radius: 6px; position: relative; box-shadow: 0 2px 10px rgba(0,0,0,0.3); transition: transform 0.2s; }
    .card.back { background: repeating-linear-gradient(45deg, #1e293b, #1e293b 5px, #334155 5px, #334155 10px); border: 2px solid #fff; }
    .card.face { background: #fff; display: flex; flex-direction: column; justify-content: center; align-items: center; font-weight: bold; font-family: 'Arial'; border: 1px solid #ccc; cursor: default; }
    .card.face .rank { font-size: 1.5rem; }
    .card.face .suit { font-size: 2rem; line-height: 1; }
    
    .bot-hand { display: flex; gap: 5px; margin-top: 10px; }
    .bot-hand .card { transform: scale(0.8); }

    .player-hand { display: flex; gap: -20px; margin-bottom: 10px; } 
    .player-hand .card { cursor: pointer; margin: 0 5px; } 
    .player-hand .card.playable:hover { transform: translateY(-10px); box-shadow: 0 0 15px #facc15; }

    .trick-area { position: absolute; top: 40%; left: 50%; transform: translate(-50%, -50%); display: flex; gap: 40px; }
    .played-card { display: flex; flex-direction: column; align-items: center; gap: 5px; }
    .played-card .label { font-size: 0.7rem; font-family: 'JetBrains Mono'; opacity: 0.7; }
    
    .trump-selector { 
        position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); 
        background: rgba(15, 23, 42, 0.95); padding: 20px; border-radius: 8px; border: 1px solid #facc15;
        text-align: center; z-index: 20;
    }
    .trump-selector h3 { margin: 0 0 10px 0; font-size: 0.9rem; color: #facc15; }
    .suit-btns { display: flex; gap: 10px; }
    .suit-btns button { 
        font-size: 2rem; background: #fff; border: none; border-radius: 4px; 
        width: 50px; height: 50px; cursor: pointer; color: #000;
    }
    .suit-btns button.red { color: #ef4444; }
    .suit-btns button:hover { transform: scale(1.1); }

    .retry-btn { padding: 10px 30px; background: #facc15; color: #000; border: none; font-weight: bold; cursor: pointer; font-family: 'JetBrains Mono'; border-radius: 4px; }
</style>