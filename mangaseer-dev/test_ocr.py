from manga_ocr import MangaOcr


mocr = MangaOcr()
text = mocr("manga_datasets/ocr/clean_10k/test/9ed74431230d4ac0bbe854607b21008c.jpg")

print(text)