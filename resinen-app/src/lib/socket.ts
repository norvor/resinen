import { writable, get } from 'svelte/store';
import { token, API_URL } from '$lib/api';

// --- TYPES ---
export interface ChatMessage {
    type: 'message';
    community_id: string;
    user_id: string;
    username: string;
    avatar_url: string;
    content: string;
    timestamp?: Date; // We'll add a local timestamp on arrival
}

// --- STORES ---
// The UI will subscribe to this to show the list of messages
export const messages = writable<ChatMessage[]>([]);

// The UI can check this to see if we are currently connected
export const isConnected = writable<boolean>(false);

// --- INTERNAL STATE ---
let socket: WebSocket | null = null;
let reconnectTimer: any = null;

// --- FUNCTIONS ---

export function connectToCommunity(communityId: string) {
    disconnect();

    const authToken = get(token);
    if (!authToken) return;

    // 1. Clean the base URL (Remove 'http://' or 'https://')
    let cleanUrl = API_URL.replace(/^https?:\/\//, '');
    
    // 2. Remove trailing slash if it exists to prevent double slash errors
    if (cleanUrl.endsWith('/')) {
        cleanUrl = cleanUrl.slice(0, -1);
    }

    // 3. Construct the clean WebSocket URL
    const wsProtocol = API_URL.startsWith('https') ? 'wss' : 'ws';
    const wsUrl = `${wsProtocol}://${cleanUrl}/ws/${communityId}?token=${authToken}`;

    console.log(`🔌 Connecting to: ${wsUrl}`); // Check this in browser console

    socket = new WebSocket(wsUrl);

    // 5. Event Handlers
    socket.onopen = () => {
        console.log("✅ Connected to Pulse.");
        isConnected.set(true);
        // Optional: Clear previous messages or keep them? 
        // For now, let's clear them when switching rooms.
        messages.set([]); 
    };

    socket.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            
            // Add a local timestamp for UI rendering
            data.timestamp = new Date();

            // Append to the store
            messages.update(current => [...current, data]);
            
        } catch (err) {
            console.error("⚠️ Failed to parse WS message:", err);
        }
    };

    socket.onclose = () => {
        console.log("🔌 Disconnected from Pulse.");
        isConnected.set(false);
        socket = null;
    };

    socket.onerror = (err) => {
        console.error("❌ Pulse Error:", err);
        // Optional: Implement auto-reconnect logic here later
    };
}

export function sendMessage(content: string, username: string, avatar: string) {
    if (socket && socket.readyState === WebSocket.OPEN) {
        const payload = {
            content,
            username,
            avatar_url: avatar
        };
        socket.send(JSON.stringify(payload));
    } else {
        console.warn("⚠️ Cannot send: Socket not open");
    }
}

export function disconnect() {
    if (socket) {
        socket.close();
        socket = null;
    }
    isConnected.set(false);
}