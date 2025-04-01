import os

import chromadb
from chroma_client import get_client
from chromadb.utils import embedding_functions

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter

chroma_client = get_client()

pdf_folder_path = "./raw_files"
documents = []

for file in os.listdir(pdf_folder_path):
    if file.endswith('.pdf'):
        pdf_path = os.path.join(pdf_folder_path, file)
        loader = PyPDFLoader(pdf_path)
        documents.extend(loader.load())
        
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=10)
chunked_documents = text_splitter.split_documents(documents)

collection = chroma_client.create_collection("sc_collection")

embedding_function = embedding_functions.DefaultEmbeddingFunction()

i = 0

for doc in chunked_documents:
    
    embeddings_doc = embedding_function(doc.page_content)
    collection.add(
        documents = doc.page_content,
        embeddings = [embeddings_doc[0].tolist()],
        metadatas = doc.metadata,
        ids=[str(i)]
    )
    print(f'doc {i}/{len(chunked_documents)} added')
    i += 1
    
print(f'all docs ({collection.count()}) loaded !')

print("test query : est ce que c'est de la diffamation ?")

results = collection.query(
    query_texts=["est ce que c'est de la diffamation ?"],
    n_results=2
)

print(results)