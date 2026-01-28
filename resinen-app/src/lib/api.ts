import { writable } from 'svelte/store';

const IS_LOCAL = false;
const BASE = IS_LOCAL ? "http://localhost:8000" : "https://api.resinen.com";
const STORAGE_API = `${BASE}/storage`;
const DASH_API = `${BASE}/dashboard`;

// Helper to get current user from localStorage
function getUser() {
    if (typeof localStorage === 'undefined') return null;
    const u = localStorage.getItem('resinen_user');
    return u ? JSON.parse(u) : null;
}

export async function saveData(key: string, data: any) {
    // 1. Always save to LocalStorage first (Instant UI update)
    if (typeof localStorage !== 'undefined') {
        localStorage.setItem(key, JSON.stringify(data));
    }

    // 2. If user is logged in, sync to Backend (Cloud Persistence)
    const user = getUser();
    if (user && user.email) {
        try {
            await fetch(`${STORAGE_API}/${key}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    user_email: user.email, 
                    data: data 
                })
            });
        } catch (e) {
            console.error("Cloud Sync Failed:", e);
        }
    }
}

export async function loadData(key: string) {
    // 1. Try LocalStorage first (Fastest)
    if (typeof localStorage !== 'undefined') {
        const local = localStorage.getItem(key);
        if (local) return JSON.parse(local);
    }
    return null;
}

export async function getDashboard(endpoint: string, params: Record<string, any> = {}) {
    try {
        const url = new URL(`${DASH_API}/${endpoint}`);
        Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
        
        const res = await fetch(url.toString());
        if (!res.ok) throw new Error("Feed Error");
        return await res.json();
    } catch (e) {
        console.error(`Failed to load ${endpoint}`, e);
        return null;
    }
}

// Call this on mount to pull fresh data from cloud
export async function syncFromCloud() {
    const user = getUser();
    if (!user || !user.email) return;

    try {
        const res = await fetch(`${STORAGE_API}/sync/all?user_email=${user.email}`);
        const cloudData = await res.json();
        
        // Update LocalStorage with Cloud Data
        Object.entries(cloudData).forEach(([key, value]) => {
            localStorage.setItem(key, JSON.stringify(value));
        });
        
        return cloudData; // Return so components can update state
    } catch (e) {
        console.error("Cloud Fetch Failed:", e);
    }
}