import os

import voyageai
import uuid
import copy

from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from langchain_voyageai import VoyageAIEmbeddings

from scraper.vehicle_listing import VehicleListing
from pinecone import Pinecone


class VectorDB:

    vo = voyageai.Client()
    pinecone = Pinecone(api_key=os.environ["PINECONE_API_KEY"], environment=os.environ["PINECONE_ENVIRONMENT_REGION"])
    index = pinecone.Index("turners-sample-stock")
    embeddings = VoyageAIEmbeddings(voyage_api_key=os.environ["VOYAGE_API_KEY"], model="voyage-large-2")

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

        PineconeVectorStore.from_documents(docs, self.embeddings, index_name="turners-sample-stock", ids=ids)

    def delete(self, doc: Document):
        for ids in self.index.list(prefix=doc['source']):
            print(ids)  # ['doc1#chunk1', 'doc1#chunk2', 'doc1#chunk3']
            self.index.delete(ids=ids)
