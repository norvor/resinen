<script lang="ts">
    // PROPS
    let { place, isOpen, onClose, onSave } = $props();

    // LOCAL STATE
    let name = $state(place?.name || "");
    let photos = $state(place?.photos ? [...place.photos] : []);
    let newPhotoUrl = $state("");

    $effect(() => {
        if (place) {
            name = place.name;
            photos = [...place.photos];
        }
    });

    function addPhoto() {
        if (!newPhotoUrl) return;
        photos = [...photos, newPhotoUrl];
        newPhotoUrl = "";
    }

    function removePhoto(index: number) {
        photos = photos.filter((_, i) => i !== index);
    }

    function handleSave() {
        onSave({ ...place, name, photos });
        onClose();
    }
</script>

{#if isOpen}
    <div class="modal-backdrop" onclick={onClose}>
        <div class="modal-window" onclick={(e) => e.stopPropagation()}>
            <div class="modal-header">
                <div class="icon-display">✈️</div>
                <input type="text" class="title-input" bind:value={name} placeholder="DESTINATION NAME" />
                <button class="close-btn" onclick={onClose}>×</button>
            </div>

            <div class="modal-body">
                <div class="section-label">VISUAL LOGS ({photos.length})</div>
                
                <div class="gallery-grid">
                    {#each photos as url, i}
                        <div class="photo-card" style="background-image: url({url})">
                            <button class="del-btn" onclick={() => removePhoto(i)}>×</button>
                        </div>
                    {/each}
                    {#if photos.length === 0}
                        <div class="empty-state">NO VISUAL DATA UPLOADED</div>
                    {/if}
                </div>

                <div class="add-section">
                    <input type="text" bind:value={newPhotoUrl} placeholder="Paste Image URL..." onkeydown={(e) => e.key === 'Enter' && addPhoto()} />
                    <button onclick={addPhoto}>ADD PHOTO</button>
                </div>
            </div>

            <div class="modal-footer">
                <button class="save-btn" onclick={handleSave}>CONFIRM TRAVEL DATA</button>
            </div>
        </div>
    </div>
{/if}

<style>
    .modal-backdrop { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); backdrop-filter: blur(8px); z-index: 9999; display: flex; justify-content: center; align-items: center; animation: fade 0.2s; }
    .modal-window { width: 600px; max-width: 90%; background: #0f172a; border: 1px solid #334155; border-radius: 16px; box-shadow: 0 20px 50px rgba(0,0,0,0.6); overflow: hidden; animation: slide 0.3s cubic-bezier(0.16, 1, 0.3, 1); display: flex; flex-direction: column; max-height: 85vh; }
    
    .modal-header { padding: 20px; background: rgba(30, 41, 59, 0.5); border-bottom: 1px solid #334155; display: flex; align-items: center; gap: 15px; }
    .icon-display { font-size: 2rem; width: 50px; height: 50px; background: rgba(96, 165, 250, 0.1); color: #60a5fa; border-radius: 8px; display: flex; justify-content: center; align-items: center; border: 1px solid #60a5fa; box-shadow: 0 0 15px rgba(96, 165, 250, 0.2); }
    .title-input { flex: 1; background: transparent; border: none; font-family: 'Space Grotesk', sans-serif; font-size: 1.5rem; font-weight: bold; color: #fff; outline: none; border-bottom: 2px solid transparent; transition: 0.2s; }
    .title-input:focus { border-bottom-color: #60a5fa; }
    .close-btn { background: none; border: none; color: #64748b; font-size: 2rem; cursor: pointer; line-height: 1; }
    .close-btn:hover { color: #ef4444; }

    .modal-body { padding: 20px; flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 15px; }
    .section-label { font-family: 'JetBrains Mono'; font-size: 0.7rem; color: #94a3b8; letter-spacing: 1px; }

    .gallery-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 10px; min-height: 100px; }
    .photo-card { aspect-ratio: 1; background-size: cover; background-position: center; border-radius: 8px; border: 1px solid #334155; position: relative; transition: 0.2s; }
    .photo-card:hover { transform: scale(1.05); border-color: #60a5fa; z-index: 2; }
    .del-btn { position: absolute; top: 5px; right: 5px; background: rgba(0,0,0,0.6); color: #fff; border: none; border-radius: 50%; width: 24px; height: 24px; cursor: pointer; opacity: 0; transition: 0.2s; display: flex; justify-content: center; align-items: center; }
    .photo-card:hover .del-btn { opacity: 1; }
    .del-btn:hover { background: #ef4444; }

    .empty-state { grid-column: 1 / -1; text-align: center; padding: 40px; color: #475569; font-family: 'JetBrains Mono'; border: 2px dashed #334155; border-radius: 8px; font-size: 0.8rem; }

    .add-section { display: flex; gap: 10px; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px; border: 1px solid #334155; }
    .add-section input { flex: 1; background: transparent; border: none; border-bottom: 1px solid #475569; color: #fff; padding: 5px; font-family: 'JetBrains Mono'; font-size: 0.8rem; outline: none; }
    .add-section input:focus { border-color: #60a5fa; }
    .add-section button { background: #60a5fa; color: #000; border: none; padding: 5px 15px; font-weight: bold; border-radius: 4px; cursor: pointer; font-family: 'JetBrains Mono'; font-size: 0.7rem; }

    .modal-footer { padding: 20px; border-top: 1px solid #334155; text-align: right; background: rgba(15, 23, 42, 0.5); }
    .save-btn { background: #fff; color: #000; border: none; padding: 12px 24px; font-weight: bold; font-family: 'Space Grotesk'; letter-spacing: 1px; cursor: pointer; border-radius: 6px; transition: 0.2s; }
    .save-btn:hover { background: #60a5fa; box-shadow: 0 0 20px rgba(96, 165, 250, 0.4); }

    @keyframes fade { from { opacity: 0; } to { opacity: 1; } }
    @keyframes slide { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
</style>