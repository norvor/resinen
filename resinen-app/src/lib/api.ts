import { logout } from '$lib/stores';

const localDev = false;
const BASE_URL = localDev ? "http://localhost:8000" : "https://api.resinen.com";

function authHeaders() {
    const token = localStorage.getItem('token');
    return {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    };
}

// Global response handler
async function handle(res: Response) {
    if (res.status === 401) {
        logout(); // Updates store, switches Layout to Login Mode instantly
        throw new Error("Unauthorized");
    }
    return res.json();
}

export const api = {
    auth: {
        login: async (username, password) => {
            const body = new URLSearchParams();
            body.append('username', username);
            body.append('password', password);
            
            const res = await fetch(`${BASE_URL}/token`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: body
            });
            if (!res.ok) throw new Error("Login failed");
            return res.json();
        }
    },

    widgets: {
        // --- DASHBOARD ---
        loadDashboard: async () => {
            const res = await fetch(`${BASE_URL}/widgets/dashboard`, { headers: authHeaders() });
            return handle(res);
        },

        // --- PUBLIC FEEDS ---
        getFeeds: async () => (await fetch(`${BASE_URL}/dashboard/feeds`)).json(),
        getVisuals: async () => (await fetch(`${BASE_URL}/dashboard/visuals`)).json(),
        getPlanetary: async () => (await fetch(`${BASE_URL}/dashboard/planetary`)).json(),
        getZen: async () => (await fetch(`${BASE_URL}/dashboard/zen`)).json(),

        // --- MISSION CONTROL ---
        getMissions: async () => {
            const res = await fetch(`${BASE_URL}/widgets/missions`, { headers: authHeaders() });
            return handle(res);
        },
        createMission: async (data: any) => {
            const res = await fetch(`${BASE_URL}/widgets/missions`, {
                method: 'POST', headers: authHeaders(), body: JSON.stringify(data)
            });
            return handle(res);
        },
        updateMission: async (id: number, data: any) => {
            const res = await fetch(`${BASE_URL}/widgets/missions/${id}`, {
                method: 'PUT', headers: authHeaders(), body: JSON.stringify(data)
            });
            return handle(res);
        },
        abortMission: async (id: number) => {
            await fetch(`${BASE_URL}/widgets/missions/${id}`, { method: 'DELETE', headers: authHeaders() });
        },

        // --- TRANSMISSION (MATCHING PYTHON: Singular '/transmission') ---
        createTransmission: async (title: string, url: string, type: string) => {
            const res = await fetch(`${BASE_URL}/widgets/transmission`, {
                method: 'POST', headers: authHeaders(), body: JSON.stringify({ title, url, type })
            });
            return handle(res);
        },
        deleteTransmission: async (id: number) => {
            await fetch(`${BASE_URL}/widgets/transmission/${id}`, { method: 'DELETE', headers: authHeaders() });
        },

        // --- LOVES (MATCHING PYTHON: Plural '/loves') ---
        // Added 'link' parameter to match backend model
        createLove: async (name: string, category: string, description: string, link: string = "") => {
            const res = await fetch(`${BASE_URL}/widgets/loves`, {
                method: 'POST', 
                headers: authHeaders(), 
                body: JSON.stringify({ name, category, description, link })
            });
            return handle(res);
        },
        deleteLove: async (id: number) => {
            await fetch(`${BASE_URL}/widgets/loves/${id}`, { method: 'DELETE', headers: authHeaders() });
        },

        // --- NOTES & TASKS ---
        createNote: async (title: string, content: string) => {
            const res = await fetch(`${BASE_URL}/widgets/notes`, {
                method: 'POST', headers: authHeaders(), body: JSON.stringify({ title, content })
            });
            return handle(res);
        },
        updateNote: async (id: number, data: any) => {
            const res = await fetch(`${BASE_URL}/widgets/notes/${id}`, {
                method: 'PUT', headers: authHeaders(), body: JSON.stringify(data)
            });
            return handle(res);
        },
        createTask: async (content: string) => {
            const res = await fetch(`${BASE_URL}/widgets/tasks`, {
                method: 'POST', headers: authHeaders(), body: JSON.stringify({ content, is_done: false })
            });
            return handle(res);
        },
        updateTask: async (id: number, task: any) => {
            const res = await fetch(`${BASE_URL}/widgets/tasks/${id}`, {
                method: 'PUT', headers: authHeaders(), body: JSON.stringify(task)
            });
            return handle(res);
        },
        deleteTask: async (id: number) => {
            await fetch(`${BASE_URL}/widgets/tasks/${id}`, { method: 'DELETE', headers: authHeaders() });
        },

        // --- BUDGET, HABITS, SCRIBBLE ---
        updateBudget: async (data: { monthly_limit: number, spent: number, currency: string }) => {
            const res = await fetch(`${BASE_URL}/widgets/budget`, {
                method: 'POST', 
                headers: authHeaders(), 
                body: JSON.stringify(data)
            });
            return handle(res);
        },
        updateHabits: async (data: any) => {
            const res = await fetch(`${BASE_URL}/widgets/habits`, {
                method: 'POST', headers: authHeaders(), body: JSON.stringify(data)
            });
            return handle(res);
        },
        updateScribble: async (content: string) => {
            await fetch(`${BASE_URL}/widgets/scribbles`, {
                method: 'POST', headers: authHeaders(), body: JSON.stringify({ content })
            });
        },

        
    }
};