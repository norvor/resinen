<script lang="ts">
	import { onMount } from 'svelte';
	import StoryCard from '$lib/components/StoryCard.svelte';
	import type { Story, Quote, CooluteImage } from '$lib/types';

	// --- 1. STATE ---
	let wireStories = $state<Story[]>([]);
	let spectrumStories = $state<Story[]>([]);
	let opinionPieces = $state<Story[]>([]);
	let happyNews = $state<Story[]>([]);
	let coolute = $state<CooluteImage[]>([]);
	let quote = $state<Quote | null>(null);
	let loading = $state(true);

	// --- 2. CLIENT-SIDE LOADING ---
	onMount(async () => {
		// Simulate fetching data from your API
		await loadFakeData();
		loading = false;
	});

	async function loadFakeData() {
		// In reality, these would be fetch('/api/wire'), fetch('/api/spectrum'), etc.
		
		// A. The Quote
		quote = { text: "The only way to deal with an unfree world is to become so absolutely free that your very existence is an act of rebellion.", author: "Albert Camus" };

		// B. The Wire (Raw feeds)
		wireStories = [
			{ id: 'w1', headline: 'Yen drops to 150 against USD', source: 'Bloomberg', sentiment: 'neutral', url: '#', summary: '', spectrum: [], timestamp: '10:00 AM' },
			{ id: 'w2', headline: 'SpaceX Starship launch scheduled for Tuesday', source: 'TechCrunch', sentiment: 'neutral', url: '#', summary: '', spectrum: [], timestamp: '09:45 AM' },
			{ id: 'w3', headline: 'New React compiler enters beta', source: 'Vercel', sentiment: 'uplifting', url: '#', summary: '', spectrum: [], timestamp: '09:30 AM' },
			{ id: 'w4', headline: 'Oil prices surge amidst supply concerns', source: 'Reuters', sentiment: 'distressing', url: '#', summary: '', spectrum: [], timestamp: '09:15 AM' },
		];

		// C. Spectrum (The Deep Dive)
		spectrumStories = [
			{
				id: 's1',
				headline: 'Global AI Treaty Signed: Safety or Stagnation?',
				summary: 'Nations agree on a baseline for compute caps. We analyzed the text against 3 frameworks.',
				source: 'Resinen Analysis',
				sentiment: 'neutral',
				url: '#',
				timestamp: 'Today',
				spectrum: [
					{ perspective: 'Claude (Safety)', summary: 'Crucial for risk mitigation.', bias: 'Pro-Reg' },
					{ perspective: 'Llama (Open)', summary: 'Stifles open-source innovation.', bias: 'Anti-Reg' }
				]
			}
		];

		// D. Opinion (Your Voice)
		opinionPieces = [
			{
				id: 'o1',
				headline: 'Why "Zero Input" is the Future of Software',
				summary: 'We are tired of filling out forms. The next generation of apps will just... know.',
				source: 'Editor Desk',
				sentiment: 'neutral',
				url: '#',
				timestamp: 'Jan 26',
				spectrum: []
			}
		];

		// E. Happy News
		happyNews = [
			{ id: 'h1', headline: 'Ozone Layer on Track to Full Recovery by 2040', source: 'UN Report', sentiment: 'uplifting', url: '#', summary: 'A historic win for environmental policy.', spectrum: [], timestamp: '' },
			{ id: 'h2', headline: 'Mandonado Village reaches 100% Literacy', source: 'Local', sentiment: 'uplifting', url: '#', summary: 'Education initiatives pay off.', spectrum: [], timestamp: '' }
		];

		// F. Coolute (Cool + Cute)
		coolute = [
			{ url: 'https://images.unsplash.com/photo-1534361960057-19889db9621e?q=80&w=600&auto=format&fit=crop', caption: 'Cyberpunk Golden Retriever' },
			{ url: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=600&auto=format&fit=crop', caption: 'Neon Tokyo Rain' }
		];
	}
</script>

<div class="newspaper-layout">
	
	<header class="masthead">
		<div class="brand">
			<h1>RESINEN</h1>
			<div class="date">{new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}</div>
		</div>
		{#if quote}
			<div class="quote-ticker">
				<span class="quote-text">"{quote.text}"</span>
				<span class="quote-author">— {quote.author}</span>
			</div>
		{/if}
	</header>

	{#if loading}
		<div class="loading">Loading the Pulse...</div>
	{:else}
		<div class="grid-container">
			
			<section class="col-wire">
				<h2 class="section-header">THE WIRE <span class="blink">●</span></h2>
				<div class="wire-list">
					{#each wireStories as item}
						<a href={item.url} class="wire-item">
							<span class="timestamp">{item.timestamp}</span>
							<span class="headline">{item.headline}</span>
							<span class="source">{item.source}</span>
						</a>
					{/each}
				</div>
			</section>

			<section class="col-center">
				<div class="spectrum-block">
					<h2 class="section-header">SPECTRUM ANALYSIS</h2>
					{#each spectrumStories as story}
						<StoryCard {story} />
					{/each}
				</div>

				<div class="opinion-block">
					<h2 class="section-header">OPINION</h2>
					{#each opinionPieces as op}
						<div class="opinion-card">
							<h3>{op.headline}</h3>
							<p>{op.summary}</p>
							<div class="author-tag">By The Architect</div>
						</div>
					{/each}
				</div>
			</section>

			<section class="col-right">
				
				<div class="coolute-block">
					<h2 class="section-header">COOLUTE</h2>
					<div class="gallery">
						{#each coolute as img}
							<div class="coolute-card">
								<img src={img.url} alt={img.caption} />
								<div class="caption">{img.caption}</div>
							</div>
						{/each}
					</div>
				</div>

				<div class="happy-block">
					<h2 class="section-header">SILVER LINING</h2>
					{#each happyNews as news}
						<div class="happy-item">
							<span class="icon">☀️</span>
							<a href={news.url}>{news.headline}</a>
						</div>
					{/each}
				</div>

			</section>

		</div>
	{/if}
</div>

<style>
	/* --- LAYOUT GRID --- */
	.newspaper-layout {
		max-width: 1400px;
		margin: 0 auto;
		padding: 2rem;
		font-family: 'Space Grotesk', sans-serif;
	}

	.grid-container {
		display: grid;
		grid-template-columns: 250px 1fr 300px; /* The NYT Ratio */
		gap: 2rem;
		align-items: start;
	}

	/* --- HEADER --- */
	.masthead {
		border-bottom: 2px solid #333;
		margin-bottom: 3rem;
		padding-bottom: 1rem;
		display: flex;
		justify-content: space-between;
		align-items: flex-end;
	}
	h1 {
		font-size: 5rem;
		margin: 0;
		line-height: 0.8;
		letter-spacing: -3px;
		background: linear-gradient(180deg, #fff 0%, #888 100%);
		-webkit-background-clip: text; -webkit-text-fill-color: transparent;
	}
	.date {
		font-family: 'JetBrains Mono', monospace;
		color: #666;
		margin-top: 0.5rem;
		letter-spacing: 1px;
	}
	.quote-ticker {
		max-width: 500px;
		text-align: right;
		font-style: italic;
		color: #a1a1aa;
		border-left: 1px solid #333;
		padding-left: 1rem;
	}
	.quote-author {
		display: block;
		font-size: 0.8rem;
		color: #4ade80;
		margin-top: 0.3rem;
		font-style: normal;
		font-family: 'JetBrains Mono', monospace;
	}

	/* --- SECTION HEADERS --- */
	.section-header {
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.9rem;
		color: #4ade80;
		border-bottom: 1px solid #333;
		padding-bottom: 0.5rem;
		margin-bottom: 1.5rem;
		letter-spacing: 2px;
	}

	/* --- COL 1: THE WIRE --- */
	.wire-list { display: flex; flex-direction: column; gap: 1rem; }
	.wire-item {
		display: block;
		text-decoration: none;
		border-left: 1px solid #333;
		padding-left: 1rem;
		transition: 0.2s;
	}
	.wire-item:hover { border-left-color: #fff; }
	.wire-item .timestamp { display: block; font-size: 0.7rem; color: #666; font-family: 'JetBrains Mono'; }
	.wire-item .headline { display: block; color: #ddd; font-size: 0.95rem; margin: 4px 0; line-height: 1.4; }
	.wire-item .source { font-size: 0.75rem; color: #888; text-transform: uppercase; }
	.blink { animation: blink 1s infinite; }

	/* --- COL 2: CENTER --- */
	.opinion-block { margin-top: 4rem; }
	.opinion-card {
		background: rgba(255,255,255,0.03);
		padding: 2rem;
		border: 1px solid rgba(255,255,255,0.1);
	}
	.opinion-card h3 { font-size: 2rem; margin: 0 0 1rem 0; color: #fff; font-family: 'Space Grotesk'; }
	.opinion-card p { font-size: 1.1rem; line-height: 1.6; color: #ccc; }
	.author-tag {
		margin-top: 1.5rem;
		font-family: 'JetBrains Mono';
		font-size: 0.8rem;
		color: #4ade80;
		text-transform: uppercase;
	}

	/* --- COL 3: RIGHT --- */
	.gallery { display: flex; flex-direction: column; gap: 1.5rem; }
	.coolute-card { position: relative; overflow: hidden; border-radius: 8px; }
	.coolute-card img { width: 100%; display: block; filter: grayscale(40%); transition: 0.5s; }
	.coolute-card:hover img { filter: grayscale(0%); transform: scale(1.05); }
	.caption {
		position: absolute; bottom: 0; left: 0; right: 0;
		background: linear-gradient(to top, rgba(0,0,0,0.9), transparent);
		padding: 1rem;
		font-size: 0.8rem; color: #fff;
	}

	.happy-block { margin-top: 3rem; background: rgba(74, 222, 128, 0.05); padding: 1.5rem; border-radius: 8px; border: 1px solid rgba(74, 222, 128, 0.2); }
	.happy-item { display: flex; gap: 10px; margin-bottom: 1rem; align-items: start; }
	.happy-item a { color: #d1fae5; text-decoration: none; line-height: 1.4; }
	.happy-item a:hover { text-decoration: underline; }

	@keyframes blink { 50% { opacity: 0; } }
	
	/* Mobile Responsive */
	@media (max-width: 1024px) {
		.grid-container { grid-template-columns: 1fr; }
		.masthead { flex-direction: column; align-items: flex-start; gap: 1rem; }
		.quote-ticker { text-align: left; border-left: none; padding-left: 0; border-top: 1px solid #333; padding-top: 1rem; width: 100%; }
	}
</style>