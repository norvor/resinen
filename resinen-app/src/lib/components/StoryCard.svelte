<script lang="ts">
    import type { Story } from '$lib/types';
    
    // Svelte 5 Props
    let { story } = $props<{ story: Story }>();
</script>

<article class="spectrum-card">
    <div class="card-header">
        <span class="source-badge">{story.source}</span>
        <span class="timestamp">{story.timestamp}</span>
    </div>

    <h3>{story.headline}</h3>
    <p class="main-summary">{story.summary}</p>

    {#if story.spectrum.length > 0}
        <div class="spectrum-split">
            {#each story.spectrum as spec}
                <div class="perspective">
                    <div class="perspective-header">
                        <span class="ai-name">{spec.perspective}</span>
                        {#if spec.bias}
                            <span class="bias-tag">{spec.bias}</span>
                        {/if}
                    </div>
                    <p class="perspective-text">{spec.summary}</p>
                </div>
            {/each}
        </div>
    {/if}

    <div class="card-footer">
        <a href={story.url} class="read-full">Read Analysis &rarr;</a>
    </div>
</article>

<style>
    .spectrum-card {
        background: #111;
        border: 1px solid #333;
        padding: 1.5rem;
        margin-bottom: 2rem;
        transition: transform 0.2s;
    }
    .spectrum-card:hover {
        border-color: #666;
    }

    .card-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 1rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #666;
    }
    .source-badge {
        color: #4ade80; /* Matrix Green */
        text-transform: uppercase;
        border: 1px solid #4ade80;
        padding: 2px 6px;
        border-radius: 2px;
    }

    h3 {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.8rem;
        line-height: 1.1;
        margin: 0 0 1rem 0;
        color: #eee;
    }

    .main-summary {
        font-size: 1rem;
        color: #aaa;
        line-height: 1.5;
        margin-bottom: 1.5rem;
    }

    /* The Split View for Perspectives */
    .spectrum-split {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        background: #0a0a0a;
        padding: 1rem;
        border-radius: 4px;
        border-left: 2px solid #4ade80;
    }

    .perspective-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
    }
    .ai-name { color: #fff; font-weight: bold; }
    .bias-tag { color: #888; background: #222; padding: 2px 4px; border-radius: 2px; }
    
    .perspective-text {
        font-size: 0.9rem;
        color: #bbb;
        margin: 0;
        line-height: 1.4;
    }

    .card-footer {
        margin-top: 1.5rem;
        text-align: right;
    }
    .read-full {
        color: #fff;
        text-decoration: none;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
    }
    .read-full:hover {
        text-decoration: underline;
        color: #4ade80;
    }

    @media (max-width: 600px) {
        .spectrum-split { grid-template-columns: 1fr; }
    }
</style>