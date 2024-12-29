import io
from langchain.document_loaders import PyPDFLoader
import os
from fpdf import FPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from textwrap import wrap

def process_pdf(uploaded_files):
    """
    processes the uploaded pdf and outputs in-memory pdf
    """

    with open("temp_document.pdf", "wb") as f:
        f.write(uploaded_files.read())

    # Use PyPDFLoader to parse the uploaded PDF
    loader = PyPDFLoader("temp_document.pdf")
    document = loader.load()
    document_content = " ".join(doc.page_content for doc in document)

    if os.path.exists("temp_document.pdf"):
        os.remove("temp_document.pdf")

    # convert string to processed in-memory pdf (fpdf)
    #pdf = FPDF()
    #pdf.set_auto_page_break(auto=True, margin=15)
    #pdf.add_page()
    #pdf.set_font("Arial", size=12)
    #for line in document_content.split("\n"):
        #pdf.multi_cell(0, 10, line)
    #buffer = io.BytesIO()
    #pdf.output(buffer)
    #buffer.seek(0)

    # convert string to processed in-memory pdf (canvas)
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    text_object = c.beginText(50, height - 50)

    text_object.setFont("Helvetica", 12)
    line_height = 14

    for line in document_content.split("\n"):
        for sub_line in wrap(line, 80):
            if text_object.getY() < 50:
                c.drawText(text_object)
                c.showPage()
                text_object = c.beginText(50, height - 50)
                text_object.setFont("Helvetica", 12)
            text_object.textLine(sub_line)

    c.drawText(text_object)
    c.save()
    buffer.seek(0)

    return buffer