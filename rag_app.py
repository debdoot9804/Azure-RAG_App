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

# Initialize tokenizer
tokenizer = tiktoken.get_encoding("cl100k_base")

def extract_text_from_pdf(file):
    """Extract text from a PDF file."""
    try:
        pdf = PdfReader(file)
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def chunk_text(text, max_tokens=500):
    """Split text into chunks based on token count."""
    paragraphs = re.split(r'\n{2,}|\.\s+', text)
    chunks = []
    current_chunk = ""
    current_tokens = 0

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        tokens = tokenizer.encode(paragraph)
        token_count = len(tokens)

        if current_tokens + token_count <= max_tokens:
            current_chunk += paragraph + "\n"
            current_tokens += token_count
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = paragraph + "\n"
            current_tokens = token_count

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def upload_and_index_document(file, filename):
    """Upload PDF to Blob Storage and index chunks in Azure AI Search."""
    try:
        # Upload to Blob Storage
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=filename)
        blob_client.upload_blob(file, overwrite=True)
        
        # Extract text
        file.seek(0)
        text = extract_text_from_pdf(file)
        if "Error" in text:
            return 0, text
        
        # Chunk text
        chunks = chunk_text(text, max_tokens=500)
        
        # Index each chunk
        documents = []
        for i, chunk in enumerate(chunks):
            document = {
                "id": f"{uuid.uuid4()}_{i}",
                "content": chunk,
                "filename": filename,
                "chunk_index": i
            }
            documents.append(document)
        
        search_client.upload_documents(documents=documents)
        return len(documents), "Success"
    except Exception as e:
        return 0, f"Error uploading and indexing: {str(e)}"

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