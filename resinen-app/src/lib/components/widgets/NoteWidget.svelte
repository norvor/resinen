<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { api } from '$lib/api';
    import { Editor } from '@tiptap/core';
    import StarterKit from '@tiptap/starter-kit';
    import Placeholder from '@tiptap/extension-placeholder';
    import Typography from '@tiptap/extension-typography';

    // --- ROBUST ICONS (Thick Strokes) ---
    // Using Lucide/Feather standard paths for maximum visibility
    const icons = {
        bold: "M6 4h8a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z M6 12h9a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z",
        italic: "M19 4h-9 M14 20H5 M15 4L9 20",
        strike: "M5 12h14 M11 5a4 4 0 0 0-4 4 M13 19a4 4 0 0 0 4-4",
        bullet: "M8 6h13 M8 12h13 M8 18h13 M3 6h.01 M3 12h.01 M3 18h.01",
        number: "M10 6h11 M10 12h11 M10 18h11 M4 6h1v4h-1 M4 10h2",
        quote: "M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V20c0 1 0 1 1 1z",
        code: "M16 18l6-6-6-6 M8 6l-6 6 6 6"
    };

    // --- STATE ---
    let editor: Editor;
    let element: HTMLElement;
    let title = $state("Untitled");
    let status = $state("Synced");
    let noteId: number | null = null;
    let activeType = $state("paragraph");
    let currentTheme = $state('modern'); 

    // --- INIT ---
    onMount(async () => {
        let content = "";
        try {
            const data = await api.widgets.loadDashboard();
            const note = data.notes[0];
            if (note) {
                noteId = note.id;
                title = note.title; 
                content = note.content;
            }
        } catch(e) {}

        editor = new Editor({
            element,
            extensions: [
                StarterKit,
                Typography,
                Placeholder.configure({ placeholder: "Start writing..." }),
            ],
            content,
            editorProps: { attributes: { class: 'prose-mirror' } },
            onTransaction: () => {
                if (editor.isActive('heading', { level: 1 })) activeType = 'h1';
                else if (editor.isActive('heading', { level: 2 })) activeType = 'h2';
                else activeType = 'paragraph';
                editor = editor; 
            },
            onUpdate: debounceSave
        });
    });

    onDestroy(() => editor?.destroy());

    // --- ACTIONS ---
    function setType(e: Event) {
        const type = (e.target as HTMLSelectElement).value;
        if (type === 'paragraph') editor.chain().focus().setParagraph().run();
        if (type === 'h1') editor.chain().focus().toggleHeading({ level: 1 }).run();
        if (type === 'h2') editor.chain().focus().toggleHeading({ level: 2 }).run();
    }

    function toggle(type: string) {
        switch(type) {
            case 'bold': editor.chain().focus().toggleBold().run(); break;
            case 'italic': editor.chain().focus().toggleItalic().run(); break;
            case 'strike': editor.chain().focus().toggleStrike().run(); break;
            case 'bullet': editor.chain().focus().toggleBulletList().run(); break;
            case 'number': editor.chain().focus().toggleOrderedList().run(); break;
            case 'quote': editor.chain().focus().toggleBlockquote().run(); break;
            case 'code': editor.chain().focus().toggleCodeBlock().run(); break;
        }
    }

    // --- SAVING ---
    let timer: any;
    function debounceSave() { 
        status = "Saving..."; 
        clearTimeout(timer); 
        timer = setTimeout(save, 1000); 
    }

    async function save() {
        if (!editor) return;
        const html = editor.getHTML();
        try {
            if (noteId) await api.widgets.updateNote(noteId, { title, content: html });
            else { const res = await api.widgets.createNote(title, html); noteId = res.id; }
            status = "Synced";
        } catch(e) { status = "Error"; }
    }
</script>

