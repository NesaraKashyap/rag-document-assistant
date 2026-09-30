import re
from .load_documents import load_documents

CHUNK_SIZE = 800       # characters per chunk, for documents with no ## headings
CHUNK_OVERLAP = 100    # overlap between chunks, to avoid cutting sentences awkwardly


def chunk_by_headings(filename, content):
    """
    Splits text into chunks based on '##' section headings.
    Used for well-structured markdown documents.
    """
    sections = re.split(r'\n(?=## )', content)

    chunks = []
    for i, section in enumerate(sections):
        section = section.strip()
        if section == "":
            continue

        lines = section.split("\n")
        heading = lines[0].replace("#", "").strip()

        body_text = "\n".join(lines[1:]).strip()
        if body_text == "":
            continue

        chunks.append({
            "chunk_id": f"{filename}::chunk_{i}",
            "source_file": filename,
            "heading": heading,
            "text": section
        })

    return chunks


def chunk_by_fixed_size(filename, content):
    """
    Splits text into fixed-size, overlapping chunks.
    Used as a fallback for documents with no '##' headings (e.g. PDFs).
    """
    chunks = []
    start = 0
    i = 0

    while start < len(content):
        end = start + CHUNK_SIZE
        chunk_text = content[start:end].strip()

        if chunk_text != "":
            chunks.append({
                "chunk_id": f"{filename}::chunk_{i}",
                "source_file": filename,
                "heading": f"Section {i + 1}",
                "text": chunk_text
            })
            i += 1

        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


def chunk_document(doc):
    """
    Chooses a chunking strategy based on whether the document
    has markdown '##' headings, then splits it into chunks.
    """
    filename = doc["filename"]
    content = doc["content"]

    if "## " in content:
        return chunk_by_headings(filename, content)
    else:
        return chunk_by_fixed_size(filename, content)


def chunk_all_documents(documents):
    """
    Runs chunk_document on every document and returns one flat list of all chunks.
    """
    all_chunks = []
    for doc in documents:
        all_chunks.extend(chunk_document(doc))
    return all_chunks


if __name__ == "__main__":
    docs = load_documents()
    chunks = chunk_all_documents(docs)

    print(f"Created {len(chunks)} chunks from {len(docs)} documents.\n")

    for chunk in chunks:
        print(f"--- {chunk['chunk_id']} ---")
        print(f"Heading: {chunk['heading']}")
        print(f"Text preview: {chunk['text'][:80]}...")
        print()