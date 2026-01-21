<script lang="ts">
    import { onMount } from 'svelte';
    import { api, type Membership } from '$lib/api';
    import { fade } from 'svelte/transition';

    export let data;
    $: community = data.community;

    let members: Membership[] = [];
    let loading = true;
    let filter = 'active'; // active, banned, pending

    onMount(async () => {
        await loadMembers();
    });

    async function loadMembers() {
        loading = true;
        try {
            members = await api.getMembers(community.id, filter);
        } catch (e) { console.error(e); } 
        finally { loading = false; }
    }

    async function updateRole(userId: string, newRole: string) {
        // In real app: api.updateMemberRole(community.id, userId, newRole)
        alert(`Promoted user ${userId} to ${newRole}`);
    }

    async function handleBan(userId: string) {
        if (!confirm("Ban this user? They will be removed immediately.")) return;
        try {
            await api.processMembership(community.id, userId, 'ban');
            await loadMembers();
        } catch (e) { alert("Ban failed"); }
    }
</script>

<div class="space-y-8 animate-fade-in-up">
    
    <div class="flex items-end justify-between border-b-4 border-black pb-6">
        <div>
            <div class="text-xs font-black uppercase text-gray-400 tracking-widest mb-1">
                CRM Engine
            </div>
            <h1 class="text-4xl font-black uppercase tracking-tighter">
                Member Registry
            </h1>
        </div>
        <div class="flex bg-gray-100 p-1 rounded gap-1">
            {#each ['active', 'pending', 'banned'] as f}
                <button 
                    on:click={() => { filter = f; loadMembers(); }}
                    class="px-4 py-2 text-xs font-bold uppercase rounded transition-colors {filter === f ? 'bg-black text-white' : 'text-gray-500 hover:bg-white'}"
                >
                    {f}
                </button>
            {/each}
        </div>
    </div>

    {#if loading}
        <div class="p-12 text-center text-gray-400 font-bold animate-pulse">Scanning Biometrics...</div>
    {:else}
        <div class="bg-white border-2 border-gray-200 rounded-xl overflow-hidden shadow-sm">
            <table class="w-full text-left">
                <thead class="bg-gray-50 border-b border-gray-200 text-xs font-black uppercase text-gray-400 tracking-widest">
                    <tr>
                        <th class="p-4">User</th>
                        <th class="p-4">Joined</th>
                        <th class="p-4">Role</th>
                        <th class="p-4 text-right">Actions</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-100 text-sm">
                    {#each members as m}
                        <tr class="hover:bg-gray-50 transition-colors">
                            <td class="p-4 flex items-center gap-3">
                                <div class="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center font-bold text-gray-500">
                                    {m.user?.full_name?.[0] || '?'}
                                </div>
                                <div>
                                    <div class="font-bold text-gray-900">{m.user?.full_name || 'Unknown'}</div>
                                    <div class="text-xs text-gray-400 font-mono">{m.user?.email || 'ID: ' + m.user_id}</div>
                                </div>
                            </td>
                            <td class="p-4 text-gray-500 font-mono text-xs">
                                {new Date(m.joined_at).toLocaleDateString()}
                            </td>
                            <td class="p-4">
                                <span class="px-2 py-1 rounded text-[10px] font-black uppercase border
                                {m.role === 'owner' ? 'bg-yellow-100 text-yellow-700 border-yellow-200' : 
                                 m.role === 'admin' ? 'bg-purple-100 text-purple-700 border-purple-200' : 
                                 'bg-gray-100 text-gray-600 border-gray-200'}">
                                    {m.role}
                                </span>
                            </td>
                            <td class="p-4 text-right flex justify-end gap-2">
                                <button on:click={() => updateRole(m.user_id, 'admin')} class="text-xs font-bold text-blue-600 hover:underline">Promote</button>
                                <button on:click={() => handleBan(m.user_id)} class="text-xs font-bold text-red-600 hover:underline">Ban</button>
                            </td>
                        </tr>
                    {/each}
                </tbody>
            </table>
        </div>
    {/if}
</div>