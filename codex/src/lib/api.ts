// codex/src/lib/api.ts

const API_URL = 'https://api.resinen.com';

// --- TYPES ---

export type Community = {
    id?: string;
    name: string;
    slug: string;
    description: string;
    settings?: Record<string, any>; // Flexible JSON for bylaws/themes
};

// --- API CLIENT ---

export const api = {
    // Check if backend is alive
    healthCheck: async () => {
        try {
            const res = await fetch(`${API_URL}/`);
            return res.json();
        } catch (e) {
            console.error("API Unreachable:", e);
            return { status: "offline" };
        }
    },

    // --- COMMUNITIES ---
    getCommunities: async (): Promise<Community[]> => {
        const res = await fetch(`${API_URL}/communities/`);
        if (!res.ok) throw new Error('Failed to fetch communities');
        return res.json();
    },

    createCommunity: async (data: Community): Promise<Community> => {
        const res = await fetch(`${API_URL}/communities/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Failed to create community');
        }
        return res.json();
    }
};