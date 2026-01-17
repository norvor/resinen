import { writable } from 'svelte/store';

// 1. POINT TO PRODUCTION
const API_URL = 'https://api.resinen.com/api/v1'; 

// 2. User Store
const storedUser = typeof localStorage !== 'undefined' ? localStorage.getItem('resinen_user') : null;
export const user = writable(storedUser ? JSON.parse(storedUser) : null);

// 3. API Helper
export async function api(method: string, endpoint: string, data?: any) {
    const headers: any = {};

    // Only set Content-Type to JSON if we aren't sending FormData (for login)
    if (!(data instanceof URLSearchParams)) {
        headers['Content-Type'] = 'application/json';
    }

    const token = localStorage.getItem('resinen_token');
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const config: any = {
        method,
        headers,
    };

    if (data) {
        config.body = data instanceof URLSearchParams ? data : JSON.stringify(data);
    }

    try {
        const res = await fetch(`${API_URL}${endpoint}`, config);
        
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
    window.location.href = '/login';
}