test_path = "/home/tim/Documents/projects/family_resemblance_tagger/family_resemblance_tagger/test/file_loader_tests/test_A.pdf"

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

if __name__=="__main__":
    print(load(test_path))