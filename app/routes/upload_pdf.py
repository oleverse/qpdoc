from pathlib import Path
from typing import List

from fastapi import UploadFile, File, APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.database.models import User
from app.database.db import get_db, SessionLocal

from app.services.upload_pdf import extract_text_from_pdf, extract_text_from_docx, extract_text_from_odt, save_pdf_to_db

router = APIRouter(prefix='/upload', tags=['upload'])

file_handlers = {
    '.pdf': extract_text_from_pdf,
    '.docx': extract_text_from_docx,
    '.odt': extract_text_from_odt,
}


@router.post("/upload/")
async def upload(files: List[UploadFile], user_id: int, db: SessionLocal = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    uploaded_files_name = []
    uploaded_files_ids = []
    try:
        for uploaded_file in files:
            file_extension = Path(uploaded_file.filename).suffix
            if file_extension in file_handlers:
                text = file_handlers[file_extension](uploaded_file.file)
                file_id = save_pdf_to_db(db, uploaded_file, text, db_user)
                uploaded_files_ids.append(file_id)
                uploaded_files_name.append(uploaded_file.filename)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported file format: {uploaded_file.filename}")

        return JSONResponse(content={"message": "Files uploaded successfully", "files id": uploaded_files_ids,
                                     "files name": uploaded_files_name})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
