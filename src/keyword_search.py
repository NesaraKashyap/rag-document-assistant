from rank_bm25 import BM25Okapi
from .chunk_documents import chunk_all_documents
from .load_documents import load_documents


def build_bm25_index():
    """
    Loads and chunks documents, then builds a BM25 keyword search index
    over the chunk texts.
    """
    docs = load_documents()
    chunks = chunk_all_documents(docs)

    # BM25 needs the text broken into individual words (tokenized),
    # not full sentences. We do a very simple split-on-whitespace + lowercase.
    tokenized_texts = [chunk["text"].lower().split() for chunk in chunks]

    bm25 = BM25Okapi(tokenized_texts)

    return bm25, chunks


def keyword_search(query, bm25, chunks, top_k=3):
    """
    Takes a plain-English question and returns the top_k chunks
    that best match on keyword overlap, using BM25 scoring.
    """
    tokenized_query = query.lower().split()

    scores = bm25.get_scores(tokenized_query)

    # Pair each chunk with its score, then sort by score descending
    # (unlike distance, HIGHER BM25 score = better match)
    scored_chunks = list(zip(chunks, scores))
    scored_chunks.sort(key=lambda x: x[1], reverse=True)

    return scored_chunks[:top_k]


def print_results(query, results):
    print(f"\nQuery: {query}\n")
    for i, (chunk, score) in enumerate(results):
        print(f"--- Match {i+1} ---")
        print(f"Chunk: {chunk['chunk_id']}")
        print(f"Source: {chunk['source_file']} > {chunk['heading']}")
        print(f"BM25 score (higher = more similar): {score:.4f}")
        print(f"Text: {chunk['text'][:200]}...")
        print()


if __name__ == "__main__":
    bm25, chunks = build_bm25_index()

    while True:
        query = input("Ask a question (or type 'exit' to quit): ")
        if query.lower() == "exit":
            break

        results = keyword_search(query, bm25, chunks)
        print_results(query, results)