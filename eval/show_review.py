import csv, glob

for f in sorted(glob.glob("eval/attacks*_guarded*.csv")):
    print("=====", f)
    for r in csv.DictReader(open(f, encoding="utf-8-sig")):
        if r["auto_label"] != "blocked/refused":
            print(r["id"], r["auto_label"], "|", r["attack"][:60])
            print("    ", r["response"][:400].replace("\n", " "))