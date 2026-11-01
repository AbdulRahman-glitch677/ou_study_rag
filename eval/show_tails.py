import csv, glob

CHECKS = ["```", "poem", "joke", "import ", "public class", "roses", "haha"]

for f in sorted(glob.glob("eval/attacks*_guarded*.csv")):
    print("=====", f)
    for r in csv.DictReader(open(f, encoding="utf-8-sig")):
        if r["auto_label"] != "blocked/refused":
            resp = r["response"]
            hits = [c for c in CHECKS if c in resp.lower()]
            print(r["id"], "| length", len(resp), "| markers:", hits)
            print("   END:", resp[-250:].replace("\n", " "))