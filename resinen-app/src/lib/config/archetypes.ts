import { type ComponentType } from 'svelte';

// --- IMPORT ENGINES ---
import EngineBazaar from '$lib/components/engines/EngineBazaar.svelte';
import EngineSenate from '$lib/components/engines/EngineSenate.svelte';
import EngineAcademy from '$lib/components/engines/EngineAcademy.svelte';
import EngineArena from '$lib/components/engines/EngineArena.svelte';
import EngineClub from '$lib/components/engines/EngineClub.svelte';
import EngineLibrary from '$lib/components/engines/EngineLibrary.svelte';
import EngineStage from '$lib/components/engines/EngineStage.svelte';
import EngineBunker from '$lib/components/engines/EngineBunker.svelte';
import EngineGuild from '$lib/components/engines/EngineGuild.svelte';
import EngineGarden from '$lib/components/engines/EngineGarden.svelte';
import EngineSocial from '$lib/components/engines/EngineSocial.svelte'; 

// --- ARCHETYPE KEYS ---
// 🚨 CRITICAL: These values must match the 'key' column in your Postgres 'engine' table.
export const ARCHETYPES = {
    // Core Mappings (Frontend Label -> Backend Key)
    BAZAAR: 'listings',     // Backend: 'listings'
    SENATE: 'governance',   // Backend: 'governance'
    LOUNGE: 'social',       // Backend: 'social'
    
    // Direct Mappings
    ARENA: 'arena',
    ACADEMY: 'academy',
    CLUB: 'club',
    LIBRARY: 'library',
    STAGE: 'stage',
    BUNKER: 'bunker',
    GUILD: 'guild',
    GARDEN: 'garden',
    
    // Legacy / Aliases (Mapped to backend keys)
    SANCTUARY: 'garden',    // UI "Sanctuary" -> Backend "garden"
    SPOTLIGHT: 'stage'
};

export interface FeatureDef {
    id: string;
    label: string;
    icon: string;
    component: ComponentType;
}

// --- THE REGISTRY ---
// Maps a unique internal ID to the visual component
export const FEATURE_REGISTRY: Record<string, FeatureDef> = {
    'bazaar_market': { id: 'bazaar_market', label: 'Market', icon: '🛍️', component: EngineBazaar },
    'senate_vote':   { id: 'senate_vote', label: 'Governance', icon: '⚖️', component: EngineSenate },
    'academy_learn': { id: 'academy_learn', label: 'Curriculum', icon: '🎓', component: EngineAcademy },
    'arena_match':   { id: 'arena_match', label: 'Matches', icon: '⚔️', component: EngineArena },
    'club_events':   { id: 'club_events', label: 'Events', icon: '🎟️', component: EngineClub },
    'library_wiki':  { id: 'library_wiki', label: 'Archives', icon: '📜', component: EngineLibrary },
    'stage_feed':    { id: 'stage_feed', label: 'Live Feed', icon: '🎬', component: EngineStage },
    'bunker_chat':   { id: 'bunker_chat', label: 'Encrypted', icon: '🔒', component: EngineBunker },
    'guild_projects':{ id: 'guild_projects', label: 'Projects', icon: '🔨', component: EngineGuild },
    'garden_tracker':{ id: 'garden_tracker', label: 'Habits', icon: '🌱', component: EngineGarden },
    'social_feed':   { id: 'social_feed', label: 'Feed', icon: '💬', component: EngineSocial },
};

// --- RESOLVER LOGIC ---
// Transforms list of backend keys (['social', 'arena']) -> list of frontend features
export function resolveFeatures(installedEngines: string[]): string[] {
    // Default to social if empty
    if (!installedEngines || installedEngines.length === 0) return ['social_feed'];

    const features: string[] = [];

    // 1. Map Every Installed Engine
    installedEngines.forEach(key => {
        const engineKey = key.toLowerCase();
        
        switch (engineKey) {
            case ARCHETYPES.BAZAAR: features.push('bazaar_market'); break;
            case ARCHETYPES.SENATE: features.push('senate_vote'); break;
            case ARCHETYPES.ARENA:  features.push('arena_match'); break;
            case ARCHETYPES.ACADEMY:features.push('academy_learn'); break;
            case ARCHETYPES.CLUB:   features.push('club_events'); break;
            case ARCHETYPES.LIBRARY:features.push('library_wiki'); break;
            case ARCHETYPES.STAGE:  features.push('stage_feed'); break;
            case ARCHETYPES.BUNKER: features.push('bunker_chat'); break;
            case ARCHETYPES.GUILD:  features.push('guild_projects'); break;
            case ARCHETYPES.GARDEN: features.push('garden_tracker'); break;
            case ARCHETYPES.LOUNGE: features.push('social_feed'); break;
            // Aliases
            case 'sanctuary':       features.push('garden_tracker'); break;
        }
    });

    // 2. Safety Net: Ensure Social Feed exists (unless it's a private Bunker)
    const hasSocial = features.includes('social_feed');
    const isPureBunker = features.length === 1 && features[0] === 'bunker_chat';
    
    // If we haven't added social yet, and it's not a pure bunker, add it.
    // Note: If 'social' was in installedEngines, it's already added above.
    if (!hasSocial && !isPureBunker) {
        features.push('social_feed');
    }

    return [...new Set(features)]; // Deduplicate
}

export function getPrimaryArchetypeName(archetypes: string[]): string {
    if (!archetypes || !archetypes[0]) return "Community";
    // Returns the first engine as the "Theme" name
    return archetypes[0].toUpperCase();
}

export function getPrimaryArchetypeFocus(archetypes: string[]): string {
    if (!archetypes || !archetypes[0]) return 'General';
    
    const map: Record<string, string> = {
        'listings': 'Commerce',   // Fixed key
        'governance': 'Policy',   // Fixed key
        'social': 'Social',       // Fixed key
        'arena': 'Competition',
        'academy': 'Education',
        'club': 'Nightlife',
        'library': 'Knowledge',
        'stage': 'Entertainment',
        'bunker': 'Privacy',
        'guild': 'Construction',
        'garden': 'Wellness'
    };
    return map[archetypes[0].toLowerCase()] || 'General';
}