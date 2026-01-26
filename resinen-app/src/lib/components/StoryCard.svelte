<script lang="ts">
	import type { Story } from '$lib/types';
	
	let { story }: { story: Story } = $props();
	let showAnalysis = $state(false);

	// Dynamic classes for the pulse effect
	const pulseClass = {
		uplifting: 'pulse-green',
		neutral: 'pulse-gray',
		distressing: 'pulse-red'
	};
</script>

<div class="card {pulseClass[story.sentiment]}">
	<div class="glass-layer"></div>
	
	<div class="content">
		<div class="meta-row">
			<span class="source-tag">WIRE :: {story.source.toUpperCase()}</span>
			<span class="sentiment-indicator"></span>
		</div>
		
		<h3><a href={story.url} target="_blank">{story.headline}</a></h3>
		
		<p class="summary">{story.summary}</p>
		
		<button class="spectrum-btn" onclick={() => showAnalysis = !showAnalysis}>
			<span class="btn-text">
				{showAnalysis ? 'COLLAPSE SPECTRUM' : 'INITIATE SPECTRUM ANALYSIS'}
			</span>
			<div class="btn-line"></div>
		</button>
	</div>

	{#if showAnalysis}
		<div class="analysis-grid">
			{#each story.spectrum as analysis}
				<div class="ai-node">
					<div class="node-header">
						<span class="ai-name">model_input: {analysis.perspective}</span>
						<span class="ai-bias">bias_detect: {analysis.bias}</span>
					</div>
					<p class="node-text">{analysis.summary}</p>
				</div>
			{/each}
		</div>
	{/if}
</div>

<style>
	.card {
		position: relative;
		margin-bottom: 2rem;
		border-radius: 16px;
		/* Glassmorphism */
		background: rgba(20, 20, 25, 0.4);
		backdrop-filter: blur(12px);
		-webkit-backdrop-filter: blur(12px);
		border: 1px solid rgba(255, 255, 255, 0.05);
		transition: transform 0.4s cubic-bezier(0.22, 1, 0.36, 1);
		overflow: hidden;
	}

	.card:hover {
		transform: translateY(-4px) scale(1.01);
		border-color: rgba(255, 255, 255, 0.15);
	}

	/* The Heartbeat Pulse Borders */
	.pulse-green { box-shadow: 0 0 0 0 rgba(74, 222, 128, 0); }
	.pulse-green:hover { animation: heartbeat-green 2s infinite; }
	
	.pulse-red { box-shadow: 0 0 0 0 rgba(248, 113, 113, 0); }
	.pulse-red:hover { animation: heartbeat-red 2s infinite; }

	.content { padding: 2rem; position: relative; z-index: 2; }

	.meta-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 1rem;
	}

	.source-tag {
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.75rem;
		color: rgba(255, 255, 255, 0.5);
		letter-spacing: 1px;
	}

	/* The blinking "Live" dot */
	.sentiment-indicator {
		width: 8px; height: 8px; border-radius: 50%;
		background: currentColor;
		box-shadow: 0 0 10px currentColor;
	}
	.pulse-green .sentiment-indicator { background: #4ade80; color: #4ade80; animation: blink 3s infinite; }
	.pulse-red .sentiment-indicator { background: #f87171; color: #f87171; animation: blink 4s infinite; }

	h3 { margin: 0 0 1rem 0; font-size: 1.6rem; font-weight: 500; line-height: 1.3; }
	h3 a { color: #fff; text-decoration: none; transition: color 0.2s; }
	h3 a:hover { text-shadow: 0 0 20px rgba(255,255,255,0.4); }

	.summary { color: #a1a1aa; line-height: 1.6; font-size: 1.05rem; max-width: 90%; }

	/* Cyberpunk Button */
	.spectrum-btn {
		background: none; border: none; padding: 0; margin-top: 1.5rem;
		cursor: pointer; display: flex; align-items: center; width: 100%;
		font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #4ade80;
	}
	.btn-text { white-space: nowrap; margin-right: 1rem; letter-spacing: 2px; }
	.btn-line {
		height: 1px; width: 100%; background: linear-gradient(90deg, #4ade80 0%, transparent 100%);
		opacity: 0.3; transition: opacity 0.3s;
	}
	.spectrum-btn:hover .btn-line { opacity: 1; }

	/* Analysis Grid */
	.analysis-grid {
		background: rgba(0,0,0,0.3);
		border-top: 1px solid rgba(255,255,255,0.05);
		padding: 2rem;
		display: grid;
		gap: 1.5rem;
		grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
		animation: slideDown 0.3s ease-out;
	}

	.ai-node { border-left: 2px solid #333; padding-left: 1rem; }
	.node-header { display: flex; flex-direction: column; margin-bottom: 0.5rem; }
	.ai-name { color: #fff; font-size: 0.8rem; font-weight: bold; }
	.ai-bias { color: #666; font-size: 0.7rem; font-family: 'JetBrains Mono', monospace; }
	.node-text { color: #ccc; font-size: 0.9rem; line-height: 1.5; margin: 0; }

	/* Animations */
	@keyframes heartbeat-green {
		0% { box-shadow: 0 0 0 0 rgba(74, 222, 128, 0.4); }
		70% { box-shadow: 0 0 0 15px rgba(74, 222, 128, 0); }
		100% { box-shadow: 0 0 0 0 rgba(74, 222, 128, 0); }
	}
	@keyframes heartbeat-red {
		0% { box-shadow: 0 0 0 0 rgba(248, 113, 113, 0.4); }
		70% { box-shadow: 0 0 0 15px rgba(248, 113, 113, 0); }
		100% { box-shadow: 0 0 0 0 rgba(248, 113, 113, 0); }
	}
	@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
	@keyframescF slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
</style>