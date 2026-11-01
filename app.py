import os
import sys
import datetime
import streamlit as st

# Streamlit Cloud stores keys as "secrets"; copy them to environment variables.
try:
    for key in ("GROQ_API_KEY", "HF_TOKEN", "DATA_REPO"):
        if key in st.secrets and not os.environ.get(key):
            os.environ[key] = st.secrets[key]
except Exception:
    pass

sys.path.insert(0, "src")

st.set_page_config(page_title="OU Study Assistant")

@st.cache_resource(show_spinner="Loading the document index. The first start takes a minute...")
def ensure_index():
    if not os.path.exists(os.path.join("chroma_db", "chroma.sqlite3")):
        from huggingface_hub import snapshot_download
        snapshot_download(
            repo_id=os.environ["DATA_REPO"],
            repo_type="dataset",
            token=os.environ["HF_TOKEN"],
            local_dir="chroma_db",
        )
    return True

ensure_index()
from guarded import guarded_answer

DAILY_CAP = 50
SESSION_CAP = 15
REFUSALS = ("I can only answer", "Not found", "That request")

@st.cache_resource
def usage():
    return {"day": "", "count": 0}

def allow_question():
    u = usage()
    today = datetime.date.today().isoformat()
    if u["day"] != today:
        u["day"], u["count"] = today, 0
    if u["count"] >= DAILY_CAP:
        return False
    u["count"] += 1
    return True

st.title("OU Study Assistant")
st.caption("Answers only from the loaded documents on Generative AI, "
           "Cyber Security and Green Building Technology.")
st.caption("Contains information from Wikipedia (CC BY-SA 4.0) and the "
           "MuseGAN paper (Dong et al., 2017).")

if "history" not in st.session_state:
    st.session_state.history = []
    st.session_state.count = 0

for role, text in st.session_state.history:
    with st.chat_message(role):
        st.markdown(text)

question = st.chat_input("Ask a question from your syllabus")
if question:
    if st.session_state.count >= SESSION_CAP:
        st.warning("You have reached the question limit for this session.")
    elif not allow_question():
        st.warning("The daily question limit for this demo has been reached. "
                   "Please try again tomorrow.")
    else:
        st.session_state.count += 1
        st.session_state.history.append(("user", question))
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Searching the documents..."):
                try:
                    text, hits = guarded_answer(question)
                except Exception:
                    text, hits = "Something went wrong. Please try again later.", []
            st.markdown(text)
            if hits and not text.startswith(REFUSALS):
                refs = []
                for _, meta, _ in hits[:4]:
                    ref = f"{meta['source']} (page {meta['page']})"
                    if ref not in refs:
                        refs.append(ref)
                st.caption("Sources: " + "; ".join(refs))
        st.session_state.history.append(("assistant", text))