import sys
import streamlit as st
sys.path.insert(0, "src")
from guarded import guarded_answer

st.set_page_config(page_title="OU Study Assistant")
st.title("OU Study Assistant")
st.caption("Answers only from the loaded documents on Generative AI, "
           "Cyber Security and Green Building Technology.")

MAX_QUESTIONS = 20
REFUSALS = ("I can only answer", "Not found", "That request")

if "history" not in st.session_state:
    st.session_state.history = []
    st.session_state.count = 0

for role, text in st.session_state.history:
    with st.chat_message(role):
        st.markdown(text)

question = st.chat_input("Ask a question from your syllabus")
if question:
    if st.session_state.count >= MAX_QUESTIONS:
        st.warning("Question limit reached for this session.")
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
                with st.expander("Sources used"):
                    for doc, meta, dist in hits[:4]:
                        st.caption(f"{meta['source']} - page {meta['page']}")
                        st.text(doc[:300])
        st.session_state.history.append(("assistant", text))