import pdftotext

def load(path):
    with open(path, "rb") as f:
        try:
            document = pdftotext.PDF(f)
            text = ("\n".join(document))
            text = text.strip()
            if not text:
                text = None
        except pdftotext.Error:
            text = None


    return text
