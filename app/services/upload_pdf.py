import PyPDF2

from app.schemas.essential import PDFFile
from app.database.models import PDFModel
from sqlalchemy.orm import Session
# import fitz
from docx import Document
from odf import text, teletype
from odf.opendocument import load
import io


def save_pdf_to_db(db, pdf_data):
    db_pdf = PDFModel(filename=pdf_data.filename, content=pdf_data.content)
    db.add(db_pdf)
    db.commit()
    db.refresh(db_pdf)
    return db_pdf


# Можна не використовувати fitz
# def extract_text_from_pdf(file):
#     pdf_document = fitz.open(file)
#     text = ""
#     for page_number in range(pdf_document.page_count):
#         page = pdf_document[page_number]
#         text += page.get_text()
#     return text
# Робота з PDF
def extract_text_from_pdf(file):
    file_content = file.read()
    pdf_stream = io.BytesIO(file_content)
    pdf_reader = PyPDF2.PdfReader(pdf_stream)
    text = ""
    for page_number in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page_number].extract_text()
    return text


# Робота з DOCX
def extract_text_from_docx(file):
    doc = Document(file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + " "
    return text.strip()


# Робота з ODT
def extract_text_from_odt(file):
    doc = load(file)
    text_content = []
    for text_node in doc.getElementsByType(text.P):
        text_content.append(teletype.extractText(text_node))
    return " ".join(text_content).strip()
