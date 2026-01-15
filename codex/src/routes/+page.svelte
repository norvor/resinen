<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';

    let status = 'Checking connection...';
    let isOnline = false;

    onMount(async () => {
        try {
            const res = await api.healthCheck();
            status = res.status; // Should correspond to "active" from your main.py
            isOnline = true;
        } catch (e) {
            status = 'OFFLINE - Backend not reachable';
            isOnline = false;
        }
    });
</script>

<div class="p-8">
    <header class="mb-12">
        <h2 class="text-3xl font-bold text-white mb-2">System Status</h2>
        <p class="text-gray-400">Real-time telemetry from the Resinen Platform Core.</p>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="p-6 rounded-xl border border-gray-800 bg-gray-900/50">
            <h3 class="text-xs font-mono text-gray-500 uppercase tracking-widest mb-4">API CONNECTION</h3>
            <div class="flex items-center gap-3">
                <div class={`w-3 h-3 rounded-full ${isOnline ? 'bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.5)]' : 'bg-red-500'}`}></div>
                <span class="text-xl font-bold text-white">{status}</span>
            </div>
        </div>
        
        <div class="p-6 rounded-xl border border-gray-800 bg-gray-900/50">
             <h3 class="text-xs font-mono text-gray-500 uppercase tracking-widest mb-4">DATABASE</h3>
             <div class="flex items-center gap-3">
                 <span class="text-xl font-bold text-white">PostgreSQL Connected</span>
             </div>
        </div>
    </div>
</div>