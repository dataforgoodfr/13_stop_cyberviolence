import os
from langchain_community.document_loaders import PyPDFLoader
import google.generativeai as genai
from pathlib import Path

pyfile_dir = Path(__file__).parent
default_dir = pyfile_dir / "../../rag/raw_files"

def load_pdfs(pdf_folder_path: str = default_dir):
    """
    Loads PDF documents from a specified folder.
    
    Args:
        pdf_folder_path (str, optional): The path to the folder containing PDF files.
            Defaults to a directory relative to the current file.

    Returns:
        list: A list of Document objects, each representing a page from the loaded PDF files.
    """
    documents = []

    for file in os.listdir(pdf_folder_path):  # Iterate through files in the specified directory
        if file.endswith('.pdf'):  # Check if the file is a PDF
            pdf_path = os.path.join(pdf_folder_path, file)  # Create the full path to the PDF file
            loader = PyPDFLoader(pdf_path)  # Initialize the PDF loader
            documents.extend(loader.load())  # Load the PDF and add its pages to the list
    return documents

def load_htmls(html_folder_path: str = default_dir):
    """
    Loads HTML documents from a specified folder (currently returns an empty list).

    Args:
        html_folder_path (str, optional): The path to the folder containing HTML files.
            Defaults to a directory relative to the current file.
    Returns:
        list: An empty list, as HTML loading is not yet implemented.
    """
    return []  # Placeholder: HTML loading is not currently implemented.

def load_docxs(docxs_folderpath: Path = default_dir):
    """
    Loads DOCX documents from a specified folder (currently returns an empty list).

    Args:
        docxs_folderpath (Path, optional): The path to the folder containing DOCX files.
            Defaults to a directory relative to the current file.
    Returns:
        list: An empty list, as DOCX loading is not yet implemented.
    """
    return []  # Placeholder: DOCX loading is not currently implemented.

def ingest_docs(
    doc_dir: str = default_dir, output_file: str = './ateliers_jeunes_complete.md',
    load_funcs: list = [load_pdfs, load_htmls, load_docxs],
    count_tokens: bool = False, model_str: str = 'models/gemini-2.0-flash'
    ):
    """
    Ingests documents from various file types in a directory, concatenates their content,
    and optionally counts the number of tokens.
    
    Args:
        doc_dir (str, optional): The directory containing the documents to ingest.
            Defaults to a directory relative to the current file.
        output_file (str, optional): The path to the output file where the concatenated
            document content will be written. Defaults to './ateliers_jeunes_complete.md'.
        load_funcs (list, optional): A list of functions to load documents from different
            file types. Defaults to [load_pdfs, load_htmls, load_docxs].
        count_tokens (bool, optional): Whether to count the number of tokens in the
            concatenated document using a specified language model. Defaults to False.
        model_str (str, optional): The name or path of the language model to use for
            token counting. Defaults to 'models/gemini-2.0-flash'.
    """

    docs = []
    
    for f in load_funcs:  # Iterate through the list of loading functions
        docs.extend(f())  # Load documents using each function and add them to the list

    with open(output_file, 'w') as f:  # Open the output file for writing
        f.write(
            "\n".join([doc.page_content for doc in docs])  # Write the page content of each document to the file
        )
        
    if count_tokens:  # Conditionally count tokens if specified

        count_tokens(output_file, model_str)
        
def count_tokens(
    file_path: str,
    model_str: str = 'models/gemini-2.0-flash',
                 ) -> int:
    """
    Counts the number of tokens in a given file using a specified language model.

    Args:
        file_path (str): The path to the file to count tokens from.
        model_str (str, optional): The name or path of the language model to use for
            token counting. Defaults to 'models/gemini-2.0-flash'.

    Returns:
        int: The number of tokens in the file.
    """
    model = genai.GenerativeModel(model_str)  # Initialize the language model
        
    with open(file_path, 'r') as f:  # Open the file for reading
        chat = model.start_chat(
            history = [{"role":"model", "parts":f.read()}]  # Initialize a chat history with the file content
        )
    
    no_tokens = model.count_tokens(chat.history)  # Count the number of tokens in the chat history

    print(model_str)
    print(no_tokens)
        
if __name__ == "__main__":
    import sys
    import fire
    
    from types import SimpleNamespace
    
    # Use SimpleNamespace to wrap the functions to be called from the command line
    funcs = SimpleNamespace(
        ingest_docs = ingest_docs,
        count_tokens = count_tokens
    )
    
    fire.Fire(funcs) # Expose the functions to comamnd line
