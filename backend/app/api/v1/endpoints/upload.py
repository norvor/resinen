from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
import uuid

router = APIRouter()

# Define where files go. 
# Make sure to run: mkdir -p static/uploads inside your backend root
UPLOAD_DIR = "static/uploads"

@router.post("/", response_model=dict)
async def upload_file(file: UploadFile = File(...)):
    # 1. Basic Validation
    allowed_types = ["image/jpeg", "image/png", "image/gif", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(400, detail="Invalid file type. Only Images and PDFs allowed.")
    
    # 2. Generate Safe Filename
    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # 3. Save
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 4. Return URL
    # This assumes your API is at api.resinen.com. 
    return {"url": f"/static/uploads/{filename}"}