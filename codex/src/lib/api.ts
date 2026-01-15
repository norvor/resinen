// codex/src/lib/api.ts

// The URL of your running FastAPI server
const API_URL = 'http://127.0.0.1:8000';

export type Framework = {
    id: string;
    name: string;
    subject: string;
    description: string;
    summary: Record<string, any>;
    isomorphism: Record<string, any>;
    nodes: Record<string, any>[];
    solution: Record<string, any>;
    formulas: Record<string, any>;
    protocol: Record<string, any>;
    values: Record<string, any>;
};

export const api = {
    // Check if backend is online
    healthCheck: async () => {
        const res = await fetch(`${API_URL}/`);
        return res.json();
    },

    // --- FRAMEWORKS ---
    getFrameworks: async (): Promise<Framework[]> => {
        const res = await fetch(`${API_URL}/frameworks`);
        return res.json();
    },

    createFramework: async (data: Framework) => {
        const res = await fetch(`${API_URL}/frameworks`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error('Failed to create framework');
        return res.json();
    }
};