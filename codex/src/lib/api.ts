import { browser } from '$app/environment';
import { writable } from 'svelte/store';

// --- CONFIGURATION ---
export const API_URL = 'https://api.resinen.com/api/v1';

// --- STORES ---
export const token = writable<string | null>(
    browser ? localStorage.getItem('codex_token') : null
);

// --- CORE TYPES ---

export type User = {
    id: string;
    email: string;
    full_name: string;
    is_superuser: boolean;
    avatar_url?: string;
    xp: number;
    level: number;
};

export type Community = {
    id: string;
    name: string;
    slug: string;
    description: string;
    is_private: boolean;
    member_count: number;
    creator_id: string;
    banner_url?: string;
    created_at: string;
    archetypes: string[]; 
    settings?: Record<string, any>;
};

export type Membership = {
    community_id: string;
    user_id: string;
    user?: User; 
    role: 'member' | 'moderator' | 'admin' | 'owner';
    status: 'pending' | 'active' | 'banned' | 'rejected';
    joined_at: string;
};

// --- ENGINE TYPES (The New Stuff) ---

// Arena (Sports)
export type Match = {
    id: string;
    title: string;
    team_a_name: string;
    team_b_name: string;
    score_a: number;
    score_b: number;
    start_time: string;
    status: 'SCHEDULED' | 'LIVE' | 'COMPLETED';
};

// Guild (Economy)
export type Bounty = {
    id: string;
    title: string;
    reward: string;
    difficulty: 'Easy' | 'Medium' | 'Hard';
    status: 'open' | 'claimed' | 'closed';
};

// Senate (Governance)
export type Proposal = {
    id: string;
    title: string;
    description: string;
    status: 'active' | 'passed' | 'rejected';
    votes_for: number;
    votes_against: number;
    end_date: string;
};

// Garden (Resources)
export type Resource = {
    id: string;
    title: string;
    url: string;
    category: string;
    is_approved: boolean;
};

// Library (Wiki)
export type WikiNode = {
    id: string;
    title: string;
    slug: string;
    type: 'folder' | 'page';
    children?: WikiNode[];
};

// Club (Events)
export type Event = {
    id: string;
    title: string;
    start_time: string;
    location: string;
};

// --- REQUEST HELPER ---

async function request<T>(method: string, endpoint: string, data?: any, isForm: boolean = false): Promise<T> {
    if (!browser) return {} as T; 

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
        
        if (res.status === 401) {
            localStorage.removeItem('codex_token');
            if (window.location.pathname !== '/login') window.location.href = '/login';
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

// --- THE CODEX CLIENT ---

export const api = {
    // SYSTEM
    healthCheck: () => request('GET', '/'),

    // AUTH
    login: async (username, password) => {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);
        const data = await request<any>('POST', '/auth/login', formData, true);
        if (browser) {
            localStorage.setItem('codex_token', data.access_token);
            token.set(data.access_token);
        }
        return data;
    },

    // COMMUNITIES (Core)
    getCommunities: (): Promise<Community[]> => request('GET', '/communities/'),
    getCommunity: (id: string): Promise<Community> => request('GET', `/communities/${id}`),
    createCommunity: (data: any) => request<Community>('POST', '/communities/', data),
    updateCommunity: (id: string, data: any) => request('PUT', `/communities/${id}`, data),
    
    getCommunityStats: (communityId: string) => request<{
        member_count: number;
        daily_active: number;
        posts_today: number;
        pending_reports: number;
    }>('GET', `/communities/${communityId}/stats`),

    // MEMBERSHIP (CRM)
    getMembers: (commId: string, status?: string) => 
        request<Membership[]>('GET', `/communities/${commId}/members${status ? `?status=${status}` : ''}`),
    updateMemberStatus: (commId: string, userId: string, status: string) => 
        request('PUT', `/communities/${commId}/members/${userId}/status`, { status }),

    // --- ENGINE MANAGEMENT (Super Admin Actions) ---

    // 1. ARENA (Sports)
    getMatches: (commId: string) => request<Match[]>('GET', `/arena/${commId}/matches`),
    createMatch: (commId: string, data: any) => request('POST', `/arena/${commId}/matches`, data),
    updateMatchScore: (matchId: string, scoreA: number, scoreB: number) => 
        request('PUT', `/arena/matches/${matchId}/score`, { score_a: scoreA, score_b: scoreB }),
    setMatchStatus: (matchId: string, status: string) => 
        request('PUT', `/arena/matches/${matchId}/status`, { status }),

    // 2. GUILD (Projects/Bounties)
    getBounties: (commId: string) => request<Bounty[]>('GET', `/guild/${commId}/bounties`),
    createBounty: (commId: string, data: any) => request('POST', `/guild/${commId}/bounties`, data),
    closeBounty: (bountyId: string) => request('DELETE', `/guild/bounties/${bountyId}`),

    // 3. SENATE (Governance)
    getProposals: (commId: string) => request<Proposal[]>('GET', `/governance/${commId}/proposals`),
    createProposal: (commId: string, data: any) => request('POST', `/governance/${commId}/proposals`, data),
    vetoProposal: (proposalId: string) => request('POST', `/governance/proposals/${proposalId}/veto`),

    // 4. GARDEN (Resources)
    getGarden: (commId: string) => request<Resource[]>('GET', `/garden/${commId}/resources`),
    plantResource: (commId: string, data: any) => request('POST', `/garden/${commId}/resources`, data),
    pruneResource: (resourceId: string) => request('DELETE', `/garden/resources/${resourceId}`),

    // 5. LIBRARY (Wiki)
    getTree: (commId: string) => request<WikiNode[]>('GET', `/library/${commId}/tree`),
    createPage: (commId: string, data: any) => request('POST', `/library/${commId}/pages`, data),
    updatePage: (pageId: string, content: string) => request('PUT', `/library/pages/${pageId}`, { content }),

    
    // 6. CLUB (Events)
    getEvents: (commId: string) => request<Event[]>('GET', `/club/${commId}/events`),
    createEvent: (commId: string, data: any) => request('POST', `/club/${commId}/events`, data),

    // 7. BUNKER (Chat)
    // Admin only: Fetch raw logs or nuke channel
    getBunkerLogs: (commId: string) => request('GET', `/bunker/${commId}/history?admin=true`),
    nukeBunker: (commId: string) => request('POST', `/bunker/${commId}/nuke`),

    // 8. SOCIAL (Feed)
    getFeed: (commId: string) => request('GET', `/social/feed?community_id=${commId}`),
    pinPost: (postId: string) => request('POST', `/social/posts/${postId}/pin`),
    deletePost: (postId: string) => request('DELETE', `/social/posts/${postId}`),
};