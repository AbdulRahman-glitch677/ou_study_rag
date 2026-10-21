import glob
from pypdf import PdfReader

for path in glob.glob("data/*.pdf"):
    reader = PdfReader(path)
    pages = len(reader.pages)
    total = sum(len(p.extract_text() or "") for p in reader.pages)
    print(path, "| pages:", pages, "| characters:", total)