import asyncio
import os
import time

from pinecone import Pinecone

import bs4
import voyageai
from langchain_community.document_loaders import WebBaseLoader
from langchain_voyageai import VoyageAIEmbeddings
from langchain_pinecone import PineconeVectorStore

from langchain_text_splitters import RecursiveCharacterTextSplitter


async def load_faq_page(page_urls):

    loader = WebBaseLoader(
        web_paths=page_urls,
        bs_kwargs = {
            "parse_only": bs4.SoupStrainer(class_="main"),
        }
    )
    docs = []
    async for doc in loader.alazy_load():
        docs.append(doc)

    return docs


vo = voyageai.Client()
pinecone = Pinecone(api_key=os.environ["PINECONE_API_KEY"], environment=os.environ["PINECONE_ENVIRONMENT_REGION"])
embeddings = VoyageAIEmbeddings(voyage_api_key=os.environ["VOYAGE_API_KEY"], model="voyage-3-large", batch_size=50, output_dimension=2048)

docs = asyncio.run(load_faq_page([
    "https://www.turners.co.nz/Cars/how-to-buy/how-to-buy-faqs/",
    "https://www.turners.co.nz/Cars/sell-your-car/selling-your-car-faqs/",
    "https://www.turners.co.nz/Turners-Live/"
]))
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=0,
    separators=["\n\n\n"]
)

vector_store = PineconeVectorStore(
    index_name="turners-faq",
    embedding=embeddings
)

for doc in docs:
    texts = text_splitter.create_documents([doc.page_content])
    BATCH_SIZE = 50
    for i in range(0, len(texts), BATCH_SIZE):
        batch_docs = texts[i:i + BATCH_SIZE]
        vector_store.add_documents(batch_docs)
        time.sleep(0.5)

print("All documents processed successfully!")