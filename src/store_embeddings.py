import chromadb
from sentence_transformers import SentenceTransformer
from .chunk_documents import chunk_all_documents
from .load_documents import load_documents

MODEL_NAME = "all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)

# This creates (or opens, if it already exists) a folder called "chroma_db"
# where all embeddings get saved permanently to disk.
client = chromadb.PersistentClient(path="chroma_db")


def build_vector_store():
    """
    Loads documents, chunks them, embeds them, and stores everything in ChromaDB.
    """
    docs = load_documents()
    chunks = chunk_all_documents(docs)

    # Delete the old collection if it exists, so we always start fresh
    # when re-running this script (avoids duplicate entries)
    try:
        client.delete_collection("nimbusdesk_docs")
    except Exception:
        pass

    collection = client.create_collection("nimbusdesk_docs")

    texts = [chunk["text"] for chunk in chunks]
    ids = [chunk["chunk_id"] for chunk in chunks]

    # Metadata is extra info we store alongside each embedding —
    # useful for showing citations later (which file/heading it came from)
    metadatas = [
        {"source_file": chunk["source_file"], "heading": chunk["heading"]}
        for chunk in chunks
    ]

    embeddings = model.encode(texts, show_progress_bar=True)

    collection.add(
        ids=ids,
        embeddings=embeddings.tolist(),
        documents=texts,
        metadatas=metadatas
    )

    print(f"\nStored {len(chunks)} chunks in ChromaDB collection 'nimbusdesk_docs'.")
    return collection


if __name__ == "__main__":
    build_vector_store()