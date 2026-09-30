import chromadb
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection("nimbusdesk_docs")


def search(query, top_k=3):
    """
    Takes a plain-English question, embeds it, and finds the top_k
    most similar chunks stored in ChromaDB.
    """
    # Turn the question into an embedding, the same way we embedded the chunks
    query_embedding = model.encode([query])[0]

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=top_k
    )

    return results


def print_results(query, results):
    print(f"\nQuery: {query}\n")
    ids = results["ids"][0]
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for i in range(len(ids)):
        print(f"--- Match {i+1} ---")
        print(f"Chunk: {ids[i]}")
        print(f"Source: {metadatas[i]['source_file']} > {metadatas[i]['heading']}")
        print(f"Distance (lower = more similar): {distances[i]:.4f}")
        print(f"Text: {documents[i][:200]}...")
        print()


if __name__ == "__main__":
    while True:
        query = input("Ask a question (or type 'exit' to quit): ")
        if query.lower() == "exit":
            break

        results = search(query)
        print_results(query, results)