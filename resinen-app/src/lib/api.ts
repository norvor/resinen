import { writable } from 'svelte/store';

// 1. Point to your Backend
const API_URL = 'https://api.resinen.com/api/v1'; // Local FastAPI

// 2. User Store (Global State)
// We check LocalStorage to see if they are already logged in
const storedUser = typeof localStorage !== 'undefined' ? localStorage.getItem('resinen_user') : null;
export const user = writable(storedUser ? JSON.parse(storedUser) : null);

// 3. Helper to make Authenticated Requests

export async function getEngines() {
    try {
        // Fetch the Engines you seeded (Talent, Governance, Culture)
        const res = await fetch(`${API_URL}/marketing/engines`);
        if (!res.ok) return [];
        return res.json();
    } catch (e) {
        console.error("Failed to load engines:", e);
        return [];
    }
}


export async function api(method: string, endpoint: string, data?: any) {
    const headers: any = {
        'Content-Type': 'application/json',
    };

    // Attach Token if we have one
    const token = localStorage.getItem('resinen_token');
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const config: any = {
        method,
        headers,
    };

    if (data) {
        config.body = JSON.stringify(data);
    }

    try {
        const res = await fetch(`${API_URL}${endpoint}`, config);
        
        // Handle 401 (Unauthorized) -> Kick them out
        if (res.status === 401) {
            logout();
            return null;
        }

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Request failed');
        }

        return res.json();
    } catch (e) {
        throw e;
    }
}

// 4. Auth Actions
export function loginUser(token: string, userData: any) {
    localStorage.setItem('resinen_token', token);
    localStorage.setItem('resinen_user', JSON.stringify(userData));
    user.set(userData);
}

export function logout() {
    localStorage.removeItem('resinen_token');
    localStorage.removeItem('resinen_user');
    user.set(null);
    window.location.href = '/login'; // Force redirect
}