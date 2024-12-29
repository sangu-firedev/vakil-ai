import streamlit as st
from models.gemini_model import response
import yaml

from utils.pdf_parser import process_pdf
from utils.file_handler import upload_file_to_gcs

with open("config.yaml", "r") as config:
    config = yaml.safe_load(config)

st.set_page_config(layout="wide")

st.title("Vakil-AI your law assistant")

uploaded_files = st.file_uploader(
    "Upload your a PDF files", accept_multiple_files=False, key="file", type="pdf"
)

messages = st.container(height=450)

if 'model_response' not in st.session_state:
    st.session_state.model_response = " "

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

        st.session_state.model_response =  response(prompt=st.session_state.prompt, blob_file=blob_url)
        return None 

    st.session_state.model_response =  response(st.session_state.prompt)

text_input = st.chat_input(placeholder="How can I help you?", key="prompt", on_submit=call_model)

if text_input:
    messages.chat_message(name="user").write(f"{text_input}")

if st.session_state.model_response:
    messages.chat_message(name="vakil").write(f"{st.session_state.model_response}")



