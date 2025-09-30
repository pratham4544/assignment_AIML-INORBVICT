import streamlit as st
import os
from pathlib import Path
from langchain_unstructured import UnstructuredLoader
from unstructured.cleaners.core import clean_extra_whitespace
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="RAG Chat", page_icon="📚", layout="wide")

if 'initialized' not in st.session_state:
    st.session_state.initialized = False
if 'vectorstore' not in st.session_state:
    st.session_state.vectorstore = None
if 'embeddings' not in st.session_state:
    st.session_state.embeddings = None
if 'llm' not in st.session_state:
    st.session_state.llm = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'docs' not in st.session_state:
    st.session_state.docs = None

if not st.session_state.initialized and Path("faiss_index").exists():
    try:
        with st.spinner("Loading vector store..."):
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
            llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0, max_tokens=2048, timeout=None, max_retries=2)
            vectorstore = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
            st.session_state.embeddings = embeddings
            st.session_state.llm = llm
            st.session_state.vectorstore = vectorstore
            st.session_state.initialized = True
    except Exception as e:
        st.error(f"Error loading vector store: {str(e)}")

PROMPT = '''You are a healthcare assistant. Answer based on the context provided.

Context: {context}
Question: {question}

Respond in JSON format:
{{
  "reply": "your answer",
  "guidance_caution": "medical disclaimer",
  "additional_resource_prompt": "follow-up suggestion"
}}'''

def fetch_documents():
    folder = "documents"
    paths = []
    if not Path(folder).exists():
        return None, "Documents folder not found"
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(('.txt', '.pdf', '.docx')):
                paths.append(os.path.join(root, file))
    if not paths:
        return None, "No documents found"
    return paths, None

def load_documents(paths):
    loader = UnstructuredLoader(paths, post_processors=[clean_extra_whitespace], chunking_strategy="basic", max_characters=700, chunk_overlap=200)
    return loader.load_and_split()

def initialize_models():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0, max_tokens=2048, timeout=None, max_retries=2)
    return embeddings, llm

def create_vector_store(embeddings, docs):
    store = FAISS.from_documents(docs, embedding=embeddings)
    store.save_local("faiss_index")
    return store

def ask_question(llm, vectorstore, question):
    docs = vectorstore.similarity_search(question, k=3)
    context = "\n\n".join([doc.page_content for doc in docs])
    prompt = PromptTemplate(template=PROMPT, input_variables=["context", "question"])
    chain = prompt | llm | JsonOutputParser()
    response = chain.invoke({"context": context, "question": question})
    response['sources'] = docs
    return response

st.title("Medical Document Q&A")
st.write("Ask questions about medical documents")
st.info("Sample Question:")
st.write('What is diabetes?')
st.write('What are the symptoms?')
st.write('How often should I check my blood sugar?')


with st.sidebar:
    st.header("System Setup")
    
    if st.session_state.initialized:
        st.success("System Ready")
        if st.session_state.docs:
            st.metric("Documents", len(st.session_state.docs))
        if st.button("Reinitialize", use_container_width=True):
            st.session_state.initialized = False
            st.session_state.vectorstore = None
            st.session_state.docs = None
            st.rerun()
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    else:
        st.warning("System Not Initialized")
        if st.button("Initialize System", use_container_width=True, type="primary"):
            with st.spinner("Initializing..."):
                try:
                    doc_paths, error = fetch_documents()
                    if error:
                        st.error(error)
                        st.stop()
                    docs = load_documents(doc_paths)
                    st.session_state.docs = docs
                    embeddings, llm = initialize_models()
                    st.session_state.embeddings = embeddings
                    st.session_state.llm = llm
                    vectorstore = create_vector_store(embeddings, docs)
                    st.session_state.vectorstore = vectorstore
                    st.session_state.initialized = True
                    st.success("System Ready")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    st.write("Instructions:")
    st.write("1. Add documents to documents/ folder")
    st.write("2. Click Initialize System")
    st.write("3. Ask your questions")

if not st.session_state.initialized:
    st.info("Initialize the system from the sidebar")
    st.write("Example questions:")
    st.write("- What is diabetes?")
    st.write("- Symptoms of heart disease?")
    st.write("- How to prevent high blood pressure?")
else:
    for msg in st.session_state.chat_history:
        if msg['role'] == 'user':
            with st.chat_message("user"):
                st.write(msg['content'])
        else:
            with st.chat_message("assistant"):
                st.write(msg['content']['reply'])
                if msg['content'].get('guidance_caution'):
                    st.warning(msg['content']['guidance_caution'])
                if msg['content'].get('additional_resource_prompt'):
                    st.info(msg['content']['additional_resource_prompt'])
                if msg['content'].get('sources'):
                    with st.expander("View Sources"):
                        for idx, doc in enumerate(msg['content']['sources'], 1):
                            st.write(f"Source {idx}:")
                            if hasattr(doc, 'metadata') and doc.metadata and 'source' in doc.metadata:
                                st.caption(f"File: {Path(doc.metadata['source']).name}")
                            st.text_area(f"Content {idx}", doc.page_content, height=150, key=f"src_{len(st.session_state.chat_history)}_{idx}", disabled=True)
    
    question = st.chat_input("Ask a question...")
    
    if question:
        st.session_state.chat_history.append({'role': 'user', 'content': question})
        with st.chat_message("user"):
            st.write(question)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = ask_question(st.session_state.llm, st.session_state.vectorstore, question)
                    st.write(response['reply'])
                    if response.get('guidance_caution'):
                        st.warning(response['guidance_caution'])
                    if response.get('additional_resource_prompt'):
                        st.info(response['additional_resource_prompt'])
                    if response.get('sources'):
                        with st.expander("View Sources"):
                            for idx, doc in enumerate(response['sources'], 1):
                                st.write(f"Source {idx}:")
                                if hasattr(doc, 'metadata') and doc.metadata and 'source' in doc.metadata:
                                    st.caption(f"File: {Path(doc.metadata['source']).name}")
                                st.text_area(f"Content {idx}", doc.page_content, height=150, key=f"src_new_{idx}", disabled=True)
                    st.session_state.chat_history.append({'role': 'assistant', 'content': response})
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.session_state.chat_history.append({'role': 'assistant', 'content': {'reply': f"Error: {str(e)}", 'guidance_caution': 'Try rephrasing', 'additional_resource_prompt': ''}})