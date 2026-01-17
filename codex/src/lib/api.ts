// codex/src/lib/api.ts

const API_URL = 'https://api.resinen.com/api/v1'; // Note the /api/v1 suffix

// --- TYPES ---

export type User = {
    id: string;
    email: string;
    full_name: string;
    is_superuser: boolean;
};

export type Community = {
    id?: string;
    name: string;
    slug: string;
    description: string;
    settings?: Record<string, any>;
};

// --- AUTH HELPER ---

function getHeader() {
    const token = localStorage.getItem('access_token');
    return token ? { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' } : { 'Content-Type': 'application/json' };
}

// --- API CLIENT ---

export const api = {
    // SYSTEM
    healthCheck: async () => {
        try {
            const res = await fetch(`${API_URL}/`); // Root check
            // If API_URL includes /api/v1, this might need adjustment depending on where you put the root endpoint. 
            // Usually root is just 'https://api.resinen.com/'
            const rootRes = await fetch('https://api.resinen.com/');
            return rootRes.json();
        } catch (e) {
            return { status: "offline" };
        }
    },

    // AUTH
    login: async (username, password) => {
        // FastAPI OAuth2 expects form-data, not JSON
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const res = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });

        if (!res.ok) throw new Error('Login failed');
        const data = await res.json();
        
        // Save Token
        localStorage.setItem('access_token', data.access_token);
        return data;
    },

    signup: async (email, password, fullName) => {
        const res = await fetch(`${API_URL}/auth/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, full_name: fullName })
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Signup failed');
        }
        return res.json();
    },

    // COMMUNITIES (Protected)
    createCommunity: async (data: Community) => {
        const res = await fetch(`${API_URL}/communities/`, {
            method: 'POST',
            headers: getHeader(), // <--- Sends Token
            body: JSON.stringify(data)
        });
        
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Failed to create community');
        }
        return res.json();
    }
};