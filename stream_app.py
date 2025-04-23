import streamlit as st
from rag_app import query_rag,clear_index
from data_ingest import upload_and_index_document

def main():
    st.title("RAG Application with Azure and Streamlit")


    # Clear index
    st.header("Manage Index")
    if st.button("Clear Index"):
        with st.spinner("Clearing index..."):
            count, message = clear_index()
            if count >= 0:
                st.success(f"{message} ({count} documents deleted)")
            else:
                st.error(message)
    
    # Document upload
    st.header("Upload Document")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file is not None:
        if st.button("Upload and Index"):
            with st.spinner("Uploading and indexing..."):
                chunk_count, message = upload_and_index_document(uploaded_file, uploaded_file.name)
                if chunk_count > 0:
                    st.success(f"Document uploaded and indexed as {chunk_count} chunks")
                else:
                    st.error(message)
    
    # Query interface
    st.header("Ask a Question")
    question = st.text_input("Enter your question:")
    if st.button("Get Answer"):
        if question:
            with st.spinner("Generating answer..."):
                answer, message = query_rag(question)
                if answer:
                    st.write("**Answer:**")
                    st.write(answer)
                else:
                    st.error(message)
        else:
            st.warning("Please enter a question.")

if __name__ == "__main__":
    main()