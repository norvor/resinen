<script lang="ts">
    import { onMount } from 'svelte';

    // --- STATE ---
    let playerHand = $state<string[]>([]);
    let botHand = $state<string[]>([]);
    let board = $state<string[]>([]);
    let stage = $state('preflop'); // preflop, flop, turn, river, showdown
    let playerChips = $state(1000);
    let botChips = $state(1000);
    let pot = $state(0);
    let currentBet = $state(0);
    let message = $state("Place your bets.");
    let loading = $state(false);
    let winnerInfo = $state<any>(null);

    // --- LOGIC ---
    async function startGame() {
        loading = true;
        resetRound();
        const res = await fetch('http://localhost:8000/games/poker/deal');
        const data = await res.json();
        playerHand = data.player;
        botHand = data.bot;
        board = data.board;
        loading = false;
        
        // Ante
        playerChips -= 10;
        botChips -= 10;
        pot = 20;
        message = "Pre-Flop: Check or Bet?";
    }

    function resetRound() {
        stage = 'preflop';
        pot = 0;
        currentBet = 0;
        winnerInfo = null;
        message = "Shuffling...";
    }

    async function handleAction(action: string) {
        if (stage === 'showdown') return;

        // Player Action
        if (action === 'fold') {
            message = "You Folded. Bot Wins.";
            botChips += pot;
            stage = 'showdown';
            return;
        }
        if (action === 'bet') {
            const amount = 50; // Fixed betting for simplicity
            playerChips -= amount;
            pot += amount;
            currentBet = amount;
        }
        
        // Bot Turn
        message = "Bot thinking...";
        const res = await fetch('http://localhost:8000/games/poker/bot-move', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                player_hand: playerHand, bot_hand: botHand, board, stage,
                pot, player_chips: playerChips, bot_chips: botChips, current_bet: currentBet
            })
        });
        const data = await res.json();
        
        if (data.action === 'fold') {
            message = "Bot Folded! You Win.";
            playerChips += pot;
            stage = 'showdown';
            return;
        } else if (data.action === 'raise' || (data.action === 'call' && currentBet > 0)) {
            botChips -= currentBet || 50;
            pot += currentBet || 50;
            message = data.action === 'raise' ? "Bot Raised!" : "Bot Calls.";
        } else {
            message = "Bot Checks.";
        }

        nextStage();
    }

    async function nextStage() {
        currentBet = 0;
        if (stage === 'preflop') stage = 'flop';
        else if (stage === 'flop') stage = 'turn';
        else if (stage === 'turn') stage = 'river';
        else if (stage === 'river') {
            stage = 'showdown';
            await calculateWinner();
            return;
        }
    }

    async function calculateWinner() {
        const res = await fetch('http://localhost:8000/games/poker/winner', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                player_hand: playerHand, bot_hand: botHand, board, stage,
                pot, player_chips: playerChips, bot_chips: botChips, current_bet: 0
            })
        });
        winnerInfo = await res.json();
        
        if (winnerInfo.winner === 'player') {
            message = `YOU WIN! (${winnerInfo.player_rank})`;
            playerChips += pot;
        } else if (winnerInfo.winner === 'bot') {
            message = `BOT WINS. (${winnerInfo.bot_rank})`;
            botChips += pot;
        } else {
            message = "SPLIT POT.";
            playerChips += pot/2;
            botChips += pot/2;
        }
    }

    function getSuitSymbol(cardStr: string) {
        const suit = cardStr[1];
        if (suit === 'h') return '♥';
        if (suit === 'd') return '♦';
        if (suit === 'c') return '♣';
        if (suit === 's') return '♠';
        return '';
    }
    
    function getRank(cardStr: string) {
        return cardStr[0].replace('T', '10');
    }

    function isRed(cardStr: string) {
        return cardStr[1] === 'h' || cardStr[1] === 'd';
    }

    onMount(() => startGame());
</script>

