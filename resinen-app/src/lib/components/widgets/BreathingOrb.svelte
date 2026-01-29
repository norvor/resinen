<script lang="ts">
    let phase = $state("In"); // In, Hold, Out
    
    // Simple cycle timer logic for text (Animation handled by CSS)
    $effect(() => {
        const i = setInterval(() => {
            setTimeout(() => phase = "Hold", 4000); // Breathe in 4s
            setTimeout(() => phase = "Out", 6000);  // Hold 2s
            setTimeout(() => phase = "In", 10000);  // Breathe out 4s -> Total 10s cycle approx
        }, 10000);
        return () => clearInterval(i);
    });
</script>

<div class="card orb-widget">
    <div class="head">MINDFULNESS</div>
    <div class="orb-container">
        <div class="orb"></div>
        <div class="orb-text">{phase === 'In' ? 'INHALE' : phase === 'Hold' ? 'HOLD' : 'EXHALE'}</div>
    </div>
</div>

<style>
    /* === DEFAULT (DARK / NIGHT AURORA) === */
    .orb-widget { 
        height: 220px; 
        display: flex; flex-direction: column; 
        background: rgba(30, 41, 59, 0.4); 
        backdrop-filter: blur(10px); 
        border: 1px solid #334155; 
        border-radius: 12px; 
        transition: 0.3s;
    }
    
    .head { 
        padding: 10px 15px; 
        border-bottom: 1px solid #334155; 
        color: #60a5fa; 
        font-family: 'JetBrains Mono'; 
        font-size: 0.7rem; 
        text-align: center; 
        letter-spacing: 1px;
    }
    
    .orb-container { 
        flex: 1; 
        display: flex; 
        justify-content: center; 
        align-items: center; 
        position: relative; 
        overflow: hidden; 
    }
    
    .orb {
        width: 60px; height: 60px;
        background: radial-gradient(circle, #60a5fa 0%, transparent 70%);
        border-radius: 50%;
        filter: blur(10px);
        animation: breathe 10s infinite ease-in-out;
        box-shadow: 0 0 30px #60a5fa;
        transition: 0.5s;
    }

    .orb-text {
        position: absolute;
        color: #fff;
        font-family: 'Space Grotesk';
        font-size: 0.8rem;
        letter-spacing: 3px;
        opacity: 0.9;
        pointer-events: none;
        text-shadow: 0 0 10px #000;
        transition: 0.3s;
    }

    /* === CLOUDY THEME OVERRIDES === */
    :global(body.cloudy) .orb-widget {
        background: rgba(255, 255, 255, 0.6);
        border: 1px solid #cbd5e1;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    :global(body.cloudy) .orb-widget .head {
        border-bottom-color: #cbd5e1;
        color: #0284c7; /* Sky Blue 600 */
        font-weight: bold;
    }

    :global(body.cloudy) .orb {
        background: radial-gradient(circle, #0ea5e9 0%, transparent 70%); /* Sky Blue 500 */
        box-shadow: 0 0 30px rgba(14, 165, 233, 0.4);
    }

    :global(body.cloudy) .orb-text {
        color: #334155; /* Slate 700 */
        text-shadow: none;
        font-weight: 700;
    }

    @keyframes breathe {
        0% { transform: scale(0.5); opacity: 0.3; }   /* Start Inhale */
        40% { transform: scale(2.5); opacity: 1; }    /* End Inhale / Start Hold */
        60% { transform: scale(2.5); opacity: 1; }    /* End Hold / Start Exhale */
        100% { transform: scale(0.5); opacity: 0.3; } /* End Exhale */
    }
</style>