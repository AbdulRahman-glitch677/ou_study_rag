import os, glob
from pypdf import PdfReader
import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(
    "study_docs", metadata={"hnsw:space": "cosine"}
)

def chunk_text(text, size=800, overlap=100):
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + size])
        start += size - overlap
    return chunks

for path in glob.glob("data/*.pdf"):
    name = os.path.basename(path)
    reader = PdfReader(path)
    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        for i, chunk in enumerate(chunk_text(text)):
            if len(chunk.strip()) < 50:
                continue
            collection.upsert(
                ids=[f"{name}-p{page_num}-c{i}"],
                documents=[chunk],
                embeddings=[model.encode(chunk).tolist()],
                metadatas=[{"source": name, "page": page_num}],
            )

print("Done. Total chunks:", collection.count())