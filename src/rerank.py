from sentence_transformers import CrossEncoder
from .hybrid_search import hybrid_search
from .keyword_search import build_bm25_index

# This model is specifically trained to judge "how relevant is this text
# to this question", given both together — different job than embeddings.
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

CONFIDENCE_THRESHOLD = -8.0


def rerank(query, shortlist_size=10, top_k=3):
    """
    Takes the fused hybrid search results, re-scores the top `shortlist_size`
    candidates using a cross-encoder, and returns the true top_k.
    """
    bm25, all_chunks = build_bm25_index()
    fused_results = hybrid_search(query, bm25, all_chunks, top_k=shortlist_size)

    chunk_lookup = {chunk["chunk_id"]: chunk for chunk in all_chunks}

    # Build (question, chunk_text) pairs — the reranker scores each pair together
    pairs = []
    candidate_chunks = []
    for chunk_id, fused_score in fused_results:
        chunk = chunk_lookup[chunk_id]
        pairs.append([query, chunk["text"]])
        candidate_chunks.append(chunk)

    # This is the actual reranking step: score every (question, chunk) pair
    rerank_scores = reranker.predict(pairs)

    # Pair each chunk with its new score, sort by score descending
    scored = list(zip(candidate_chunks, rerank_scores))
    scored.sort(key=lambda x: x[1], reverse=True)

    return scored[:top_k]


def rerank_with_confidence(query, shortlist_size=10, top_k=3):
    """
    Same as rerank(), but adds a confidence check based on the top score.
    Returns (results, is_confident) so the caller knows whether to trust
    the top result or tell the user honestly that nothing good was found.
    """
    results = rerank(query, shortlist_size=shortlist_size, top_k=top_k)

    if len(results) == 0:
        return results, False

    top_score = results[0][1]
    is_confident = top_score >= CONFIDENCE_THRESHOLD

    return results, is_confident


def print_results(query, results):
    print(f"\nQuery: {query}\n")
    for i, (chunk, score) in enumerate(results):
        print(f"--- Match {i+1} ---")
        print(f"Chunk: {chunk['chunk_id']}")
        print(f"Source: {chunk['source_file']} > {chunk['heading']}")
        print(f"Rerank score (higher = more relevant): {score:.4f}")
        print(f"Text: {chunk['text'][:200]}...")
        print()


if __name__ == "__main__":
    while True:
        query = input("Ask a question (or type 'exit' to quit): ")
        if query.lower() == "exit":
            break

        results, is_confident = rerank_with_confidence(query)

        if not is_confident:
            print(f"\nQuery: {query}")
            print("I couldn't find a confident answer to this in the documents.\n")
        else:
            print_results(query, results)