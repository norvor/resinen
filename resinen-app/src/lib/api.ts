import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export const user = writable<User | null>(null);

export interface User {
    id: string;
    email: string;
    full_name: string;
    avatar_url?: string;
    is_superuser: boolean;
    level: number;
    reputation_score: number;
    xp: number;
}

export interface Community {
    id: string;
    name: string;
    slug: string;
    description: string;
    banner_url?: string;
    member_count: number;
    archetypes: string[];
    config: any;
    is_private: boolean;
    creator_id?: string;
}

class ApiClient {
    private baseUrl: string;

    constructor() {
        // Points to FastAPI backend
        this.baseUrl = "https://api.resinen.com/api/v1";
    }

    private getHeaders() {
        const headers: Record<string, string> = {
            'Content-Type': 'application/json',
        };
        if (browser) {
            const token = localStorage.getItem('token');
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
        }
        return headers;
    }

    private async request(endpoint: string, options: RequestInit = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = this.getHeaders();
        
        const config = {
            ...options,
            headers: {
                ...headers,
                ...options.headers,
            },
        };

        const res = await fetch(url, config);

        if (!res.ok) {
            if (res.status === 401 && browser) {
                // Auto logout on 401
                localStorage.removeItem('token');
                user.set(null);
                window.location.href = '/login'; 
            }
            const errorData = await res.json().catch(() => ({}));
            throw new Error(errorData.detail || `API Error: ${res.status}`);
        }

        return res.json();
    }

    // --- GENERIC METHODS ---
    async get(endpoint: string) {
        return this.request(endpoint, { method: 'GET' });
    }

    async post(endpoint: string, body: any) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(body),
        });
    }

    async put(endpoint: string, body: any) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(body),
        });
    }

    async delete(endpoint: string) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    // --- AUTH & USER ---
    
    // ✅ FIXED: Points to /users/ (The trailing slash is important for FastAPI)
    async signup(data: { email: string; password: string; full_name: string }) {
        // 1. Create the user
        await this.post('/users', {
            email: data.email,
            password: data.password,
            full_name: data.full_name,
            is_superuser: false
        });
        
        // 2. Automatically log them in
        const formData = new FormData();
        formData.append('username', data.email);
        formData.append('password', data.password);
        return this.login(formData);
    }

    async login(formData: FormData) {
        // OAuth2 form data requires specific encoding
        const params = new URLSearchParams();
        formData.forEach((value, key) => {
            params.append(key, value as string);
        });

        const res = await fetch(`${this.baseUrl}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: params,
        });

        if (!res.ok) throw new Error('Login failed');
        const data = await res.json();
        
        if (browser) {
            localStorage.setItem('token', data.access_token);
        }
        return data;
    }

    async getMe() {
        const userData = await this.get('/users/me');
        user.set(userData);
        return userData;
    }

    async updateMe(data: any) {
        const updated = await this.request('/users/me', {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
        user.update(u => ({ ...u, ...updated }));
        return updated;
    }

    // --- COMMUNITIES ---
    async getCommunities() {
        return this.get('/communities/');
    }

    async getCommunityBySlug(slug: string) {
        return this.get(`/communities/${slug}`);
    }

    async getMembershipStatus(communityId: string) {
        return this.get(`/communities/${communityId}/membership`);
    }

    // --- ENGINE 1: BAZAAR ---
    async getListings(communityId: string) {
        return this.get(`/listings/?community_id=${communityId}`);
    }
    async vouchListing(listingId: string) {
        return this.post(`/listings/${listingId}/vouch`, {});
    }

    // --- ENGINE 2: SENATE ---
    async getProposals(communityId: string) {
        return this.get(`/governance/?community_id=${communityId}`);
    }
    async voteProposal(proposalId: string, choice: string) {
        return this.post(`/governance/${proposalId}/vote`, { choice });
    }

    // --- ENGINE 3: ACADEMY ---
    async getCurriculum(communityId: string) {
        return this.get(`/academy/?community_id=${communityId}`);
    }
    async completeLesson(lessonId: string) {
        return this.post(`/academy/lessons/${lessonId}/complete`, {});
    }

    // --- ENGINE 4: ARENA ---
    async getMatches(communityId: string) {
        return this.get(`/arena/?community_id=${communityId}`);
    }
    async predictMatch(matchId: string, teamId: string) {
        return this.post(`/arena/predict`, { match_id: matchId, team_id: teamId });
    }

    // --- ENGINE 5: CLUB ---
    async getEvents(communityId: string) {
        return this.get(`/club/?community_id=${communityId}`);
    }
    async rsvpEvent(eventId: string, status: string) {
        return this.post(`/club/${eventId}/rsvp`, { status });
    }

    // --- ENGINE 6: LIBRARY ---
    async getPageTree(communityId: string) {
        return this.get(`/library/tree?community_id=${communityId}`);
    }
    async getPage(communityId: string, slug: string) {
        return this.get(`/library/page/${slug}?community_id=${communityId}`);
    }

    // --- ENGINE 7: STAGE ---
    async getStageFeed(communityId: string) {
        return this.get(`/stage/?community_id=${communityId}`);
    }

    // --- ENGINE 8: BUNKER ---
    async getBunkerMessages(communityId: string) {
        return this.get(`/bunker/?community_id=${communityId}`);
    }
    async postBunkerMessage(communityId: string, content: string, isAnon: boolean, ttl: number) {
        return this.post(`/bunker/`, { community_id: communityId, content, is_anonymous: isAnon, ttl_seconds: ttl });
    }

    // --- ENGINE 9: GUILD ---
    async getProjects(communityId: string) {
        return this.get(`/guild/projects?community_id=${communityId}`);
    }
    async getBounties(communityId: string) {
        return this.get(`/guild/bounties?community_id=${communityId}`);
    }

    // --- ENGINE 10: GARDEN ---
    async getGarden(communityId: string) {
        return this.get(`/garden/?community_id=${communityId}`);
    }
    async checkInHabit(habitId: string) {
        return this.post(`/garden/${habitId}/check`, {});
    }
}

export const api = new ApiClient();