def load(filepath):
    text = None
    with open(filepath, "r") as f:
        try:
            text = f.read()
            text = text.strip()
        except UnicodeDecodeError:
            text = None
    return text
