import { error } from '@sveltejs/kit';
import { api } from '$lib/api';

// This function runs BEFORE the page renders.
// It fetches the community and passes it down to 'export let data' in ALL child pages.
export const load = async ({ params, fetch }) => {
    try {
        console.log("🌉 Layout Bridge: Fetching Community", params.id);
        
        // 🚀 FAST: Only fetch the identity. No stats. No heavy lifting.
        const community = await api.getCommunity(params.id);
        
        if (!community) {
             throw error(404, 'Community not found');
        }

        // This object becomes 'data' in +page.svelte, social/+page.svelte, etc.
        return {
            community
        };

    } catch (err) {
        console.error("Bridge Failed:", err);
        throw error(404, 'Community not found');
    }
};