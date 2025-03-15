import chromadb

path_client = "./client"

def get_client():
    return chromadb.PersistentClient(path=path_client)