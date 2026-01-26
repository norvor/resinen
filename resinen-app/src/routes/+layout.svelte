<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';
	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous">
	<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Space+Grotesk:wght@300;500;700&display=swap" rel="stylesheet">
</svelte:head>

<div class="ocean-container">
	<div class="wave"></div>
	<div class="wave"></div>
	<div class="noise-overlay"></div>
	
	<div class="content-wrapper">
		{@render children()}
	</div>
</div>

<style>
	:global(body) {
		margin: 0;
		padding: 0;
		background-color: #050505; /* Deepest Void */
		color: #e0e0e0;
		font-family: 'Space Grotesk', sans-serif;
		overflow-x: hidden;
	}

	.ocean-container {
		position: relative;
		min-height: 100vh;
		width: 100%;
		overflow: hidden;
		background: radial-gradient(circle at 50% 10%, #1a1f35 0%, #050505 80%);
	}

	/* The Ocean Waves - Slow, hypnotic movement */
	.wave {
		position: absolute;
		top: -50%;
		left: -50%;
		width: 200%;
		height: 200%;
		background: radial-gradient(circle at 50% 50%, rgba(76, 175, 80, 0.03), transparent 60%);
		animation: drift 25s infinite linear;
		pointer-events: none;
		z-index: 0;
	}
	.wave:nth-child(2) {
		background: radial-gradient(circle at 60% 40%, rgba(56, 189, 248, 0.04), transparent 50%);
		animation-duration: 35s;
		animation-direction: reverse;
	}

	.noise-overlay {
		position: fixed;
		top: 0; left: 0; width: 100%; height: 100%;
		opacity: 0.03;
		pointer-events: none;
		background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
		z-index: 1;
	}

	.content-wrapper {
		position: relative;
		z-index: 2;
	}

	@keyframes drift {
		from { transform: rotate(0deg); }
		to { transform: rotate(360deg); }
	}
</style>