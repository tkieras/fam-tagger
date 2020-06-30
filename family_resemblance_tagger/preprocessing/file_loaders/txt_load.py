testpath = "tests/test_A.txt"
testpath = "/Users/tim/Documents/library/Theology/church/Council Vatican I/VaticanI_Dei_Filius.pdf"

def load(filepath):
    text = None
    with open(filepath, "r") as f:
        try:
            text = f.read()
            text = text.strip()
        except UnicodeDecodeError:
            text = None

    
    return text

if __name__ == "__main__":
	print(load(testpath))
