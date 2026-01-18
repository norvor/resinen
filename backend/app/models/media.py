from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services.storage import storage 
from app.models.user import User
from app.api import deps

router = APIRouter()

@router.post("/upload")
async def upload_media(
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Upload an image or video to the Local Vault (MinIO).
    Returns the public URL.
    """
    # 1. Validation: Only allow Images and Videos
    if not file.content_type.startswith(("image/", "video/")):
         raise HTTPException(status_code=400, detail="Invalid file type. Images or Video only.")

    # 2. Upload to MinIO
    try:
        file_url = await storage.upload_file(file)
        return {"url": file_url, "type": file.content_type}
    except Exception as e:
        # Log the error for debugging
        print(f"Upload Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not upload file.")