import pymupdf
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings

db_name = "vector_db"
db_abs_path = os.path.abspath(db_name)
embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url="http://localhost:11434")

def convert_document(uploaded_file):
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        pdf = pymupdf.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in pdf:
                text += page.get_text()
        pdf.close()
        doc = Document(page_content=text, metadata={"source": uploaded_file.name})
        text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, 
                chunk_overlap=100
        )
        chunks = text_splitter.split_documents([doc])
        return chunks
    return None
    
def vector_store_document(chunks):
    if chunks:
        if os.path.exists(db_name):
            vector_store = FAISS.load_local(
                db_name, 
                embeddings, 
                allow_dangerous_deserialization=True
            )
            vector_store.add_documents(chunks)
        else:
            vector_store = FAISS.from_documents(chunks, embeddings)
        vector_store.save_local(db_name)
        return True
    return False
    
def vectorize_document(uploaded_file):
    chunks = convert_document(uploaded_file)
    return vector_store_document(chunks)