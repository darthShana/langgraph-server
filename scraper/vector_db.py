import os
import time

import uuid
import copy

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

from scraper.vehicle_listing import VehicleListing
from pinecone import Pinecone
import multiprocessing
# Force the 'spawn' method which is more compatible
multiprocessing.set_start_method('spawn', force=True)

class VectorDB:

    pinecone = Pinecone(api_key=os.environ["PINECONE_API_KEY"], environment=os.environ["PINECONE_ENVIRONMENT_REGION"])
    index = pinecone.Index("turners-sample-stock")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large", dimensions=2048)

    def __init__(self):
        pass

    def save(self, listing: VehicleListing, doc: Document):
        doc.metadata.update(listing.metadata.dict(exclude_none=True))

        docs = [
            Document(page_content=listing.manufacturer_details, metadata=copy.deepcopy(doc.metadata)),
            Document(page_content=listing.feature_details, metadata=copy.deepcopy(doc.metadata)),
            Document(page_content=listing.condition_details, metadata=copy.deepcopy(doc.metadata)),
            Document(page_content=listing.possible_uses, metadata=copy.deepcopy(doc.metadata)),
            Document(page_content=listing.other, metadata=copy.deepcopy(doc.metadata))
        ]
        ids = [doc.metadata['source'] + str(uuid.uuid4()) for doc in docs]

        BATCH_SIZE = 50
        for i in range(0, len(docs), BATCH_SIZE):
            batch_docs = docs[i:i + BATCH_SIZE]
            batch_ids = ids[i:i + BATCH_SIZE]
            PineconeVectorStore.from_documents(batch_docs, index_name="turners-sample-stock", embedding=self.embeddings,
                                               ids=batch_ids)
            time.sleep(0.5)

    def delete(self, doc: Document):
        for ids in self.index.list(prefix=doc['source']):
            print(ids)  # ['doc1#chunk1', 'doc1#chunk2', 'doc1#chunk3']
            self.index.delete(ids=ids)
