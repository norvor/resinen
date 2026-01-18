<script lang="ts">
    import { page } from '$app/stores';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    
    // --- MOCK DATA (Connecting to Reality later) ---
    // This represents a "Vision" or "Chapter" of the community
    let journey = {
        title: "The Iron Code",
        subtitle: "Chapter 1: The Foundation",
        total_steps: 4,
        steps: [
            {
                type: 'text',
                title: "Welcome to the Fortress",
                content: "You have stepped into a sovereign territory. Here, code is law, and reputation is currency. Before you can speak in the Town Square, you must understand our way of life.",
                image: "https://images.unsplash.com/photo-1614728853911-ec4055942f35?q=80&w=2670&auto=format&fit=crop"
            },
            {
                type: 'manifesto',
                title: "Rule #1: Contribution",
                content: "We do not tolerate lurkers. If you consume, you must create. A citizen who does not build is merely a tourist.",
            },
            {
                type: 'quiz',
                title: "Prove Your Understanding",
                question: "What is the primary currency of this territory?",
                options: ["Bitcoin", "Reputation", "Dollars"],
                answer: 1
            },
            {
                type: 'ceremony',
                title: "The Oath",
                content: "I hereby pledge to uphold the Iron Code. I understand that my Citizenship can be revoked by a Jury of my peers at any time.",
            }
        ]
    };

    let currentStepIndex = 0;
    let selectedOption: number | null = null;
    let isCompleted = false;

    // Derived state
    $: currentStep = journey.steps[currentStepIndex];
    $: progress = ((currentStepIndex + 1) / journey.total_steps) * 100;

    function nextStep() {
        if (currentStep.type === 'quiz' && selectedOption !== currentStep.answer) {
            alert("Incorrect. Reread the doctrine.");
            return;
        }

        if (currentStepIndex < journey.total_steps - 1) {
            currentStepIndex++;
            selectedOption = null;
        } else {
            finishJourney();
        }
    }

    function finishJourney() {
        isCompleted = true;
        // In the real app, this sends an API call to grant "Citizen" Role
    }

    function returnToWorld() {
        const slug = $page.params.slug;
        goto(`/communities/${slug}`);
    }
</script>

<div class="fixed inset-0 bg-black text-white z-50 overflow-y-auto flex flex-col">
    
    <div class="h-2 bg-gray-900 w-full">
        <div class="h-full bg-sp-green transition-all duration-500 ease-out" style="width: {progress}%"></div>
    </div>
    
    <div class="p-6 flex justify-between items-center max-w-5xl mx-auto w-full">
        <div class="text-xs font-black uppercase tracking-widest text-gray-500">
            {journey.title} // <span class="text-white">{journey.subtitle}</span>
        </div>
        <button on:click={returnToWorld} class="text-xs font-bold uppercase text-gray-500 hover:text-white transition-colors">
            Exit Vision ✕
        </button>
    </div>

    <div class="flex-grow flex items-center justify-center p-4 md:p-8">
        <div class="max-w-3xl w-full">
            
            {#if isCompleted}
                <div class="text-center animate-fade-in-up">
                    <div class="text-6xl mb-6">🎖️</div>
                    <h1 class="text-5xl md:text-7xl font-black uppercase mb-6 leading-none">Citizenship<br>Granted</h1>
                    <p class="text-xl text-gray-400 font-bold mb-12 max-w-lg mx-auto">
                        You have absorbed the vision. The Town Square is now open to you.
                    </p>
                    <button 
                        on:click={returnToWorld}
                        class="bg-white text-black font-black uppercase text-xl py-6 px-12 hover:bg-sp-green hover:scale-105 transition-all shadow-[8px_8px_0px_0px_rgba(255,255,255,0.2)]"
                    >
                        Enter The Territory
                    </button>
                </div>

            {:else}
                <div class="animate-fade-in">
                    
                    {#if currentStep.image}
                        <div class="w-full h-64 md:h-80 mb-8 overflow-hidden border-4 border-white">
                            <img src={currentStep.image} alt="Vision" class="w-full h-full object-cover" />
                        </div>
                    {/if}

                    <h2 class="text-4xl md:text-6xl font-black uppercase mb-6 leading-tight">{currentStep.title}</h2>
                    
                    {#if currentStep.type === 'text' || currentStep.type === 'manifesto' || currentStep.type === 'ceremony'}
                        <p class="text-xl md:text-2xl text-gray-300 font-medium leading-relaxed mb-12 border-l-4 border-sp-green pl-6">
                            {currentStep.content}
                        </p>
                    {/if}

                    {#if currentStep.type === 'quiz'}
                        <p class="text-2xl font-bold mb-8 text-white">{currentStep.question}</p>
                        <div class="grid gap-4 mb-12">
                            {#each currentStep.options as option, i}
                                <button 
                                    on:click={() => selectedOption = i}
                                    class="text-left p-6 border-2 font-bold text-lg transition-all
                                    {selectedOption === i ? 'bg-white text-black border-white' : 'border-gray-700 hover:border-white text-gray-400'}"
                                >
                                    <span class="mr-4 opacity-50">{i + 1}.</span> {option}
                                </button>
                            {/each}
                        </div>
                    {/if}

                    <div class="flex items-center gap-4 border-t border-gray-800 pt-8">
                        <button 
                            on:click={nextStep}
                            disabled={currentStep.type === 'quiz' && selectedOption === null}
                            class="bg-sp-blue text-white font-black uppercase py-4 px-10 hover:bg-white hover:text-black transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                        >
                            {currentStepIndex === journey.total_steps - 1 ? 'Take The Oath' : 'Next Sequence →'}
                        </button>
                        <div class="text-xs font-mono text-gray-600">
                            STEP {currentStepIndex + 1} / {journey.total_steps}
                        </div>
                    </div>

                </div>
            {/if}

        </div>
    </div>

</div>

<style>
    /* Simple animation for smooth transitions */
    .animate-fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>