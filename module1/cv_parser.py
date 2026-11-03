import os
import fitz
from docx import Document
from docx.oxml.ns import qn


def extract_docx_hyperlinks(doc):
    hyperlinks = []

    # Find hyperlinks inside the Word document
    for hyperlink in doc.part.element.iter(qn("w:hyperlink")):

        relationship_id = hyperlink.get(qn("r:id"))

        if not relationship_id:
            continue

        relationship = doc.part.rels.get(relationship_id)
        if not relationship:
            continue

        url = relationship.target_ref

        # Extract the visible hyperlink text
        label = "".join(
            node.text or ""
            for node in hyperlink.iter(qn("w:t"))
        ).strip()

        hyperlinks.append((label, url))

    return hyperlinks


def extract_pdf_hyperlinks(pdf):
    hyperlinks = []

    for page in pdf:
        words = page.get_text("words")

        for link in page.get_links():

            url = link.get("uri")
            if not url:
                continue

            link_rect = fitz.Rect(link["from"])

            # Find the visible text inside the hyperlink area
            linked_words = []

            for word in words:
                word_rect = fitz.Rect(word[:4])

                if word_rect.intersects(link_rect):
                    linked_words.append(word)

            linked_words.sort(
                key=lambda word: (word[5], word[6], word[7])
            )

            label = " ".join(word[4] for word in linked_words)

            hyperlinks.append((label, url))

    return hyperlinks


def format_hyperlinks(hyperlinks):
    if not hyperlinks:
        return ""

    lines = ["\n\nHYPERLINKS FOUND IN THE DOCUMENT:"]

    seen = set()

    for label, url in hyperlinks:

        if (label, url) in seen:
            continue

        seen.add((label, url))
        
        if label:
            lines.append(f"{label}: {url}")
        else:
            lines.append(url)

    return "\n".join(lines)


def read_cv(file_path: str) -> str:

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    extension = os.path.splitext(file_path)[-1].lower()

    hyperlinks = []

    if extension == ".pdf":

        with fitz.open(file_path) as pdf:

            text = "\n".join(
                page.get_text()
                for page in pdf
            )

            hyperlinks = extract_pdf_hyperlinks(pdf)

    elif extension == ".docx":

        doc = Document(file_path)

        paragraphs = [
            paragraph.text
            for paragraph in doc.paragraphs
        ]

        tables = [
            "\n".join(
                " | ".join(cell.text for cell in row.cells)
                for row in table.rows
            )
            for table in doc.tables
        ]

        text = "\n".join(paragraphs + tables)

        hyperlinks = extract_docx_hyperlinks(doc)

    elif extension == ".txt":

        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()

    else:

        raise ValueError(
            "Unsupported file format. Please upload a PDF, DOCX, or TXT file."
        )

    text = text.strip()

    # Add extracted hyperlink URLs to the CV text
    text += format_hyperlinks(hyperlinks)

    return text