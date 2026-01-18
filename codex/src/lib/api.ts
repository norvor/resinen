import { browser } from '$app/environment';
import { writable } from 'svelte/store';

// --- CONFIGURATION ---
export const API_URL = 'https://api.resinen.com/api/v1';

// --- STORES ---
export const token = writable<string | null>(
    browser ? localStorage.getItem('codex_token') : null
);

// --- TYPES ---

export type User = {
    id: string;
    email: string;
    full_name: string;
    is_superuser: boolean;
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

// FIX: Strict Type for Creation to ensure is_private works
export type CreateCommunityDTO = {
    name: string;
    slug: string;
    description: string;
    is_private: boolean; // <--- This ensures the checkbox data sends correctly
    settings?: Record<string, any>;
};

export type Community = {
    id: string;
    name: string;
    slug: string;
    description: string;
    is_private: boolean;
    member_count: number;
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
    is_liked: boolean;
    comments?: Comment[];
};

// --- CORE REQUEST HELPER (The "Proper" Way) ---

async function request(method: string, endpoint: string, data?: any, isForm: boolean = false) {
    if (!browser) return; // Prevent SSR issues

    const _token = localStorage.getItem('codex_token');
    
    const headers: any = {};
    if (!isForm) headers['Content-Type'] = 'application/json';
    if (_token) headers['Authorization'] = `Bearer ${_token}`;

    const config: RequestInit = {
        method,
        headers,
        body: data ? (isForm ? data : JSON.stringify(data)) : undefined
    };

    try {
        const res = await fetch(`${API_URL}${endpoint}`, config);
        
        // Auto-Logout on 401
        if (res.status === 401) {
            localStorage.removeItem('codex_token');
            window.location.href = '/login';
            throw new Error('Session expired');
        }

        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            throw new Error(errData.detail || `API Error: ${res.status}`);
        }

        return res.json();
    } catch (e) {
        throw e;
    }
}

// --- API CLIENT ---

export const api = {
    // SYSTEM
    healthCheck: () => request('GET', '/'), // Root check

    // CONTENT BLOCKS (CMS)
    getContentBlock: (slug: string): Promise<ContentBlock> => request('GET', `/content/${slug}`),
    getSectionBlocks: (section: string): Promise<ContentBlock[]> => request('GET', `/content/section/${section}`),
    createContentBlock: (data: Partial<ContentBlock>) => request('POST', '/content/', data),
    updateContentBlock: (slug: string, data: Partial<ContentBlock>) => request('PUT', `/content/${slug}`, data),

    // USER / PROFILE
    getMe: (): Promise<User> => request('GET', '/users/me'),
    updateProfile: (data: Partial<User>) => request('PUT', '/users/me', data),

    // AUTHENTICATION
    login: async (username, password) => {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);
        
        const data = await request('POST', '/auth/login', formData, true);
        if (browser) {
            localStorage.setItem('codex_token', data.access_token);
            token.set(data.access_token);
        }
        return data;
    },

    signup: (email, password, fullName) => {
        return request('POST', '/auth/signup', { email, password, full_name: fullName });
    },

    // COMMUNITIES (Fixed Logic)
    getCommunities: (): Promise<Community[]> => request('GET', '/communities/'),
    
    getCommunity: async (id: string): Promise<Community | undefined> => {
        // Optimization: Fetch single if API supports it, otherwise filter list
        try {
            return await request('GET', `/communities/${id}`); // Assumes backend supports by ID
        } catch {
            const all = await request('GET', '/communities/');
            return all.find((c: any) => c.id === id);
        }
    },

    // THE FIX: Use strict DTO to ensure is_private sends correctly
    createCommunity: (data: CreateCommunityDTO) => request('POST', '/communities/', data),
    
    updateCommunity: (id: string, data: Partial<Community>) => request('PUT', `/communities/${id}`, data),
    deleteCommunity: (id: string) => request('DELETE', `/communities/${id}`),
    
    getMembers: (communityId: string, status?: string) => 
        request('GET', `/communities/${communityId}/members${status ? `?status=${status}` : ''}`),

    processMembership: (communityId: string, userId: string, action: 'approve' | 'reject' | 'ban') => 
        request('POST', `/communities/${communityId}/members/${userId}/process?action=${action}`),

    // CHAPTERS
    getChapters: (communityId: string): Promise<Chapter[]> => request('GET', `/chapters/?community_id=${communityId}`),
    getChapter: (id: string): Promise<Chapter> => request('GET', `/chapters/${id}`),
    createChapter: (data: { community_id: string, name: string, location: string }) => request('POST', '/chapters/', data),
    updateChapter: (id: string, data: Partial<Chapter>) => request('PUT', `/chapters/${id}`, data),
    deleteChapter: (id: string) => request('DELETE', `/chapters/${id}`),

    // SOCIAL ENGINE
    getFeed: (communityId: string, chapterId?: string): Promise<Post[]> => {
        let url = `/social/feed?community_id=${communityId}`; // Adjusted to standard endpoint
        if (chapterId) url += `&chapter_id=${chapterId}`;
        return request('GET', url);
    },
    
    createPost: (data: { community_id: string, chapter_id?: string, content: string, title?: string }) => request('POST', '/social/posts', data),
    
    toggleLike: (postId: string) => request('POST', `/social/posts/${postId}/like`),
    
    createComment: (postId: string, content: string) => request('POST', '/social/comments', { post_id: postId, content }),
};