<div class="card app-root theme-{currentTheme}">
    
    <div class="app-header">
        <div class="file-info">
            <span class="app-icon">
                {#if currentTheme === 'modern'}📄
                {:else if currentTheme === 'retro'}📜
                {:else}👾{/if}
            </span>
            <input 
                type="text" 
                class="file-title" 
                bind:value={title} 
                oninput={debounceSave} 
                placeholder="Note Title" 
            />
        </div>
        
        <div class="header-controls">
            <span class="status">{status}</span>
            <div class="theme-switcher">
                <button class:active={currentTheme==='modern'} onclick={() => currentTheme = 'modern'} title="Modern">M</button>
                <button class:active={currentTheme==='retro'} onclick={() => currentTheme = 'retro'} title="Retro">R</button>
                <button class:active={currentTheme==='cyber'} onclick={() => currentTheme = 'cyber'} title="Cyber">C</button>
            </div>
        </div>
    </div>

    <div class="toolbar-float-container">
        <div class="glass-toolbar">
            
            <div class="tools-section">
                <select value={activeType} onchange={setType} class="format-select">
                    <option value="paragraph">Normal</option>
                    <option value="h1">Heading 1</option>
                    <option value="h2">Heading 2</option>
                </select>
                
                <div class="sep"></div>

                <button class:active={editor?.isActive('bold')} onclick={() => toggle('bold')}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d={icons.bold}/>
                    </svg>
                </button>
                
                <button class:active={editor?.isActive('italic')} onclick={() => toggle('italic')}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d={icons.italic}/>
                    </svg>
                </button>
                
                <button class:active={editor?.isActive('strike')} onclick={() => toggle('strike')}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d={icons.strike}/>
                    </svg>
                </button>
            </div>

            <div class="tools-section">
                <button class:active={editor?.isActive('bulletList')} onclick={() => toggle('bullet')}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d={icons.bullet}/>
                    </svg>
                </button>
                
                <button class:active={editor?.isActive('orderedList')} onclick={() => toggle('number')}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d={icons.number}/>
                    </svg>
                </button>
                
                <div class="sep"></div>
                
                <button class:active={editor?.isActive('blockquote')} onclick={() => toggle('quote')}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d={icons.quote}/>
                    </svg>
                </button>
                
                <button class:active={editor?.isActive('codeBlock')} onclick={() => toggle('code')}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d={icons.code}/>
                    </svg>
                </button>
            </div>

        </div>
    </div>

    <div class="app-workspace" onclick={() => editor?.commands.focus()}>
        <div class="page-sheet">
            <div bind:this={element}></div>
        </div>
    </div>

</div>

<style>
    /* --- GLOBAL --- */
    .app-root {
        display: flex; flex-direction: column;
        height: 100%; min-height: 650px;
        border-radius: 12px; overflow: hidden;
        border: 1px solid transparent;
        position: relative;
    }

    /* HEADER */
    .app-header {
        display: flex; justify-content: space-between; align-items: center;
        padding: 12px 20px; z-index: 30; background: inherit;
    }
    .file-info { display: flex; align-items: center; gap: 10px; flex: 1; }
    .file-title {
        background: transparent; border: none; outline: none;
        font-size: 1.2rem; font-weight: 700; width: 100%;
    }
    .header-controls { display: flex; align-items: center; gap: 15px; }
    .status { font-size: 0.75rem; opacity: 0.7; font-weight: 500; }

    /* THEME SWITCHER */
    .theme-switcher {
        display: flex; gap: 4px; background: rgba(0,0,0,0.05); 
        padding: 3px; border-radius: 8px;
    }
    .theme-switcher button {
        width: 26px; height: 26px; font-size: 0.75rem; font-weight: 800;
        border-radius: 6px; border: none; cursor: pointer;
        display: flex; align-items: center; justify-content: center;
        transition: 0.2s;
    }

    /* --- TOOLBAR (CRITICAL FIXES) --- */
    .toolbar-float-container {
        position: sticky; top: 10px; z-index: 100;
        display: flex; justify-content: center;
        padding: 0 20px; pointer-events: none;
    }

    .glass-toolbar {
        pointer-events: auto;
        display: flex; justify-content: space-between; align-items: center; gap: 20px;
        padding: 8px 16px; border-radius: 12px;
        backdrop-filter: blur(16px) saturate(180%);
        -webkit-backdrop-filter: blur(16px) saturate(180%);
        box-shadow: 0 10px 40px -10px rgba(0,0,0,0.3);
    }

    .tools-section { display: flex; align-items: center; gap: 6px; }
    
    .sep { 
        width: 1px; height: 20px; margin: 0 8px; 
        background: currentColor; opacity: 0.3; 
    }
    
    .glass-toolbar button {
        width: 36px; height: 36px; border-radius: 6px; border: none; cursor: pointer;
        display: flex; align-items: center; justify-content: center; background: transparent;
        color: inherit; /* This ensures it takes the theme color */
        transition: 0.1s;
    }
    .glass-toolbar button:hover { background: rgba(0,0,0,0.1); }
    
    .format-select {
        background: transparent; border: none; outline: none; cursor: pointer;
        font-size: 0.9rem; font-weight: 700; color: inherit; padding: 4px;
    }

    /* WORKSPACE */
    .app-workspace {
        flex: 1; overflow-y: auto; padding: 0;
        display: flex; justify-content: center; scroll-behavior: smooth;
    }
    .page-sheet {
        width: 100%; max-width: 800px; min-height: 100%;
        padding: 40px 50px 100px 50px; cursor: text; transition: 0.3s;
    }
    .page-sheet:focus { outline: none; }


    /* =========================================
       THEME 1: MODERN
       ========================================= */
    .theme-modern { background: #f3f4f6; color: #1f2937; font-family: 'Inter', sans-serif; border: 1px solid #e5e7eb; }
    .theme-modern .app-header { background: #fff; border-bottom: 1px solid #e5e7eb; }
    .theme-modern .file-title { color: #111; }
    
    /* Modern Toolbar: White glass, Black icons */
    .theme-modern .glass-toolbar {
        background: rgba(255, 255, 255, 0.95); 
        border: 1px solid rgba(0,0,0,0.1);
        color: #000000; /* FORCE BLACK ICONS */
    }
    .theme-modern .glass-toolbar button.active { background: #000; color: #fff; }

    .theme-modern .page-sheet { background: #ffffff; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-top: 20px; border-radius: 6px; }
    .theme-modern .theme-switcher { background: #e5e7eb; }
    .theme-modern .theme-switcher button.active { background: #000; color: #fff; }

    /* Modern Type */
    .theme-modern :global(.prose-mirror) { line-height: 1.6; font-size: 16px; }
    .theme-modern :global(h1) { font-size: 2.2em; font-weight: 700; color: #111; margin-top: 1em; }


    /* =========================================
       THEME 2: RETRO
       ========================================= */
    .theme-retro { background: #2a2a2a; color: #111; font-family: 'Courier Prime', monospace; border: 1px solid #000; }
    .theme-retro .app-header { background: #333; color: #ddd; border-bottom: 1px solid #111; }
    .theme-retro .file-title { color: #facc15; text-transform: uppercase; letter-spacing: 1px; }

    /* Retro Toolbar: Off-white glass, Black icons */
    .theme-retro .glass-toolbar {
        background: #e5e5e5; /* Opaque Grey-White */
        border: 2px solid #000;
        box-shadow: 4px 4px 0px #000;
        color: #000000; /* FORCE BLACK ICONS */
    }
    .theme-retro .glass-toolbar button:hover { background: #ccc; }
    .theme-retro .glass-toolbar button.active { background: #000; color: #facc15; }

    .theme-retro .page-sheet { background: #fdfbf7; box-shadow: 0 0 20px rgba(0,0,0,0.5); margin-top: 20px; }
    .theme-retro .theme-switcher { background: #111; }
    .theme-retro .theme-switcher button { color: #666; }
    .theme-retro .theme-switcher button.active { background: #facc15; color: #000; }

    /* Retro Type */
    .theme-retro :global(.prose-mirror) { line-height: 1.4; font-size: 15px; }
    .theme-retro :global(h1) { font-size: 1.8em; font-weight: bold; text-transform: uppercase; border-bottom: 3px double #000; margin-top: 1.5em; }


    /* =========================================
       THEME 3: CYBER
       ========================================= */
    .theme-cyber { background: #020617; color: #e2e8f0; font-family: 'JetBrains Mono', monospace; border: 1px solid #1e293b; }
    .theme-cyber .app-header { background: #020617; border-bottom: 1px solid #1e293b; }
    .theme-cyber .file-title { color: #2dd4bf; text-shadow: 0 0 8px rgba(45, 212, 191, 0.4); }

    /* Cyber Toolbar: Dark glass, Neon icons */
    .theme-cyber .glass-toolbar {
        background: rgba(15, 23, 42, 0.9); 
        border: 1px solid rgba(45, 212, 191, 0.4);
        box-shadow: 0 0 15px rgba(45, 212, 191, 0.15);
        color: #2dd4bf; /* NEON TEAL ICONS */
    }
    .theme-cyber .glass-toolbar button:hover { background: rgba(45, 212, 191, 0.15); color: #fff; }
    .theme-cyber .glass-toolbar button.active { background: #2dd4bf; color: #000; box-shadow: 0 0 10px #2dd4bf; }

    .theme-cyber .page-sheet { background: transparent; }
    .theme-cyber .theme-switcher { background: #0f172a; border: 1px solid #1e293b; }
    .theme-cyber .theme-switcher button { color: #475569; }
    .theme-cyber .theme-switcher button.active { background: #2dd4bf; color: #000; }

    /* Cyber Type */
    .theme-cyber :global(.prose-mirror) { line-height: 1.7; font-size: 15px; }
    .theme-cyber :global(h1) { color: #f8fafc; margin-top: 1em; }
    .theme-cyber :global(h1)::before { content: '> '; color: #2dd4bf; }

    /* SCROLLBARS */
    .app-workspace::-webkit-scrollbar { width: 8px; }
    .theme-modern .app-workspace::-webkit-scrollbar-thumb { background: #ccc; border-radius: 4px; }
    .theme-retro .app-workspace::-webkit-scrollbar-thumb { background: #555; }
    .theme-cyber .app-workspace::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 4px; }
    
    :global(.prose-mirror) { outline: none; }
    :global(.prose-mirror p.is-editor-empty:first-child::before) {
        content: attr(data-placeholder); float: left; height: 0; pointer-events: none; opacity: 0.5;
    }
</style>