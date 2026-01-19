<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    export let community: any;

    let modules: any[] = [];
    let loading = true;

    async function loadCurriculum() {
        try {
            modules = await api.getCurriculum(community.id);
        } catch (e) {
            console.error(e);
        } finally {
            loading = false;
        }
    }

    onMount(loadCurriculum);

    async function finish(lessonId: string) {
        try {
            await api.completeLesson(lessonId);
            // Optimistic update: Find the lesson and mark it complete
            modules = modules.map(m => ({
                ...m,
                lessons: m.lessons.map((l: any) => 
                    l.id === lessonId ? {...l, is_completed: true} : l
                )
            }));
        } catch (e) {
            console.error(e);
        }
    }
</script>

{#if loading}
    <div class="p-8 text-center animate-pulse text-skin-muted font-bold uppercase">Loading Curriculum...</div>
{:else}
    <div class="space-y-10">
        {#each modules as mod, i}
            <div class="relative">
                <div class="flex items-end gap-4 mb-6 border-b border-skin-border pb-4">
                    <div class="text-4xl font-black text-skin-accent/20 absolute -top-4 -left-4 select-none pointer-events-none">
                        0{i + 1}
                    </div>
                    <div class="relative z-10">
                        <h2 class="text-xl font-black uppercase tracking-tight text-skin-text">{mod.title}</h2>
                        <p class="text-xs text-skin-muted font-bold uppercase tracking-wider">{mod.description}</p>
                    </div>
                </div>
                
                <div class="grid gap-3">
                    {#each mod.lessons as lesson}
                        <div class="bg-skin-surface border border-skin-border p-4 rounded-lg flex items-center justify-between group transition-all hover:border-skin-accent/50
                            {lesson.is_completed ? 'opacity-60 bg-skin-fill border-dashed' : 'opacity-100 shadow-sm'}">
                            
                            <div class="flex items-center gap-4">
                                <div class="w-10 h-10 rounded-full border-2 flex items-center justify-center font-black text-sm transition-colors shrink-0
                                    {lesson.is_completed 
                                        ? 'bg-green-500 border-green-500 text-skin-fill' 
                                        : 'border-skin-border text-skin-muted bg-skin-fill'}">
                                    {lesson.is_completed ? '✓' : i + 1 + '.' + (lesson.order_index + 1)}
                                </div>
                                
                                <div>
                                    <div class="font-bold text-sm text-skin-text {lesson.is_completed ? 'line-through decoration-skin-muted' : ''}">
                                        {lesson.title}
                                    </div>
                                    <div class="flex items-center gap-2 mt-1">
                                        <span class="text-[10px] uppercase font-bold text-skin-muted bg-skin-fill px-1.5 py-0.5 rounded border border-skin-border/50">
                                            {lesson.duration_min} min
                                        </span>
                                        {#if lesson.video_url}
                                            <span class="text-[10px] uppercase font-bold text-skin-accent">▶ Video</span>
                                        {/if}
                                    </div>
                                </div>
                            </div>
                            
                            {#if !lesson.is_completed}
                                <button on:click={() => finish(lesson.id)} class="text-[10px] font-black uppercase bg-skin-fill hover:bg-skin-accent hover:text-white px-4 py-2 border border-skin-border transition-colors rounded">
                                    Mark Done
                                </button>
                            {/if}
                        </div>
                    {/each}
                </div>
            </div>
        {/each}

        {#if modules.length === 0}
            <div class="p-12 text-center border-2 border-dashed border-skin-border rounded-xl">
                <div class="text-4xl mb-2">🎓</div>
                <div class="font-bold text-skin-muted uppercase tracking-widest text-xs">No Curriculum Found</div>
            </div>
        {/if}
    </div>
{/if}