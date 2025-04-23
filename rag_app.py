import os
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient
from openai import AzureOpenAI
from PyPDF2 import PdfReader
import uuid
import tiktoken
import re
from dotenv import load_dotenv


load_dotenv()

# Azure configuration
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_BLOB_CONNECTION_STRING = os.getenv("AZURE_BLOB_CONNECTION_STRING")
INDEX_NAME = "rag-index"
CONTAINER_NAME = "documents"
MODEL_NAME = "gpt-4o-mini"

# Initialize clients
search_client = SearchClient(AZURE_SEARCH_ENDPOINT, INDEX_NAME, AzureKeyCredential(AZURE_SEARCH_KEY))
blob_service_client = BlobServiceClient.from_connection_string(AZURE_BLOB_CONNECTION_STRING)
openai_client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_KEY,
    api_version="2024-02-15-preview"
)





def query_rag(question):
    """Perform RAG query using Azure AI Search and OpenAI."""
    try:
        # Search for relevant chunks
        search_results = search_client.search(search_text=question, top=3)
        context = ""
        for result in search_results:
            context += result["content"] + "\n"
        
        # Generate response
        prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
        response = openai_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful assistant,assist the use with alltheir queries, greet them"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content, "Success"
    except Exception as e:
        return None, f"Error generating answer: {str(e)}"