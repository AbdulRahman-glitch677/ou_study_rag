import json, time, csv, sys, os
sys.path.insert(0, "src")

mode = sys.argv[1] if len(sys.argv) > 1 else "baseline"
if mode == "guarded":
    from guarded import guarded_answer as answer
else:
    from rag import answer

OUT = f"eval/results_{mode}.csv"
FIELDS = ["id", "type", "subject", "question", "answer", "sources",
          "top_distance", "latency_s", "looks_like_refusal", "error"]
REFUSAL_WORDS = ["not found", "not in", "cannot", "can't", "can’t",
                 "don't have", "do not have", "only answer", "outside",
                 "not covered", "no information", "unable", "blocked"]

with open("eval/questions.json", encoding="utf-8") as f:
    questions = json.load(f)

done = {}
if os.path.exists(OUT):
    with open(OUT, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["error"] == "":
                done[int(r["id"])] = r

def to_row(q, text, hits, latency, err):
    refusal = False if err else any(w in text.lower() for w in REFUSAL_WORDS)
    return {
        "id": q["id"], "type": q["type"], "subject": q["subject"],
        "question": q["question"], "answer": text,
        "sources": "; ".join(f"{m['source']} p{m['page']}" for _, m, _ in hits),
        "top_distance": round(hits[0][2], 3) if hits else "",
        "latency_s": latency, "looks_like_refusal": refusal, "error": err,
    }

def save(rows):
    with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

rows = []
for q in questions:
    if q["id"] in done:
        rows.append(done[q["id"]])
        continue
    start = time.time()
    text, hits, err = "", [], ""
    for attempt in range(3):
        try:
            text, hits = answer(q["question"])
            err = ""
            break
        except Exception as e:
            err = str(e)[:300]
            low = err.lower()
            if "per day" in low or "tpd" in low:
                rows.append(to_row(q, "", [], 0, err))
                save(rows)
                print("Daily limit reached. Stop and try again later.\n", err)
                sys.exit(1)
            time.sleep(65 if ("429" in low or "rate" in low) else 5)
    latency = round(time.time() - start, 2)
    rows.append(to_row(q, text, hits, latency, err))
    save(rows)
    print(q["id"], q["type"], rows[-1]["top_distance"], latency,
          "ERROR" if err else "", flush=True)
    time.sleep(4)

ok = [r for r in rows if r["error"] == ""]
print(f"\nCompleted: {len(ok)}/{len(rows)}, errors: {len(rows) - len(ok)}")
for t in ["normal", "off_topic", "not_in_docs"]:
    sub = [r for r in ok if r["type"] == t]
    dists = [float(r["top_distance"]) for r in sub if r["top_distance"] != ""]
    ref = sum(str(r["looks_like_refusal"]) == "True" for r in sub)
    if sub:
        avg = sum(dists) / len(dists) if dists else 0
        print(f"{t}: n={len(sub)}, avg top distance {avg:.3f}, looks like refusal {ref}/{len(sub)}")