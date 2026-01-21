// src/lib/api.ts
import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import type { User, Post, Community, Membership, Role } from './types';

// --- GLOBAL STORES ---
export const currentUser = writable<User | null>(null);
export const activeMembership = writable<Membership | null>(null);

class ApiClient {
    private baseUrl: string;

    constructor() {
        // Keeping your remote URL as requested.
        // Change to "http://127.0.0.1:8000/api/v1" if testing strictly locally.
        this.baseUrl = "https://api.resinen.com/api/v1";
    }

    // --- INTERNAL HELPERS ---
    private getHeaders(isUpload = false) {
        const headers: Record<string, string> = {};
        if (!isUpload) headers['Content-Type'] = 'application/json';
        
        if (browser) {
            // Standardized to 'access_token' for OAuth2 compliance
            const token = localStorage.getItem('access_token');
            if (token) headers['Authorization'] = `Bearer ${token}`;
        }
        return headers;
    }

    private async request<T>(endpoint: string, config: RequestInit = {}): Promise<T> {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = this.getHeaders();
        
        const res = await fetch(url, { ...config, headers: { ...headers, ...config.headers } });

        if (!res.ok) {
            // Auto-Logout on 401 (Unauthorized)
            if (res.status === 401 && browser) {
                this.logout();
                return Promise.reject('Unauthorized');
            }
            
            // Codex Access Denied (Super Admin protection)
            if (res.status === 403) {
                throw new Error("CODEX_DENIED: Insufficient Clearance.");
            }

            const err = await res.json().catch(() => ({ detail: "Network Error" }));
            throw new Error(err.detail || `API Error ${res.status}`);
        }

        // Handle 204 No Content (Success but empty)
        if (res.status === 204) return {} as T;

        return res.json();
    }

    // --- AUTH & USER ---
    async signup(data: { email: string; password: string; full_name: string }) {
        await this.request('/users', {
            method: 'POST',
            body: JSON.stringify({
                email: data.email,
                password: data.password,
                full_name: data.full_name,
                is_superuser: false
            })
        });
        
        // Auto-login after signup
        const formData = new FormData();
        formData.append('username', data.email);
        formData.append('password', data.password);
        return this.login(formData);
    }

    async login(formData: FormData) {
        // OAuth2 standard expects form-data
        const res = await fetch(`${this.baseUrl}/auth/login`, {
            method: 'POST',
            body: formData 
        });
        if (!res.ok) throw new Error('Invalid Credentials');
        
        const data = await res.json();
        if (browser) {
            localStorage.setItem('access_token', data.access_token);
            await this.getMe(); // Hydrate store immediately
        }
        return data;
    }

    async logout() {
        if (browser) localStorage.removeItem('access_token');
        currentUser.set(null);
        activeMembership.set(null);
        if (browser) window.location.href = '/login';
    }

    async getMe() {
        const user = await this.request<User>('/users/me');
        currentUser.set(user);
        return user;
    }

