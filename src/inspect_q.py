import sys
from rag import retrieve

q = " ".join(sys.argv[1:])
for doc, meta, dist in retrieve(q, k=4):
    print(round(dist, 3), meta["source"], "p", meta["page"])
    print(doc[:200].replace("\n", " "))
    print()