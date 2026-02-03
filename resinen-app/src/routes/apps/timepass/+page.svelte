<script lang="ts">
    import { fly, fade, scale } from 'svelte/transition';
    import { cubicOut } from 'svelte/easing';

    // --- 1. THE LIBRARY OF CALM (15 Moral Stories) ---
    type Story = {
        id: string;
        title: string;
        author: string;
        issue: string;
        color: string;
        summary: string;
        content: string[]; 
    };

    const STORIES: Story[] = [
        {
            id: 's-01',
            title: "The Starfish Thrower",
            author: "Modern Fable",
            issue: "ISSUE #1: IMPACT",
            color: "#10b981", // Emerald
            summary: "A young boy teaches an old man that even small acts can make a world of difference.",
            content: [
                "An old man was walking along a beach after a terrible storm had passed. The vast beach was littered with thousands of starfish that had been washed ashore by the high waves. As he walked, he saw a young boy in the distance, bending down, picking something up, and gently throwing it back into the ocean.",
                "As the old man got closer, he called out, 'Good morning! May I ask what you are doing?' The boy paused, looked up, and replied, 'Throwing starfish back into the ocean. The tide has gone out, and the sun is up. If I don't throw them back, they'll die.'",
                "The old man laughed to himself and said, 'But there are miles and miles of beach and thousands of starfish. You can't possibly make a difference!'",
                "The boy bent down, picked up another starfish, and threw it past the breaking waves into the water. He smiled at the old man and said, 'It made a difference for that one.'",
                "MORAL: Do not let the scale of a problem stop you from doing the good you can do today."
            ]
        },
        {
            id: 's-02',
            title: "The Stone Cutter",
            author: "Japanese Folktale",
            issue: "ISSUE #2: ENVY",
            color: "#f59e0b", // Amber
            summary: "A stone cutter wishes to be everything he is not, only to realize the power he held all along.",
            content: [
                "There was once a stone cutter who was dissatisfied with himself and his position in life. One day he passed a wealthy merchant's house. Seeing the merchant's power, he grew envious and wished he could be a merchant. Suddenly, he became one! He was carried in a luxury sedan chair, envied by all. But soon he felt the heat of the sun and wished he could be the Sun.",
                "He became the Sun, shining fiercely down on the earth, scorching the fields. But then a huge black cloud moved between him and the earth, so he wished to be a Cloud. As a cloud, he flooded the fields and villages, but he found he could not move a giant rock. So he wished to be the Rock.",
                "As the Rock, he felt powerful and immovable. But then he heard a sound: chink, chink, chink. He looked down and saw a stone cutter hammering away at his base. He realized that the stone cutter was more powerful than the rock.",
                "He wished to be himself again, and there he was—a stone cutter, hammering away, perfectly content with who he was.",
                "MORAL: Often, what we seek outside ourselves is already within us."
            ]
        },
        {
            id: 's-03',
            title: "The Farmer's Watch",
            author: "Traditional",
            issue: "ISSUE #3: QUIET",
            color: "#8b5cf6", // Violet
            summary: "A farmer loses his precious watch in a barn and learns that a quiet mind finds what a busy mind misses.",
            content: [
                "A farmer lost his precious watch while working in a barn full of hay. It was a gift from his father and held deep sentimental value. He searched for an hour among the hay but could not find it. Exhausted, he asked a group of children playing outside to help him.",
                "The children searched frantically, tossing the hay here and there, but they too failed to find the watch. The farmer gave up and sat down on a stool, head in his hands. Just then, a little boy came up to him and asked, 'Can I try one more time, but alone?'",
                "The farmer agreed. The boy went into the barn and closed the door. Five minutes later, he came out with the watch in his hand. The farmer was amazed. 'How did you find it when all of us failed?'",
                "The boy replied, 'I didn't do anything. I just sat on the ground and listened. In the silence, I could hear the ticking of the watch, and I just walked to where the sound was coming from.'",
                "MORAL: A quiet mind can perceive what a chaotic mind misses."
            ]
        },
        {
            id: 's-04',
            title: "The Two Wolves",
            author: "Cherokee Legend",
            issue: "ISSUE #4: CHOICE",
            color: "#ec4899", // Pink
            summary: "A grandfather explains the internal battle we all face and how we decide the winner.",
            content: [
                "One evening, an old Cherokee grandfather told his grandson about a battle that goes on inside people. He said, 'My son, the battle is between two wolves inside us all.'",
                "'One is Evil. It is anger, envy, jealousy, sorrow, regret, greed, arrogance, self-pity, guilt, resentment, inferiority, lies, false pride, superiority, and ego.'",
                "'The other is Good. It is joy, peace, love, hope, serenity, humility, kindness, benevolence, empathy, generosity, truth, compassion, and faith.'",
                "The grandson thought about it for a minute and then asked his grandfather: 'Which wolf wins?'",
                "The old Cherokee simply replied, 'The one you feed.'",
                "MORAL: The thoughts and habits you nurture will determine your character."
            ]
        },
        {
            id: 's-05',
            title: "The Cracked Pot",
            author: "Indian Folktale",
            issue: "ISSUE #5: VALUE",
            color: "#3b82f6", // Blue
            summary: "A flawed pot feels useless until it sees the beauty its flaws have created along the path.",
            content: [
                "A water bearer had two large pots, each hung on the ends of a pole which he carried across his neck. One of the pots had a crack in it, while the other pot was perfect and always delivered a full portion of water. At the end of the long walk from the stream to the house, the cracked pot arrived only half full.",
                "For a full two years, this went on daily. The perfect pot was proud of its accomplishments. But the poor cracked pot was ashamed of its own imperfection, and miserable that it could only do half of what it had been made to do.",
                "One day, the cracked pot spoke to the water bearer: 'I am ashamed of myself, because this crack in my side causes water to leak out all the way back to your house.' The bearer said, 'Did you notice that there were flowers only on your side of the path, but not on the other pot's side?'",
                "'That's because I have always known about your flaw, so I planted flower seeds on your side of the path. Every day while we walk back, you water them. For two years I have been able to pick these beautiful flowers to decorate the table. Without you being just the way you are, there would not be this beauty to grace the house.'",
                "MORAL: Our flaws are what make our lives interesting and rewarding."
            ]
        },
        {
            id: 's-06',
            title: "The Invisible String",
            author: "Patrice Karst",
            issue: "ISSUE #6: LOVE",
            color: "#f43f5e", // Rose
            summary: "A lesson that we are never truly alone, connected by love to everyone we hold dear.",
            content: [
                "A mother noticed her children were frightened during a thunderstorm. She gathered them close and told them about the Invisible String. 'What kind of string?' asked the twins.",
                "'People who love each other are always connected by a very special string made of love. Even though you can't see it with your eyes, you can feel it with your heart and know that you are always connected to everyone you love.'",
                "'When you're at school and you miss me, your love travels all the way along the string until I feel a tug on my heart. And when I tug it back, you feel it in your hearts.'",
                "The children asked, 'Does the string go away when you're mad at us?' 'Never,' said the mother. 'Love is stronger than anger, and as long as love is in your heart, the string will always be there.'",
                "MORAL: Distance cannot break the bond of love."
            ]
        },
        {
            id: 's-07',
            title: "The Golden Plate",
            author: "Jataka Tale",
            issue: "ISSUE #7: TRUTH",
            color: "#eab308", // Gold
            summary: "A greedy merchant tries to cheat an old woman, while an honest one gains a fortune.",
            content: [
                "Once, two merchants traveled to a city to sell their wares. An old woman, who had once been rich but was now poor, had an old, grimy plate she wanted to sell. She invited the first merchant in. He scratched the plate and realized it was made of pure gold, but hoping to get it for free, he threw it on the ground and said, 'It is worthless!' thinking he would return later.",
                "Later, the second merchant passed by. The woman called him in. He examined the plate and bowed. 'Mother, this plate is worth more than all my goods and money combined. I cannot afford it.'",
                "The woman was shocked. 'The other merchant threw it on the ground! Because you are honest, I give it to you.' She took only a small coin for her needs and gave him the plate.",
                "When the first merchant returned, the woman chased him away. He lost a fortune because of his greed, while the second merchant gained one through his honesty.",
                "MORAL: Honesty is the highest form of currency."
            ]
        },
        {
            id: 's-08',
            title: "The Butterfly",
            author: "Nature Parable",
            issue: "ISSUE #8: GROWTH",
            color: "#06b6d4", // Cyan
            summary: "A man tries to help a butterfly emerge, only to realize that the struggle was necessary for its flight.",
            content: [
                "A man found a cocoon of a butterfly. One day a small opening appeared, and he sat and watched the butterfly for several hours as it struggled to force its body through that little hole. Then, it seemed to stop making any progress.",
                "So the man decided to help the butterfly. He took a pair of scissors and snipped off the remaining bit of the cocoon. The butterfly then emerged easily. But it had a swollen body and small, shriveled wings.",
                "The man continued to watch the butterfly because he expected that, at any moment, the wings would enlarge and expand to be able to support the body. Neither happened! In fact, the butterfly spent the rest of its life crawling around with a swollen body and shriveled wings. It never was able to fly.",
                "What the man, in his kindness and haste, did not understand was that the restricting cocoon and the struggle required for the butterfly to get through the tiny opening were nature's way of forcing fluid from the body of the butterfly into its wings so that it would be ready for flight.",
                "MORAL: Sometimes struggles are exactly what we need in our life to grow."
            ]
        },
        {
            id: 's-09',
            title: "The Empty Box",
            author: "Zen Story",
            issue: "ISSUE #9: MIND",
            color: "#64748b", // Slate
            summary: "A professor learns that you cannot fill a cup that is already full.",
            content: [
                "A university professor went to visit a famous Zen master to inquire about Zen. The master served tea. He poured his visitor's cup full, and then kept on pouring.",
                "The professor watched the overflow until he no longer could restrain himself. 'It is overfull. No more will go in!'",
                "'Like this cup,' the master said, 'you are full of your own opinions and speculations. How can I show you Zen unless you first empty your cup?'",
                "The professor realized he had come not to learn, but to confirm what he already thought he knew.",
                "MORAL: To learn something new, you must first let go of the old."
            ]
        },
        {
            id: 's-10',
            title: "The Wind & Sun",
            author: "Aesop",
            issue: "ISSUE #10: GENTLE",
            color: "#f97316", // Orange
            summary: "A contest between force and warmth to see who can make a traveler remove his coat.",
            content: [
                "The Wind and the Sun were disputing which was the stronger. Suddenly they saw a traveler coming down the road, wrapped in a heavy coat. They agreed that the one who could make the traveler take his coat off should be considered stronger.",
                "The Wind blew as hard as it could, but the harder he blew, the more closely the traveler wrapped his coat around him. Eventually, the Wind gave up in despair.",
                "Then the Sun came out and shone in all his glory. He did not blow or force; he simply glowed. Within minutes, the traveler felt the warmth, wiped his brow, and took off his heavy coat.",
                "The Wind realized that force is not always the answer.",
                "MORAL: Persuasion and kindness are better than force."
            ]
        },
        {
            id: 's-11',
            title: "The Salt Lake",
            author: "Philosophical",
            issue: "ISSUE #11: PAIN",
            color: "#14b8a6", // Teal
            summary: "A master teaches his apprentice that the size of your world determines the bitterness of your pain.",
            content: [
                "An old master instructed an unhappy apprentice to put a handful of salt in a glass of water and then to drink it. 'How does it taste?' the master asked. 'Awful,' spat the apprentice.",
                "The master chuckled and then asked the young man to take another handful of salt and put it in the lake nearby. The two walked in silence to the nearby lake and the apprentice swirled his handful of salt into the lake. The old man said, 'Now drink from the lake.'",
                "As the water dripped down the apprentice's chin, the master asked, 'How does it taste?' 'Good!' remarked the apprentice. 'Do you taste the salt?' asked the master. 'No,' said the young man.",
                "The master sat beside this troubled young man, took his hands, and said, 'The pain of life is pure salt; no more, no less. However, the amount of bitterness we taste depends on the container we put it into. So when you are in pain, the only thing you can do is to enlarge your sense of things. Stop being a glass. Become a lake.'",
                "MORAL: Expand your perspective to dissolve your pain."
            ]
        },
        {
            id: 's-12',
            title: "The Blind Men",
            author: "Indian Parable",
            issue: "ISSUE #12: VIEW",
            color: "#84cc16", // Lime
            summary: "Six blind men touch an elephant and argue about what it is, learning that everyone holds a piece of the truth.",
            content: [
                "Six blind men lived in a village. One day the villagers told them, 'Hey, there is an elephant in the village today.' They had no idea what an elephant was. They decided, 'Even though we would not be able to see it, let us go and feel it.'",
                "One touched the trunk and said, 'The elephant is like a thick snake!' Another touched the ear and said, 'No, it is like a fan!' The third touched the leg, 'It is a tree trunk!' The fourth touched the side, 'It is a wall!' The fifth touched the tail, 'It is a rope!'",
                "They began to argue, shouting at each other. A wise man was passing by and asked what was wrong. After hearing them, he explained, 'You are all right. The reason every one of you is telling it differently is because each one of you touched a different part of the elephant.'",
                "The blind men realized they were arguing over parts of a whole.",
                "MORAL: Truth is often larger than our single perspective."
            ]
        },
        {
            id: 's-13',
            title: "The Carpenter",
            author: "Workplace Tale",
            issue: "ISSUE #13: LIFE",
            color: "#a855f7", // Purple
            summary: "A retiring carpenter builds one last house with no heart, only to realize the house is for him.",
            content: [
                "An elderly carpenter was ready to retire. He told his employer of his plans to leave the house-building business to live a more leisurely life with his family. The contractor was sorry to see his good worker go and asked if he could build just one more house as a personal favor.",
                "The carpenter agreed, but over time it was easy to see that his heart was not in his work. He resorted to shoddy workmanship and used inferior materials. It was an unfortunate way to end a dedicated career.",
                "When the carpenter finished his work, his employer came to inspect the house. Then he handed the front-door key to the carpenter and said, 'This is your house... my gift to you.'",
                "The carpenter was shocked! If he had only known he was building his own house, he would have done it all so differently. Now he had to live in a home he had built none too well.",
                "MORAL: Build your life with care, for you are the one who must live in it."
            ]
        },
        {
            id: 's-14',
            title: "The Lion & Mouse",
            author: "Aesop",
            issue: "ISSUE #14: HELP",
            color: "#ef4444", // Red
            summary: "A mighty lion spares a mouse, who later saves the lion from a hunter's net.",
            content: [
                "A Lion was asleep in the forest, his great head resting on his paws. A timid little Mouse came upon him unexpectedly, and in her fright and haste to get away, ran across the Lion's nose. Roused from his nap, the Lion laid his huge paw angrily on the tiny creature to kill her.",
                "'Spare me!' begged the poor Mouse. 'Please let me go and some day I will surely repay you.' The Lion was much amused to think that a Mouse could ever help him. But he was generous and finally let the Mouse go.",
                "Some days later, while stalking his prey in the forest, the Lion was caught in the toils of a hunter's net. Unable to free himself, he filled the forest with his angry roaring.",
                "The Mouse knew the voice and quickly found the Lion struggling in the net. Running to one of the great ropes that bound him, she gnawed it until it parted, and soon the Lion was free.",
                "MORAL: No act of kindness, no matter how small, is ever wasted."
            ]
        },
        {
            id: 's-15',
            title: "The Bamboo",
            author: "Chinese Parable",
            issue: "ISSUE #15: FAITH",
            color: "#22c55e", // Green
            summary: "A lesson in patience as a farmer waters a seed for years with no results, until a miracle happens.",
            content: [
                "Like the fern, the Chinese Bamboo tree requires care. A farmer plants the seed, waters it, and fertilizes it. For the first year, he sees nothing. For the second year, he waters and fertilizes, and still sees nothing.",
                "This continues for year three, and year four. There is no sign of life above the soil. People might say, 'Why do you waste your time?' But the farmer keeps faith.",
                "Then, in the fifth year, a tiny sprout breaks through the earth. And within six weeks, the Chinese Bamboo tree grows to be ninety feet tall!",
                "During those first four years, it was growing a massive root system underground to support its potential height. If the farmer had stopped watering it, it would have died.",
                "MORAL: Patience and persistence prepare you for great growth."
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

<svelte:body style:overflow={activeStory ? 'hidden' : ''} />

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
        <div class="rack-carousel">
            {#each STORIES as story, i}
                <button 
                    class="magazine-cover"
                    style="--theme-color: {story.color}"
                    onclick={() => openStory(story)}
                    in:fly={{ y: 30, delay: i * 50, duration: 600, easing: cubicOut }}
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
        height: 100vh; /* Fixed height for carousel layout */
        background: #fdf6e3;
        color: #2c3e50;
        display: flex; flex-direction: column;
        font-family: 'Merriweather', serif;
        overflow: hidden; /* Prevent vertical body scroll */
    }

    /* --- HEADER --- */
    .app-header {
        padding: 20px 40px;
        display: flex; justify-content: space-between; align-items: center;
        border-bottom: 4px double #d4c5a9;
        background: #fff;
        flex-shrink: 0;
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
        flex: 1; 
        background: linear-gradient(to bottom, #fdf6e3, #ece0c8);
        display: flex;
        align-items: center; /* Center books vertically */
        overflow: hidden;
    }
    
    /* CAROUSEL STYLES */
    .rack-carousel {
        display: flex;
        gap: 60px;
        overflow-x: auto;
        padding: 60px 80px;
        width: 100%;
        height: 100%;
        align-items: center;
        scroll-snap-type: x mandatory;
        /* Scrollbar styling */
        scrollbar-width: thin;
        scrollbar-color: #d4c5a9 transparent;
    }
    
    /* Webkit scrollbar specific */
    .rack-carousel::-webkit-scrollbar { height: 8px; }
    .rack-carousel::-webkit-scrollbar-track { background: transparent; }
    .rack-carousel::-webkit-scrollbar-thumb { background: #d4c5a9; border-radius: 4px; }

    /* --- MAGAZINE COVER --- */
    .magazine-cover {
        flex: 0 0 340px; /* Fixed width, no shrinking */
        scroll-snap-align: center;
        
        background: #fff;
        border: none; padding: 0;
        text-align: left;
        display: flex; flex-direction: column;
        height: 520px;
        box-shadow: 
            5px 5px 15px rgba(0,0,0,0.1),
            0 0 0 1px rgba(0,0,0,0.05);
        transition: transform 0.3s, box-shadow 0.3s;
        cursor: pointer;
        position: relative;
    }
    .magazine-cover:hover {
        transform: translateY(-15px);
        box-shadow: 10px 20px 30px rgba(0,0,0,0.15);
    }
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
        overscroll-behavior: contain;
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
        .rack-carousel { padding: 40px 30px; gap: 30px; }
        .magazine-cover { flex: 0 0 280px; height: 420px; }
        .book-content { padding: 40px 25px; }
        .chapter-title { font-size: 2.5rem; }
        .story-text p { font-size: 1.1rem; text-align: left; }
    }
</style>