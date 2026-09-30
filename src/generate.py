import ollama
import time
import os
from .rerank import rerank_with_confidence
from .verify_citations import verify_answer, print_verification

MODEL_NAME = "llama3.2:3b"

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
ollama_client = ollama.Client(host=OLLAMA_HOST)


def build_prompt(query, chunks):
    """
    Builds the prompt we send to the LLM: the question, plus the
    retrieved chunks as numbered, citable context blocks.
    """
    context_blocks = []
    for i, chunk in enumerate(chunks):
        context_blocks.append(
            f"[{i+1}] Source: {chunk['source_file']} > {chunk['heading']}\n{chunk['text']}"
        )

    context_text = "\n\n".join(context_blocks)

    prompt = f"""You are a helpful assistant answering questions using ONLY the context provided below.

Rules:
- Only use information from the context blocks below. Do not use outside knowledge.
- Cite the source of every claim using the bracketed number, like [1] or [2].
- If the context does not fully answer the question, say so honestly instead of guessing.
- Keep your answer concise — 2-3 sentences maximum.

Context:
{context_text}

Question: {query}

Answer:"""

    return prompt


def generate_answer(query):
    """
    Runs the full pipeline: retrieve chunks with confidence check,
    then generate a grounded answer citing sources.
    """
    retrieval_start = time.time()
    results, is_confident = rerank_with_confidence(query)
    retrieval_time = time.time() - retrieval_start

    if not is_confident:
        return "I couldn't find a confident answer to this in the documents.", [], retrieval_time, 0

    chunks = [chunk for chunk, score in results]
    prompt = build_prompt(query, chunks)

    generation_start = time.time()
    response = ollama_client.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        options={"num_predict": 150}
    )
    generation_time = time.time() - generation_start

    answer = response["message"]["content"]

    return answer, chunks, retrieval_time, generation_time


def print_sources(chunks):
    print("\nSources used:")
    for i, chunk in enumerate(chunks):
        print(f"  [{i+1}] {chunk['source_file']} > {chunk['heading']}")


if __name__ == "__main__":
    while True:
        query = input("\nAsk a question (or type 'exit' to quit): ")
        if query.lower() == "exit":
            break

        answer, chunks, retrieval_time, generation_time = generate_answer(query)

        print(f"\nAnswer:\n{answer}")

        if chunks:
            print_sources(chunks)
            verification_results = verify_answer(answer, chunks)
            print_verification(verification_results)

        print(f"\n[TIMING] Retrieval: {retrieval_time:.2f}s | Generation: {generation_time:.2f}s | Total: {retrieval_time + generation_time:.2f}s")