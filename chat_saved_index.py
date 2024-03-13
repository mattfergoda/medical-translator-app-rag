import logging
import sys
import os
import json

from llama_index.core import SummaryIndex, StorageContext, Settings, load_index_from_storage, get_response_synthesizer
from llama_index.core.indices.document_summary import (
    DocumentSummaryIndexEmbeddingRetriever,
)
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.embeddings.huggingface  import HuggingFaceEmbedding
from llama_index.agent.openai import OpenAIAgent
import openai
from dotenv import load_dotenv

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

load_dotenv()

openai.api_key = os.environ["OPENAI_API_KEY"]
Settings.embed_model = HuggingFaceEmbedding(model_name="WhereIsAI/UAE-Large-V1")

with open('urls.json', 'r') as file:
    urls = json.load(file)

index_set = {}
for category in urls.keys():
    storage_context = StorageContext.from_defaults(
        persist_dir=f"./storage/{category}"
    )
    index = load_index_from_storage(storage_context)
    index_set[category] = index
    
    
individual_query_engine_tools = [
    QueryEngineTool(
        query_engine=index_set[cat].as_query_engine(),
        metadata=ToolMetadata(
            name=f"doc_summary_index_{cat}",
            description=f"useful for when you want to answer queries about {cat}",
        ),
    )
    for cat in urls.keys()
]


# assemble query engine
query_engine = SubQuestionQueryEngine.from_defaults(query_engine_tools=individual_query_engine_tools)


query_engine_tool = QueryEngineTool(
    query_engine=query_engine,
    metadata=ToolMetadata(
        name="sub_question_query_engine",
        description="useful for when you want to answer queries that require considering diseases, symptoms, and procedures.",
    ),
)

tools = individual_query_engine_tools + [query_engine_tool]

system_prompt = """
    You are playing the role of a patient, medical expert. Please answer the following
    question from a patient in simple, straightforward language. If they ask you
    something that is not medical in nature, kindly let them know that is outside
    the scope of your functionality. Please use only the below resources to answer
    the patient question. If the answer isn't included in these resources, politely
    let the patient know that you don't know the answer, but they could always
    ask a doctor. 
"""

chat_history = []
agent = OpenAIAgent.from_tools(
    tools, 
    system_prompt=system_prompt,
    verbose=True
)

while True:
    text_input = input("User: ")
    if text_input == "exit":
        break
    response = agent.chat(text_input)
    print(f"Agent: {response}")