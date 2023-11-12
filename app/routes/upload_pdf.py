from fastapi import FastAPI, UploadFile, File, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import List
from app.schemas.essential import PDFFile
from app.database.models import PDFModel
from app.database.db import get_db
from app.services.upload_pdf import save_pdf_to_db
import io
import PyPDF2

router = APIRouter(prefix='/upload', tags=['upload'])


@router.post("/uploadpdf/")
async def upload_pdf(files: List[UploadFile] = File(...)):
    try:
        db = next(get_db())

        for file in files:
            if not file.filename.endswith('.pdf'):
                raise HTTPException(status_code=400, detail=f"Invalid file format for {file.filename}. Please provide a PDF file.")

            file_content = await file.read()
            pdf_stream = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_stream)
            text = ""
            for page_number in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page_number].extract_text()

            pdf_data = PDFFile(filename=file.filename, content=text)
            pdf_model = save_pdf_to_db(db, pdf_data)

        return JSONResponse(content={"message": "PDF files uploaded successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
