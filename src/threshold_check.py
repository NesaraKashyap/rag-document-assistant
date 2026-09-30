from run_eval import load_golden_dataset
from rerank import rerank


def check_score_distribution():
    """
    Runs every eval question through the reranker and prints the
    top-1 rerank score, grouped by whether the question is answerable
    or a known no-answer trick question. This helps us pick a sensible
    confidence threshold based on real data, not a guess.
    """
    dataset = load_golden_dataset()

    print("\n--- Scores for ANSWERABLE questions (should score higher) ---")
    for item in dataset:
        if item["expected_chunk"] is not None:
            top_results = rerank(item["question"], top_k=1)
            top_chunk, top_score = top_results[0]
            print(f"{top_score:.4f}  |  {item['question']}")

    print("\n--- Scores for NO-ANSWER questions (should score lower) ---")
    for item in dataset:
        if item["expected_chunk"] is None:
            top_results = rerank(item["question"], top_k=1)
            top_chunk, top_score = top_results[0]
            print(f"{top_score:.4f}  |  {item['question']}")


if __name__ == "__main__":
    check_score_distribution()