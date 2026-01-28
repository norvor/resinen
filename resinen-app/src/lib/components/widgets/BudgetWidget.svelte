<script lang="ts">
    import { onMount } from 'svelte';
    import * as api from '$lib/api'; // <--- Import API

    let budget = $state(0);
    let balance = $state(0);
    let startDate = $state<number | null>(null);
    let history = $state<number[]>([]);
    let spendInput = $state("");
    let isSettingUp = $state(true);

    let daysLasted = $derived.by(() => {
        if (!startDate) return 0;
        const end = Date.now();
        return Math.floor((end - startDate) / (1000 * 60 * 60 * 24));
    });

    function initBudget() {
        const b = parseFloat(spendInput); if (isNaN(b) || b <= 0) return;
        budget = b; balance = b; startDate = Date.now(); history = []; spendInput = ""; isSettingUp = false;
        save();
    }

    function addSpend() {
        const val = parseFloat(spendInput); if (isNaN(val)) return;
        history = [val, ...history]; balance -= val; spendInput = "";
        save();
    }

    function reset() {
        if(confirm("Reset Budget?")) {
            isSettingUp = true; budget = 0; balance = 0; startDate = null;
            save();
        }
    }

    // --- UPDATED SAVE ---
    function save() {
        api.saveData('resinen_budget', { budget, balance, startDate, history, isSettingUp });
    }

    onMount(() => {
        const data = localStorage.getItem('resinen_budget');
        if (data) {
            const parsed = JSON.parse(data);
            budget = parsed.budget; balance = parsed.balance;
            startDate = parsed.startDate; history = parsed.history;
            isSettingUp = parsed.isSettingUp;
        }
    });
</script>

<div class="card budget-widget">
    <div class="head"><span>FINANCE RUN</span>{#if !isSettingUp}<button class="reset-btn" onclick={reset}>↺</button>{/if}</div>
    {#if isSettingUp}
        <div class="setup-mode">
            <div class="label">SET TOTAL BUDGET</div>
            <input type="number" bind:value={spendInput} placeholder="0.00" onkeydown={(e)=>e.key==='Enter' && initBudget()} />
            <button onclick={initBudget}>START RUN</button>
        </div>
    {:else}
        <div class="active-mode">
            <div class="survival-counter"><span class="day-big">{daysLasted}</span><span class="day-label">DAYS SURVIVED</span></div>
            <div class="progress-bar"><div class="fill" style="width: {Math.max(0, (balance/budget)*100)}%; background: {balance < budget*0.2 ? '#ef4444' : '#2dd4bf'};"></div></div>
            <div class="stats-row"><span class="curr">${balance.toFixed(0)}</span><span class="total">/ ${budget}</span></div>
            <div class="input-row"><input type="number" bind:value={spendInput} placeholder="Spend amount..." onkeydown={(e)=>e.key==='Enter' && addSpend()} /><button onclick={addSpend}>-</button></div>
        </div>
    {/if}
</div>

<style>
    /* ... Copy styles from previous BudgetWidget response ... */
    .budget-widget { height: 220px; display: flex; flex-direction: column; background: rgba(30, 41, 59, 0.4); backdrop-filter: blur(10px); border: 1px solid #334155; border-radius: 12px; overflow: hidden; } .head { padding: 10px 15px; border-bottom: 1px solid #334155; color: #2dd4bf; font-family: 'JetBrains Mono'; font-size: 0.7rem; display: flex; justify-content: space-between; } .reset-btn { background: none; border: none; color: #64748b; cursor: pointer; } .setup-mode, .active-mode { flex: 1; padding: 15px; display: flex; flex-direction: column; gap: 10px; justify-content: center; } .label { font-size: 0.7rem; color: #94a3b8; text-align: center; } input { background: rgba(0,0,0,0.3); border: 1px solid #334155; color: #fff; padding: 8px; border-radius: 4px; text-align: center; font-family: 'Space Grotesk'; outline: none; font-size: 1rem; } input:focus { border-color: #2dd4bf; } button { background: #2dd4bf; color: #000; border: none; padding: 8px; border-radius: 4px; font-weight: bold; cursor: pointer; } .survival-counter { text-align: center; margin-bottom: 5px; } .day-big { font-size: 2.5rem; font-weight: bold; line-height: 1; color: #fff; display: block; } .day-label { font-size: 0.6rem; color: #64748b; letter-spacing: 2px; } .progress-bar { height: 6px; background: #1e293b; border-radius: 3px; overflow: hidden; } .fill { height: 100%; transition: width 0.5s cubic-bezier(0.16, 1, 0.3, 1); } .stats-row { display: flex; justify-content: space-between; font-family: 'JetBrains Mono'; font-size: 0.8rem; } .curr { color: #fff; font-weight: bold; } .total { color: #64748b; } .input-row { display: flex; gap: 5px; margin-top: auto; } .input-row input { flex: 1; text-align: left; } .input-row button { width: 40px; background: rgba(239, 68, 68, 0.2); color: #ef4444; } .input-row button:hover { background: #ef4444; color: #fff; }
</style>