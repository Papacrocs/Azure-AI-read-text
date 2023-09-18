import streamlit as st

import os
import time


from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision import ComputerVisionClient

#load_dotenv()


st.set_page_config(
    page_title="Papacrocs App",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)




# Display the welcome statement
st.write("""
# Welcome to the OCR Text Extraction App

Built by Stephen Samuel (PapaCrocs), a Beta Microsoft Learn Student Ambassador (MLSA), with assistance from Josiah Adesola, a BETA MLSA.

This app utilizes Azure AI to extract text from images and documents.

Get started by uploading an image or PDF in the sidebar.
""")




def GetTextRead(image_data):
    global cv_client
    cog_key = st.secrets['COG_SERVICE_KEY']
    cog_endpoint = st.secrets['COG_SERVICE_ENDPOINT']
    credential = CognitiveServicesCredentials(cog_key)
    cv_client = ComputerVisionClient(cog_endpoint, credential)


    read_op = cv_client.read_in_stream(image_data, raw=True)
    operation_location = read_op.headers["Operation-Location"]
    operation_id = operation_location.split("/")[-1]

    while True:
        read_results = cv_client.get_read_result(operation_id)
        if read_results.status not in [OperationStatusCodes.running, OperationStatusCodes.not_started]:
            break
        time.sleep(1)

    extracted_text = ""

    if read_results.status == OperationStatusCodes.succeeded:
        for page in read_results.analyze_result.read_results:
            for line in page.lines:
                extracted_text += line.text + ".  \n"

    return extracted_text


def main():
    
    uploaded_file = st.file_uploader(
        "Choose an image or PDF...", type=["jpg", "png", "pdf"])

    if uploaded_file is not None and uploaded_file.type == "image/jpeg":
        st.image(uploaded_file, caption='Uploaded Image.',
                use_column_width=True)
        st.write("")
        st.write("Classifying...")

        extracted_text = ""

        extracted_text = GetTextRead(uploaded_file)
        

        st.subheader("Extracted Text:")
        st.write(extracted_text)

    elif uploaded_file is not None and uploaded_file.type == "application/pdf":
        # images = convert_pdf_to_images(uploaded_file)
        # for image in images:

        st.write("")
        st.warning("Classifying...")

        extracted_text = ""

        extracted_text += GetTextRead(uploaded_file)

        st.subheader("Extracted Text:")
        st.success(extracted_text)

if __name__ == "__main__":
    main()