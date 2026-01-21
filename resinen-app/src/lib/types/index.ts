// place files you want to import through the `$lib` alias in this folder.
// src/lib/types/index.ts

// --- 1. CORE IDENTITY ---
// This defines the hierarchy of power in the Codex
export type Role = 'guest' | 'member' | 'moderator' | 'admin' | 'owner';

export interface User {
    id: string;
    email: string;
    full_name: string;
    avatar_url?: string;
    is_superuser: boolean; // This grants access to the CODEX (Super Admin Panel)
    created_at: string;
    
    // Global Gamification (Carries across all communities)
    level: number;
    xp: number;
    reputation_score: number;
}

export interface Community {
    id: string;
    slug: string;
    name: string;
    description: string;
    is_private: boolean;
    banner_url?: string;
    theme_color?: string; // e.g. "zinc", "blue", "amber"
    
    // Feature Flags: Which Engines are active?
    features: {
        senate: boolean;
        arena: boolean;
        market: boolean;
        // ... extend as needed
    };
}

export interface Membership {
    community_id: string;
    user_id: string;
    role: Role;
    joined_at: string;
    
    // Local Reputation (Specific to this community)
    local_xp: number;
    title?: string; // e.g. "Head Gardener"
}

// --- 2. ENGINE: SOCIAL (The Feed) ---
export interface Post {
    id: string;
    community_id: string;
    content: string;
    
    // Author Data (Flattened for UI performance)
    author_id: string;
    author_name: string;
    author_avatar?: string;
    author_role: Role; // Used to show "MOD" badges
    
    // Metrics
    view_count: number;
    like_count: number;
    comment_count: number;
    
    // User State
    is_liked_by_me: boolean;
    is_pinned: boolean; // Admin only feature
    created_at: string;
}

// --- 3. THE CODEX (Audit Logs) ---
// This is for the Super Admin Panel
export interface AuditLog {
    id: string;
    actor_id: string;
    action: string; // "DELETE_POST", "BAN_USER", "FORCE_VOTE"
    target_id: string;
    timestamp: string;
    ip_address?: string;
    metadata?: any;
}