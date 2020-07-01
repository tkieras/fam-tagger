from family_resemblance_tagger.preprocessing.file_loaders import epub_load

def test_load_normal():
	path = "data/sample_1.epub"
	result = epub_load.load(path)
	assert(result.startswith("Chapter 1 Images of the Mandelbrot"))
	assert(result.endswith("https://en.wikipedia.org/wiki/Mandelbrot_set"))

def test_load_blank():
	path = "data/blank.epub"
	result = epub_load.load(path)
	print(result)
	assert(len(result) == 0)