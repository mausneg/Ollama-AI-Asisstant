import pymupdf
import os
from pathlib import Path
import tempfile

def convert_document(uploaded_file):
    if uploaded_file is not None:
        bytearray = uploaded_file.read()
        pdf = pymupdf.open(stream=bytearray, filetype="pdf")

        context = ""
        for page in pdf:
            context = context + "\n\n" + page.get_text()

        pdf.close()
        return context