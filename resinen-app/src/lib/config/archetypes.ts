import { type ComponentType } from 'svelte';

// --- IMPORT ENGINES (We will create these next!) ---
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

// Default Fallback
import EngineSocial from '$lib/components/engines/EngineSocial.svelte'; 

export const ARCHETYPES = {
    SANCTUARY: 'sanctuary',
    BAZAAR: 'bazaar',
    SENATE: 'senate',
    ARENA: 'arena',
    ACADEMY: 'academy',
    CLUB: 'club',
    LIBRARY: 'library',
    STAGE: 'stage',
    BUNKER: 'bunker',
    GUILD: 'guild',
    GARDEN: 'garden',
    
    // Mixed / Aliases
    LOUNGE: 'lounge',
    SPOTLIGHT: 'spotlight'
};

export interface FeatureDef {
    id: string;
    label: string;
    icon: string;
    component: ComponentType;
}

// --- THE REGISTRY ---
export const FEATURE_REGISTRY: Record<string, FeatureDef> = {
    // 1. BAZAAR
    'bazaar_market': { id: 'bazaar_market', label: 'Market', icon: '🛍️', component: EngineBazaar },
    
    // 2. SENATE
    'senate_vote': { id: 'senate_vote', label: 'Governance', icon: '⚖️', component: EngineSenate },
    
    // 3. ACADEMY
    'academy_learn': { id: 'academy_learn', label: 'Curriculum', icon: '🎓', component: EngineAcademy },

    // 4. ARENA
    'arena_match': { id: 'arena_match', label: 'Matches', icon: '⚔️', component: EngineArena },

    // 5. CLUB
    'club_events': { id: 'club_events', label: 'Events', icon: '🎟️', component: EngineClub },

    // 6. LIBRARY
    'library_wiki': { id: 'library_wiki', label: 'Archives', icon: '📜', component: EngineLibrary },

    // 7. STAGE
    'stage_feed': { id: 'stage_feed', label: 'Live Feed', icon: '🎬', component: EngineStage },

    // 8. BUNKER
    'bunker_chat': { id: 'bunker_chat', label: 'Encrypted', icon: '🔒', component: EngineBunker },

    // 9. GUILD
    'guild_projects': { id: 'guild_projects', label: 'Projects', icon: '🔨', component: EngineGuild },

    // 10. GARDEN
    'garden_tracker': { id: 'garden_tracker', label: 'Habits', icon: '🌱', component: EngineGarden },
    
    // DEFAULT
    'social_feed': { id: 'social_feed', label: 'Feed', icon: '💬', component: EngineSocial },
};

// --- RESOLVER LOGIC ---
export function resolveFeatures(archetypes: string[]): string[] {
    if (!archetypes || archetypes.length === 0) return ['social_feed'];

    const features: string[] = [];
    const primary = archetypes[0].toLowerCase();

    // Map Archetype -> Feature Key
    switch (primary) {
        case ARCHETYPES.BAZAAR: features.push('bazaar_market'); break;
        case ARCHETYPES.SENATE: features.push('senate_vote'); break;
        case ARCHETYPES.ARENA: features.push('arena_match'); break;
        case ARCHETYPES.ACADEMY: features.push('academy_learn'); break;
        case ARCHETYPES.CLUB: features.push('club_events'); break;
        case ARCHETYPES.LIBRARY: features.push('library_wiki'); break;
        case ARCHETYPES.STAGE: features.push('stage_feed'); break;
        case ARCHETYPES.SPOTLIGHT: features.push('stage_feed'); break; // Alias
        case ARCHETYPES.BUNKER: features.push('bunker_chat'); break;
        case ARCHETYPES.GUILD: features.push('guild_projects'); break;
        case ARCHETYPES.GARDEN: features.push('garden_tracker'); break;
        
        // Mixed Types
        case ARCHETYPES.LOUNGE: 
            features.push('garden_tracker'); 
            features.push('club_events'); 
            break;
            
        case ARCHETYPES.SANCTUARY:
            features.push('library_wiki');
            features.push('garden_tracker');
            break;
            
        default: features.push('social_feed');
    }

    // Always append social feed as a secondary tab unless it's a Bunker (Private)
    if (primary !== ARCHETYPES.BUNKER) {
        features.push('social_feed');
    }

    return features;
}

export function getPrimaryArchetypeName(archetypes: string[]): string {
    if (!archetypes || !archetypes[0]) return "Community";
    return archetypes[0].toUpperCase();
}

export function getPrimaryArchetypeFocus(archetypes: string[]): string {
    const map: Record<string, string> = {
        'bazaar': 'Commerce',
        'senate': 'Policy',
        'arena': 'Competition',
        'academy': 'Education',
        'club': 'Social',
        'library': 'Knowledge',
        'stage': 'Entertainment',
        'bunker': 'Privacy',
        'guild': 'Construction',
        'garden': 'Wellness'
    };
    return map[archetypes[0]] || 'General';
}