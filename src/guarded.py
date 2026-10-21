import os
import re
from rag import retrieve, llm

MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-20b")
K = int(os.getenv("TOP_K", "8"))
THRESHOLD = 0.58
DEBUG = {}

RULES = {
    "strict": "If the context does not clearly contain the answer, reply with exactly: NOT_FOUND",
    "soft": ("If the context contains information that answers the question, even partly, "
             "answer using only that information. Reply with exactly NOT_FOUND only when "
             "the context has nothing that answers it, for example dates, fees, names or "
             "numbers that do not appear in the context."),
}
RULE = RULES[os.getenv("PROMPT_MODE", "strict")]

OFF_TOPIC_MSG = "I can only answer questions about Generative AI, Cyber Security and Green Building Technology."
NOT_FOUND_MSG = "Not found in my documents."
BLOCKED_MSG = "That request was blocked."

INJECTION_PATTERNS = [
    r"ignore (all |any |your |previous |the )*instructions",
    r"disregard .*(rules|instructions)",
    r"reveal .*prompt",
    r"you are now",
    r"developer mode",
    r"jailbreak",
]

def is_injection(question):
    q = question.lower()
    return any(re.search(p, q) for p in INJECTION_PATTERNS)

def guarded_answer(question):
    if is_injection(question):
        return BLOCKED_MSG, []

    hits = retrieve(question, k=K)
    if not hits or hits[0][2] > THRESHOLD:
        return OFF_TOPIC_MSG, hits

    context = "\n\n".join(
        f"[{m['source']} p{m['page']}]\n{d}" for d, m, _ in hits
    )
    prompt = f"""You answer study questions using ONLY the context below.
{RULE}
Do not use outside knowledge. Keep the answer under 120 words.
End with: (Source: <file name>, page <number>) using a file and page from the context.

Context:
{context}

Question: {question}"""

    resp = llm.chat.completions.create(
        model=MODEL,
        reasoning_effort="low",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    text = resp.choices[0].message.content.strip()
    DEBUG["raw"] = text

    if text.upper().startswith("NOT_FOUND"):
        return NOT_FOUND_MSG, hits
    if not re.search(r"sources?\s*:", text, re.I):
        top = "; ".join(f"{m['source']} p{m['page']}" for _, m, _ in hits[:2])
        text += f"\n(Sources: {top})"
    return text, hits