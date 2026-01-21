<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    import { fade, scale } from 'svelte/transition';

    export let data;
    $: community = data.community;

    let courses: any[] = [];
    let loading = true;
    let showCreate = false;

    let newCourse = {
        title: '',
        description: '',
        difficulty: 'Beginner',
        image_url: ''
    };

    onMount(async () => {
        await loadAcademy();
    });

    async function loadAcademy() {
        loading = true;
        try {
            // Replace with real API call
            // const res = await api.getCourses(community.id);
            // courses = res;
            setTimeout(() => { courses = []; loading = false; }, 500); 
        } catch (e) { loading = false; }
    }

    async function handleCreate() {
        // api.createCourse(community.id, newCourse)
        courses = [...courses, { ...newCourse, id: Date.now(), modules: 0, students: 0 }];
        showCreate = false;
        newCourse = { title: '', description: '', difficulty: 'Beginner', image_url: '' };
    }
</script>

<div class="space-y-8 animate-fade-in-up">
    
    <div class="flex items-end justify-between border-b-4 border-black pb-6">
        <div>
            <div class="text-xs font-black uppercase text-teal-600 tracking-widest mb-1 flex items-center gap-2">
                <span>🎓</span> Academy Engine
            </div>
            <h1 class="text-4xl font-black uppercase tracking-tighter">
                Curriculum Control
            </h1>
        </div>
        <button 
            on:click={() => showCreate = true}
            class="px-6 py-3 bg-teal-600 text-white font-black rounded uppercase text-xs shadow-[4px_4px_0px_black] hover:-translate-y-1 hover:shadow-[6px_6px_0px_black] transition-all"
        >
            + Create Course
        </button>
    </div>

    {#if loading}
        <div class="p-12 text-center text-gray-400 font-bold animate-pulse">Loading Syllabus...</div>
    {:else if courses.length === 0}
        <div class="p-20 text-center border-4 border-dashed border-gray-200 rounded-xl text-gray-400">
            <span class="text-4xl block mb-2">🧠</span>
            <span class="font-bold uppercase tracking-widest">No Courses Created</span>
        </div>
    {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            {#each courses as course}
                <div class="bg-white border-2 border-gray-200 p-6 rounded-xl relative group hover:border-black transition-colors flex flex-col">
                    <div class="flex justify-between items-start mb-4">
                        <div class="w-10 h-10 bg-teal-100 rounded flex items-center justify-center text-xl">📖</div>
                        <span class="px-2 py-1 bg-gray-100 text-[10px] font-bold uppercase rounded">{course.difficulty}</span>
                    </div>
                    
                    <h3 class="font-black text-xl mb-2">{course.title}</h3>
                    <p class="text-sm text-gray-500 mb-6">{course.description}</p>
                    
                    <div class="mt-auto grid grid-cols-2 gap-2 text-center mb-4">
                        <div class="bg-gray-50 p-2 rounded">
                            <div class="text-[10px] font-bold uppercase text-gray-400">Modules</div>
                            <div class="font-black">{course.modules || 0}</div>
                        </div>
                        <div class="bg-gray-50 p-2 rounded">
                            <div class="text-[10px] font-bold uppercase text-gray-400">Students</div>
                            <div class="font-black">{course.students || 0}</div>
                        </div>
                    </div>

                    <div class="flex gap-2">
                        <button class="flex-1 py-2 border-2 border-black text-black font-bold uppercase text-xs hover:bg-black hover:text-white transition-colors">
                            Edit Content
                        </button>
                        <button class="px-3 py-2 border-2 border-red-100 text-red-500 font-bold uppercase text-xs hover:bg-red-500 hover:text-white transition-colors">
                            Delete
                        </button>
                    </div>
                </div>
            {/each}
        </div>
    {/if}

    {#if showCreate}
        <div class="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4 backdrop-blur-sm" transition:fade>
            <div class="bg-white w-full max-w-lg rounded-xl p-8 shadow-2xl" in:scale>
                <h2 class="font-black text-2xl uppercase mb-6">Draft Course</h2>
                
                <div class="space-y-4">
                    <div>
                        <label class="block text-xs font-bold uppercase text-gray-500 mb-1">Title</label>
                        <input bind:value={newCourse.title} class="w-full border-2 border-gray-200 p-3 rounded font-bold focus:border-black outline-none" placeholder="e.g. Intro to Design" />
                    </div>
                    <div>
                        <label class="block text-xs font-bold uppercase text-gray-500 mb-1">Summary</label>
                        <textarea bind:value={newCourse.description} class="w-full border-2 border-gray-200 p-3 rounded font-bold focus:border-black outline-none h-24 resize-none"></textarea>
                    </div>
                    
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs font-bold uppercase text-gray-500 mb-1">Difficulty</label>
                            <select bind:value={newCourse.difficulty} class="w-full border-2 border-gray-200 p-3 rounded font-bold focus:border-black outline-none bg-white">
                                <option>Beginner</option><option>Intermediate</option><option>Advanced</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs font-bold uppercase text-gray-500 mb-1">Cover Image</label>
                            <input bind:value={newCourse.image_url} class="w-full border-2 border-gray-200 p-3 rounded font-bold focus:border-black outline-none" placeholder="URL" />
                        </div>
                    </div>
                </div>

                <div class="flex gap-2 mt-8">
                    <button on:click={() => showCreate = false} class="flex-1 py-3 text-gray-500 font-bold hover:bg-gray-100 rounded">Cancel</button>
                    <button on:click={handleCreate} class="flex-1 py-3 bg-teal-600 text-white font-bold uppercase rounded">Create Course</button>
                </div>
            </div>
        </div>
    {/if}

</div>