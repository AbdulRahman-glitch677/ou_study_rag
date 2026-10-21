import sys, json
sys.path.insert(0, "src")
import guarded

qs = {q["id"]: q["question"]
      for q in json.load(open("eval/questions.json", encoding="utf-8"))}

print("Debug run started. K =", guarded.K)

for i in [44, 49, 50]:
    guarded.DEBUG.clear()
    ans, hits = guarded.guarded_answer(qs[i])
    raw = guarded.DEBUG.get("raw", "(no model call)")
    print(f"Q{i} | {qs[i][:55]}")
    print("  RAW:", raw[:110].replace("\n", " "))
    print("  FINAL:", ans[:50].replace("\n", " "))

print("Debug run finished.")