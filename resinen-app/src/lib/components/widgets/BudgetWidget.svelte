<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api';

    let monthlyLimit = $state(0);
    let totalSpent = $state(0);
    let currency = $state("USD"); 
    let isSettingUp = $state(true);
    
    // UI Inputs
    let amountInput = $state("");
    let isBusy = $state(false);

    // Derived
    let remaining = $derived(monthlyLimit - totalSpent);
    let percentUsed = $derived(monthlyLimit > 0 ? (totalSpent / monthlyLimit) * 100 : 0);
    let healthColor = $derived(percentUsed > 90 ? '#ef4444' : percentUsed > 75 ? '#f59e0b' : '#10b981');

    onMount(async () => {
        // 1. Local Cache
        if (typeof localStorage !== 'undefined') {
            const local = localStorage.getItem('resinen_budget');
            if (local) applyData(JSON.parse(local));
        }

        // 2. Cloud Sync
        try {
            const data = await api.widgets.loadDashboard();
            if (data && data.budget) {
                applyData(data.budget);
                saveLocal(data.budget);
            }
        } catch(e) { console.log("Offline mode"); }
    });

    function applyData(b: any) {
        monthlyLimit = b.monthly_limit || 0;
        totalSpent = b.spent || 0; 
        currency = b.currency || "USD";
        isSettingUp = monthlyLimit <= 0;
    }

    function saveLocal(data: any) {
        if (typeof localStorage !== 'undefined') localStorage.setItem('resinen_budget', JSON.stringify(data));
    }

    async function sync(newLimit: number, newSpent: number, newCurr: string) {
        isBusy = true;
        // Optimistic Update
        monthlyLimit = newLimit;
        totalSpent = newSpent;
        currency = newCurr;

        const payload = { 
            monthly_limit: newLimit, 
            spent: newSpent, 
            currency: newCurr 
        };

        try {
            await api.widgets.updateBudget(payload);
            saveLocal(payload);
        } catch(e) {
            console.error("Budget Sync Failed", e);
            alert("Sync failed. Check connection.");
        } finally {
            isBusy = false;
        }
    }

    function initializeBudget() {
        const val = parseFloat(amountInput);
        if (isNaN(val) || val <= 0) return;
        
        isSettingUp = false;
        amountInput = "";
        sync(val, 0, currency);
    }

    function addExpense() {
        const val = parseFloat(amountInput);
        if (isNaN(val) || val <= 0) return;
        
        const newTotal = totalSpent + val;
        amountInput = "";
        sync(monthlyLimit, newTotal, currency);
    }

    function reset() {
        if(confirm("Reset entire budget tracker?")) {
            isSettingUp = true;
            amountInput = "";
            sync(0, 0, currency);
        }
    }
</script>