    async updateMe(data: Partial<User>) {
        const updated = await this.request<User>('/users/me', {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
        currentUser.update(u => ({ ...u, ...updated }));
        return updated;
    }

    // --- COMMUNITIES & MEMBERSHIP ---
    async getCommunities() {
        return this.request<Community[]>('/communities/');
    }

    async getCommunityBySlug(slug: string) {
        return this.request<Community>(`/communities/by-slug/${slug}`);
    }

    async getMembershipStatus(communityId: string) {
        const membership = await this.request<Membership>(`/communities/${communityId}/membership_status`);
        activeMembership.set(membership);
        return membership;
    }

    async joinCommunity(communityId: string) {
        return this.request<Membership>(`/communities/${communityId}/join`, { method: 'POST' });
    }

    // --- ENGINE 1: SOCIAL (The Feed) ---
   async getFeed(communityId: string, skip = 0) {
        return this.request<Post[]>(`/social/feed?community_id=${communityId}&skip=${skip}`, { 
            method: 'GET' 
        });
    }

    async createPost(data: { community_id: string; content: string; title?: string }) {
        return this.request<Post>('/social/posts', { 
            method: 'POST', 
            body: JSON.stringify(data) 
        });
    }

    async getPost(postId: string) {
        return this.request<Post>(`/social/posts/${postId}`, { 
            method: 'GET' 
        });
    }

    async likePost(postId: string) {
        return this.request<{ status: string; likes: number }>(`/social/posts/${postId}/like`, { 
            method: 'POST' 
        });
    }

    async deletePost(postId: string) {
        return this.request<{ status: string }>(`/social/posts/${postId}`, { 
            method: 'DELETE' 
        });
    }

    // --- COMMENTS ---

    async getComments(postId: string) {
        return this.request<Comment[]>(`/social/posts/${postId}/comments`, { 
            method: 'GET' 
        });
    }

    async createComment(postId: string, content: string) {
        return this.request<Comment>(`/social/posts/${postId}/comments`, { 
            method: 'POST', 
            body: JSON.stringify({ content }) 
        });
    }

    async likeComment(commentId: string) {
        return this.request<{ status: string }>(`/social/comments/${commentId}/like`, { 
            method: 'POST' 
        });
    }

    async deleteComment(commentId: string) {
        return this.request<{ status: string }>(`/social/comments/${commentId}`, { 
            method: 'DELETE' 
        });
    }
    // --- ENGINE 2: BAZAAR ---
    async getListings(communityId: string) {
        return this.request(`/listings/?community_id=${communityId}`);
    }
    async vouchListing(listingId: string) {
        return this.request(`/listings/${listingId}/vouch`, { method: 'POST' });
    }

    // --- ENGINE 3: SENATE ---
    async getProposals(communityId: string) {
        return this.request(`/governance/?community_id=${communityId}`);
    }
    async voteProposal(proposalId: string, choice: string) {
        return this.request(`/governance/${proposalId}/vote`, { 
            method: 'POST',
            body: JSON.stringify({ choice })
        });
    }

    // --- ENGINE 4: ACADEMY ---
    async getCurriculum(communityId: string) {
        return this.request(`/academy/?community_id=${communityId}`);
    }
    async completeLesson(lessonId: string) {
        return this.request(`/academy/lessons/${lessonId}/complete`, { method: 'POST' });
    }

    // --- ENGINE 5: ARENA ---
    async getMatches(communityId: string) {
        return this.request(`/arena/?community_id=${communityId}`);
    }
    async predictMatch(matchId: string, teamId: string) {
        return this.request(`/arena/predict`, { 
            method: 'POST',
            body: JSON.stringify({ match_id: matchId, team_id: teamId })
        });
    }

    // --- ENGINE 6: CLUB ---
    async getEvents(communityId: string) {
        return this.request(`/club/?community_id=${communityId}`);
    }
    async rsvpEvent(eventId: string, status: string) {
        return this.request(`/club/${eventId}/rsvp`, { 
            method: 'POST',
            body: JSON.stringify({ status })
        });
    }

    // --- ENGINE 7: LIBRARY ---
    async getPageTree(communityId: string) {
        return this.request(`/library/tree?community_id=${communityId}`);
    }
    async getPage(communityId: string, slug: string) {
        return this.request(`/library/page/${slug}?community_id=${communityId}`);
    }

    // --- ENGINE 8: STAGE ---
    async getStageFeed(communityId: string) {
        return this.request(`/stage/?community_id=${communityId}`);
    }

    // --- ENGINE 9: BUNKER ---
    async getBunkerMessages(communityId: string) {
        return this.request(`/bunker/?community_id=${communityId}`);
    }
    async postBunkerMessage(communityId: string, content: string, isAnon: boolean, ttl: number) {
        return this.request(`/bunker/`, { 
            method: 'POST',
            body: JSON.stringify({ community_id: communityId, content, is_anonymous: isAnon, ttl_seconds: ttl })
        });
    }

    // --- ENGINE 10: GUILD ---
    async getProjects(communityId: string) {
        return this.request(`/guild/projects?community_id=${communityId}`);
    }
    async getBounties(communityId: string) {
        return this.request(`/guild/bounties?community_id=${communityId}`);
    }

    // --- ENGINE 11: GARDEN ---
    async getGarden(communityId: string) {
        return this.request(`/garden/?community_id=${communityId}`);
    }
    async checkInHabit(habitId: string) {
        return this.request(`/garden/${habitId}/check`, { method: 'POST' });
    }
}

export const api = new ApiClient();