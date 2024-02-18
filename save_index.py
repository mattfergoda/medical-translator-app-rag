import logging
import sys
import os
import json

from llama_index.core import DocumentSummaryIndex, StorageContext, Settings
from llama_index.readers.web import SimpleWebPageReader
from llama_index.embeddings.huggingface  import HuggingFaceEmbedding
import openai
from dotenv import load_dotenv

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

load_dotenv()


openai.api_key = os.environ["OPENAI_API_KEY"]

Settings.embed_model = HuggingFaceEmbedding(model_name="WhereIsAI/UAE-Large-V1")

with open('urls.json', 'r') as file:
    urls = json.load(file)

for category, urls in urls.items():
    documents = SimpleWebPageReader(html_to_text=True).load_data(urls)
    summary_query = """
    Please summarize the following article about a medical disease, symptom, or 
    procedure.
    Please leave out any information about the Mayo Clinic or its website or any 
    other information not relevant to the main topic of the article.
    """
    index = DocumentSummaryIndex.from_documents(
        documents, 
        summary_query=summary_query
        )
    index.storage_context.persist(persist_dir=f"./storage/{category}")

# query_engine = index.as_query_engine()
# response = query_engine.query("What is atrial fibrillation?")

# print(response)