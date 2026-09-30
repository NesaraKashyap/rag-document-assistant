\# NimbusDesk RAG Assistant



A production-style Retrieval-Augmented Generation (RAG) system that answers questions over a company's internal documentation using hybrid search, reranking, grounded generation, and automated citation verification — built entirely with free, local tooling.



\*\*Live demo stack:\*\* React frontend + FastAPI backend + local LLM (Ollama), fully containerized with Docker Compose.



\## Key results



\- \*\*93.3% retrieval accuracy\*\* across a hand-built 17-question evaluation set (easy/medium/hard/no-answer difficulty tiers)

\- \*\*Hybrid search (dense + sparse + reranking) recovered correct results that plain semantic search or plain keyword search each missed independently\*\* — see "What I learned" below

\- \*\*Confidence threshold, set empirically from real score distributions\*\*, correctly triggers an honest "I don't know" instead of hallucinating on out-of-scope questions

\- \*\*Compared two citation verification strategies\*\* (LLM-based judge vs. word-overlap scoring) and found the simpler, non-LLM approach more reliable in practice



\## Architecture



```

User Question

&#x20;    │

&#x20;    ▼

┌─────────────────────────────────────┐

│  Hybrid Retrieval                    │

│  ├─ Dense search (sentence-transformers embeddings, ChromaDB)

│  └─ Sparse search (BM25 keyword matching)

│         │

│         ▼

│  Reciprocal Rank Fusion (merges both rankings)

└─────────────────────────────────────┘

&#x20;    │

&#x20;    ▼

┌─────────────────────────────────────┐

│  Cross-Encoder Reranking             │

│  (second-pass relevance scoring on shortlist)

└─────────────────────────────────────┘

&#x20;    │

&#x20;    ▼

┌─────────────────────────────────────┐

│  Confidence Threshold                │

│  (empirically set at -8.0 based on score distribution)

└─────────────────────────────────────┘

&#x20;    │

&#x20;    ├─ Below threshold → "I couldn't find a confident answer"

&#x20;    │

&#x20;    ▼ (above threshold)

┌─────────────────────────────────────┐

│  Grounded Generation (Ollama, local LLM)

└─────────────────────────────────────┘

&#x20;    │

&#x20;    ▼

┌─────────────────────────────────────┐

│  Citation Verification               │

│  (word-overlap scoring per cited claim)

└─────────────────────────────────────┘

&#x20;    │

&#x20;    ▼

Answer + Sources + Verification → React UI

```



\## Tech stack



| Component | Tool |

|---|---|

| Embeddings | `sentence-transformers` (all-MiniLM-L6-v2), local, free |

| Vector store | ChromaDB |

| Keyword search | BM25 (`rank\_bm25`) |

| Fusion | Reciprocal Rank Fusion (custom implementation) |

| Reranking | Cross-encoder (`ms-marco-MiniLM-L-6-v2`) |

| LLM generation | Ollama, local (`llama3.2:3b`) |

| Backend | FastAPI |

| Frontend | React (Vite) |

| Containerization | Docker + Docker Compose |



\## What I learned (real engineering tradeoffs)



\*\*Hybrid search beats either method alone, but isn't foolproof.\*\* On adversarial, heavily-paraphrased queries, BM25 alone sometimes ranked the correct chunk last, and pure hybrid fusion could still be outranked by a chunk that happened to share common vocabulary. The reranker recovered most, but not all, of these cases — this is documented as a known limitation, tested against a specific eval question rather than hidden.



\*\*LLM-based citation verification was unreliable at this scale.\*\* Using a small (3B parameter) local model to fact-check citations produced false negatives even on exact word-for-word source matches. Switching to a simple word-overlap scoring method produced more consistent, defensible verdicts — a good example of "the more complex approach isn't always the better one."



\*\*Model size vs. latency tradeoff, measured directly:\*\* `llama3` (8B) produced more thorough answers but took 3-4 minutes per response on CPU-only hardware. `llama3.2:1b` cut generation to under 2 seconds but occasionally fabricated specific details (invented document section numbers, incorrect specific figures) even while citing the correct general source. Settled on `llama3.2:3b` as the best balance for this hardware.



\*\*Confidence thresholds should be set from data, not guessed.\*\* Ran the reranker against known-answerable and known-unanswerable questions, found a real gap in score distributions, and set the threshold at the boundary — rather than picking an arbitrary number.



\## Project structure



```

rag-project/

├── documents/            # Source documents (markdown)

├── src/                  # Python backend (chunking, search, generation, API)

├── eval/                 # Golden evaluation dataset

├── frontend/              # React UI

├── Dockerfile             # Backend container

├── frontend/Dockerfile    # Frontend container

└── docker-compose.yml     # Orchestrates both containers

```



\## Running it



\*\*Prerequisites:\*\* Docker Desktop, and \[Ollama](https://ollama.com) running locally with `llama3.2:3b` pulled (`ollama pull llama3.2:3b`).



```bash

docker-compose up

```



Then visit `http://localhost:5173`.



\## Evaluation methodology



The golden dataset (`eval/golden\_dataset.json`) contains 17 hand-written questions spanning:

\- \*\*Easy\*\* (5) — wording close to source text, sanity checks

\- \*\*Medium\*\* (5) — realistic paraphrasing

\- \*\*Hard\*\* (5) — heavily paraphrased, adversarial test cases

\- \*\*No-answer\*\* (2) — trick questions with no correct answer in the documents, testing the system's honesty rather than accuracy



Run `python src/run\_eval.py` to reproduce the 93.3% retrieval accuracy result.

