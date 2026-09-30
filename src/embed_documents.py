from sentence_transformers import SentenceTransformer
from chunk_documents import chunk_all_documents
from load_documents import load_documents

# Load the embedding model. First run will download it (~90MB), one time only.
MODEL_NAME = "all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)


def embed_chunks(chunks):
    """
    Takes a list of chunk dictionaries and adds an 'embedding' field to each one,
    containing the numeric vector representation of that chunk's text.
    """
    texts = [chunk["text"] for chunk in chunks]

    # This is the actual AI step: convert all chunk texts into embeddings at once
    embeddings = model.encode(texts, show_progress_bar=True)

    for chunk, embedding in zip(chunks, embeddings):
        chunk["embedding"] = embedding

    return chunks


if __name__ == "__main__":
    docs = load_documents()
    chunks = chunk_all_documents(docs)
    chunks = embed_chunks(chunks)

    print(f"\nEmbedded {len(chunks)} chunks.\n")

    # Just show the first chunk's details so we can eyeball that it worked
    first = chunks[0]
    print(f"Example chunk: {first['chunk_id']}")
    print(f"Embedding length: {len(first['embedding'])}")
    print(f"First 5 numbers of the embedding: {first['embedding'][:5]}")