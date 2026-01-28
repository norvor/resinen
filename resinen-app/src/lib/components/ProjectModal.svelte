<script lang="ts">
    // PROPS
    let { project, isOpen, onClose, onSave } = $props();

    // LOCAL STATE FOR EDITING
    let name = $state(project?.name || "");
    let org = $state(project?.org || "");
    let description = $state(project?.description || "");
    let links = $state(project?.links ? [...project.links] : []);
    
    let newLinkName = $state("");
    let newLinkUrl = $state("");

    // SYNC WHEN PROJECT OPENS
    $effect(() => {
        if (project) {
            name = project.name;
            org = project.org || "";
            description = project.description || "";
            links = [...project.links];
        }
    });

    function addLink() {
        if (!newLinkName || !newLinkUrl) return;
        links = [...links, { name: newLinkName, url: newLinkUrl }];
        newLinkName = "";
        newLinkUrl = "";
    }

    function removeLink(index: number) {
        links = links.filter((_, i) => i !== index);
    }

    // Fixes links that don't have http/https
    function ensureUrl(url: string) {
        if (!url) return '';
        if (!/^https?:\/\//i.test(url)) {
            return 'https://' + url;
        }
        return url;
    }

    function handleSave() {
        onSave({ ...project, name, org, description, links });
        onClose();
    }
</script>

