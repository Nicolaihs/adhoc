import fitz  # PyMuPDF
import pdfplumber
from typing import List, Dict, Any


def extract_text_blocks_from_pdf(pdf_path: str) -> List[List[Dict[str, Any]]]:
    """Extracts text blocks from each page of the PDF."""
    text_blocks = []
    with fitz.open(pdf_path) as pdf_document:
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            blocks = page.get_text("dict")["blocks"]
            page_blocks = []
            for block in blocks:
                if block["type"] == 0:  # Text block
                    page_blocks.append({"bbox": block["bbox"], "text": block["lines"]})
            text_blocks.append(page_blocks)
    return text_blocks


def extract_tables_from_pdf(pdf_path: str) -> List[Dict]:
    """Extracts tables from each page of the PDF."""
    tables = []
    with pdfplumber.open(pdf_path) as pdf_document:
        for page in pdf_document.pages:
            page_tables = page.extract_tables()
            tables.append({"page_number": page.page_number, "tables": page_tables})
    return tables


def main():
    pdf_path = "/Users/nhs/Downloads/104844_SprogHistorie_bd3_r1_LKF.pdf"

    # Extract text blocks
    text_blocks = extract_text_blocks_from_pdf(pdf_path)
    for i, blocks in enumerate(text_blocks):
        print(f"Text blocks on page {i + 1}:")
        for block in blocks:
            print(f"Block bounding box: {block['bbox']}")
            for line in block["text"]:
                line_text = " ".join([span["text"] for span in line["spans"]])
                print(line_text)
            print("\n")

    # Extract tables
    tables = extract_tables_from_pdf(pdf_path)
    for table_info in tables:
        page_number = table_info["page_number"]
        page_tables = table_info["tables"]
        print(f"Tables on page {page_number}:")
        for table in page_tables:
            for row in table:
                print(row)
            print("\n")

    import ipdb

    ipdb.set_trace()


if __name__ == "__main__":
    main()
