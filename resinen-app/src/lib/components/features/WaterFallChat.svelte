<script lang="ts">
    // We reuse the WebSocket component we just fixed
    import LiveChat from '$lib/components/LiveChat.svelte';

    // --- STANDARD FEATURE PROPS ---
    // Every feature component must accept these 3 props, even if it doesn't use all of them.
    // This allows the Engine to blindly pass data to any module.
    export let community: any;
    export let currentUser: any = null;
    export let membership: any = null;
</script>

<div class="h-full min-h-[500px] flex flex-col">
    <div class="bg-black text-white px-4 py-2 font-black uppercase text-xs tracking-widest flex justify-between items-center">
        <span>Real-Time Frequency</span>
        <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
    </div>

    <div class="flex-1 border-4 border-black border-t-0 shadow-hard bg-white relative">
        <LiveChat communityId={community.id} />
    </div>
</div>