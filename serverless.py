import os

from dotenv import load_dotenv
from modal import Image, Secret, Stub, web_endpoint

from chat import chat

load_dotenv()

image = Image.debian_slim()
image = image.copy_local_dir("storage")
image = image.copy_local_dir("index")
image = image.pip_install(
    "llama_index",
    "openai",
    "python-dotenv",
    "llama-index-agent-openai==0.1.1",
    "llama-index-core==0.10.5",
    "llama-index-embeddings-huggingface==0.1.1",
    "llama-index-embeddings-openai==0.1.1",
    "llama-index-legacy==0.9.48",
    "llama-index-llms-openai==0.1.1",
    "llama-index-multi-modal-llms-openai==0.1.1",
    "llama-index-program-openai==0.1.1",
    "llama-index-question-gen-openai==0.1.1",
    "llama-index-readers-file==0.1.3",
    "llama-index-readers-web==0.1.5",
    "llama-index-vector-stores-postgres==0.1.1",
)

stub = Stub(
    name="medical-qa",
    image=image,
    secrets=[Secret.from_local_environ(os.environ)],
)


@stub.function()
@web_endpoint(method="GET")
def web(query: str):
    answer = chat(query)
    return {
        "answer": answer,
    }

@stub.function()
def cli(query: str):
    answer = chat(query)
    # Terminal codes for pretty-printing.
    bold, end = "\033[1m", "\033[0m"

    print(f"{bold}ANSWER:{end}")
    print(answer)