{#if isOpen}
    <div class="modal-backdrop" onclick={onClose}>
        <div class="modal-window" onclick={(e) => e.stopPropagation()}>
            <div class="modal-header">
                <div class="rune-display">{project.rune || '✦'}</div>
                <div class="header-inputs">
                    <input type="text" class="title-input" bind:value={name} placeholder="PROJECT NAME" />
                    <input type="text" class="org-input" bind:value={org} placeholder="ORGANIZATION / CLIENT" />
                </div>
                <button class="close-btn" onclick={onClose}>×</button>
            </div>

            <div class="modal-body">
                
                <div class="section-group">
                    <div class="section-label">DIRECTIVE / DESCRIPTION</div>
                    <textarea class="desc-input" bind:value={description} placeholder="Enter mission details, goals, or brief..."></textarea>
                </div>

                <div class="section-group">
                    <div class="section-label">MISSION RESOURCES</div>
                    
                    <div class="links-list">
                        {#each links as link, i}
                            <div class="link-row">
                                <div class="link-info">
                                    <span class="l-name">{link.name}</span>
                                    <span class="l-url">{link.url}</span>
                                </div>
                                <div class="actions">
                                    <a href="{ensureUrl(link.url)}" target="_blank" class="visit-btn" rel="noopener noreferrer">↗</a>
                                    <button class="del-btn" onclick={() => removeLink(i)}>×</button>
                                </div>
                            </div>
                        {/each}
                        {#if links.length === 0}
                            <div class="empty-state">NO ACTIVE UPLINKS</div>
                        {/if}
                    </div>

                    <div class="add-section">
                        <input type="text" bind:value={newLinkName} placeholder="Resource Name (e.g. Basecamp)" />
                        <input type="text" bind:value={newLinkUrl} placeholder="URL..." onkeydown={(e) => e.key === 'Enter' && addLink()} />
                        <button onclick={addLink}>ADD</button>
                    </div>
                </div>
            </div>

            <div class="modal-footer">
                <button class="save-btn" onclick={handleSave}>CONFIRM UPDATES</button>
            </div>
        </div>
    </div>
{/if}

<style>
    .modal-backdrop { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); backdrop-filter: blur(5px); z-index: 9999; display: flex; justify-content: center; align-items: center; animation: fade 0.2s; }
    .modal-window { width: 600px; max-width: 90%; background: #0f172a; border: 1px solid #334155; border-radius: 12px; box-shadow: 0 20px 50px rgba(0,0,0,0.5); overflow: hidden; animation: slide 0.3s cubic-bezier(0.16, 1, 0.3, 1); display: flex; flex-direction: column; max-height: 85vh; }
    
    .modal-header { padding: 20px; background: rgba(30, 41, 59, 0.5); border-bottom: 1px solid #334155; display: flex; align-items: flex-start; gap: 15px; }
    .header-inputs { flex: 1; display: flex; flex-direction: column; gap: 5px; }
    .rune-display { font-size: 2rem; width: 50px; height: 50px; background: rgba(45, 212, 191, 0.1); color: #2dd4bf; border-radius: 8px; display: flex; justify-content: center; align-items: center; border: 1px solid #2dd4bf; box-shadow: 0 0 15px rgba(45, 212, 191, 0.2); }
    
    .title-input { width: 100%; background: transparent; border: none; font-family: 'Space Grotesk', sans-serif; font-size: 1.5rem; font-weight: bold; color: #fff; outline: none; border-bottom: 2px solid transparent; transition: 0.2s; padding: 0; }
    .title-input:focus { border-bottom-color: #2dd4bf; }
    
    .org-input { width: 100%; background: transparent; border: none; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #94a3b8; outline: none; padding: 0; letter-spacing: 1px; }
    .org-input:focus { color: #fff; }

    .close-btn { background: none; border: none; color: #64748b; font-size: 2rem; cursor: pointer; line-height: 1; }
    .close-btn:hover { color: #ef4444; }

    .modal-body { padding: 20px; flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 25px; }
    .section-group { display: flex; flex-direction: column; gap: 8px; }
    .section-label { font-family: 'JetBrains Mono'; font-size: 0.7rem; color: #2dd4bf; letter-spacing: 1px; font-weight: bold; }
    
    .desc-input { width: 100%; height: 80px; background: rgba(255,255,255,0.03); border: 1px solid #334155; border-radius: 6px; color: #cbd5e1; padding: 10px; font-family: sans-serif; font-size: 0.9rem; resize: none; outline: none; transition: 0.2s; }
    .desc-input:focus { border-color: #2dd4bf; background: rgba(255,255,255,0.05); }

    .links-list { display: flex; flex-direction: column; gap: 8px; }
    .link-row { background: rgba(255,255,255,0.03); border: 1px solid #334155; padding: 10px; border-radius: 6px; display: flex; justify-content: space-between; align-items: center; transition: 0.2s; }
    .link-row:hover { background: rgba(255,255,255,0.05); border-color: #94a3b8; }
    .link-info { display: flex; flex-direction: column; overflow: hidden; }
    .l-name { font-weight: bold; font-size: 0.9rem; color: #e2e8f0; }
    .l-url { font-family: 'JetBrains Mono'; font-size: 0.7rem; color: #64748b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 350px; }
    
    .actions { display: flex; gap: 5px; }
    .visit-btn, .del-btn { width: 30px; height: 30px; display: flex; justify-content: center; align-items: center; border-radius: 4px; border: none; cursor: pointer; transition: 0.2s; text-decoration: none; }
    .visit-btn { background: rgba(45, 212, 191, 0.1); color: #2dd4bf; }
    .visit-btn:hover { background: #2dd4bf; color: #000; }
    .del-btn { background: rgba(239, 68, 68, 0.1); color: #ef4444; }
    .del-btn:hover { background: #ef4444; color: #fff; }

    .empty-state { text-align: center; padding: 15px; color: #475569; font-family: 'JetBrains Mono'; border: 2px dashed #334155; border-radius: 6px; font-size: 0.8rem; }

    .add-section { display: flex; gap: 10px; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px; border: 1px solid #334155; margin-top: 5px; }
    .add-section input { flex: 1; background: transparent; border: none; border-bottom: 1px solid #475569; color: #fff; padding: 5px; font-family: 'JetBrains Mono'; font-size: 0.8rem; outline: none; }
    .add-section input:focus { border-color: #2dd4bf; }
    .add-section button { background: #2dd4bf; color: #000; border: none; padding: 5px 15px; font-weight: bold; border-radius: 4px; cursor: pointer; }

    .modal-footer { padding: 20px; border-top: 1px solid #334155; text-align: right; background: rgba(15, 23, 42, 0.5); }
    .save-btn { background: #fff; color: #000; border: none; padding: 12px 24px; font-weight: bold; font-family: 'Space Grotesk'; letter-spacing: 1px; cursor: pointer; border-radius: 6px; transition: 0.2s; }
    .save-btn:hover { background: #2dd4bf; box-shadow: 0 0 20px rgba(45, 212, 191, 0.4); }

    @keyframes fade { from { opacity: 0; } to { opacity: 1; } }
    @keyframes slide { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
</style>