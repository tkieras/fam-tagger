from ebooklib import epub
import ebooklib
from bs4 import BeautifulSoup

def load(path):
    try:
        book = epub.read_epub(path)
    except ebooklib.epub.EpubException:
        return None

    extracted_text = []

    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        html_to_text = BeautifulSoup(item.get_body_content(), features="html.parser")
        extracted_text.append(html_to_text.get_text(" ", strip=True))

    return " ".join(extracted_text)
