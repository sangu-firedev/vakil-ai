import streamlit as st
from utils.file_handler import upload_file_to_gcs
from models.gemini_model import response
import yaml
from langchain.document_loaders import PyPDFLoader
import os
from fpdf import FPDF
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from textwrap import wrap

with open("config.yaml", "r") as config:
    config = yaml.safe_load(config)

st.set_page_config(layout="wide")

st.title("Vakil-AI your law assistant")

uploaded_files = st.file_uploader(
    "Upload your a PDF files", accept_multiple_files=False, key="file", type="pdf"
)

#if uploaded_files is not None:
#    # Save the uploaded file temporarily
#    with open("temp_document.pdf", "wb") as f:
#        f.write(uploaded_files.read())
#
#    # Use PyPDFLoader to parse the uploaded PDF
#    loader = PyPDFLoader("temp_document.pdf")
#    if "documents" not in st.session_state:
#        st.session_state.documents = loader.load()

messages = st.container(height=450)

if 'model_response' not in st.session_state:
    st.session_state.model_response = " "

#def call_model():
#
#    blob_url = ""
#    if uploaded_files:
#        source_file = uploaded_files.read()
#        destination_blob = f"{config['storage']['bucket_name']}/uploaded-files/{uploaded_files.name}"
#        blob_url = upload_file_to_gcs(source_file=source_file, 
#                                      destination_blob=destination_blob
#                                      )
#    
#        st.session_state.model_response =  response(st.session_state.prompt, blob_url)
#        return None 
#
#    st.session_state.model_response =  response(st.session_state.prompt)

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

def call_model():

    blob_url = ""
    if uploaded_files: # and (documents := st.session_state.documents):

        source_file = process_pdf(uploaded_files)

        file_name = uploaded_files.name
        #file_name = file_name.replace(".pdf", "") 
        destination_blob = f"/uploaded-files/{file_name}"

        #document_content = " ".join(doc.page_content for doc in documents)


        blob_url = upload_file_to_gcs(source_file=source_file, 
                                        destination_blob=destination_blob
                                        )
        print(f"############{blob_url}")
        print(f"############{uploaded_files.name}")

        st.session_state.model_response =  response(prompt=st.session_state.prompt, blob_file=blob_url)
        return None 

    st.session_state.model_response =  response(st.session_state.prompt)
text_input = st.chat_input(placeholder="How can I help you?", key="prompt", on_submit=call_model)

if text_input:
    messages.chat_message(name="user").write(f"{text_input}")

if st.session_state.model_response:
    messages.chat_message(name="vakil").write(f"{st.session_state.model_response}")



