import fitz  # PyMuPDF
import pdfplumber
from typing import List, Dict


def extract_text_from_pdf(pdf_path: str) -> List[str]:
    """Extracts text from each page of the PDF."""
    text_pages = []
    with fitz.open(pdf_path) as pdf_document:
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text = page.get_text()
            text_pages.append(text)
    return text_pages


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

    # Extract text
    text_pages = extract_text_from_pdf(pdf_path)
    for i, text in enumerate(text_pages):
        print(f"Text on page {i + 1}:\n{text}\n")

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
