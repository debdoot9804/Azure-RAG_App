## 🌟 Azure RAG App


A sleek Retrieval-Augmented Generation (RAG) app to upload PDFs, index their content, and answer questions using Azure AI services and Streamlit. Powered by Azure AI Search, Azure Blob Storage, and Azure OpenAI (gpt-4o-mini).

🚀 Features
📄 Upload PDFs: Store text-based PDFs in Azure Blob Storage.
✂️ Chunk Text: Split PDFs into ~500-token chunks with tiktoken and pdfplumber.
🔍 Index & Search: Index chunks in Azure AI Search for fast retrieval.
💬 Smart Answers: Generate answers with Azure OpenAI.
🗑️ Clear Index: Remove outdated documents easily.
🌐 Streamlit UI: Intuitive interface for uploads and queries.

🛠️ Architecture
Backend (rag_app.py): Handles PDF extraction, chunking, indexing, and RAG queries.
Frontend (streamlit_app.py): Streamlit interface for user interaction.
Azure Services:
AI Search: rag-search-deb (East US).
Blob Storage: appstore99, documents container (East US).
OpenAI: rag-openai-debdoot, gpt-4o-mini (West US).

📋 Prerequisites
Azure account with AI Search, Blob Storage, and OpenAI access.
Python 3.12.
GitHub and Streamlit Cloud accounts.

⚙️ Setup
Clone Repo: git clone https://github.com/debdoot9804/Azure-RAG_App.git
cd Azure-RAG_App

The Streamlit front-end can be accessed here : https://azure-ragapp-debdoot.streamlit.app/

![image](https://github.com/user-attachments/assets/a7f853eb-2f76-457c-b57b-ab69792fbf94)



