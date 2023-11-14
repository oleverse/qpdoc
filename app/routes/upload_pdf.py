from fastapi import UploadFile, File, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import List
from app.schemas.essential import PDFFile
from app.database.db import get_db
from app.services.upload_pdf import save_pdf_to_db, extract_text_from_docx, extract_text_from_odt, extract_text_from_pdf

router = APIRouter(prefix='/upload', tags=['upload'])


@router.post("/upload/")
async def upload(files: List[UploadFile] = File(...)):
    try:
        db = next(get_db())

        for file in files:
            if file.filename.endswith('.pdf'):
                text = extract_text_from_pdf(file.file)

                pdf_data = PDFFile(filename=file.filename, content=text)
                pdf_model = save_pdf_to_db(db, pdf_data)
            elif file.filename.endswith('.docx'):
                text = extract_text_from_docx(file.file)

                pdf_data = PDFFile(filename=file.filename, content=text)
                pdf_model = save_pdf_to_db(db, pdf_data)
            elif file.filename.endswith('.odt'):
                text = extract_text_from_odt(file.file)

                pdf_data = PDFFile(filename=file.filename, content=text)
                pdf_model = save_pdf_to_db(db, pdf_data)
            else:
                raise HTTPException(status_code=400,
                                    detail=f"Unsupported file format for {file.filename}. Please provide a PDF, DOCX, "
                                           f"or ODT file.")

        return JSONResponse(content={"message": "Files uploaded successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
