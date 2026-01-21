<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';

    export let communityId: string;

    let nextLesson: any = null;
    let moduleTitle: string = '';
    let loading = true;
    let completing = false;

    // Fallback Mock
    const MOCK_LESSON = {
        id: 'demo',
        title: 'Intro to Game Theory',
        xp: 100,
        is_completed: false
    };

    onMount(async () => {
        try {
            const modules = await api.getCurriculum(communityId);
            // Find the first module with an incomplete lesson
            for (const mod of modules) {
                const incomplete = mod.lessons.find((l: any) => !l.is_completed);
                if (incomplete) {
                    nextLesson = incomplete;
                    moduleTitle = mod.title;
                    break;
                }
            }
        } catch {
            nextLesson = null;
        } finally {
            loading = false;
        }
    });

    async function handleComplete() {
        if (!nextLesson) return;
        completing = true;
        try {
            await api.completeLesson(nextLesson.id);
            nextLesson.is_completed = true;
            // Visual feedback delay before removing/updating
        } catch (e) {
            alert("Failed to submit assignment.");
            completing = false;
        }
    }
</script>

<div class="h-full w-full">
    {#if loading}
        <div class="h-full bg-white animate-pulse rounded-2xl border border-zinc-200"></div>
    {:else if nextLesson || MOCK_LESSON}
        {@const l = nextLesson || MOCK_LESSON}
        
        <div class="h-full bg-white rounded-2xl border border-zinc-300 shadow-[0_4px_0_#e4e4e7] p-6 flex flex-col justify-between relative group hover:-translate-y-1 hover:shadow-[0_8px_0_#e4e4e7] transition-all duration-300">
            
            <div class="absolute top-0 left-8 bottom-0 w-[1px] bg-red-100 z-0"></div>
            <div class="absolute top-8 left-0 right-0 h-[1px] bg-blue-100 z-0"></div>

            <div class="relative z-10">
                <div class="flex justify-between items-start mb-2">
                    <span class="text-[9px] font-black uppercase text-zinc-400 bg-zinc-100 px-1.5 py-0.5 rounded">
                        {moduleTitle || 'Curriculum'}
                    </span>
                    <span class="text-[9px] font-bold text-blue-600">+{l.xp} XP</span>
                </div>
                <h3 class="text-xl font-serif font-bold italic text-zinc-800 leading-tight">
                    {l.title}
                </h3>
            </div>

            <div class="relative z-10 mt-4">
                {#if l.is_completed}
                    <div class="w-full py-2 bg-green-100 text-green-700 text-center rounded-lg border border-green-200">
                        <span class="text-xs font-black uppercase">Assignment Complete</span>
                    </div>
                {:else}
                    <button 
                        on:click={handleComplete}
                        disabled={completing}
                        class="w-full py-2 bg-zinc-900 text-white text-xs font-black uppercase rounded shadow-lg hover:bg-blue-700 hover:shadow-blue-500/20 transition-all flex items-center justify-center gap-2"
                    >
                        {#if completing}
                            <span>Studying...</span>
                        {:else}
                            <span>Complete Lesson</span>
                            <span class="text-[9px] opacity-70">-></span>
                        {/if}
                    </button>
                {/if}
            </div>

            <div class="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cream-paper.png')] opacity-20 pointer-events-none rounded-2xl"></div>
        </div>
    {:else}
        <div class="h-full bg-zinc-50 rounded-2xl border-2 border-dashed border-zinc-200 flex items-center justify-center flex-col text-zinc-400">
            <span class="text-2xl mb-1">🎓</span>
            <span class="text-[10px] font-bold uppercase">No Classes</span>
        </div>
    {/if}
</div>