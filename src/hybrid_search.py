from .search import model, collection
from .keyword_search import build_bm25_index, keyword_search


RRF_K = 60  # standard constant used in Reciprocal Rank Fusion


def get_embedding_ranking(query, top_k=20):
    """
    Returns a ranked list of chunk_ids from embedding search,
    best match first.
    """
    query_embedding = model.encode([query])[0]
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=top_k
    )
    return results["ids"][0]  # already ordered best-to-worst


def get_bm25_ranking(query, bm25, chunks, top_k=20):
    """
    Returns a ranked list of chunk_ids from BM25 search,
    best match first.
    """
    results = keyword_search(query, bm25, chunks, top_k=top_k)
    return [chunk["chunk_id"] for chunk, score in results]


def reciprocal_rank_fusion(embedding_ranking, bm25_ranking):
    """
    Combines two ranked lists of chunk_ids into one fused ranking,
    using Reciprocal Rank Fusion.
    """
    fused_scores = {}

    for rank, chunk_id in enumerate(embedding_ranking):
        fused_scores[chunk_id] = fused_scores.get(chunk_id, 0) + 1 / (RRF_K + rank + 1)

    for rank, chunk_id in enumerate(bm25_ranking):
        fused_scores[chunk_id] = fused_scores.get(chunk_id, 0) + 1 / (RRF_K + rank + 1)

    # Sort chunk_ids by their fused score, highest first
    fused_ranking = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)

    return fused_ranking


def hybrid_search(query, bm25, chunks, top_k=3):
    """
    Runs both embedding and BM25 search, fuses the results,
    and returns the top_k chunk_ids with their fused scores.
    """
    embedding_ranking = get_embedding_ranking(query)
    bm25_ranking = get_bm25_ranking(query, bm25, chunks)

    fused = reciprocal_rank_fusion(embedding_ranking, bm25_ranking)

    return fused[:top_k]


def print_results(query, fused_results, chunks):
    print(f"\nQuery: {query}\n")

    # Build a quick lookup so we can print full chunk info, not just the id
    chunk_lookup = {chunk["chunk_id"]: chunk for chunk in chunks}

    for i, (chunk_id, score) in enumerate(fused_results):
        chunk = chunk_lookup[chunk_id]
        print(f"--- Match {i+1} ---")
        print(f"Chunk: {chunk_id}")
        print(f"Source: {chunk['source_file']} > {chunk['heading']}")
        print(f"Fused RRF score (higher = more similar): {score:.4f}")
        print(f"Text: {chunk['text'][:200]}...")
        print()


def debug_rankings(query, bm25, chunks):
    """
    Temporary debug helper: shows exactly where a specific chunk
    landed in each individual ranking, before fusion.
    """
    embedding_ranking = get_embedding_ranking(query)
    bm25_ranking = get_bm25_ranking(query, bm25, chunks)

    target = "refund_policy.md::chunk_2"

    emb_rank = embedding_ranking.index(target) + 1 if target in embedding_ranking else "not in top 20"
    bm25_rank = bm25_ranking.index(target) + 1 if target in bm25_ranking else "not in top 20"

    print(f"\n[DEBUG] '{target}' rank in embedding search: {emb_rank}")
    print(f"[DEBUG] '{target}' rank in BM25 search: {bm25_rank}\n")


if __name__ == "__main__":
    bm25, chunks = build_bm25_index()

    while True:
        query = input("Ask a question (or type 'exit' to quit): ")
        if query.lower() == "exit":
            break

        debug_rankings(query, bm25, chunks)
        results = hybrid_search(query, bm25, chunks)
        print_results(query, results, chunks)