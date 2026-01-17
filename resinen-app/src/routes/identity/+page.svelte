<script lang="ts">
    import { user } from '$lib/api';
</script>

<div class="max-w-2xl mx-auto">
    
    <div class="bg-white border-4 border-black p-0 shadow-hard-lg relative overflow-hidden">
        
        <div class="bg-sp-blue p-6 border-b-4 border-black flex justify-between items-center">
            <h1 class="text-white text-2xl font-black uppercase tracking-widest">Citizen ID</h1>
            <div class="w-12 h-12 bg-white/20 rounded-full border-2 border-white/50 flex items-center justify-center">
                <span class="text-2xl">🏔️</span>
            </div>
        </div>

        <div class="p-8 flex flex-col md:flex-row gap-8 items-center md:items-start">
            
            <div class="flex-shrink-0">
                <div class="w-32 h-32 bg-sp-yellow border-4 border-black flex items-center justify-center text-5xl font-black shadow-hard">
                    {$user?.full_name?.charAt(0)}
                </div>
            </div>

            <div class="flex-grow space-y-4 w-full">
                <div>
                    <label class="block text-xs font-black text-gray-400 uppercase">Full Name</label>
                    <div class="text-2xl font-black uppercase">{$user?.full_name}</div>
                </div>

                <div>
                    <label class="block text-xs font-black text-gray-400 uppercase">Digital Identity (Email)</label>
                    <div class="text-xl font-bold font-mono">{$user?.email}</div>
                </div>

                <div>
                    <label class="block text-xs font-black text-gray-400 uppercase">User ID</label>
                    <div class="text-sm font-bold font-mono bg-gray-100 p-2 border-2 border-black inline-block">
                        {$user?.id || 'UNREGISTERED'}
                    </div>
                </div>
            </div>
        </div>

        <div class="bg-gray-100 p-4 border-t-4 border-black text-center">
            <p class="text-xs font-bold text-gray-500 uppercase">
                Issued by Resinen Governance Protocol • Valid Forever
            </p>
        </div>
    </div>

</div>