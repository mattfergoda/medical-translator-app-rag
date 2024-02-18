import re

import requests
from bs4 import BeautifulSoup
import psycopg2
from llama_index.embeddings.huggingface  import HuggingFaceEmbedding

URLS = [
    "https://www.health.harvard.edu/a-through-c",
    "https://www.health.harvard.edu/d-through-i",
    "https://www.health.harvard.edu/j-through-p",
    "https://www.health.harvard.edu/q-through-z",
]

EMBED_MODEL = HuggingFaceEmbedding(
    model_name="WhereIsAI/UAE-Large-V1"  # open-source embedding model
)

conn = psycopg2.connect("dbname=medical_translator_app user=Matt")
cur = conn.cursor()
cur.execute(
    """
    CREATE EXTENSION IF NOT EXISTS vector;
    DROP TABLE IF EXISTS medical_terms;
    CREATE TABLE medical_terms (
        term VARCHAR(100) not null,
        definition VARCHAR(1000) not null,
        embedding vector(1024) not null,
        inserted_at TIMESTAMP WITH TIME ZONE DEFAULT now()
    );
    """
)


for url in URLS:
    page = requests.get(url)

    soup = BeautifulSoup(page.content, "html.parser")

    title_pattern = re.compile(r'<p><strong>(.*?): </strong>(.*?)</p>')
    remove_pattern = re.compile(r'^<a name="_GoBack"></a>\s*')

    # Find all the strong tags matching the pattern
    paragraphs = soup.find_all("p")

    # Extract and print the titles and corresponding definitions
    for paragraph in paragraphs:
        match = title_pattern.search(str(paragraph))
        if match:
            title = re.sub(remove_pattern, '', match.group(1))
            definition = match.group(2)
            embedding = EMBED_MODEL.get_text_embedding(f"{title} refers to {definition}")

            cur.execute(
                """
                INSERT INTO medical_terms (term, definition, embedding) 
                    VALUES (%s, %s, %s)
                """,
                (title, definition, embedding)
            )


cur.close()
conn.commit()
conn.close()