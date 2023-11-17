import docx
from PyPDF2 import PdfReader
from fastapi import UploadFile

from odf import text, teletype
from odf.opendocument import load

from app.database.db import SessionLocal
from app.database.models import User, PDFModel


def extract_text_from_pdf(file_stream):
    reader = PdfReader(file_stream)
    text = "".join([page.extract_text() for page in reader.pages])
    return text


def extract_text_from_docx(file_stream):
    doc = docx.Document(file_stream)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text


# Робота з ODT
def extract_text_from_odt(file_stream):
    document = load(file_stream)
    all_texts = document.getElementsByType(text.P)
    return " ".join(teletype.extractText(t) for t in all_texts)


def save_pdf_to_db(db: SessionLocal, uploaded_file: UploadFile, text: str, db_user: User) -> int:
    new_pdf = PDFModel(filename=uploaded_file.filename, content=text, user=db_user)
    db.add(new_pdf)
    db.commit()
    db.refresh(new_pdf)
    return new_pdf.id
