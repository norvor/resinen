<script lang="ts">
    import { fly, fade, scale } from 'svelte/transition';
    import { cubicOut } from 'svelte/easing';

    // --- 1. DUMMY DATA (Classic Tales) ---
    type Story = {
        id: string;
        title: string;
        author: string;
        issue: string;
        color: string;
        summary: string;
        content: string[]; // Array of paragraphs
    };

    const STORIES: Story[] = [
        {
            id: 'tp-01',
            title: "The Selfish Giant",
            author: "Oscar Wilde",
            issue: "ISSUE #1: KINDNESS",
            color: "#10b981", // Emerald
            summary: "A giant builds a wall to keep children out of his garden, only to find that winter never leaves.",
            content: [
                "Every afternoon, as they were coming from school, the children used to go and play in the Giant's garden.",
                "It was a large lovely garden, with soft green grass. Here and there over the grass stood beautiful flowers like stars, and there were twelve peach-trees that in the spring-time broke out into delicate blossoms of pink and pearl, and in the autumn bore rich fruit. The birds sat on the trees and sang so sweetly that the children used to stop their games in order to listen to them. 'How happy we are here!' they cried to each other.",
                "One day the Giant came back. He had been to visit his friend the Cornish ogre, and had stayed with him for seven years. After the seven years were over he had said all that he had to say, for his conversation was limited, and he determined to return to his own castle. When he arrived he saw the children playing in the garden.",
                "'What are you doing here?' he cried in a very gruff voice, and the children ran away.",
                "'My own garden is my own garden,' said the Giant; 'any one can understand that, and I will allow nobody to play in it but myself.' So he built a high wall all round it, and put up a notice-board: TRESPASSERS WILL BE PROSECUTED.",
                "He was a very selfish Giant."
            ]
        },
        {
            id: 'tp-02',
            title: "The Velveteen Rabbit",
            author: "Margery Williams",
            issue: "ISSUE #2: REAL",
            color: "#f59e0b", // Amber
            summary: "A stuffed rabbit's quest to become Real through the love of his owner.",
            content: [
                "There was once a velveteen rabbit, and in the beginning he was really splendid. He was fat and bunchy, as a rabbit should be; his coat was spotted brown and white, he had real thread whiskers, and his ears were lined with pink sateen. On Christmas morning, when he sat wedged in the top of the Boy's stocking, with a sprig of holly between his paws, the effect was charming.",
                "There were other things in the stocking, nuts and oranges and a toy engine, and chocolate almonds and a clockwork mouse, but the Rabbit was quite the best of all. For at least two hours the Boy loved him, and then Aunts and Uncles came to dinner, and there was a great rustling of tissue paper and unwrapping of parcels, and in the excitement of looking at all the new presents the Velveteen Rabbit was forgotten.",
                "For a long time he lived in the toy cupboard or on the nursery floor, and no one thought very much about him. He was naturally shy, and being only made of velveteen, some of the more expensive toys quite snubbed him. The mechanical toys were very superior, and looked down upon every one else; they were full of modern ideas, and pretended they were real.",
                "'What is REAL?' asked the Rabbit one day, when they were lying side by side near the nursery fender, before Nana came to tidy the room. 'Does it mean having things that buzz inside you and a stick-out handle?'",
                "'Real isn't how you are made,' said the Skin Horse. 'It's a thing that happens to you. When a child loves you for a long, long time, not just to play with, but REALLY loves you, then you become Real.'"
            ]
        },
        {
            id: 'tp-03',
            title: "The Emperor's New Clothes",
            author: "H.C. Andersen",
            issue: "ISSUE #3: TRUTH",
            color: "#8b5cf6", // Violet
            summary: "Two weavers promise an emperor a new suit of clothes that is invisible to those who are unfit for their positions.",
            content: [
                "Many years ago there lived an Emperor, who was so excessively fond of new clothes, that he spent all his money in dress. He did not care for his soldiers, nor for the theatre, nor for driving in the woods, except for the sake of showing off his new clothes. He had a costume for every hour in the day.",
                "One day two swindlers came to this great city; they made people believe that they were weavers, and declared they could manufacture the finest cloth to be imagined. Their colours and patterns, they said, were not only exceptionally beautiful, but the clothes made of their material possessed the wonderful quality of being invisible to any man who was unfit for his office or unpardonably stupid.",
                "'That must be wonderful cloth,' thought the Emperor. 'If I were to be dressed in a suit made of this cloth I should be able to find out which men in my empire were unfit for their places, and I could distinguish the clever from the stupid.'",
                "So he gave the two swindlers a great deal of money beforehand, in order that they might begin their work at once."
            ]
        }
    ];

    // --- 2. STATE ---
    let activeStory = $state<Story | null>(null);

    function openStory(story: Story) {
        activeStory = story;
    }

    function closeStory() {
        activeStory = null;
    }
