import streamlit as st

st.set_page_config(
    page_title="Healthcare Chatbot System",
    page_icon="🏥",
    layout="wide"
)

st.title("Healthcare Chatbot System")
st.write("Welcome to the healthcare chatbot platform")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Flow Chat")
    st.write("Step-by-step patient registration system")
    st.write("")
    st.write("Features:")
    st.write("- Collect patient information")
    st.write("- Validate each field")
    st.write("- Calculate BMI automatically")
    st.write("- Save to JSON file")
    st.write("")
    st.info("Use the sidebar to navigate to Flow Chat")

with col2:
    st.subheader("RAG Chat")
    st.write("Ask questions about medical documents")
    st.write("")
    st.write("Features:")
    st.write("- Query medical documents")
    st.write("- Get AI-powered answers")
    st.write("- View source documents")
    st.write("- Chat history")
    st.write("")
    st.info("Use the sidebar to navigate to RAG Chat")

st.markdown("---")

st.write("Select a page from the sidebar to get started")