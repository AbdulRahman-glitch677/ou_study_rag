import os
from dotenv import load_dotenv
from groq import Groq
import chromadb
from sentence_transformers import SentenceTransformer

load_dotenv()
llm = Groq(api_key=os.getenv("GROQ_API_KEY"))
model = SentenceTransformer("all-MiniLM-L6-v2")
collection = chromadb.PersistentClient(path="chroma_db").get_collection("study_docs")

def retrieve(question, k=4):
    emb = model.encode(question).tolist()
    res = collection.query(query_embeddings=[emb], n_results=k)
    return list(zip(res["documents"][0], res["metadatas"][0], res["distances"][0]))

def answer(question):
    hits = retrieve(question)
    context = "\n\n".join(
        f"[{m['source']} p{m['page']}]\n{d}" for d, m, _ in hits
    )
    prompt = f"""Answer the question using only the context below.
Mention the source file and page.

Context:
{context}

Question: {question}"""
    resp = llm.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return resp.choices[0].message.content, hits

if __name__ == "__main__":
    q = input("Ask: ")
    a, hits = answer(q)
    print(a)