import yaml
import os

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)


PROJECT_ID = config["project_ids"]["PROJECT_ID"]
LOCATION = config["project_ids"]["LOCATION"]
SERVICE_AC = config["service_account"]["path"]

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_AC

import vertexai

vertexai.init(project=PROJECT_ID, location=LOCATION)

import json

from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
    HarmBlockThreshold,
    HarmCategory,
    Part,
)

# Load the Gemini 1.5 Flash model
model = GenerativeModel(
    "gemini-1.5-flash",
    safety_settings={
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH 
        },
)

generation_config = GenerationConfig(
    temperature=0.0, response_mime_type="application/json"
)

PDF_MIME_TYPE = "application/pdf"


def process_document(
        prompt: str,
        file_uri: str = None,
        mime_type: str = PDF_MIME_TYPE,
        generation_config: GenerationConfig | None = None,
        print_prompt: bool = False,
        print_raw_response: bool = False,
) ->str:
    # Load file from gcs
    file_part = Part.from_uri(
        uri=file_uri,
        mime_type=mime_type,
    )

    #system_prompt = f"""You are a legal document analysis assistant. Your primary role is to analyze legal documents from GCS and answer user queries about them.

    #For each interaction, you will receive:
    #1. USER QUERY: {prompt} 
    #2. DOCUMENT REFERENCE: Ask them to upload any file is necessary
    #3. USER EXPERTISE LEVEL: Professional or Layperson

    #Process Steps:
    #1. Read and analyze the provided document from GCS path
    #2. Focus on specific sections relevant to user's query
    #3. Extract and reference actual text from the document in your responses
    #4. When quoting the document, always include page numbers and section references
    #5. If document sections are unclear, request clarification about specific pages or sections

    #Response Framework:
    #1. For document contents:
    #   - Quote relevant text with page numbers
    #   - Provide section references
    #   - Include contextual information

    #2. Format responses based on expertise level:
    #   Professional:
    #   - Use legal terminology
    #   - Cite specific sections with page numbers
    #   - Reference applicable statutes
    #   - Provide technical analysis

    #   Layperson:
    #   - Use plain language
    #   - Explain legal terms
    #   - Provide practical examples
    #   - Break down complex concepts
    #   - Include step-by-step guidance

    #3. Always include:
    #   - Direct quotes from document with page numbers
    #   - Clear explanations
    #   - Practical implications
    #   - Next steps
    #   - References to specific document sections"""

    system_prompt = f""" {prompt} """

    # Load contents
    contents = []
    if file_uri:
        contents = [file_part, system_prompt]
    else: 
        contents = system_prompt
    
    print(f"###########################{contents}")

    # Send to Gemini
    response = model.generate_content(contents)

    return response.text

def response(prompt, blob_file=None):

    response_text = process_document(
        prompt,
        file_uri=blob_file,
    )

    return response_text