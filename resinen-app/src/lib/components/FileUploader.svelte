<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import { get } from 'svelte/store';
    import { API_URL, token } from '$lib/api';

    // Props
    export let label: string = "Upload Media";
    export let accept: string = "image/*"; // Default to images
    export let uploadingText: string = "Uploading to Vault...";

    const dispatch = createEventDispatcher();

    let fileInput: HTMLInputElement;
    let isUploading: boolean = false;
    let error: string | null = null;
    let previewUrl: string | null = null;

    async function handleFileSelect() {
        const file = fileInput.files?.[0];
        if (!file) return;

        // 1. Reset State
        isUploading = true;
        error = null;
        
        // 2. Create Immediate Preview (UX)
        previewUrl = URL.createObjectURL(file);

        try {
            // 3. Prepare Payload
            const formData = new FormData();
            formData.append('file', file);

            // 4. Get Auth Token
            const currentToken = get(token);
            const headers: HeadersInit = {};
            
            if (currentToken) {
                headers['Authorization'] = `Bearer ${currentToken}`;
            }
            // Note: We do NOT set Content-Type header for FormData; 
            // the browser automatically sets it with the correct boundary.

            // 5. Send to Backend
            const res = await fetch(`${API_URL}/media/upload`, {
                method: 'POST',
                headers,
                body: formData
            });

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.detail || 'Upload failed');
            }

            const data = await res.json();

            // 6. Success: Dispatch URL back to parent
            // Expected backend response: { "url": "https://minio..." }
            dispatch('success', { url: data.url });

        } catch (e: any) {
            console.error("Upload Error:", e);
            error = e.message || "Failed to upload.";
            previewUrl = null; // Clear preview on failure
        } finally {
            isUploading = false;
        }
    }

    function triggerSelect() {
        fileInput.click();
    }
</script>

<div class="uploader">
    <div class="label">{label}</div>

    <button 
        type="button" 
        class="preview-area" 
        on:click={triggerSelect} 
        disabled={isUploading}
    >
        {#if isUploading}
            <div class="status loading">
                <span class="spinner">↻</span> {uploadingText}
            </div>
        {:else if previewUrl}
            <img src={previewUrl} alt="Preview" class="preview-img" />
            <div class="overlay">Change</div>
        {:else}
            <div class="placeholder">
                <span class="icon">⬆️</span>
                <span>Click to Upload</span>
            </div>
        {/if}
    </button>

    {#if error}
        <div class="error">{error}</div>
    {/if}

    <input 
        bind:this={fileInput}
        type="file" 
        {accept}
        on:change={handleFileSelect}
        style="display: none;" 
    />
</div>

<style>
    .uploader {
        width: 100%;
        max-width: 100%;
        font-family: inherit;
    }

    .label {
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #374151; /* Tailwind gray-700 */
    }

    .preview-area {
        width: 100%;
        height: 160px;
        border: 2px dashed #d1d5db; /* gray-300 */
        border-radius: 0.5rem;
        background: #f9fafb; /* gray-50 */
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        padding: 0;
        overflow: hidden;
        position: relative;
        transition: all 0.2s;
    }

    .preview-area:hover:not(:disabled) {
        border-color: #6366f1; /* Indigo-500 (Brand color?) */
        background: #eef2ff;
    }

    .preview-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .placeholder {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
        color: #6b7280; /* gray-500 */
        font-size: 0.9rem;
    }

    .icon {
        font-size: 1.5rem;
    }

    .overlay {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        background: rgba(0,0,0,0.6);
        color: white;
        font-size: 0.8rem;
        padding: 4px;
        text-align: center;
        opacity: 0;
        transition: opacity 0.2s;
    }

    .preview-area:hover .overlay {
        opacity: 1;
    }

    .status.loading {
        color: #6366f1;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .spinner {
        display: inline-block;
        animation: spin 1s linear infinite;
    }

    .error {
        margin-top: 0.5rem;
        font-size: 0.8rem;
        color: #ef4444; /* red-500 */
    }

    @keyframes spin {
        100% { transform: rotate(360deg); }
    }
</style>