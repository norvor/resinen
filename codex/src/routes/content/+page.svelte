<script>
    import { Globe, Layout, PenTool } from 'lucide-svelte';
</script>

<div class="p-8 max-w-7xl mx-auto">
    <h1 class="text-3xl font-bold text-white mb-8">Content Management</h1>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <a href="/content/global" class="p-8 bg-gray-900 border border-gray-800 rounded-xl hover:border-cyan-500 transition-colors group">
            <Globe class="w-8 h-8 text-cyan-500 mb-4 group-hover:scale-110 transition-transform" />
            <h3 class="text-xl font-bold text-white mb-2">Global Identity</h3>
            <p class="text-gray-400 text-sm">Logo, Footer, Social Links, and Brand Colors.</p>
        </a>

        <a href="/content/homepage" class="p-8 bg-gray-900 border border-gray-800 rounded-xl hover:border-purple-500 transition-colors group">
            <Layout class="w-8 h-8 text-purple-500 mb-4 group-hover:scale-110 transition-transform" />
            <h3 class="text-xl font-bold text-white mb-2">Homepage</h3>
            <p class="text-gray-400 text-sm">Hero section, tickers, and featured selection.</p>
        </a>

        <a href="/content/blog" class="p-8 bg-gray-900 border border-gray-800 rounded-xl hover:border-pink-500 transition-colors group">
            <PenTool class="w-8 h-8 text-pink-500 mb-4 group-hover:scale-110 transition-transform" />
            <h3 class="text-xl font-bold text-white mb-2">Transmission Log</h3>
            <p class="text-gray-400 text-sm">Manage blog posts, press releases, and updates.</p>
        </a>
        
        <a href="/content/doctrine" class="p-8 bg-gray-900 border border-gray-800 rounded-xl hover:border-yellow-500 transition-colors group">
            <div class="text-yellow-500 mb-4 group-hover:scale-110 transition-transform">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
            </div>
            <h3 class="text-xl font-bold text-white mb-2">The Doctrine</h3>
            <p class="text-gray-400 text-sm">Manifesto, principles, and team leadership.</p>
        </a>

        <a href="/content/contact" class="p-8 bg-gray-900 border border-gray-800 rounded-xl hover:border-blue-500 transition-colors group">
            <div class="text-blue-500 mb-4 group-hover:scale-110 transition-transform">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
            </div>
            <h3 class="text-xl font-bold text-white mb-2">Contact & Locations</h3>
            <p class="text-gray-400 text-sm">Office data, email routing, and engagement settings.</p>
        </a>
    </div>
</div>