from app.schemas.essential import PDFFile
from app.database.models import PDFModel
from sqlalchemy.orm import Session
import fitz

def save_pdf_to_db(db, pdf_data):
    db_pdf = PDFModel(filename=pdf_data.filename, content=pdf_data.content)
    db.add(db_pdf)
    db.commit()
    db.refresh(db_pdf)
    return db_pdf

def extract_text_from_pdf(file):
    pdf_document = fitz.open(file)
    text = ""
    for page_number in range(pdf_document.page_count):
        page = pdf_document[page_number]
        text += page.get_text()
    return text