<div class="card budget-widget">
    <div class="widget-header">
        <div class="title-grp">
            <span class="icon">💳</span>
            <span class="label">BUDGET</span>
        </div>
        {#if !isSettingUp}
            <button class="reset-btn" onclick={reset} title="Reset Budget">
                RESET
            </button>
        {/if}
    </div>

    <div class="content-area">
        {#if isSettingUp}
            <div class="setup-form">
                <div class="instruction">CONFIGURE WALLET</div>
                
                <div class="input-row">
                    <input type="text" class="curr-input" bind:value={currency} placeholder="Sym" maxlength="4" />
                    <input 
                        type="number" 
                        class="limit-input" 
                        bind:value={amountInput} 
                        placeholder="Monthly Limit" 
                        onkeydown={(e)=>e.key==='Enter' && initializeBudget()}
                        autoFocus 
                    />
                </div>
                
                <button class="action-btn" onclick={initializeBudget} disabled={isBusy}>
                    {isBusy ? 'SYNCING...' : 'ACTIVATE PROTOCOL'}
                </button>
            </div>
        {:else}
            <div class="wallet-view">
                <div class="digital-card" style="border-color: {healthColor}">
                    <div class="card-chip"></div>
                    <div class="card-balance">
                        <span class="curr">{currency}</span>
                        <span class="val">{remaining.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>
                    </div>
                    <div class="card-meta">
                        <span class="meta-label">REMAINING</span>
                        <span class="meta-limit"> / {currency}{monthlyLimit.toLocaleString()}</span>
                    </div>
                </div>

                <div class="progress-container">
                    <div class="progress-bg">
                        <div 
                            class="progress-fill" 
                            style="width: {Math.min(100, percentUsed)}%; background: {healthColor};"
                        ></div>
                    </div>
                    <div class="progress-text" style="color: {healthColor}">
                        {percentUsed.toFixed(1)}% DEPLETED
                    </div>
                </div>

                <div class="quick-add">
                    <input 
                        type="number" 
                        bind:value={amountInput} 
                        placeholder="Enter expense..." 
                        onkeydown={(e)=>e.key==='Enter' && addExpense()}
                    />
                    <button class="spend-btn" onclick={addExpense}>
                        PAY
                    </button>
                </div>
            </div>
        {/if}
    </div>
</div>

<style>
    .budget-widget {
        background: #0f172a; /* Slate 900 */
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 0;
        display: flex; flex-direction: column;
        height: 100%; min-height: 250px;
        font-family: 'JetBrains Mono', monospace;
        overflow: hidden;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }

    /* HEADER */
    .widget-header {
        display: flex; justify-content: space-between; align-items: center;
        padding: 12px 16px; background: #1e293b;
        border-bottom: 1px solid #334155;
    }
    .title-grp { display: flex; align-items: center; gap: 8px; color: #94a3b8; font-size: 0.75rem; font-weight: bold; letter-spacing: 1px; }
    
    .reset-btn { 
        background: none; 
        border: 1px solid #334155; 
        border-radius: 4px;
        color: #64748b; 
        cursor: pointer; 
        font-size: 0.65rem; 
        padding: 2px 6px; 
        font-family: 'JetBrains Mono';
        font-weight: bold;
        transition: 0.2s;
    }
    .reset-btn:hover { 
        background: #334155; 
        color: #f8fafc; 
    }

    /* CONTENT AREA */
    .content-area { flex: 1; padding: 16px; display: flex; flex-direction: column; justify-content: center; }

    /* SETUP FORM */
    .setup-form { display: flex; flex-direction: column; gap: 15px; width: 100%; }
    .instruction { text-align: center; color: #64748b; font-size: 0.8rem; letter-spacing: 2px; }
    
    .input-row { display: flex; gap: 10px; }
    
    input {
        background: #020617; border: 1px solid #334155; color: #f8fafc;
        padding: 12px; border-radius: 6px; font-family: 'Space Grotesk', sans-serif;
        outline: none; font-size: 1rem; text-align: center;
        transition: 0.2s;
    }
    input:focus { border-color: #38bdf8; box-shadow: 0 0 10px rgba(56, 189, 248, 0.1); }
    
    .curr-input { width: 60px; font-weight: bold; text-transform: uppercase; }
    .limit-input { flex: 1; }

    .action-btn {
        background: #38bdf8; color: #0f172a; border: none; padding: 12px;
        border-radius: 6px; font-weight: bold; font-family: 'JetBrains Mono';
        cursor: pointer; transition: 0.2s;
    }
    .action-btn:hover { background: #7dd3fc; }
    .action-btn:disabled { opacity: 0.5; cursor: not-allowed; }

    /* WALLET VIEW */
    .wallet-view { display: flex; flex-direction: column; gap: 15px; height: 100%; }

    /* DIGITAL CARD VISUAL */
    .digital-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 2px solid #10b981; /* Dynamic Color */
        border-radius: 10px; padding: 15px;
        position: relative; overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        transition: border-color 0.5s;
    }
    
    .card-chip {
        width: 35px; height: 25px;
        background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);
        border-radius: 4px; margin-bottom: 10px;
        position: relative;
    }
    .card-chip::after {
        content: ''; position: absolute; top: 50%; left: 0; width: 100%; height: 1px; background: rgba(0,0,0,0.2);
    }

    .card-balance { font-family: 'Space Grotesk', sans-serif; color: #fff; font-size: 1.8rem; font-weight: bold; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }
    .curr { font-size: 1rem; color: #94a3b8; margin-right: 4px; }
    
    .card-meta { display: flex; justify-content: space-between; margin-top: 5px; font-size: 0.7rem; color: #64748b; }
    .meta-limit { color: #94a3b8; }

    /* PROGRESS */
    .progress-container { display: flex; flex-direction: column; gap: 4px; }
    .progress-bg { height: 6px; background: #334155; border-radius: 3px; overflow: hidden; }
    .progress-fill { height: 100%; border-radius: 3px; transition: width 0.5s ease-out, background 0.5s; }
    .progress-text { font-size: 0.65rem; text-align: right; font-weight: bold; transition: color 0.5s; }

    /* QUICK ADD */
    .quick-add { display: flex; gap: 8px; margin-top: auto; }
    .quick-add input { flex: 1; padding: 8px; font-size: 0.9rem; text-align: left; }
    
    .spend-btn {
        background: #ef4444; color: #fff; border: none; padding: 0 15px;
        border-radius: 6px; font-weight: bold; font-family: 'JetBrains Mono';
        cursor: pointer; transition: 0.2s;
    }
    .spend-btn:hover { background: #f87171; box-shadow: 0 0 10px rgba(239, 68, 68, 0.4); }
</style>