<script lang="ts">
    // Import all 10 Engines
    import EngineSocial from './engines/EngineSocial.svelte';
    import EngineSenate from './engines/EngineSenate.svelte';
    import EngineArena from './engines/EngineArena.svelte';
    import EngineClub from './engines/EngineClub.svelte';
    import EngineLibrary from './engines/EngineLibrary.svelte';
    import EngineStage from './engines/EngineStage.svelte';
    import EngineBunker from './engines/EngineBunker.svelte';
    import EngineGarden from './engines/EngineGarden.svelte';
    import EngineGuild from './engines/EngineGuild.svelte';
    import EngineMarketplace from './engines/EngineMarketplace.svelte'; // Replaces Academy

    export let activeEngine: string; // 'social' | 'arena' | etc.
    export let community: any;
    export let currentUser: any;
</script>

{#if activeEngine === 'social'}
    <EngineSocial {community} {currentUser} />
{:else if activeEngine === 'senate'}
    <EngineSenate {community} {currentUser} />
{:else if activeEngine === 'arena'}
    <EngineArena {community} {currentUser} />
{:else if activeEngine === 'club'}
    <EngineClub {community} {currentUser} />
{:else if activeEngine === 'library'}
    <EngineLibrary {community} {currentUser} />
{:else if activeEngine === 'stage'}
    <EngineStage {community} {currentUser} />
{:else if activeEngine === 'bunker'}
    <EngineBunker {community} {currentUser} />
{:else if activeEngine === 'garden'}
    <EngineGarden {community} {currentUser} />
{:else if activeEngine === 'guild'}
    <EngineGuild {community} {currentUser} />
{:else if activeEngine === 'marketplace'}
    <EngineMarketplace {community} {currentUser} />
{:else}
    <div class="p-20 text-center text-gray-400 font-bold uppercase">
        Engine "{activeEngine}" not installed.
    </div>
{/if}