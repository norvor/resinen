import { browser } from '$app/environment';

// --- CONFIGURATION ---
const API_URL = 'https://api.resinen.com/api/v1';

// --- TYPES ---

export type User = {
    id: string;
    email: string;
    full_name: string;
    is_superuser: boolean;
    
    // New Fields
    headline?: string;
    bio?: string;
    location?: string;
    website?: string;
    linkedin?: string;
    twitter?: string;
    github?: string;
    xp: number;
    level: number;
};

export type Community = {
    id: string;
    name: string;
    slug: string;
    description: string;
    settings?: Record<string, any>;
};

export type Chapter = {
    id: string;
    community_id: string;
    name: string;
    location: string;
};

export type Comment = {
    id: string;
    post_id: string;
    content: string;
    author_name: string;
    created_at: string;
};

export type ContentBlock = {
    id: string;
    slug: string;
    section: string;
    title: string;
    body: string;
    image_url?: string;
    link_text?: string;
    link_url?: string;
    is_active: boolean;
};

export type Post = {
    id: string;
    content: string;
    author_id: string;
    author_name: string;
    created_at: string;
    
    like_count: number;
    is_liked: boolean; // <--- ADD THIS
    
    comments?: Comment[];
};

// --- HELPERS ---

function getHeader() {
    if (!browser) return { 'Content-Type': 'application/json' };
    
    const token = localStorage.getItem('access_token');
    return token 
        ? { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' } 
        : { 'Content-Type': 'application/json' };
}

async function handleResponse(res: Response) {
    if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || `Request failed: ${res.status}`);
    }
    return res.json();
}

// --- API CLIENT ---

export const api = {
    // SYSTEM
    healthCheck: async () => {
        try { return await (await fetch('https://api.resinen.com/')).json(); } 
        catch (e) { return { status: "offline" }; }
    },

    getContentBlock: async (slug: string): Promise<ContentBlock> => {
        const res = await fetch(`${API_URL}/content/${slug}`, { headers: getHeader() });
        return handleResponse(res);
    },

    getSectionBlocks: async (section: string): Promise<ContentBlock[]> => {
        const res = await fetch(`${API_URL}/content/section/${section}`, { headers: getHeader() });
        return handleResponse(res);
    },

    createContentBlock: async (data: Partial<ContentBlock>) => {
        const res = await fetch(`${API_URL}/content/`, {
            method: 'POST',
            headers: getHeader(),
            body: JSON.stringify(data)
        });
        return handleResponse(res);
    },

    updateContentBlock: async (slug: string, data: Partial<ContentBlock>) => {
        const res = await fetch(`${API_URL}/content/${slug}`, {
            method: 'PUT',
            headers: getHeader(),
            body: JSON.stringify(data)
        });
        return handleResponse(res);
    },

    getMe: async (): Promise<User> => {
        const res = await fetch(`${API_URL}/users/me`, { headers: getHeader() });
        return handleResponse(res);
    },

    updateProfile: async (data: Partial<User>) => {
        const res = await fetch(`${API_URL}/users/me`, {
            method: 'PUT',
            headers: getHeader(),
            body: JSON.stringify(data)
        });
        return handleResponse(res);
    },

    // AUTH
    login: async (username, password) => {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);
        const res = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });
        const data = await handleResponse(res);
        if (browser) localStorage.setItem('access_token', data.access_token);
        return data;
    },

    signup: async (email, password, fullName) => {
        const res = await fetch(`${API_URL}/auth/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, full_name: fullName })
        });
        return handleResponse(res);
    },

    // COMMUNITIES
    getCommunities: async (): Promise<Community[]> => handleResponse(await fetch(`${API_URL}/communities/`, { headers: getHeader() })),
    getCommunity: async (id: string): Promise<Community | undefined> => {
        const all = await handleResponse(await fetch(`${API_URL}/communities/`, { headers: getHeader() }));
        return all.find((c: any) => c.id === id);
    },
    createCommunity: async (data: Partial<Community>) => handleResponse(await fetch(`${API_URL}/communities/`, { method: 'POST', headers: getHeader(), body: JSON.stringify(data) })),
    updateCommunity: async (id: string, data: Partial<Community>) => handleResponse(await fetch(`${API_URL}/communities/${id}`, { method: 'PUT', headers: getHeader(), body: JSON.stringify(data) })),
    deleteCommunity: async (id: string) => handleResponse(await fetch(`${API_URL}/communities/${id}`, { method: 'DELETE', headers: getHeader() })),

    // CHAPTERS
    getChapters: async (communityId: string): Promise<Chapter[]> => handleResponse(await fetch(`${API_URL}/chapters/?community_id=${communityId}`, { headers: getHeader() })),
    getChapter: async (id: string): Promise<Chapter> => handleResponse(await fetch(`${API_URL}/chapters/${id}`, { headers: getHeader() })),
    createChapter: async (data: { community_id: string, name: string, location: string }) => handleResponse(await fetch(`${API_URL}/chapters/`, { method: 'POST', headers: getHeader(), body: JSON.stringify(data) })),
    updateChapter: async (id: string, data: Partial<Chapter>) => handleResponse(await fetch(`${API_URL}/chapters/${id}`, { method: 'PUT', headers: getHeader(), body: JSON.stringify(data) })),
    deleteChapter: async (id: string) => handleResponse(await fetch(`${API_URL}/chapters/${id}`, { method: 'DELETE', headers: getHeader() })),

    // SOCIAL
    createPost: async (data: { community_id: string, chapter_id?: string, content: string }) => {
        const res = await fetch(`${API_URL}/social/`, {
            method: 'POST',
            headers: getHeader(),
            body: JSON.stringify(data)
        });
        return handleResponse(res);
    },
    
    toggleLike: async (postId: string) => {
        const res = await fetch(`${API_URL}/social/posts/${postId}/like`, {
            method: 'POST',
            headers: getHeader()
        });
        return handleResponse(res);
    },

    getFeed: async (communityId: string, chapterId?: string): Promise<Post[]> => {
        let url = `${API_URL}/social/?community_id=${communityId}`;
        if (chapterId) url += `&chapter_id=${chapterId}`;
        const res = await fetch(url, { headers: getHeader() });
        return handleResponse(res);
    },

    createComment: async (postId: string, content: string) => {
        const res = await fetch(`${API_URL}/social/comments`, {
            method: 'POST',
            headers: getHeader(),
            body: JSON.stringify({ post_id: postId, content })
        });
        return handleResponse(res);
    },
};