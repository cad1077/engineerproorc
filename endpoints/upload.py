# 📁 endpoints/upload.py
from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os

UPLOAD_DIR = "data/uploads"
router = APIRouter()

@router.post("/upload-zip")
async def upload_zip(file: UploadFile = File(...)):
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Somente arquivos .zip são permitidos.")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": file.filename, "status": "Upload realizado com sucesso."}