</script>

<svelte:head>
    <title>TimePass Magazine</title>
</svelte:head>

<div class="magazine-bg">
    
    <header class="app-header">
        <div class="brand">
            <span class="logo-icon">⏳</span>
            <div class="titles">
                <h1>TimePass</h1>
                <span class="subtitle">TALES FOR THE CURIOUS</span>
            </div>
        </div>
        <a href="/" class="exit-btn">Exit to OS</a>
    </header>

    <main class="rack-container">
        <div class="rack-grid">
            {#each STORIES as story, i}
                <button 
                    class="magazine-cover"
                    style="--theme-color: {story.color}"
                    onclick={() => openStory(story)}
                    in:fly={{ y: 30, delay: i * 100, duration: 600, easing: cubicOut }}
                >
                    <div class="cover-art">
                        <div class="issue-badge">{story.issue}</div>
                        <h2 class="cover-title">{story.title}</h2>
                        <span class="cover-author">By {story.author}</span>
                    </div>
                    <div class="cover-footer">
                        <p>{story.summary}</p>
                        <span class="read-btn">READ NOW &rarr;</span>
                    </div>
                </button>
            {/each}
        </div>
    </main>

    {#if activeStory}
        <div class="reader-overlay" transition:fade={{ duration: 200 }}>
            <div 
                class="reader-book"
                in:scale={{ start: 0.95, duration: 300, easing: cubicOut }}
            >
                <div class="book-header" style="background: {activeStory.color}">
                    <button class="back-btn" onclick={closeStory}>&larr; Back to Rack</button>
                    <span class="book-issue">{activeStory.issue}</span>
                </div>

                <div class="book-content">
                    <h1 class="chapter-title">{activeStory.title}</h1>
                    <h3 class="chapter-author">{activeStory.author}</h3>
                    
                    <div class="separator">***</div>

                    <article class="story-text">
                        {#each activeStory.content as paragraph}
                            <p>{paragraph}</p>
                        {/each}
                    </article>

                    <div class="end-mark">
                        <span>THE END</span>
                    </div>
                </div>
            </div>
        </div>
    {/if}

</div>

<style>
    @import url('https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,300;0,400;0,700;1,300&family=Playfair+Display:wght@700;900&display=swap');

    /* --- LAYOUT --- */
    .magazine-bg {
        min-height: 100vh;
        background: #fdf6e3; /* Creamy paper background */
        color: #2c3e50;
        display: flex; flex-direction: column;
        font-family: 'Merriweather', serif;
    }

    /* --- HEADER --- */
    .app-header {
        padding: 20px 40px;
        display: flex; justify-content: space-between; align-items: center;
        border-bottom: 4px double #d4c5a9;
        background: #fff;
    }
    
    .brand { display: flex; align-items: center; gap: 15px; }
    .logo-icon { font-size: 2.5rem; }
    .titles { display: flex; flex-direction: column; }
    .titles h1 {
        font-family: 'Playfair Display', serif;
        font-size: 2rem; margin: 0; line-height: 1;
        letter-spacing: -1px;
    }
    .subtitle {
        font-family: sans-serif; font-size: 0.7rem; letter-spacing: 2px;
        color: #888; font-weight: 700; margin-top: 5px;
    }

    .exit-btn {
        text-decoration: none; color: #e74c3c; font-weight: 700;
        font-family: sans-serif; font-size: 0.9rem;
        border: 2px solid #e74c3c; padding: 8px 16px; border-radius: 30px;
        transition: 0.2s;
    }
    .exit-btn:hover { background: #e74c3c; color: #fff; }

    /* --- MAGAZINE RACK --- */
    .rack-container {
        flex: 1; padding: 60px;
        background: linear-gradient(to bottom, #fdf6e3, #ece0c8);
    }
    .rack-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
        gap: 40px;
        max-width: 1400px; margin: 0 auto;
    }

    /* --- MAGAZINE COVER --- */
    .magazine-cover {
        background: #fff;
        border: none; padding: 0;
        text-align: left;
        display: flex; flex-direction: column;
        height: 480px;
        box-shadow: 
            5px 5px 15px rgba(0,0,0,0.1),
            0 0 0 1px rgba(0,0,0,0.05);
        transition: transform 0.3s, box-shadow 0.3s;
        cursor: pointer;
        position: relative;
    }
    .magazine-cover:hover {
        transform: translateY(-10px);
        box-shadow: 10px 20px 30px rgba(0,0,0,0.15);
    }
    /* Colorful spine on the left */
    .magazine-cover::before {
        content: ''; position: absolute; left: 0; top: 0; bottom: 0;
        width: 10px; background: var(--theme-color);
        opacity: 0.8;
    }

    .cover-art {
        flex: 2;
        background: var(--theme-color);
        padding: 30px;
        color: #fff;
        display: flex; flex-direction: column; justify-content: center;
        position: relative;
        overflow: hidden;
    }
    /* Texture overlay for cover */
    .cover-art::after {
        content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: radial-gradient(circle, transparent 20%, rgba(0,0,0,0.2) 100%);
    }
    
    .issue-badge {
        font-family: sans-serif; font-weight: 700; font-size: 0.7rem; letter-spacing: 1px;
        opacity: 0.8; margin-bottom: 20px;
    }
    .cover-title {
        font-family: 'Playfair Display', serif; font-size: 2.5rem; margin: 0 0 10px 0;
        line-height: 1.1; z-index: 1;
    }
    .cover-author {
        font-family: 'Merriweather', serif; font-style: italic; z-index: 1;
    }

    .cover-footer {
        flex: 1; padding: 25px;
        display: flex; flex-direction: column; justify-content: space-between;
    }
    .cover-footer p {
        font-size: 0.95rem; line-height: 1.6; color: #555;
        margin: 0;
        display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
    }
    .read-btn {
        font-family: sans-serif; font-weight: 900; font-size: 0.8rem;
        color: var(--theme-color); text-transform: uppercase; letter-spacing: 1px;
    }

    /* --- READER MODE --- */
    .reader-overlay {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(253, 246, 227, 0.95);
        backdrop-filter: blur(5px);
        z-index: 100;
        display: flex; justify-content: center; align-items: flex-start;
        overflow-y: auto;
    }

    .reader-book {
        width: 100%; max-width: 800px;
        background: #fff;
        min-height: 100vh;
        box-shadow: 0 0 50px rgba(0,0,0,0.1);
        display: flex; flex-direction: column;
    }

    .book-header {
        padding: 15px 30px;
        color: #fff;
        display: flex; justify-content: space-between; align-items: center;
        position: sticky; top: 0;
    }
    .back-btn {
        background: rgba(0,0,0,0.2); border: none; color: #fff;
        padding: 8px 16px; border-radius: 20px; cursor: pointer;
        font-family: sans-serif; font-weight: 600; font-size: 0.85rem;
        transition: 0.2s;
    }
    .back-btn:hover { background: rgba(0,0,0,0.3); }
    .book-issue { font-family: sans-serif; font-weight: 700; font-size: 0.8rem; letter-spacing: 1px; opacity: 0.9; }

    .book-content {
        padding: 60px 80px 100px 80px;
    }

    .chapter-title {
        font-family: 'Playfair Display', serif; font-size: 3.5rem; margin: 0 0 10px 0;
        text-align: center; color: #1a1a1a;
    }
    .chapter-author {
        text-align: center; font-style: italic; color: #666; font-weight: 400;
        margin-bottom: 40px;
    }
    .separator { text-align: center; color: #ccc; margin: 30px 0; letter-spacing: 5px; }

    .story-text p {
        font-size: 1.25rem; line-height: 1.8; margin-bottom: 1.5rem;
        color: #333; text-align: justify;
    }
    .story-text p:first-of-type::first-letter {
        font-family: 'Playfair Display', serif;
        font-size: 3.5rem; float: left; line-height: 0.8;
        padding-right: 10px; padding-top: 5px;
    }

    .end-mark {
        text-align: center; margin-top: 80px;
        border-top: 1px solid #eee; padding-top: 40px;
    }
    .end-mark span {
        font-family: sans-serif; font-weight: 900; letter-spacing: 3px;
        color: #ccc; font-size: 0.8rem;
    }

    /* RESPONSIVE */
    @media (max-width: 768px) {
        .rack-grid { grid-template-columns: 1fr; }
        .book-content { padding: 40px 25px; }
        .chapter-title { font-size: 2.5rem; }
        .story-text p { font-size: 1.1rem; text-align: left; }
    }
</style>