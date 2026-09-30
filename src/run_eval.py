import json
from .rerank import rerank


def load_golden_dataset(path="eval/golden_dataset.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_evaluation(top_k=3):
    dataset = load_golden_dataset()

    results = []
    correct_count = 0
    answerable_count = 0

    for item in dataset:
        question = item["question"]
        expected = item["expected_chunk"]

        top_results = rerank(question, top_k=top_k)
        retrieved_ids = [chunk["chunk_id"] for chunk, score in top_results]

        if expected is None:
            # This is a "no answer exists" question — we're not scoring
            # pass/fail on it yet, just recording what the system retrieved
            # so we can eyeball whether it's confidently wrong.
            results.append({
                "question": question,
                "difficulty": item["difficulty"],
                "expected": None,
                "retrieved": retrieved_ids,
                "correct": None
            })
            continue

        answerable_count += 1
        is_correct = expected in retrieved_ids
        if is_correct:
            correct_count += 1

        results.append({
            "question": question,
            "difficulty": item["difficulty"],
            "expected": expected,
            "retrieved": retrieved_ids,
            "correct": is_correct
        })

    accuracy = correct_count / answerable_count if answerable_count > 0 else 0

    return results, accuracy


def print_report(results, accuracy):
    print("\n" + "=" * 60)
    print("EVALUATION REPORT")
    print("=" * 60 + "\n")

    for r in results:
        if r["expected"] is None:
            status = "N/A (no correct answer exists)"
        else:
            status = "PASS" if r["correct"] else "FAIL"

        print(f"[{status}] ({r['difficulty']}) {r['question']}")
        print(f"    Expected: {r['expected']}")
        print(f"    Retrieved: {r['retrieved']}")
        print()

    print("=" * 60)
    print(f"OVERALL RETRIEVAL ACCURACY: {accuracy:.1%}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    results, accuracy = run_evaluation()
    print_report(results, accuracy)