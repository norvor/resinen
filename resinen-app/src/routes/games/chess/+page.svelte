<script lang="ts">
    import { onMount } from 'svelte';
    import { Chess } from 'chess.js';

    // --- GAME STATE ---
    let chess = new Chess();
    let board = $state<any[]>([]);
    let selectedSquare = $state<string | null>(null);
    let validMoves = $state<string[]>([]);
    let status = $state("Your Move (White)");
    let gameOver = $state(false);
    let isThinking = $state(false);

    // PIECE ASSETS
    const PIECES: any = {
        'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚',
        'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔'
    };

    function updateBoard() {
        const tempBoard = [];
        const rawBoard = chess.board();
        for (let r = 0; r < 8; r++) {
            for (let c = 0; c < 8; c++) {
                const square = String.fromCharCode(97 + c) + (8 - r);
                tempBoard.push({
                    square,
                    color: (r + c) % 2 === 0 ? 'light' : 'dark',
                    piece: rawBoard[r][c] ? PIECES[rawBoard[r][c].color === 'w' ? rawBoard[r][c].type.toUpperCase() : rawBoard[r][c].type] : null,
                    pieceObj: rawBoard[r][c]
                });
            }
        }
        board = tempBoard;
        
        if (chess.isGameOver()) {
            gameOver = true;
            if (chess.isCheckmate()) status = "CHECKMATE! " + (chess.turn() === 'w' ? "Black Wins" : "White Wins");
            else status = "DRAW";
        } else {
            status = chess.turn() === 'w' ? "Your Move" : "Rivendell Thinking...";
        }
    }

    async function makeAiMove() {
        if (gameOver) return;
        isThinking = true;
        status = "Rivendell Computing...";

        try {
            const res = await fetch('https://api.resinen.com/games/chess/move', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ fen: chess.fen(), difficulty: 3 })
            });
            const data = await res.json();
            
            if (data.move) {
                chess.move(data.move);
                updateBoard();
                // Play Sound?
            } else {
                gameOver = true;
                status = "Game Over";
            }
        } catch (e) {
            console.error("AI Error", e);
            status = "AI Disconnected";
        } finally {
            isThinking = false;
        }
    }

    function handleSquareClick(sq: any) {
        if (gameOver || isThinking || chess.turn() !== 'w') return;

        // Deselect
        if (selectedSquare === sq.square) {
            selectedSquare = null;
            validMoves = [];
            return;
        }

        // Move
        if (selectedSquare) {
            try {
                const move = chess.move({ from: selectedSquare, to: sq.square, promotion: 'q' });
                if (move) {
                    updateBoard();
                    selectedSquare = null;
                    validMoves = [];
                    // Trigger AI
                    setTimeout(makeAiMove, 500);
                    return;
                }
            } catch (e) {}
        }

        // Select
        if (sq.pieceObj && sq.pieceObj.color === 'w') {
            selectedSquare = sq.square;
            const moves = chess.moves({ square: sq.square, verbose: true });
            validMoves = moves.map((m: any) => m.to);
        } else {
            selectedSquare = null;
            validMoves = [];
        }
    }

    function resetGame() {
        chess.reset();
        gameOver = false;
        selectedSquare = null;
        validMoves = [];
        updateBoard();
    }

    onMount(() => updateBoard());
</script>

<div class="game-container">
    <div class="bg-layer stars"></div>
    
    <div class="game-ui">
        <div class="header">
            <h1>RIVENDELL CHESS</h1>
            <div class="status" class:pulse={isThinking}>{status}</div>
        </div>

        <div class="chess-board" class:locked={isThinking}>
            {#each board as sq}
                <div 
                    class="square {sq.color} {selectedSquare === sq.square ? 'selected' : ''} {validMoves.includes(sq.square) ? 'valid' : ''}"
                    role="button"
                    tabindex="0"
                    onclick={() => handleSquareClick(sq)}
                >
                    {#if sq.piece}<span class="piece">{sq.piece}</span>{/if}
                    {#if validMoves.includes(sq.square)}<div class="dot"></div>{/if}
                </div>
            {/each}
        </div>

        <div class="controls">
            <button onclick={resetGame}>RESET BOARD</button>
        </div>
    </div>
</div>

<style>
    :global(body) { margin: 0; background-color: #020617; color: #f8fafc; font-family: 'Space Grotesk', sans-serif; overflow: hidden; touch-action: manipulation; }
    .stars { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; background: radial-gradient(#fff 1px, transparent 1px); background-size: 50px 50px; opacity: 0.1; pointer-events: none;}
    
    .game-container { height: 100vh; width: 100vw; display: flex; justify-content: center; align-items: center; position: relative; }
    .game-ui { z-index: 1; display: flex; flex-direction: column; align-items: center; gap: 20px; width: 100%; max-width: 600px; padding: 10px; box-sizing: border-box; }
    
    .header { text-align: center; width: 100%; position: relative; margin-bottom: 5px; }
    h1 { font-size: 2rem; letter-spacing: -1px; margin: 0; color: #fff; text-shadow: 0 0 10px #fbbf24; }
    
    .status { font-family: 'JetBrains Mono'; color: #2dd4bf; margin-top: 5px; min-height: 24px; font-size: 0.9rem; }
    .status.pulse { animation: pulse 1s infinite; color: #fbbf24; }

    /* RESPONSIVE BOARD */
    .chess-board { 
        /* Cell Size Logic:
           1. Max 60px (Desktop)
           2. 11vw (Fits 8 cols in mobile width)
           3. 55vh (Fits in mobile landscape height)
        */
        --cell-size: min(60px, 11vw, 55vh);
        
        display: grid; 
        grid-template-columns: repeat(8, var(--cell-size)); 
        grid-template-rows: repeat(8, var(--cell-size)); 
        border: 10px solid #1e293b; 
        border-radius: 4px; 
        box-shadow: 0 0 50px rgba(0,0,0,0.5); 
        transition: opacity 0.2s;
    }
    .chess-board.locked { opacity: 0.7; pointer-events: none; cursor: wait; }
    
    .square { 
        width: var(--cell-size); 
        height: var(--cell-size); 
        display: flex; justify-content: center; align-items: center; 
        font-size: calc(var(--cell-size) * 0.75); /* Pieces scale with cell */
        cursor: pointer; 
        position: relative; 
    }
    .square.light { background-color: #475569; color: #e2e8f0; }
    .square.dark { background-color: #1e293b; color: #475569; }
    .square.selected { background-color: rgba(251, 191, 36, 0.5) !important; }
    
    /* Touch devices don't hover well, so we only apply hover on non-touch */
    @media (hover: hover) {
        .square:hover { filter: brightness(1.2); }
    }
    
    .piece { z-index: 2; user-select: none; }
    .dot { width: 20%; height: 20%; background: rgba(45, 212, 191, 0.5); border-radius: 50%; position: absolute; }

    .controls button {
        background: transparent; border: 1px solid #fbbf24; color: #fbbf24; 
        padding: 10px 30px; font-family: 'JetBrains Mono'; font-size: 1rem; 
        cursor: pointer; transition: 0.2s; border-radius: 4px;
    }
    .controls button:hover { background: #fbbf24; color: #000; box-shadow: 0 0 20px #fbbf24; }

    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }

    /* MOBILE TWEAKS */
    @media (max-width: 500px) {
        h1 { font-size: 1.5rem; }
        .chess-board { border-width: 5px; }
    }
</style>