<div class="game-container">
    <div class="bg-layer stars"></div>
    
    <div class="poker-table">
        <div class="header">
            <a href="/" class="back-btn">← DOCK</a>
            <h1>TEXAS HOLD'EM</h1>
            <div class="pot-display">POT: ${pot}</div>
        </div>

        <div class="player-area bot">
            <div class="chips">CHIPS: ${botChips}</div>
            <div class="hand">
                {#each botHand as card}
                    <div class="card back" class:revealed={stage === 'showdown'}>
                        {#if stage === 'showdown'}
                            <div class="rank" class:red={isRed(card)}>{getRank(card)}</div>
                            <div class="suit" class:red={isRed(card)}>{getSuitSymbol(card)}</div>
                        {:else}
                            <div class="pattern"></div>
                        {/if}
                    </div>
                {/each}
            </div>
        </div>

        <div class="community-area">
            {#each [0, 1, 2, 3, 4] as i}
                <div class="card" class:hidden={i > 2 && stage === 'preflop' || i > 3 && stage === 'flop' || i > 4 && stage === 'turn'}>
                    {#if (i < 3 && stage !== 'preflop') || (i < 4 && (stage === 'turn' || stage === 'river' || stage === 'showdown')) || (stage === 'river' || stage === 'showdown')}
                        <div class="rank" class:red={isRed(board[i])}>{getRank(board[i])}</div>
                        <div class="suit" class:red={isRed(board[i])}>{getSuitSymbol(board[i])}</div>
                    {:else}
                        <div class="pattern"></div>
                    {/if}
                </div>
            {/each}
        </div>

        <div class="status-msg">{message}</div>

        <div class="player-area">
            <div class="hand">
                {#each playerHand as card}
                    <div class="card">
                        <div class="rank" class:red={isRed(card)}>{getRank(card)}</div>
                        <div class="suit" class:red={isRed(card)}>{getSuitSymbol(card)}</div>
                    </div>
                {/each}
            </div>
            <div class="chips">CHIPS: ${playerChips}</div>
        </div>

        <div class="controls" class:disabled={stage === 'showdown' || loading}>
            <button class="fold" onclick={() => handleAction('fold')}>FOLD</button>
            <button class="check" onclick={() => handleAction('check')}>CHECK/CALL</button>
            <button class="bet" onclick={() => handleAction('bet')}>BET $50</button>
        </div>
        
        {#if stage === 'showdown'}
            <button class="next-round" onclick={startGame}>DEAL NEXT HAND</button>
        {/if}
    </div>
</div>

<style>
    :global(body) { margin: 0; background-color: #050505; color: #f8fafc; font-family: 'Space Grotesk', sans-serif; overflow: hidden; }
    .stars { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: radial-gradient(#fff 1px, transparent 1px); background-size: 50px 50px; opacity: 0.1; }
    
    .game-container { height: 100vh; display: flex; justify-content: center; align-items: center; position: relative; background: radial-gradient(circle at center, #1a1a1a 0%, #000 100%); }
    .poker-table { width: 800px; display: flex; flex-direction: column; align-items: center; gap: 20px; z-index: 1; }
    
    .header { text-align: center; width: 100%; position: relative; }
    .back-btn { position: absolute; left: 0; top: 50%; transform: translateY(-50%); text-decoration: none; color: #94a3b8; font-family: 'JetBrains Mono'; font-size: 0.8rem; border: 1px solid #334155; padding: 5px 10px; border-radius: 4px; }
    h1 { font-size: 2.5rem; letter-spacing: 2px; margin: 0; color: #facc15; text-shadow: 0 0 20px rgba(250, 204, 21, 0.3); }
    .pot-display { font-family: 'JetBrains Mono'; color: #4ade80; font-size: 1.2rem; margin-top: 5px; }

    /* CARDS */
    .hand, .community-area { display: flex; gap: 10px; justify-content: center; }
    .card { 
        width: 60px; height: 90px; background: #fff; border-radius: 6px; 
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        box-shadow: 0 5px 15px rgba(0,0,0,0.5); position: relative; color: #000; font-weight: bold;
        transition: transform 0.3s;
    }
    .card.back { background: #1e293b; border: 2px solid #334155; }
    .card.back .pattern { width: 100%; height: 100%; background: repeating-linear-gradient(45deg, #1e293b, #1e293b 10px, #334155 10px, #334155 20px); opacity: 0.3; }
    .card.hidden { opacity: 0.2; background: #000; border: 1px dashed #333; }
    .rank { font-size: 1.2rem; }
    .suit { font-size: 1.5rem; }
    .red { color: #ef4444; }

    .player-area { display: flex; flex-direction: column; align-items: center; gap: 10px; }
    .chips { font-family: 'JetBrains Mono'; font-size: 0.9rem; color: #fbbf24; }
    
    .status-msg { font-family: 'JetBrains Mono'; color: #fff; min-height: 24px; font-size: 1.1rem; text-shadow: 0 0 10px #fff; }

    .controls { display: flex; gap: 15px; margin-top: 20px; }
    .controls.disabled { opacity: 0.5; pointer-events: none; }
    button { padding: 10px 20px; font-family: 'JetBrains Mono'; font-weight: bold; border: none; cursor: pointer; border-radius: 4px; transition: 0.2s; }
    .fold { background: #ef4444; color: #fff; }
    .check { background: #3b82f6; color: #fff; }
    .bet { background: #facc15; color: #000; }
    button:hover { transform: translateY(-2px); box-shadow: 0 0 15px currentColor; }
    
    .next-round { background: #fff; color: #000; margin-top: 10px; padding: 10px 40px; }
</style>