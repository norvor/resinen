// src/lib/config/themes.ts

// 1. Map Archetypes to Themes
// Default is "Neo-Brutalist" (No class needed)
const THEME_MAP: Record<string, string> = {
    // CALM (Serenity)
    'sanctuary': 'theme-serenity',
    'library': 'theme-serenity',
    'garden': 'theme-serenity',
    'academy': 'theme-serenity',

    // ENERGETIC (Voltage)
    'arena': 'theme-voltage',
    'club': 'theme-voltage',
    'stage': 'theme-voltage',
    'bunker': 'theme-voltage',

    // DEFAULT / BRUTALIST (The Bazaar, Senate, Guild, Lounge)
    // defined as '' (empty string) so it falls back to :root variables
    'bazaar': '',
    'senate': '',
    'guild': '',
    'lounge': '' 
};

// 2. The Resolver
export function resolveTheme(archetypes: string[]): string {
    if (!archetypes || archetypes.length === 0) return '';
    
    // We strictly use the FIRST archetype to decide the theme
    // (You can't be both "Serene" and "Neon" at the same time visually)
    const primary = archetypes[0].toLowerCase();
    
    return THEME_MAP[primary] || '';
}