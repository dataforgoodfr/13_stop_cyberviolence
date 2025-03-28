import os
from langchain.document_loaders import PyPDFLoader


def load_pdfs(pdf_folder_path: str = "../../rag/raw_files"):
    
    documents = []

    for file in os.listdir(pdf_folder_path):
        if file.endswith('.pdf'):
            pdf_path = os.path.join(pdf_folder_path, file)
            loader = PyPDFLoader(pdf_path)
            documents.extend(loader.load())
            
    return documents