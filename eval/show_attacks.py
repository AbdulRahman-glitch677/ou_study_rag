import csv

for mode in ["baseline", "guarded"]:
    print("=====", mode)
    for r in csv.DictReader(open(f"eval/attacks_{mode}.csv", encoding="utf-8-sig")):
        print(r["id"], r["auto_label"], "|", r["attack"][:45], "->", r["response"][:80].replace("\n", " "), r["error"][:40])