<script>
    import '../app.css';
    import { Boxes, Zap, FileText, Settings, Globe, Layout, PenTool } from 'lucide-svelte';
</script>

<div class="flex h-screen bg-gray-900 text-gray-300 font-sans">
    <aside class="w-64 border-r border-gray-800 flex flex-col bg-gray-950">
        <div class="p-6 border-b border-gray-800">
            <h1 class="text-xl font-bold text-white tracking-widest flex items-center gap-2">
                <div class="w-3 h-3 bg-cyan-500 rounded-full"></div>
                CODEX
            </h1>
            <p class="text-xs text-gray-500 mt-1 font-mono">INTERNAL CONTROL</p>
        </div>

        <nav class="flex-1 p-4 space-y-2 overflow-y-auto">
            <a href="/" class="flex items-center gap-3 px-4 py-3 rounded hover:bg-gray-900 hover:text-white transition-colors">
                <Boxes size={18} />
                <span class="text-sm font-medium">System Status</span>
            </a>
            
            <div class="pt-6 pb-2 px-4 text-xs font-mono text-gray-600 uppercase tracking-widest">Core Doctrine</div>
            
            <a href="/frameworks" class="flex items-center gap-3 px-4 py-3 rounded hover:bg-gray-900 hover:text-white transition-colors">
                <FileText size={18} />
                <span class="text-sm font-medium">Frameworks</span>
            </a>
            <a href="/engines" class="flex items-center gap-3 px-4 py-3 rounded hover:bg-gray-900 hover:text-white transition-colors">
                <Zap size={18} />
                <span class="text-sm font-medium">Engines</span>
            </a>

            <div class="pt-6 pb-2 px-4 text-xs font-mono text-gray-600 uppercase tracking-widest">Marketing Control</div>

            <a href="/content" class="flex items-center gap-3 px-4 py-3 rounded hover:bg-purple-900/20 hover:text-purple-400 transition-colors group">
                <Layout size={18} class="text-gray-500 group-hover:text-purple-400"/>
                <span class="text-sm font-medium">Content Dashboard</span>
            </a>
            
            <a href="/content/blog" class="flex items-center gap-3 px-4 py-3 rounded hover:bg-pink-900/20 hover:text-pink-400 transition-colors group">
                <PenTool size={18} class="text-gray-500 group-hover:text-pink-400" />
                <span class="text-sm font-medium">Transmissions</span>
            </a>

            <div class="pt-6 pb-2 px-4 text-xs font-mono text-gray-600 uppercase tracking-widest">Weave OS</div>
             <a href="/blueprints" class="flex items-center gap-3 px-4 py-3 rounded hover:bg-gray-900 hover:text-white transition-colors text-gray-600 cursor-not-allowed">
                <Settings size={18} />
                <span class="text-sm font-medium">App Blueprints</span>
            </a>
        </nav>
        
        <div class="p-4 border-t border-gray-800">
            <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-cyan-900/50 border border-cyan-500/30 flex items-center justify-center text-cyan-500 text-xs font-bold">R</div>
                <div>
                    <p class="text-sm text-white">Admin User</p>
                    <p class="text-xs text-green-500">Secure Link Active</p>
                </div>
            </div>
        </div>
    </aside>

    <main class="flex-1 overflow-auto bg-gray-900">
        <slot />
    </main>
</div>