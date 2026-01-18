import { browser } from '$app/environment';
import { writable } from 'svelte/store';

// --- CONFIGURATION ---
export const API_URL = 'https://api.resinen.com/api/v1';

// --- STORES ---
export const token = writable<string | null>(
    browser ? localStorage.getItem('token') : null
);

export const user = writable<User | null>(null);

// --- TYPES ---
export interface User {
    id: string;
    email: string;
    full_name: string;
    avatar_url?: string;
    xp: number;
    level: number;
    reputation_score: number;
}

export interface Comment {
    id: string;
    post_id: string;
    author_id: string;
    author_name: string;
    author_avatar?: string;
    author_level: number;
    content: string;
    created_at: string;
    like_count: number;
    is_liked: boolean;
    parent_id?: string; // For nested replies
}

export interface Post {
    id: string;
    community_id: string;
    author_name: string;
    author_id: string;
    author_avatar?: string;
    author_level: number;
    content: string;
    created_at: string;
    like_count: number;
    comment_count: number;
    is_liked: boolean;
    title?: string;
    image_url?: string;
    link_url?: string;
}

// --- CORE REQUEST HELPER ---
async function request<T>(method: string, endpoint: string, data?: any, isForm: boolean = false): Promise<T> {
    if (!browser) return {} as T;

    const _token = localStorage.getItem('token');
    
    const headers: any = {};
    if (!isForm) headers['Content-Type'] = 'application/json';
    if (_token) headers['Authorization'] = `Bearer ${_token}`;

    const config: RequestInit = {
        method,
        headers,
        body: data ? (isForm ? data : JSON.stringify(data)) : undefined
    };

    const res = await fetch(`${API_URL}${endpoint}`, config);

    if (res.status === 401) {
        logout();
        throw new Error('Unauthorized');
    }

    if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'API Request Failed');
    }
    return res.json();
}

// --- STANDALONE FUNCTIONS ---

export const logout = () => {
    if (browser) {
        localStorage.removeItem('token');
        token.set(null);
        user.set(null);
        window.location.href = '/login';
    }
};

export const loginUser = async (email: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    
    const data = await request<any>('POST', '/auth/login', formData, true);
    
    if (browser) {
        localStorage.setItem('token', data.access_token);
        token.set(data.access_token);
    }
    return data;
};

export const signupUser = async (email: string, password: string, fullName: string) => {
    return request('POST', '/auth/signup', { 
        email, 
        password, 
        full_name: fullName 
    });
};

// --- API OBJECT (The Main Export) ---
export const api = {
    // AUTH
    login: loginUser,   
    signup: signupUser, 
    logout: logout,

    getMe: async () => {
        const data = await request<User>('GET', '/users/me');
        user.set(data);
        return data;
    },

    // COMMUNITIES
    getMyCommunities: () => request<any[]>('GET', '/users/me/communities'),
    
    getCommunity: (id: string) => request<any>('GET', `/communities/${id}`),

    getCommunities: (query?: string) => 
        request<any[]>('GET', `/communities/${query ? `?q=${query}` : ''}`),
    
    getCommunityBySlug: (slug: string) => request<any>('GET', `/communities/by-slug/${slug}`),
    
    joinCommunity: (id: string) => request('POST', `/communities/${id}/join`),

    // SOCIAL FEED
    getFeed: (communityId: string) => 
        request<Post[]>('GET', `/feed?scope=community&community_id=${communityId}`),
        
    createPost: (communityId: string, content: string) => 
        request<Post>('POST', '/posts', { community_id: communityId, content }),
        
    likePost: (postId: string) => 
        request<{status: string, likes: number}>('POST', `/posts/${postId}/like`),

    // --- COMMENTS SYSTEM (NEW) ---
    getComments: (postId: string) => 
        request<Comment[]>('GET', `/posts/${postId}/comments`),

    createComment: (postId: string, content: string, parentId?: string) => 
        request<Comment>('POST', `/posts/${postId}/comments`, { 
            content, 
            parent_id: parentId 
        }),

    likeComment: (commentId: string) => 
        request<{status: string, likes: number}>('POST', `/comments/${commentId}/like`),
};

export default api;