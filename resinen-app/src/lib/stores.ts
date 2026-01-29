import { writable } from 'svelte/store';
import { browser } from '$app/environment';

const initialToken = browser ? localStorage.getItem('token') : null;

export const authState = writable({
    isAuthenticated: !!initialToken,
    token: initialToken
});

export function logout() {
    if (browser) localStorage.removeItem('token');
    authState.set({ isAuthenticated: false, token: null });
}

export function login(token: string) {
    if (browser) localStorage.setItem('token', token);
    authState.set({ isAuthenticated: true, token });
}