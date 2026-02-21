# frontend/app.py
import streamlit as st
import requests
import time

API_UPLOAD = "http://127.0.0.1:8000/upload"
API_ASK = "http://127.0.0.1:8000/ask"

st.set_page_config(page_title="Document Assistant", layout="wide")
st.title("📄 Intelligent Document Assistant")

# Upload area
st.header("1) Upload a PDF to index")
uploaded_file = st.file_uploader("Upload a PDF (will replace current index)", type=["pdf"])

if uploaded_file:
    if st.button("Upload & Index"):
        with st.spinner("Uploading and indexing..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            try:
                res = requests.post(API_UPLOAD, files=files, timeout=600)
                res.raise_for_status()
                data = res.json()
                st.success(f"Indexed: {data.get('filename')}")
                st.write("Ingest summary:", data.get("ingest", {}))
            except Exception as e:
                st.error(f"Upload or ingestion failed: {e}")

st.divider()

# Chat area
st.header("2) Ask questions about the indexed PDF")

if "messages" not in st.session_state:
    st.session_state.messages = []

# display previous messages
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

user_input = st.chat_input("Ask a question about the uploaded PDF...")

if user_input:
    # add user message to UI
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # call backend
    with st.chat_message("assistant"):
        with st.spinner("Fetching answer..."):
            payload = {"question": user_input, "top_k": 6}
            try:
                r = requests.post(API_ASK, json=payload, timeout=600)
                r.raise_for_status()
                resp = r.json()
                answer = resp.get("answer", "No answer returned.")
                sources = resp.get("sources", [])
            except Exception as e:
                answer = f"Error: {e}"
                sources = []

        st.markdown(answer)

        if sources:
            with st.expander("Sources used"):
                for s in sources:
                    st.markdown(f"**{s.get('chunk_id', '')}** — pages {s.get('page_start')}-{s.get('page_end')} (score: {round(s.get('score', 3), 3)})")
                    st.code(s.get("content", "")[:500])

    st.session_state.messages.append({"role": "assistant", "content": answer})
