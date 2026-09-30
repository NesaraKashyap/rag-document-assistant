import os
from pypdf import PdfReader

DOCUMENTS_FOLDER = "documents"


def extract_pdf_text(filepath):
    """
    Extracts all text from a PDF file, page by page, joined together.
    """
    reader = PdfReader(filepath)
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)
    return "\n\n".join(text_parts)


def load_documents():
    """
    Reads every .md, .txt, and .pdf file in the documents folder
    and returns a list of dictionaries with the filename and its text content.
    """
    documents = []

    for filename in os.listdir(DOCUMENTS_FOLDER):
        filepath = os.path.join(DOCUMENTS_FOLDER, filename)

        if filename.endswith(".md") or filename.endswith(".txt"):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            documents.append({
                "filename": filename,
                "content": content
            })

        elif filename.endswith(".pdf"):
            content = extract_pdf_text(filepath)
            documents.append({
                "filename": filename,
                "content": content
            })

    return documents


if __name__ == "__main__":
    docs = load_documents()

    print(f"Loaded {len(docs)} documents.\n")

    for doc in docs:
        print(f"--- {doc['filename']} ---")
        print(f"Character count: {len(doc['content'])}")
        print(f"First 100 characters: {doc['content'][:100]}")
        print()