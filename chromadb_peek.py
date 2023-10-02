import streamlit as st
import chromadb
from chromadb.config import Settings
from pprint import pformat

def run_code():
    persist_directory = "chromadb"
    chroma_client = chromadb.PersistentClient(path=persist_directory)
    collection = chroma_client.get_or_create_collection(name="knowledge_base")

    output1 = f'KB presently has {collection.count()} entries'
    output2 = '\n\nBelow are the top 10 entries:\n'
    results = collection.peek()
    output3 = pformat(results)

    return f"{output1}{output2}{output3}"

st.title("Chromadb GUI")

if st.button("Run Code"):
    result = run_code()
    st.text_area("Output", result, height=200)
