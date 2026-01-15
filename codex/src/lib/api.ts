// codex/src/lib/api.ts

const API_URL = 'https://api.resinen.com';

// --- TYPES ---

export type SiteConfig = {
    id: string;
    brand_name: string;
    logo_url: string;
    contact_email: string;
    footer_text: string;
    social_links: Record<string, string>;
    navigation: { label: string, url: string }[];
};

export type HomePage = {
    id: string;
    hero_title: string;
    hero_subtitle: string;
    hero_cta_primary: string;
    hero_cta_secondary: string;
    featured_insights: string[];
    ticker_items: { label: string, value: string }[];
};

export type BlogPost = {
    slug: string;
    title: string;
    summary: string;
    cover_image: string;
    content: string;
    category: string;
    published: boolean;
};

export type Framework = {
    id: string;
    name: string;
    subject: string;
    description: string;
    summary: Record<string, any>;
    isomorphism: Record<string, any>;
    nodes: Record<string, any>[];
    solution: Record<string, any>;
    formulas: Record<string, any>;
    protocol: Record<string, any>;
    values: Record<string, any>;
};

export type Engine = {
    id: string;
    name: string;
    category: string;
    description: string;
    hero: Record<string, any>;
    modules: Record<string, any>[];
    comparison: Record<string, any>;
    bottomLine: string;
};

export type DoctrinePage = {
    id: string;
    title: string;
    subtitle: string;
    intro_text: string;
    principles: { title: string, desc: string }[];
    team_members: { name: string, role: string, bio: string }[];
};

export type ContactPage = {
    id: string;
    title: string;
    subtitle: string;
    locations: { city: string, address: string, email: string }[];
    form_success_message: string;
    support_email: string;
};

// --- API CLIENT ---

export const api = {
    healthCheck: async () => (await fetch(`${API_URL}/`)).json(),

    // --- GLOBAL CONFIG ---
    getConfig: async (): Promise<SiteConfig> => (await fetch(`${API_URL}/config`)).json(),
    updateConfig: async (data: SiteConfig) => {
        await fetch(`${API_URL}/config`, { method: 'POST', body: JSON.stringify(data), headers: { 'Content-Type': 'application/json' }});
    },

    // --- HOMEPAGE ---
    getHomePage: async (): Promise<HomePage> => (await fetch(`${API_URL}/homepage`)).json(),
    updateHomePage: async (data: HomePage) => {
        await fetch(`${API_URL}/homepage`, { method: 'POST', body: JSON.stringify(data), headers: { 'Content-Type': 'application/json' }});
    },

    // --- BLOG ---
    getPosts: async (): Promise<BlogPost[]> => (await fetch(`${API_URL}/posts`)).json(),
    savePost: async (data: BlogPost) => {
        await fetch(`${API_URL}/posts`, { method: 'POST', body: JSON.stringify(data), headers: { 'Content-Type': 'application/json' }});
    },
    deletePost: async (slug: string) => {
        await fetch(`${API_URL}/posts/${slug}`, { method: 'DELETE' });
    },

    getDoctrine: async (): Promise<DoctrinePage> => (await fetch(`${API_URL}/doctrine`)).json(),
    updateDoctrine: async (data: DoctrinePage) => fetch(`${API_URL}/doctrine`, { method: 'POST', body: JSON.stringify(data), headers: { 'Content-Type': 'application/json' }}),

    getContact: async (): Promise<ContactPage> => (await fetch(`${API_URL}/contact`)).json(),
    updateContact: async (data: ContactPage) => fetch(`${API_URL}/contact`, { method: 'POST', body: JSON.stringify(data), headers: { 'Content-Type': 'application/json' }}),

    // --- FRAMEWORKS ---
    getFrameworks: async (): Promise<Framework[]> => {
        const res = await fetch(`${API_URL}/frameworks`);
        return res.json();
    },

    createFramework: async (data: Framework) => {
        const res = await fetch(`${API_URL}/frameworks`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error('Failed to create framework');
        return res.json();
    },

    // --- ENGINES (NEW) ---
    getEngines: async (): Promise<Engine[]> => {
        const res = await fetch(`${API_URL}/engines`);
        return res.json();
    },

    createEngine: async (data: Engine) => {
        const res = await fetch(`${API_URL}/engines`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error('Failed to create engine');
        return res.json();
    }
};