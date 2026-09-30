import re
import ollama

MODEL_NAME = "llama3.2:3b"


def split_into_claims(answer_text):
    """
    Splits the generated answer into individual sentences, and figures out
    which citation number(s) each sentence references, if any.
    """
    sentences = re.split(r'(?<=[.!?])\s+', answer_text.strip())

    # Merge any fragment that is ONLY a citation marker (e.g. "[1]")
    # back onto the previous real sentence, since it has no content on its own.
    merged_sentences = []
    for sentence in sentences:
        stripped = sentence.strip()
        is_citation_only = bool(re.fullmatch(r'(\[\d+\]\s*)+', stripped))

        if is_citation_only and merged_sentences:
            merged_sentences[-1] = merged_sentences[-1] + " " + stripped
        else:
            merged_sentences.append(sentence)

    claims = []
    for sentence in merged_sentences:
        citation_numbers = re.findall(r'\[(\d+)\]', sentence)
        if citation_numbers:
            claims.append({
                "sentence": sentence,
                "citation_numbers": [int(n) for n in citation_numbers]
            })

    return claims


def verify_claim(claim_sentence, chunk_text):
    """
    Asks the LLM a narrow yes/no question: does this specific chunk
    actually support this specific claim?
    """
    prompt = f"""You are a strict fact-checker. Below is a CLAIM and a SOURCE TEXT.
Determine if the SOURCE TEXT actually supports the CLAIM.

Respond with exactly one word: YES, NO, or PARTIAL.
- YES: every specific fact/number in the claim is directly stated in the source
- PARTIAL: the general idea is supported, but some specific detail (a number, date, or condition) is NOT in the source
- NO: the source does not support this claim at all

SOURCE TEXT:
{chunk_text}

CLAIM:
{claim_sentence}

Answer (YES, NO, or PARTIAL only):"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        options={"num_predict": 5}
    )

    verdict = response["message"]["content"].strip().upper()

    if "YES" in verdict:
        return "YES"
    elif "PARTIAL" in verdict:
        return "PARTIAL"
    else:
        return "NO"


# A small list of common filler words to ignore — they appear everywhere
# and don't tell us anything about whether a claim is actually supported.
STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "to", "of", "in", "on", "at", "for", "and", "or", "but", "if", "then",
    "this", "that", "these", "those", "it", "its", "as", "by", "with",
    "from", "not", "no", "does", "do", "did", "will", "would", "can",
    "could", "may", "might", "must", "you", "your"
}


def normalize_words(text):
    """
    Lowercases text, strips punctuation, splits into words,
    and removes common filler words — leaving only the meaningful ones.
    """
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)  # remove punctuation
    words = text.split()
    return set(word for word in words if word not in STOPWORDS)


def verify_claim_word_overlap(claim_sentence, chunk_text):
    """
    Checks how much of the claim's meaningful vocabulary actually
    appears in the source chunk — a fast, non-LLM alternative to
    verify_claim(). Returns YES, PARTIAL, or NO plus the overlap ratio.
    """
    claim_words = normalize_words(claim_sentence)
    chunk_words = normalize_words(chunk_text)

    if len(claim_words) == 0:
        return "NO", 0.0

    overlapping = claim_words.intersection(chunk_words)
    overlap_ratio = len(overlapping) / len(claim_words)

    if overlap_ratio >= 0.75:
        verdict = "YES"
    elif overlap_ratio >= 0.45:
        verdict = "PARTIAL"
    else:
        verdict = "NO"

    return verdict, overlap_ratio


def verify_answer(answer_text, chunks, method="overlap"):
    """
    Runs verification on every citation-bearing sentence in the answer.
    `method` can be "overlap" (fast, non-LLM) or "llm" (slower, uses the model).
    `chunks` should be the same list of chunks used to generate the answer,
    in order, so citation [1] maps to chunks[0], [2] maps to chunks[1], etc.
    """
    claims = split_into_claims(answer_text)
    verification_results = []

    for claim in claims:
        for citation_num in claim["citation_numbers"]:
            chunk_index = citation_num - 1  # [1] refers to chunks[0]

            if chunk_index < 0 or chunk_index >= len(chunks):
                continue  # citation number doesn't match any real chunk

            chunk = chunks[chunk_index]

            if method == "llm":
                verdict = verify_claim(claim["sentence"], chunk["text"])
                overlap_ratio = None
            else:
                verdict, overlap_ratio = verify_claim_word_overlap(claim["sentence"], chunk["text"])

            verification_results.append({
                "sentence": claim["sentence"],
                "citation": citation_num,
                "source": f"{chunk['source_file']} > {chunk['heading']}",
                "verdict": verdict,
                "overlap_ratio": overlap_ratio
            })

    return verification_results


def print_verification(results):
    print("\n--- Citation Verification ---")
    for r in results:
        ratio_text = f" (overlap: {r['overlap_ratio']:.0%})" if r['overlap_ratio'] is not None else ""
        print(f"[{r['verdict']}]{ratio_text} \"{r['sentence']}\" (cites [{r['citation']}] {r['source']})")
    print()