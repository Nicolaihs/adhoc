import fitz  # PyMuPDF
import pdfplumber
import click
from typing import List, Dict, Any, Optional


def extract_text_blocks_from_pdf(
    pdf_path: str, page_num: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Extracts text blocks from each page of the PDF."""
    text_blocks = []
    with fitz.open(pdf_path) as pdf_document:
        pages = range(len(pdf_document)) if page_num is None else [page_num - 1]
        for page_index in pages:
            page = pdf_document.load_page(page_index)
            blocks = page.get_text("dict")["blocks"]
            page_blocks = []
            for block in blocks:
                if block["type"] == 0:  # Text block
                    block_font_size = block["lines"][0]["spans"][0]["size"]
                    block_font = block["lines"][0]["spans"][0]["font"]
                    block_info = {
                        "bbox": block["bbox"],
                        "font": block_font,
                        "font_size": block_font_size,
                        "lines": [],
                    }
                    for line in block["lines"]:
                        text = " ".join([span["text"] for span in line["spans"]])
                        block_info["lines"].append(text)
                        # line_info = {
                        #     "text": " ".join([span["text"] for span in line["spans"]]),
                        #     "size": line["spans"][0]["size"],
                        #     "font": line["spans"][0]["font"],
                        # }
                        # block_info["lines"].append(line_info)
                    page_blocks.append(block_info)
            text_blocks.append({"page_number": page_index + 1, "blocks": page_blocks})
    return text_blocks


def extract_tables_from_pdf(
    pdf_path: str, page_num: Optional[int] = None
) -> List[Dict]:
    """Extracts tables from each page of the PDF."""
    tables = []
    with pdfplumber.open(pdf_path) as pdf_document:
        pages = (
            pdf_document.pages
            if page_num is None
            else [pdf_document.pages[page_num - 1]]
        )
        for page in pages:
            page_tables = page.extract_tables()
            tables.append({"page_number": page.page_number, "tables": page_tables})
    return tables


@click.command()
@click.argument("pdf_path", type=click.Path(exists=True))
@click.option("--page", type=int, help="Page number to extract (1-based index)")
def main(pdf_path: str, page: Optional[int]):
    """Extracts and prints text blocks and tables from a PDF."""
    # Extract text blocks
    text_blocks = extract_text_blocks_from_pdf(pdf_path, page)
    for page_info in text_blocks:
        print(f"Text blocks on page {page_info['page_number']}:")
        for block in page_info["blocks"]:
            print(
                f"Block bounding box: {block['bbox']}, Font: {block['font']}, Font size: {block['font_size']}"
            )
            for line in block["lines"]:
                print(line)

            print("\n")

    # Extract tables
    tables = extract_tables_from_pdf(pdf_path, page)
    for table_info in tables:
        page_number = table_info["page_number"]
        page_tables = table_info["tables"]
        print(f"Tables on page {page_number}:")
        for table in page_tables:
            for row in table:
                for line in row:
                    print(line)
            print("\n")


if __name__ == "__main__":
    main()
